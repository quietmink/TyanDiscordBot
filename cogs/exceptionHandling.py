import disnake
from disnake.ext import commands

class ExceptionHandling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_slash_command_error(self, inter, error):
        if isinstance(error, (commands.MissingAnyRole, commands.MissingRole)):
            await inter.send(embed = disnake.Embed(description = f"У вас нет необходимых ролей! 🤬"), delete_after = 5, ephemeral = True)
        else:
            print(error)
        await inter.delete_original_response(delay = 5)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            await ctx.send(embed = disnake.Embed(description = f"🤬 Данная команда доступна только для создателя."), delete_after = 5, ephemeral = True)
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send(embed = disnake.Embed(description = f"❔ Неизвестная команда."), delete_after = 5, ephemeral = True)
        else:
            print(error)
        await ctx.message.delete(delay = 5)

def setup(bot):
    bot.add_cog(ExceptionHandling(bot))  