import disnake
from disnake.ext import commands

class DataBaseCreation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        guild = disnake.utils.get(self.bot.guilds, id = 616665797301108757)

        self.bot.db_cursor.executescript(f"""
            CREATE TABLE IF NOT EXISTS temp_channels (
                channel_id INT
            );

            CREATE TABLE IF NOT EXISTS permanent_channels (
                member_id INT PRIMARY KEY,
                channel_id INT
            );
        """)
        self.bot.db_connection.commit()
    
        # Удаление пустых временных каналов, оставшихся в БД
        try:
            temp_channels = self.bot.db_cursor.execute(f"SELECT channel_id FROM temp_channels").fetchall()
            perm_channels = self.bot.db_cursor.execute(f"SELECT member_id, channel_id FROM permanent_channels").fetchall()
            
            for channelquery in perm_channels:
                if not guild.get_role(798228559675916350) in guild.get_member(channelquery[0]).roles:
                    await guild.get_channel(channelquery[1]).delete()
                    self.bot.db_cursor.execute(f"DELETE FROM permanent_channels WHERE channel_id = {channelquery[1]};")

            for channel_id in temp_channels:
                channel = guild.get_channel(channel_id)
                if channel and len(channel.members) == 0:
                    await channel.delete()
                    self.bot.db_cursor.execute(f"DELETE FROM temp_channels WHERE channel_id = {channel_id[0]};")
            self.bot.db_connection.commit()
        except Exception as e:
            print(e)

def setup(bot):
    bot.add_cog(DataBaseCreation(bot))