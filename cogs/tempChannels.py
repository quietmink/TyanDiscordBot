import disnake
from disnake.ext import commands

class TempChannels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel != None:
            if after.channel.id == 756607939137110127:
                for guild in self.bot.guilds:
                    maincategory = disnake.utils.get(guild.categories, id = 756607938566815904)
                    newchannel = await guild.create_voice_channel(name = f"{member.display_name}\'s channel", category = maincategory)
                    await newchannel.set_permissions(member, connect = True, move_members = True, manage_channels = True)
                    await member.move_to(newchannel)
                    def check(x, y, z):
                        return len(newchannel.members) == 0
                    await self.bot.wait_for("voice_state_update", check = check)
                    await newchannel.delete()

def setup(bot):
    bot.add_cog(TempChannels(bot))
    