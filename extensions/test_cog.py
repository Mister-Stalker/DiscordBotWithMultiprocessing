import discord
from discord.ext import commands

import discord_ext


class TestingCog(commands.Cog):
    def __init__(self, bot) -> None:
        super().__init__()
        self.bot = bot

    @discord.app_commands.command(name="test_wp")
    @discord_ext.connect_func()
    async def test_wp(self, interaction: discord.Interaction):
        # пример команды к которой подключена тяжелая функция
        # код этой функции будет выполнен перед вызовом тяжелой функции
        # noinspection PyUnresolvedReferences
        await interaction.response.send_message("its work!", ephemeral=True)


async def setup(bot: discord_ext.Bot) -> None:
    await bot.add_cog(TestingCog(bot))
