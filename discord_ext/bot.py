import multiprocessing

from discord.ext import commands

from discord_ext import message_sender, configs, function_manager, logger


class Bot(commands.Bot):

    def __init__(self,
                 sender: message_sender.Sender,
                 f_manager: function_manager.FunctionManager,
                 configs_manager: configs.ConfigsManager,
                 logger_queue: multiprocessing.Queue,
                 logger_: logger.Logger,
                 queues,
                 worker_queue: multiprocessing.Queue,
                 *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.queues = queues

        self.sender: message_sender.Sender = sender
        self.sender_q = sender.q

        self.function_manager = f_manager
        self.configs_manager = configs_manager

        self.logger = logger_
        self.logger_queue = logger_queue
        self.logger_channel = self.logger.log_channels["default"]

        self.worker_queue = worker_queue
