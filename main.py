import multiprocessing
import time

import bot
import logger_bot
from discord_ext import configs, logger, message_sender
from discord_ext import function_manager as fm


def test(conf_proxy):
    print(conf_proxy.config_proxy)
    print(type(conf_proxy.config_proxy))
    time.sleep(1)
    print(conf_proxy.config_proxy)
    time.sleep(1)
    print(conf_proxy.config_proxy)


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
    sender = message_sender.Sender(q=sender_queue)

    # function manager
    function_manager = fm.FunctionManager(sender=sender, _logger=fm_logger)

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

    )

    # create processes

    processes = [
        # main bot process
        multiprocessing.Process(target=bot.main, kwargs=kwargs, name="main_bot_thread"),
        # logger bot process
        multiprocessing.Process(target=logger_bot.main, kwargs=kwargs, name="main_bot_thread"),
    ]

    [p.start() for p in processes]
    [p.join() for p in processes]


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
