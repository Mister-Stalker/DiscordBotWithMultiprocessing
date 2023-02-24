import functools
import importlib
import logging
import traceback

import discord

from discord_ext import message_sender, logger


class FunctionNotFound(Exception):
    ...


class FunctionManager:

    def __init__(self, sender: message_sender.Sender, _logger: logger.Logger):
        self.logger = _logger
        self.sender = sender

    def add_cog(self, cog_obj):
        """
        add cog object
        :param cog_obj:
        :return:
        """

        name = cog_obj.name
        self.__setattr__(name, cog_obj)

    def load_extension(self, name: str):
        """"
        load extension file
        in extension file must be "init" func

        """
        try:
            module = importlib.import_module(name)
            module.init(self)
        except ModuleNotFoundError:
            logging.error(f"extension {name} not found")
        except Exception as e:
            logging.error(f"can`t load extension {name}  {e}")

    def get_func(self, name: str):
        """
        get func by full name (with class)
        """
        cls, func = name.split(".")
        try:
            return self.__getattribute__(cls).__getattribute__(func)
        except:
            raise FunctionNotFound


def connect_func(name=None):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(cog_self, interaction: discord.Interaction, *args, **kwargs):
            await func(cog_self, interaction, *args, **kwargs)
            _name = name
            if not _name:
                _name = f"{type(cog_self).__name__}.{func.__name__}"
            try:
                f = cog_self.bot.function_manager.get_func(_name)

                cog_self.bot.worker_queue.put({
                    "type": "app_command",
                    "task": {
                        "function": f,
                        "args": [interaction.interaction_data],
                    }
                })

            except Exception as e:

                traceback.print_exc()

        return wrapper

    return decorator
