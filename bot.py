"""
создание основного бота
"""

import asyncio
import multiprocessing

import json5 as json
import discord
from discord.ext import commands
import discord_ext

cogs_folder = "extensions"
extensions_folder = "extensions"


async def load_ext(bot: discord_ext.Bot):
    """
    подключение расширений
    cogs - список Cog для бота
    extensions - список подключаемых функций
    :param bot:
    :return:
    """
    cogs = ["cog", "test_cog"]
    extensions = ["test_cog_funcs"]
    [await bot.load_extension(f"{cogs_folder}.{cog}") for cog in cogs]
    [bot.function_manager.load_extension(f"{extensions_folder}.{extension}") for extension in extensions]


def main(sender: discord_ext.Sender,
         function_manager: discord_ext.FunctionManager,
         configs_manager: discord_ext.ConfigsManager,
         logger_queue: multiprocessing.Queue,
         main_logger: discord_ext.logger.Logger,
         worker_queue: multiprocessing.Queue,
         queues,
         **kwargs):
    """
    Процесс основного бота
    :param sender:
    :param function_manager:
    :param configs_manager:
    :param logger_queue:
    :param main_logger:
    :param worker_queue:
    :param queues:
    :param kwargs:
    :return:
    """
    bot = discord_ext.Bot(sender=sender,
                          f_manager=function_manager,
                          configs_manager=configs_manager,
                          logger_queue=logger_queue,
                          logger_=main_logger,
                          queues=queues,
                          # discord Bot settings
                          command_prefix=commands.when_mentioned_or('-'),
                          case_insensitive=True,
                          worker_queue=worker_queue,
                          intents=discord.Intents.all()
                          )

    asyncio.run(load_ext(bot))
    bot.run(json.load(open("bot_configs.json5", encoding="UTF-8"), encoding="UTF-8")["token"])
