from disnake.ext import commands

class TestCom(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description = "Тестовая команда.", required = True)
    async def testo(self, inter):
        pass
        
def setup(bot):
    bot.add_cog(TestCom(bot))