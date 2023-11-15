import disnake
from disnake.ext import commands

class PermanentChannels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description = "Создание приватной комнаты.")
    async def cpc(self, 
                  inter, 
                  access: bool = commands.Param(name = "lock", 
                                                choices = [True, False], 
                                                description = "Первичная настройка доступа.", 
                                                default = False),
                  name: str = commands.Param(name = "name", 
                                             description = "Название.", 
                                             default = lambda inter: inter.author.display_name + "\'s channel")):
        
        # Проверка на присутствие роли бустера
        premium_role = inter.guild.get_role(763079486743904316)
        if not premium_role in inter.author.roles: raise commands.MissingRole(premium_role)
        
        # Проверка на существование канала
        permquery = self.bot.db_cursor.execute(f"SELECT member_id, channel_id FROM permanent_channels_{inter.guild.id} WHERE member_id = {inter.author.id}").fetchone()
        if permquery == None or disnake.utils.get(inter.guild.channels, id = permquery[1]) == None:
            try:
                # Задание первичных настроек канала
                permcategory = disnake.utils.get(inter.guild.categories, id = 1173949858634272819)
                overwrites = {
                    disnake.utils.get(inter.guild.roles, id = 1167532972212240516): disnake.PermissionOverwrite(connect = not access),
                    inter.author: disnake.PermissionOverwrite(connect = True, manage_channels = True)
                }
                
                # Создание канала
                permchannel = await inter.guild.create_voice_channel(name = name, category = permcategory, overwrites = overwrites)
                
                # Добавление канала в БД
                self.bot.db_cursor.execute(f"INSERT OR REPLACE INTO permanent_channels_{inter.guild.id} VALUES ({inter.author.id}, {permchannel.id})")
                self.bot.db_connection.commit()
                
                await inter.send(
                    embed = disnake.Embed(description = f"✅ Приватная комната успешно создана."), 
                    delete_after = 5, 
                    ephemeral = True)
            except Exception as e:
                await inter.send(
                    embed = disnake.Embed(description = f"❌ Ошибка создания приватной комнаты."), 
                    delete_after = 5, 
                    ephemeral = True)
                print(e)
        else:
            await inter.send(
                embed = disnake.Embed(description = f"❌ Приватная комната уже существует."), 
                delete_after = 5, 
                ephemeral = True)             
            
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        removed_roles = set(before.roles) - set(after.roles)
        if before.guild.get_role(763079486743904316) in removed_roles:
            permquery = self.bot.db_cursor.execute(f"SELECT channel_id FROM permanent_channels_{before.guild.id} WHERE member_id = {before.id}").fetchone()
            if permquery != None:
                try:
                    channel = before.guild.get_channel(permquery[0])
                    if channel: await channel.delete()
                    
                    self.bot.db_cursor.execute(f"DELETE FROM permanent_channels_{before.guild.id} WHERE channel_id = {permquery[0]}")
                    self.bot.db_connection.commit()
                except Exception as e:
                    print(e)                                
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        permquery = self.bot.db_cursor.execute(f"SELECT channel_id FROM permanent_channels_{member.guild.id} WHERE member_id = {member.id}").fetchone()
        if  permquery != None:
            channel = member.guild.get_channel(permquery[0])
            if channel: await channel.delete()
            self.bot.db_cursor.execute(f"DELETE FROM permanent_channels_{member.guild.id} WHERE member_id = {member.id}")
            self.bot.db_connection.commit()
            
def setup(bot):
    bot.add_cog(PermanentChannels(bot))