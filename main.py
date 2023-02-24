import multiprocessing

import bot
import logger_bot
from discord_ext import configs, logger, message_sender, worker_proceses
from discord_ext import function_manager as fm

# fast settings
SUB_BOTS_COUNT = 2  # count of sub bots (worker processes)


def main():
    # create main manager

    manager = multiprocessing.Manager()

    # create main_namespace, queues, manages and other

    # proxy
    main_namespace = manager.Namespace()
    configs_proxy = manager.dict()
    configs_manager = configs.ConfigsManager(configs_proxy=configs_proxy)
    configs.init_configs(configs_proxy=configs_proxy)

    # loggers
    logger_queue = manager.Queue()
    main_namespace.logger_queue = logger_queue
    main_logger = logger.create_logger(configs_manager=configs_manager,
                                       name="main",
                                       q=logger_queue)
    fm_logger = logger.create_logger(configs_manager=configs_manager,
                                     name="function manager",
                                     q=logger_queue)
    logger_bot_logger = logger.create_logger(configs_manager=configs_manager,
                                             name="logger",
                                             q=logger_queue)

    # sender
    sender_queue = manager.Queue()
    main_namespace.sender_queue = sender_queue
    sender = message_sender.Sender(q=sender_queue)

    # function manager
    function_manager = fm.FunctionManager(sender=sender, _logger=fm_logger)

    worker_queue = manager.Queue()
    main_namespace.worker_queue = worker_queue
    # create kwargs for processes

    kwargs = dict(
        manager=None,
        queues=main_namespace,
        configs_proxy=configs_proxy,
        configs_manager=configs_manager,
        logger_queue=logger_queue,
        logger_bot_logger=logger_bot_logger,
        main_logger=main_logger,
        sender_queue=sender_queue,
        sender=sender,
        function_manager=function_manager,
        log_q=logger_queue,
        worker_queue=worker_queue,
    )

    # create processes

    processes = [
        # main bot process
        multiprocessing.Process(target=bot.main, kwargs=kwargs, name="main_bot_thread"),
        # logger bot process
        multiprocessing.Process(target=logger_bot.main, kwargs=kwargs, name="main_bot_thread"),
    ]
    processes.extend(worker_proceses.get_procs(count=SUB_BOTS_COUNT,
                                               worker_q=worker_queue,
                                               bot_token=configs.get_json("bot_configs.json5")["token"],
                                               logger_q=logger_queue,
                                               configs_manager=configs_manager))
    [p.start() for p in processes]
    [p.join() for p in processes]


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
