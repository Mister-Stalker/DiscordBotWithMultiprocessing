import multiprocessing

import json5 as json
import discord.ext.commands

from discord_ext import configs

# some variables :)
NOTHING = 0
ERROR = 1
WARNING = 2
INFO = 3


class Logger:
    __slots__ = ["q", "debug_level", "name", "show_prints", "send_to_discord", "log_channels"]

    def __init__(self,
                 log_channels: dict = None,
                 q: multiprocessing.Queue = None,
                 name: str = "MAIN",
                 debug_level: int = ERROR,
                 show_prints: bool = True,
                 send_to_discord: bool = True,
                 ):
        """

        :param log_channels: discord log channels by levels
        :param q: Queue for send messages to discord
        :param name: name of logger
        :param debug_level: debug level
        :param show_prints: need show prints?
        :param send_to_discord: need send to discord?

        :type log_channels: dict
        :type q: multiprocessing.Queue
        :type name: str
        :type debug_level: int
        :type show_prints: bool
        :type send_to_discord: bool
        """
        self.q = q
        self.debug_level: int = debug_level
        self.name = name
        self.show_prints = show_prints
        self.send_to_discord = send_to_discord
        self.log_channels = log_channels if log_channels is not None else {}

    def _send_message(self,
                      channel: int,
                      message=None, *_, **kwargs):
        self.q.put(
            {
                "type": "send_mess",
                "body": {
                    channel: {
                        "content": f"{message}",
                    }}
            }
        )

    def _get_channel_id(self, error_type):
        if error_type in self.log_channels.keys():
            return self.log_channels.get(error_type)
        elif "default" in self.log_channels.keys():
            return self.log_channels.get("default")
        return None

    def error(self, message="", embed_text=""):
        if self.debug_level >= ERROR:

            if (channel_id := self._get_channel_id("error")) and self.send_to_discord and self.q is not None:
                self._send_message(channel_id, f"[ERROR] [{self.name}] {message}")
            if self.show_prints:
                print(f"[ERROR] [{self.name}] {message}")

    def warning(self, message="", embed_text=""):
        if self.debug_level >= WARNING:
            if (channel_id := self._get_channel_id("warning")) and self.send_to_discord and self.q is not None:
                self._send_message(channel_id, f"[WARNING] [{self.name}] {message}")
            if self.show_prints:
                print(f"[WARNING] [{self.name}] {message}")

    def info(self, message="", embed_text=""):
        if self.debug_level >= INFO:
            if (channel_id := self._get_channel_id("info")) and self.send_to_discord and self.q is not None:
                self._send_message(channel_id, f"[INFO] [{self.name}] {message}")
            if self.show_prints:
                print(f"[INFO] [{self.name}] {message}")


def create_logger(
        configs_manager: configs.ConfigsManager,
        q: multiprocessing.Queue = None,
        debug_level=None,
        name: str = "MAIN"
) -> Logger:
    log_channels = configs_manager.logger["channels"]

    return Logger(log_channels=configs_manager.logger["channels"],
                  q=q,
                  name=name,
                  show_prints=configs_manager.logger["show_prints"],
                  send_to_discord=configs_manager.logger["send_to_discord"],
                  debug_level=configs_manager.logger["debug_level"] if debug_level is None else debug_level
                  )


class LoggingBot(discord.ext.commands.Bot):
    def __init__(self,
                 log_q: multiprocessing.Queue,
                 logger,
                 configs_manager,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.q = log_q
        self.logger = logger
        self.configs_manager = configs_manager,
