import time

import discord


class CustomTestCog:
    bot = None

    def __init__(self):
        self.name = "TestingCog"

    async def test_wp(self, bot, interaction: discord.Interaction, *args, **kwargs):
        print(bot.name, interaction, args, kwargs)
        await interaction.edit_original_response(content=f'{bot.name}')
        await self.some_cpu_test(interaction, bot, 5_00_000_000)

    async def some_cpu_test(self, interaction: discord.Interaction, bot, n=1000000, ):
        # print("some cpu test")
        sn = n
        t = time.time()
        while n:
            n -= 1
        await interaction.edit_original_response(
            content=f"some cpu test ({sn}) end in {time.time() - t:4f}s in {bot.name}")


def init(manager):
    manager.add_cog(CustomTestCog())
