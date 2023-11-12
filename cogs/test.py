import disnake
from disnake.ext import commands

class TestCom(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def test(self):
        pass
        

def setup(bot):
    bot.add_cog(TestCom(bot))