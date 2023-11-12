import disnake
from disnake.ext import commands

class TempChannels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        
        if after.channel != None and after.channel.id == 756607939137110127:
            try:
                guild = after.channel.guild
                maincategory = disnake.utils.get(guild.categories, id = after.channel.category_id)
                newchannel = await guild.create_voice_channel(name = f"{member.display_name}\'s channel", category = maincategory)
                await newchannel.set_permissions(member, connect = True, move_members = True, manage_channels = True)
                try:
                    await member.move_to(newchannel)

                    self.bot.db_cursor.execute(f"INSERT INTO temp_channels_{guild.id} VALUES ({newchannel.id}, {guild.id})")
                    self.bot.db_connection.commit()
                except:
                    await newchannel.delete()
            except Exception as e:
                print(e)

        if before.channel != None and before.channel.guild.get_channel(before.channel.id):
            if self.bot.db_cursor.execute(f"SELECT channel_id FROM temp_channels_{before.channel.guild.id} WHERE channel_id = {before.channel.id}").fetchone() != None:
                if len(before.channel.members) == 0:
                    try:
                        await before.channel.delete()
                        self.bot.db_cursor.execute(f"DELETE FROM temp_channels_{before.channel.guild.id} WHERE channel_id = {before.channel.id};")
                        self.bot.db_connection.commit()
                    except Exception as e:
                        print(e)
        
def setup(bot):
    bot.add_cog(TempChannels(bot))