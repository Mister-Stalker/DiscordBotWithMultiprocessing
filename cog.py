import asyncio
import traceback

import discord
from discord.ext import commands, tasks

import discord_ext.bot as _bot


class Cog(commands.Cog):
    def __init__(self, bot: _bot.Bot) -> None:
        self.bot: _bot.Bot = bot
        super().__init__()

    @commands.Cog.listener()
    async def on_ready(self):
        # self.bot.sender.send_message(channel=self.bot.logger_channel, message="Main bot running!")
        self.bot.logger.info("initialize")

        self.sender_loop.start()

    @commands.command()
    async def ping(self, ctx: discord.ext.commands.Context):

        await ctx.send(f"bot ping {round(self.bot.latency, 4)}s")
        try:
            a = 1 / 0
        except:
            self.bot.logger.error(exc=traceback.format_exc())

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
                        await self.bot.get_channel(int(c)).send(**mess)
                    except:
                        pass

    @tasks.loop(seconds=0.1)
    async def sender_loop(self) -> None:
        while not self.bot.sender_q.empty():
            t = self.bot.sender_q.get()
            try:

                self.bot.logger.info(f"parse {t}")
            except Exception as e:
                self.bot.logger.warning(f"parse (can`t print) {e}")
            try:
                await self.parse_command(t)
            except:
                self.bot.logger.error(f"Error in sender_loop \n {traceback.format_exc()}")

            await asyncio.sleep(0.05)  # for correct work


async def setup(bot: _bot.Bot) -> None:
    await bot.add_cog(Cog(bot))
