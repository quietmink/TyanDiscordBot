import disnake
from disnake.ext import commands

class ExeptionHandling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_slash_command_error(self, inter, error):
        if isinstance(error, commands.MissingAnyRole):
            await inter.send(embed = disnake.Embed(description = f"У вас нет необходимых ролей! 🤬"), delete_after = 4)
        else:
            print(error)

def setup(bot):
    bot.add_cog(ExeptionHandling(bot))
    