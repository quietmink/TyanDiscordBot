import disnake
from disnake.ext import commands
import os

class LoadingModules(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = 'load_ext')
    @commands.is_owner()
    async def load_extension_command(self, ctx, cog_name):
        if os.path.exists(os.path.join("cogs", f"{cog_name}.py")):
            try:
                self.bot.load_extension(f"cogs.{cog_name}")
                await ctx.send(embed = disnake.Embed(description = f"✅ Модуль успешно загружен."), delete_after = 5)
            except:
                await ctx.send(embed = disnake.Embed(description = f"❌ Ошибка загрузки модуля."), delete_after = 5)
        else:
            await ctx.send(embed = disnake.Embed(description = f"❌ Модуль не найден."), delete_after = 5)
        await ctx.message.delete(delay = 5)

    @commands.command(name = 'unload_ext')
    @commands.is_owner()
    async def unload_extension_command(self, ctx, cog_name):
        try:
            self.bot.unload_extension(f"cogs.{cog_name}")
            await ctx.send(embed = disnake.Embed(description = f"✅ Модуль успешно выгружен."), delete_after = 5)
        except:
            await ctx.send(embed = disnake.Embed(description = f"❌ Ошибка выгрузки модуля."), delete_after = 5)
        await ctx.message.delete(delay = 5)

def setup(bot):
    bot.add_cog(LoadingModules(bot))