import asyncio
import multiprocessing

import json5 as json
import discord
from discord.ext import commands

from discord_ext import configs, logger, message_sender
from discord_ext import bot as _bot
from discord_ext import function_manager as fm


async def load_ext(bot: _bot.Bot):
    cogs = ["cog"]
    extensions = ["thread_funcs"]
    [await bot.load_extension(cog) for cog in cogs]
    [bot.function_manager.load_extension(extension) for extension in extensions]


def main(sender: message_sender.Sender,
         function_manager: fm.FunctionManager,
         configs_manager: configs.ConfigsManager,
         logger_queue: multiprocessing.Queue,
         main_logger: logger.Logger,
         worker_queue: multiprocessing.Queue,
         queues,
         **kwargs):

    bot = _bot.Bot(sender=sender,
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
