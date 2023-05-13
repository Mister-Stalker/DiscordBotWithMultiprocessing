import asyncio
import traceback

import discord
from discord.ext import commands, tasks

import discord_ext


class Cog(commands.Cog):
    """
    Cog для основного бота:
        команда ping
        команда init (синхронизация слеш команд)
        отправка сообщений из очереди
        обработка on_ready
    """

    def __init__(self, bot: discord_ext.Bot) -> None:
        self.bot: discord_ext.Bot = bot
        super().__init__()

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.logger.info("initialize")  # сообщение о запуске
        self.sender_loop.start()  # запускаем цикл обработки очереди

    @commands.command()
    async def ping(self, ctx: discord.ext.commands.Context):
        await ctx.send(f"bot ping {round(self.bot.latency, 4)}s")

    @commands.command()
    async def init(self, ctx: discord.ext.commands.Context):
        self.bot.tree.copy_global_to(guild=ctx.guild)
        await self.bot.tree.sync(guild=ctx.guild)
        await ctx.send(f"command initialized!")

    async def parse_command(self, d: dict) -> None:

        # initialize views
        if "kwargs" in d["body"].keys():
            if "view" in d["body"]["kwargs"].keys():
                if isinstance(d["body"]["kwargs"]["view"], type):  # если передан класс view
                    d["body"]["kwargs"]["view"] = d["body"]["kwargs"]["view"]()
                else:  # если передан объект у которого надо вызвать .init()
                    d["body"]["kwargs"]["view"].init()

        # send
        match d["type"]:
            case "send_mess":
                for c, mess in d["body"].items():
                    await self.bot.get_channel(int(c)).send(**mess)

    @tasks.loop(seconds=0.1)
    async def sender_loop(self) -> None:
        while not self.bot.sender_q.empty():  # while sender_q is not empty
            t = self.bot.sender_q.get()  # get task from queue
            try:
                self.bot.logger.info(f"parse {t}")  # log
            except Exception as e:
                self.bot.logger.info(f"parse (can`t print) {e}")  # log if can`t print
            try:

                await self.parse_command(t)
            except Exception:
                # handle error
                self.bot.logger.error(f"Error in sender_loop \n {traceback.format_exc()}")

            await asyncio.sleep(0.05)  # for correct work


async def setup(bot: discord_ext.Bot) -> None:
    await bot.add_cog(Cog(bot))
