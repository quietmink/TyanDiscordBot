import disnake
from disnake.ext import commands

import asyncio

class UserCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description = "Создание жалобы.", required = True)
    async def report(self, inter, subject: disnake.Member =  commands.Param(name = "subject", description = "Нарушитель."), sugg: str = commands.Param(description = "Содержание жалобы.")):
        suggchannel = self.bot.get_channel(647855647622168576)
        emb = disnake.Embed(title = "👺 Новая жалоба.", color = 0xc20000, timestamp = inter.created_at)
        emb.add_field(name = "Нарушитель:", value = subject.mention, inline = False)
        emb.add_field(name = "Содержание:", value = sugg, inline = False)
        emb.set_footer(text = inter.author.name, icon_url = inter.author.display_avatar.url)
        await suggchannel.send(embed = emb)
        await inter.send(embed = disnake.Embed(description = f"✅ Ваше сообщение было доставлено и будет рассмотрено в скором времени."), delete_after = 10, ephemeral = True)

def setup(bot):
    bot.add_cog(UserCommands(bot))
    