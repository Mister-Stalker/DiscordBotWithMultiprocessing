import asyncio
import multiprocessing

import discord
import discord.ext
import json5 as json
from discord.ext import commands



class LoggingBot(discord.ext.commands.Bot):
    def __init__(self,
                 log_q: multiprocessing.Queue,
                 logger,
                 configs_manager,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.q = log_q
        self.logger = logger
        self.configs_manager = configs_manager,


async def load_ext(bot: LoggingBot):
    from discord_ext.logger import logger_bot_cog
    await bot.add_cog(logger_bot_cog.Cog(bot=bot))


def main(log_q, logger_bot_logger, configs_manager, **kwargs):
    bot = LoggingBot(
        log_q=log_q,
        logger=logger_bot_logger,
        configs_manager=configs_manager,
        # discord Bot settings
        command_prefix=commands.when_mentioned_or('#'),
        case_insensitive=True,
        intents=discord.Intents.all()
    )

    asyncio.run(load_ext(bot))
    bot.run(json.load(open("bot_configs.json5", encoding="UTF-8"), encoding="UTF-8")["logger_token"])

