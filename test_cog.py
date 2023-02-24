import discord
from discord.ext import commands

import discord_ext.bot as _bot
from discord_ext import function_manager


class TestingCog(commands.GroupCog, name="testing"):
    def __init__(self, bot) -> None:
        self.bot = bot
        super().__init__()

    async def test_worker(self, interaction, *args, **kwargs):
        print(self.bot.name, interaction, args, kwargs)

    @discord.app_commands.command(name="test_wp")
    @function_manager.connect_func()
    async def test_wp(self, interaction: discord.Interaction):
        # print(interaction)

        await interaction.response.send_message("its work!", ephemeral=True)


async def setup(bot: _bot.Bot) -> None:
    await bot.add_cog(TestingCog(bot))
