from disnake.ext import commands

class DataBaseCreation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # Создание таблицы с серверами
        self.bot.db_cursor.executescript(f"""                                   
            CREATE TABLE IF NOT EXISTS servers(
                server_id INT,
                server_name TEXT
            )
        """)
        self.bot.db_connection.commit()

        # Добавление актуальных серверов в БД
        for guild in self.bot.guilds:
            if self.bot.db_cursor.execute(f"SELECT server_id FROM servers WHERE server_id = {guild.id}").fetchone() == None:
                insertionServer(self, guild)
    
        # Удаление пустых временных каналов, оставшихся в БД
        try:
            for guild in self.bot.guilds:

                temp_channels = self.bot.db_cursor.execute(f"SELECT channel_id FROM temp_channels_{guild.id};").fetchall()

                for channel_id in temp_channels:
                    channel = guild.get_channel(channel_id[0])
                    if channel and len(channel.members) == 0:
                        await channel.delete()
                        self.bot.db_cursor.execute(f"DELETE FROM temp_channels_{guild.id} WHERE channel_id = {channel_id[0]};")
            self.bot.db_connection.commit()
        except Exception as e:
            print(e)

        # Удаление серверов из БД, в которых бот уже не состоит
        try:
            all_server = self.bot.db_cursor.execute("SELECT server_id FROM servers;").fetchall()

            for server in all_server:
                server_id = server[0]
                guild = self.bot.get_guild(server_id)

                if guild is None:
                    dropServer(self, server_id)
        except Exception as e:
            print(e)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):        
        insertionServer(self, guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild): 
        dropServer(self, guild)

# Добавление сервера в БД и таблицы с временными каналами
def insertionServer(self, guild):
    self.bot.db_cursor.executescript(f"""
        INSERT INTO servers VALUES ({guild.id}, '{guild.name}');

        CREATE TABLE IF NOT EXISTS temp_channels_{guild.id} (
            channel_id INT
        );

        CREATE TABLE IF NOT EXISTS permanent_channels_{guild.id} (
            member_id INT PRIMARY KEY,
            channel_id INT
        );
    """)
    self.bot.db_connection.commit()
# Удаление сервера из БД
def dropServer(self, guild_id):
    self.bot.db_cursor.executescript(f"""
        DROP TABLE temp_channels_{guild_id};
        DROP TABLE permanent_channels_{guild_id};
        DELETE FROM servers WHERE server_id = {guild_id};
    """)
    self.bot.db_connection.commit()

def setup(bot):
    bot.add_cog(DataBaseCreation(bot))