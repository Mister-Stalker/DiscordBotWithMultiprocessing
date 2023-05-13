import asyncio
import traceback

import discord.ext
from discord.ext import commands, tasks

from discord_ext.worker.worker_bot import WorkerBot


class Cog(commands.Cog):
    def __init__(self, bot: WorkerBot) -> None:
        self.bot: WorkerBot = bot
        super().__init__()

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.logger.info("initialize")
        self.sender_loop.start()

    @commands.command()
    async def ping(self, ctx: discord.ext.commands.Context):
        # simple ping command (#wpping)
        await asyncio.sleep(2 * self.bot.number)  # sleep
        await ctx.send(f'{self.bot.name} ping: {round(self.bot.latency, 4)}s')

    @tasks.loop(seconds=0.05)
    async def sender_loop(self) -> None:
        try:
            if not self.bot.work_q.empty():
                try:
                    task = self.bot.work_q.get(timeout=1)  # get task from  queue
                except Exception:
                    return
                if task["type"] == "app_command":  # if it is app_command
                    task = task["task"]
                    interaction_data = task["args"][0]

                    # noinspection PyProtectedMember
                    interaction = discord.Interaction(data=interaction_data, state=self.bot.connection)

                    self.bot.logger.info(f"start function {task['function'].__name__}")

                    coro = task["function"](self.bot, interaction, *task["args"][1:], **task.get("kwargs", {}))
                    await coro
                elif task["type"] == "standard_command":  # if it is standard command (commands.command)
                    task = task["task"]
                    message_data = task["args"][0]
                    message = discord.Message(state=self.bot.connection,
                                              data=message_data["data"],
                                              channel=self.bot.get_channel(message_data["channel_id"], )
                                              )
                    ctx = discord.ext.commands.Context(message=message, bot=self.bot, view=message_data["view"])
                    coro = task["function"](self.bot, ctx, *task["args"][1:], **task.get("kwargs", {}))

                    try:
                        await coro
                    except Exception:
                        self.bot.logger.error("Error in coro", tb=traceback.format_exc())

        except Exception as e:
            self.bot.logger.error(exc=traceback.format_exc())

    @commands.Cog.listener("on_error")
    async def on_error(self, event, *args, **kwargs):
        if isinstance(event, discord.ext.commands.CommandNotFound):
            ...
        else:
            raise event
