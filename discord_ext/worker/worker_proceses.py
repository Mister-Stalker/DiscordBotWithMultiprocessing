import asyncio
import multiprocessing
import time

import discord

from discord_ext import configs, logger
from discord_ext.worker.worker_bot import WorkerBot
from discord_ext.worker.worker_bot_cog import Cog


def worker_process(name: str,
                   process_num,
                   worker_q: multiprocessing.Queue,
                   configs_manager: configs.ConfigsManager,
                   logger_q: multiprocessing.Queue,
                   bot_token):
    """
    this is a bot subprocess
    :param process_num:
    :param name:
    :param worker_q:
    :param configs_manager:
    :param logger_q:
    :param bot_token:
    :return:
    """
    time.sleep(5*(process_num+1))  # sleep for correct work
    logger_ = logger.create_logger(configs_manager=configs_manager, q=logger_q, name=name)
    bot = WorkerBot(work_q=worker_q,
                    logger_=logger_,
                    name=name,
                    number=process_num,
                    # discord settings
                    command_prefix="#wp",
                    intents=discord.Intents.all())

    asyncio.run(bot.add_cog(Cog(bot)))
    bot.run(bot_token)


def get_procs(count: int, worker_q: multiprocessing.Queue, bot_token, configs_manager, logger_q):
    procs = []
    for i in range(count):
        procs.append(multiprocessing.Process(target=worker_process,
                                             kwargs=dict(name=f"worker_process_{i}",
                                                         process_num=i,
                                                         worker_q=worker_q,
                                                         bot_token=bot_token,
                                                         logger_q=logger_q,
                                                         configs_manager=configs_manager),
                                             name=f"worker_process_{i}"))
    return procs
