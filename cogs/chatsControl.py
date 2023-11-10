import disnake
from disnake.ext import commands

import requests
from bs4 import BeautifulSoup

class ChatModeration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == 1168889477352140831 and not message.author == self.bot.user:
            if message.content.startswith('https://open.spotify.com'):
                response = requests.get(message.content)
                soup = BeautifulSoup(response.content, 'html.parser')
                header_text = soup.find('h1').text
                
                if 'Page not found' in header_text or 'Page not available' in header_text:
                    await message.delete()
            else:
                await message.delete()

        if message.channel.id == 1168668785671159898 and not message.author == self.bot.user:
            if message.content.startswith('https://tenor.com'):
                response = requests.get(message.content)
                soup = BeautifulSoup(response.content, 'html.parser')
                header_text = soup.find('h1').text

                if '404 Error' in header_text or 'Ошибка 404' in header_text:
                    await message.delete()
            else:
                await message.delete()

        if message.channel.id == 878755267439886379:
            guild = message.guild
            emoji1 = disnake.utils.get(guild.emojis, name = 'upcat')
            emoji2 = disnake.utils.get(guild.emojis, name = 'downcat')
            
            emojis = [emoji1, emoji2]
            
            for emoji in emojis:
                await message.add_reaction(emoji)

        if message.channel.id == 1171004843595403314 and not message.author == self.bot.user:
            if message.attachments:
                for attachment in message.attachments:
                    if not attachment.content_type.startswith('image') or attachment.content_type.endswith('gif'):
                        await message.delete()
                        break
            else:
                await message.delete() 

def setup(bot):
    bot.add_cog(ChatModeration(bot))