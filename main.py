import multiprocessing

import bot
import discord_ext

# fast settings
SUB_BOTS_COUNT = 2  # count of sub bots (worker processes)

"""
Универсальные обозначения

подключение функций к командам - подключение функции которая будет выполнена доп ботом в отдельном процессе после выполнения команды

sub-bot/worker_bot/worker - дополнительный бот для выполнения команд
logger_queue/logger_q - очередь на отправку лог сообщений 
sender_queue/sender_q  - очередь на отправку сообщений основного бота
worker_queue/worker_q - очередь команд для выполнения доп ботами

queues - Namespace с очередями (sender_queue, worker_queue, logger_queue)

sender - обертка для sender_q для удобства
logger - логгер  

function_manager - менеджер функции (подключает функции, выполняемые доп ботами, к командам)

configs_proxy - общий словарь (прокси) для конфигов 





"""


def main():
    # create main manager

    manager = multiprocessing.Manager()

    # create main_namespace, queues, manages and other

    # proxy
    main_namespace = manager.Namespace()
    configs_proxy = manager.dict()
    configs_manager = discord_ext.ConfigsManager(configs_proxy=configs_proxy)
    discord_ext.configs.init_configs(configs_proxy=configs_proxy)

    # loggers
    logger_queue = manager.Queue()
    main_namespace.logger_queue = logger_queue
    main_logger = discord_ext.logger.create_logger(configs_manager=configs_manager,
                                                   name="main",
                                                   q=logger_queue)
    fm_logger = discord_ext.logger.create_logger(configs_manager=configs_manager,
                                                 name="function manager",
                                                 q=logger_queue)
    logger_bot_logger = discord_ext.logger.create_logger(configs_manager=configs_manager,
                                                         name="logger",
                                                         q=logger_queue)

    # sender
    sender_queue = manager.Queue()
    main_namespace.sender_queue = sender_queue
    sender = discord_ext.Sender(q=sender_queue)

    # function manager
    function_manager = discord_ext.FunctionManager(sender=sender, logger=fm_logger)

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
        multiprocessing.Process(target=discord_ext.logger.logger_bot.main, kwargs=kwargs, name="main_bot_thread"),
    ]
    # add worker bot processes
    processes.extend(discord_ext.worker.get_procs(count=SUB_BOTS_COUNT,
                                                  worker_q=worker_queue,
                                                  bot_token=discord_ext.configs.get_json("bot_configs.json5")["token"],
                                                  logger_q=logger_queue,
                                                  configs_manager=configs_manager))
    [p.start() for p in processes]
    [p.join() for p in processes]


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
