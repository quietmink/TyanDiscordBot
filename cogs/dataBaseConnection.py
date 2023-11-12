from disnake.ext import commands

class DataBaseCreation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.db_cursor.executescript("""
            CREATE TABLE IF NOT EXISTS servers(
                server_id INTEGER PRIMARY KEY,
                server_name TEXT
        );
            CREATE TABLE IF NOT EXISTS temp_channels (
                channel_id INTEGER PRIMARY KEY,
                server_id INTEGER,
                FOREIGN KEY (server_id) REFERENCES servers (server_id)
        );
            """)

def setup(bot):
    bot.add_cog(DataBaseCreation(bot))