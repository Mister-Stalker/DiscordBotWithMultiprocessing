import asyncio
import time
import traceback

import discord
from discord.ext import commands, tasks

import discord_ext.bot as _bot


async def some_cpu_test(interaction: discord.Interaction, bot, n=1000000, ):
    # print("some cpu test")
    sn = n
    t = time.time()
    while n:
        n -= 1
    await interaction.edit_original_response(content=f"some cpu test ({sn}) end in {time.time() - t:4f}s in {bot.name}")


class TestCog(commands.GroupCog, name="test"):
    def __init__(self, bot) -> None:
        self.bot = bot
        super().__init__()

    @discord.app_commands.command(name="test")
    async def test_t(self, interaction: discord.Interaction):
        # print(interaction)
        self.bot.worker_queue.put({
            "type": "app_command",
            "task": {
                "function": some_cpu_test,
                "args": [interaction.interaction_data, 500000000],
            }
        })
        await interaction.response.send_message("its work!", ephemeral=True)


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
        # try:
        #     a = 1 / 0
        # except:
        #     self.bot.logger.error(exc=traceback.format_exc())

    @commands.command()
    async def init(self, ctx: discord.ext.commands.Context):
        self.bot.tree.copy_global_to(guild=ctx.guild)
        await self.bot.tree.sync(guild=ctx.guild)
        await ctx.send(f"command initialized!")

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
    await bot.add_cog(TestCog(bot))
