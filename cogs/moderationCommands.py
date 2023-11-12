import disnake
from disnake.ext import commands

class ModerationCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description = "Очистка сообщений.", required = True)
    @commands.has_any_role(798272928960479242, 763079486743904316)
    async def clear(self, inter, amount: int = commands.Param(description = "Количество сообщений для удаления.")):
            await inter.send(embed = disnake.Embed(description = f"⌛ Удаление..."))
            processMessage = await inter.original_response()
            try:
                deleted = await inter.channel.purge(limit = amount, before = processMessage)
                await inter.edit_original_response(embed = disnake.Embed(description = f"✅ Удалено {len(deleted)} сообщений."))
                await inter.delete_original_response(delay = 4)
            except:
                await inter.edit_original_response(embed = disnake.Embed(description = f"❌ Сообщения не были удалены."))
                await inter.delete_original_response(delay = 4)


def setup(bot):
    bot.add_cog(ModerationCommands(bot))