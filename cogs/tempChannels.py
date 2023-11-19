import disnake
from disnake.ext import commands

class TempChannels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        
        # Создание временного канала
        if after.channel != None and after.channel.id == 756607939137110127:
            try:
                guild = after.channel.guild
                tempcategory = disnake.utils.get(guild.categories, id = after.channel.category_id)
                tempchannel = await guild.create_voice_channel(name = f"{member.display_name}\'s channel", category = tempcategory)
                await tempchannel.set_permissions(member, connect = True, manage_channels = True)
                try:
                    await member.move_to(tempchannel)

                    self.bot.db_cursor.execute(f"INSERT INTO temp_channels VALUES ({tempchannel.id})")
                    self.bot.db_connection.commit()
                except:
                    await tempchannel.delete()
            except Exception as e:
                print(e)

        # Удаление временного канала
        if before.channel != None:
            if self.bot.db_cursor.execute(f"SELECT channel_id FROM temp_channels WHERE channel_id = {before.channel.id}").fetchone() != None and len(before.channel.members) == 0:
                if before.channel.guild.get_channel(before.channel.id):
                    await before.channel.delete()
                self.bot.db_cursor.execute(f"DELETE FROM temp_channels WHERE channel_id = {before.channel.id}")
                self.bot.db_connection.commit()
        
def setup(bot):
    bot.add_cog(TempChannels(bot))