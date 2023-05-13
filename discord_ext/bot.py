import multiprocessing

from discord.ext import commands

import discord_ext


class Bot(commands.Bot):
    """
    стандартный бот из Discord.py, но с дополнительными полями
    """

    def __init__(self,
                 sender: discord_ext.Sender,
                 f_manager: discord_ext.FunctionManager,
                 configs_manager: discord_ext.ConfigsManager,
                 logger_queue: multiprocessing.Queue,
                 logger_: discord_ext.logger.Logger,
                 queues,
                 worker_queue: multiprocessing.Queue,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.queues = queues

        self.sender: discord_ext.Sender = sender
        self.sender_q = sender.q

        self.function_manager = f_manager
        self.configs_manager = configs_manager

        self.logger = logger_
        self.logger_queue = logger_queue
        self.logger_channel = self.logger.log_channels["default"]

        self.worker_queue = worker_queue

    @property
    def connection(self):
        return self._connection
