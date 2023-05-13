import multiprocessing

from discord.ext import commands

from discord_ext import logger


class WorkerBot(commands.Bot):
    def __init__(self,
                 work_q,
                 logger_,
                 name,
                 number,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.work_q: multiprocessing.Queue = work_q
        self.logger: logger.Logger = logger_
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

    @property
    def connection(self):
        return self._connection