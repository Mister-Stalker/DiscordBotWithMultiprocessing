import traceback

import discord
from discord.ext import commands, tasks


class Cog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        super().__init__()

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.logger.info("initialize")
        self.sender_loop.start()

    @commands.Cog.listener("on_error")
    async def on_error(self, event, *args, **kwargs):
        if isinstance(event, discord.ext.commands.CommandNotFound):
            ...
        else:
            raise event

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
                        # print(c, mess)
                        await self.bot.get_channel(int(c)).send(**mess)
                    except Exception:
                        traceback.print_exc()
                        pass

    @tasks.loop(seconds=0.5)
    async def sender_loop(self) -> None:
        while not self.bot.q.empty():
            t = self.bot.q.get()
            try:
                await self.parse_command(t)
            except Exception:
                self.bot.logger.error(f"Error in sender_loop", tb=traceback.format_exc())
