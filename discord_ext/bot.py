import multiprocessing

from discord.ext import commands

from discord_ext import message_sender, configs


class Bot(commands.Bot):

    def __init__(self,
                 sender,
                 function_manager,
                 manager,
                 configs_manager: configs.ConfigsManager,
                 logger_queue: multiprocessing.Queue,
                 logger,
                 queues,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sender: message_sender.Sender = sender
        self.sender_q = sender.q
        self.function_manager = function_manager
        self.manager = manager
        self.configs_manager = configs_manager
        self.logger = logger
        self.logger_queue = logger_queue
        self.queues = queues
        self.logger_channel = self.logger.log_channels["default"]
