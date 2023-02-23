import asyncio
import traceback

import discord
import json5 as json
from discord.ext import commands, tasks

from discord_ext import logger


class Cog(commands.Cog):
    def __init__(self, bot: logger.LoggingBot) -> None:
        self.bot: logger.LoggingBot = bot
        super().__init__()

    @commands.Cog.listener()
    async def on_ready(self):
        # self.bot.sender.send_message(channel=self.bot.logger_channel, message="Logger bot running!")
        self.bot.logger.info("initialize")

        # os.system('color')
        # print(termcolor.colored("logger бот запущен и готов к работе", "blue"))

        self.sender_loop.start()

    @commands.command()
    async def ping(self, ctx: discord.ext.commands.Context):

        await ctx.send(f'bot ping {round(self.bot.latency, 4)}s. This is a "logger" bot')

    async def parse_command(self, d: dict) -> None:

        # initialize views

        if "kwargs" in d["body"].keys():
            if "view" in d["body"]["kwargs"].keys():
                if type(d["body"]["kwargs"]["view"]) == type:
                    d["body"]["kwargs"]["view"] = d["body"]["kwargs"]["view"]()
                else:
                    d["body"]["kwargs"]["view"].init()

        # send
        match d["type"]:
            case "send_mess":
                for c, mess in d["body"].items():
                    try:
                        if "embed" in mess.keys():
                            mess["embed"].set_author(name=f"Logger", icon_url=self.bot.user.avatar.url)
                        print(c, mess)
                        await self.bot.get_channel(int(c)).send(**mess)
                    except:
                        traceback.print_exc()
                        pass

    @tasks.loop(seconds=0.5)
    async def sender_loop(self) -> None:
        while not self.bot.q.empty():
            t = self.bot.q.get()
            try:

                print(f"[sender_loop] send {t}")
            except:
                print(f"[sender_loop] send (can`t print)")
            try:
                await self.parse_command(t)
            except:
                self.bot.logger.error(f"Error in sender_loop \n {traceback.format_exc()}")
                traceback.print_exc()


async def load_ext(bot: logger.LoggingBot):
    await bot.add_cog(Cog(bot=bot))


def main(log_q, logger_bot_logger, configs_manager, **kwargs):
    bot = logger.LoggingBot(
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
