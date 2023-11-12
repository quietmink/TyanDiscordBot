import disnake
from disnake.ext import commands

class TestCom(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description = "Тест.")
    async def testo(self, inter):
        await inter.send(embed = disnake.Embed(description = f"Пон"))

def setup(bot):
    bot.add_cog(TestCom(bot))