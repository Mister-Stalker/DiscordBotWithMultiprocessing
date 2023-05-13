import datetime
import multiprocessing

import discord.ext.commands
from colorama import Fore, Style

from discord_ext import configs

# some variables :)
NOTHING = 0
ERROR = 1
WARNING = 2
INFO = 3


class Logger:
    __slots__ = [
        "q",
        "debug_level",
        "name",
        "show_prints",
        "send_to_discord",
        "log_channels",
    ]

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
        mess = kwargs
        if message:
            mess["content"] = message

        self.q.put(
            {
                "type": "send_mess",
                "body": {
                    channel: mess
                }
            }
        )

    def _get_channel_id(self, error_type):
        if error_type in self.log_channels.keys():
            return self.log_channels.get(error_type)
        elif "default" in self.log_channels.keys():
            return self.log_channels.get("default")
        return None

    def error(self, message="", embed_text="", tb="", exc="", force_send=False):
        if self.debug_level >= ERROR or force_send:

            if (channel_id := self._get_channel_id("error")) and self.send_to_discord and self.q is not None:
                embed = discord.Embed(title=f"{self.name}", colour=discord.Colour.red())
                embed.add_field(name="error", value=f"{message}", inline=False)
                if tb:
                    embed.add_field(name="Traceback",
                                    value=f"{tb}",
                                    inline=False)
                if exc:
                    embed.add_field(name="Traceback",
                                    value=f"{exc}",
                                    inline=False)
                embed.set_footer(text=f"{datetime.datetime.now().strftime('%d.%m.%Y, %H:%M:%S')}")
                self._send_message(channel_id, embed=embed)
            if self.show_prints:
                print(Fore.RED + Style.BRIGHT + f"[ERROR]:[{self.name}]: {message}")
                if tb:
                    print(tb)
                if exc:
                    print(exc)
                print(Style.RESET_ALL, end="")

    def warning(self, message="", embed_text="", force_send=False):
        if self.debug_level >= WARNING or force_send:
            if (channel_id := self._get_channel_id("warning")) and self.send_to_discord and self.q is not None:
                embed = discord.Embed(title=f"{self.name}", colour=discord.Colour.yellow())
                embed.add_field(name="warning", value=f"{message}", inline=False)

                embed.set_footer(text=f"{datetime.datetime.now().strftime('%d.%m.%Y, %H:%M:%S')}")
                self._send_message(channel_id, embed=embed)
            if self.show_prints:
                print(Fore.YELLOW + f"[WARNING]:[{self.name}]: {message}")
                print(Style.RESET_ALL, end="")

    def info(self, message="", embed_text="", force_send=False):
        if self.debug_level >= INFO or force_send:
            if (channel_id := self._get_channel_id("info")) and self.send_to_discord and self.q is not None:
                embed = discord.Embed(title=f"{self.name}", colour=discord.Colour.green())
                embed.add_field(name="info", value=f"{message}", inline=False)
                embed.set_footer(text=f"{datetime.datetime.now().strftime('%d.%m.%Y, %H:%M:%S')}")
                self._send_message(channel_id, embed=embed)
            if self.show_prints:
                print(Fore.CYAN + f"[INFO]:[{self.name}]: {message}")
                print(Style.RESET_ALL, end="")


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
