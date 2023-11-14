import disnake
from disnake.ext import commands

class PermanentChannels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description = "Создание приватной комнаты.")
    @commands.has_role(798228559675916350)
    async def cpc(self, 
                  inter, 
                  access: bool = commands.Param(name = "lock", 
                                                choices = [True, False], 
                                                description = "Первичная настройка доступа.", 
                                                default = False),
                  name: str = commands.Param(name = "name", 
                                             description = "Название.", 
                                             default = lambda inter: inter.author.display_name + "\'s channel")):
        
        if self.bot.db_cursor.execute(f"SELECT member_id FROM permanent_channels_{inter.author.guild.id} WHERE member_id = {inter.author.id}").fetchone() == None:
            try:
                # Задание первичных настроек канала
                permcategory = disnake.utils.get(inter.author.guild.categories, id = 1173949858634272819)
                overwrites = {
                    disnake.utils.get(inter.author.guild.roles, id = 1167532972212240516): disnake.PermissionOverwrite(connect = not access),
                    inter.author: disnake.PermissionOverwrite(connect = True, move_members = True, manage_channels = True)
                }
                
                # Создание канала
                permchannel = await inter.author.guild.create_voice_channel(name = name, category = permcategory, overwrites = overwrites)
                
                # Добавление канала в БД
                self.bot.db_cursor.execute(f"INSERT INTO permanent_channels_{inter.author.guild.id} VALUES ({inter.author.id}, {permchannel.id})")
                self.bot.db_connection.commit()
                
                await inter.send(
                    embed = disnake.Embed(description = f"✅ Приватная комната была создана."), 
                    delete_after = 10, 
                    ephemeral = True)
            except:
                await inter.send(
                    embed = disnake.Embed(description = f"❌ Ошибка создания приватной комнаты."), 
                    delete_after = 10, 
                    ephemeral = True)
        else:
            await inter.send(
                embed = disnake.Embed(description = f"❌ Превышен лимит приватных комнат."), 
                delete_after = 10, 
                ephemeral = True)

def setup(bot):
    bot.add_cog(PermanentChannels(bot))