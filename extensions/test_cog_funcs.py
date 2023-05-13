import time

import discord

import discord_ext


class CustomTestCog(discord_ext.BaseFunctionsCog):
    """
    пример как должен быть организован класс с функциями
    наследование от discord_ext.BaseFunctionsCog необязательно
    """
    bot = None

    def __init__(self):
        self.name = "TestingCog"  # то к какому Cog это относится

    async def test_wp(self, bot, interaction: discord.Interaction, *args, **kwargs):
        """
        пример функции
        просто тяжелая команда которая долго выполняется и отправляет сообщение по завершению
        не очень хороший пример (можно решить задачу без этого), но ситуации могут быть разные
        :param bot: обязательный параметр - выполняющий команду бот
        :param interaction: обязательный параметр
        :param args:
        :param kwargs:
        :return:
        """
        print(bot.name, interaction, args, kwargs)
        await interaction.edit_original_response(content=f'{bot.name}')
        await self.some_cpu_test(interaction, bot, 5_00_000_000)

    async def some_cpu_test(self, interaction: discord.Interaction, bot, n=1000000, ):
        """
        просто пример тяжелого кода который нельзя оптимизировать и уменьшить время выполнения
        не стоит делать слишком тяжелые функции, что бы намертво не стопорить бота надолго
        :param interaction:
        :param bot:
        :param n:
        :return:
        """
        sn = n
        t = time.time()
        while n:
            n -= 1
        await interaction.edit_original_response(
            content=f"some cpu test ({sn}) end in {time.time() - t:4f}s in {bot.name}")


def init(manager):
    manager.add_cog(CustomTestCog())
