from disnake.ext import commands

class DataBaseCreation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.db_cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS servers(
                server_id INT,
                server_name TEXT
            )
        """)
        self.bot.db_connection.commit()

        for guild in self.bot.guilds:
            if self.bot.db_cursor.execute(f"SELECT server_id FROM servers WHERE server_id = {guild.id}").fetchone() == None:
                self.bot.db_cursor.executescript(f"""
                    INSERT INTO servers VALUES ({guild.id}, '{guild.name}');

                    CREATE TABLE temp_channels_{guild.id} (
                        channel_id INT,
                        server_id INT,
                        FOREIGN KEY (server_id) REFERENCES servers (server_id)
                    );
                """)
                self.bot.db_connection.commit()

    @commands.Cog.listener()
    async def on_guild_join(self, guild):        
        self.bot.db_cursor.executescript(f"""
            INSERT INTO servers VALUES ({guild.id}, '{guild.name}');

            CREATE TABLE IF NOT EXISTS temp_channels_{guild.id} (
                channel_id INT,
                server_id INT,
                FOREIGN KEY (server_id) REFERENCES servers (server_id)
            );
        """)
        self.bot.db_connection.commit()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):        
        self.bot.db_cursor.executescript(f"""
            DROP TABLE IF EXISTS temp_channels_{guild.id};
            DELETE FROM servers WHERE server_id = {guild.id};
        """)
        self.bot.db_connection.commit()

def setup(bot):
    bot.add_cog(DataBaseCreation(bot))