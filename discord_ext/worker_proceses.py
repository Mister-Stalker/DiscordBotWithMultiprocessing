import time
import traceback
import asyncio
import multiprocessing

import discord
from discord.ext import commands, tasks

from discord_ext import configs, logger


class WorkerBot(commands.Bot):
    def __init__(self,
                 work_q,
                 logger_,
                 name,
                 number,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.work_q: multiprocessing.Queue = work_q
        self.logger = logger_
        self.logger_queue = logger_.q
        self.logger_channel = self.logger.log_channels["default"]
        self.name = name
        self.number = number

        async def on_error(*_):
            pass

        self.tree.on_error = on_error  # disable app_commands errors

    async def on_command_error(self, context, exception) -> None:
        ...

    async def on_error(self, event_method, *args, **kwargs):
        ...


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
        await asyncio.sleep(2 * self.bot.number)
        await ctx.send(f'{self.bot.name} ping: {round(self.bot.latency, 4)}s')

    @tasks.loop(seconds=0.05)
    async def sender_loop(self) -> None:
        try:
            if not self.bot.work_q.empty():
                task = self.bot.work_q.get(timeout=1)  # get task from  queue
                if task["type"] == "app_command":  # if it is app_command
                    task = task["task"]
                    interaction_data = task["args"][0]
                    interaction = discord.Interaction(data=interaction_data, state=self.bot._connection)

                    self.bot.logger.info(f"start function {task['function'].__name__}")

                    coro = task["function"](interaction, self.bot, *task["args"][1:], **task.get("kwargs", {}))
                    await coro

        except Exception as e:
            self.bot.logger.error(tb=traceback.format_exc())

    @commands.Cog.listener("on_error")
    async def on_error(self, event, *args, **kwargs):
        if isinstance(event, discord.ext.commands.CommandNotFound):
            ...
        else:
            raise event


def worker_process(name: str,
                   process_num,
                   worker_q: multiprocessing.Queue,
                   configs_manager: configs.ConfigsManager,
                   logger_q: multiprocessing.Queue,
                   bot_token):
    """
    this is a bot subprocess
    :param process_num:
    :param name:
    :param worker_q:
    :param configs_manager:
    :param logger_q:
    :param bot_token:
    :return:
    """
    time.sleep(5*(process_num+1))  # sleep for correct work
    logger_ = logger.create_logger(configs_manager=configs_manager, q=logger_q, name=name)
    bot = WorkerBot(work_q=worker_q,
                    logger_=logger_,
                    name=name,
                    number=process_num,
                    # discord settings
                    command_prefix="#wp",
                    intents=discord.Intents.all())

    asyncio.run(bot.add_cog(Cog(bot)))
    bot.run(bot_token)


def get_procs(count: int, worker_q: multiprocessing.Queue, bot_token, configs_manager, logger_q):
    procs = []
    for i in range(count):
        procs.append(multiprocessing.Process(target=worker_process,
                                             kwargs=dict(name=f"worker_process_{i}",
                                                         process_num=i,
                                                         worker_q=worker_q,
                                                         bot_token=bot_token,
                                                         logger_q=logger_q,
                                                         configs_manager=configs_manager),
                                             name=f"worker_process_{i}"))
    return procs
