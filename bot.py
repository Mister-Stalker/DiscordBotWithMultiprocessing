import asyncio
import multiprocessing

import discord
from discord.ext import commands
import json5 as json

from discord_ext import configs
from discord_ext import bot as _bot


async def load_ext(bot: _bot.Bot):
    cogs = ["cog"]
    extensions = ["thread_funcs"]
    [await bot.load_extension(cog) for cog in cogs]
    [bot.function_manager.load_extension(extension) for extension in extensions]


def main(sender,
         function_manager,
         manager,
         configs_manager: configs.ConfigsManager,
         logger_queue: multiprocessing.Queue,
         main_logger,
         queues, **kwargs):
    bot = _bot.Bot(sender=sender,
                   function_manager=function_manager,
                   manager=manager,
                   configs_manager=configs_manager,
                   logger_queue=logger_queue,
                   logger=main_logger,
                   queues=queues,
                   # discord Bot settings
                   command_prefix=commands.when_mentioned_or('-'),
                   case_insensitive=True,
                   intents=discord.Intents.all()
                   )

    asyncio.run(load_ext(bot))
    bot.run(json.load(open("bot_configs.json5", encoding="UTF-8"), encoding="UTF-8")["token"])
