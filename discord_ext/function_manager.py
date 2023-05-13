import functools
import importlib
import logging
import traceback

import discord
import discord.ext

import discord_ext


class FunctionNotFound(Exception):
    ...


class BaseFunctionsCog:
    name: str


class FunctionManager:
    __slots__ = [
        "logger",
        "sender"
    ]

    def __init__(self, sender: discord_ext.Sender, logger: discord_ext.logger.Logger):
        self.logger = logger
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
        except Exception:
            raise FunctionNotFound


def connect_func(name=None):
    """
    декоратор для подключения функции которую выполнит дополнительный бот
    работает только с app_commands!!!!
    Как это работает:
        в очередь worker_q добавляется словарь в котором указаны:
            тип "задачи"
            функция которая должна быть выполнена
            данные которые должны для создания объекта Interaction (в Readme сказано что нужно сделать что бы оно заработало)
            прочие аргументы

    :param name:
    :return:
    """

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(cog_self, interaction: discord.Interaction, *args, **kwargs):
            await func(cog_self, interaction, *args, **kwargs)  # call the func
            _name = name if name else f"{type(cog_self).__name__}.{func.__name__}"

            try:
                f = cog_self.bot.function_manager.get_func(_name)
                # create the task
                cog_self.bot.worker_queue.put({
                    "type": "app_command",
                    "task": {
                        "function": f,
                        "args": [interaction.source_data],
                    }
                })

            except Exception as e:
                cog_self.bot.function_manager.logger.error("error in [connect_func]", exc=traceback.format_exc())

        return wrapper

    return decorator


def connect_func_standard(name=None):
    """
    декоратор для подключения функции которую выполнит дополнительный бот

    работает только с commands.Command()!!!!

    Как это работает:
        в очередь worker_q добавляется словарь в котором указаны:
            тип задачи
            функция которая должна быть выполнена
            данные для создания discord.ext.commands.Context

    :param name: имя функции (ClassName.function_name) если не указано то берется автоматически
    :return:
    """

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(cog_self, ctx: discord.ext.commands.Context, *args, **kwargs):
            await func(cog_self, ctx, *args, **kwargs)  # call the func
            _name = name if name else f"{type(cog_self).__name__}.{func.__name__}"

            try:
                f = cog_self.bot.function_manager.get_func(_name)  # get the func
                # create the task
                cog_self.bot.worker_queue.put({
                    "type": "standard_command",
                    "task": {
                        "function": f,
                        "args": [{
                            "data": ctx.message.source_data,
                            "channel_id": ctx.channel.id,
                            "view": ctx.view,
                        }] + list(args),
                        "kwargs": kwargs,
                    }
                })

            except Exception as e:
                cog_self.bot.function_manager.logger.error("error in [connect_func_standard]",
                                                           tb=traceback.format_exc())
                # traceback.print_exc()

        return wrapper

    return decorator
