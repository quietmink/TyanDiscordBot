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
        
        if self.bot.db_cursor.execute(f"SELECT member_id FROM permanent_channels_{inter.guild.id} WHERE member_id = {inter.author.id}").fetchone() == None:
            try:
                # Задание первичных настроек канала
                permcategory = disnake.utils.get(inter.guild.categories, id = 1173949858634272819)
                overwrites = {
                    disnake.utils.get(inter.guild.roles, id = 1167532972212240516): disnake.PermissionOverwrite(connect = not access),
                    inter.author: disnake.PermissionOverwrite(connect = True, move_members = True, manage_channels = True)
                }
                
                # Создание канала
                permchannel = await inter.guild.create_voice_channel(name = name, category = permcategory, overwrites = overwrites)
                
                # Добавление канала в БД
                self.bot.db_cursor.execute(f"INSERT INTO permanent_channels_{inter.guild.id} VALUES ({inter.author.id}, {permchannel.id})")
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
                embed = disnake.Embed(description = f"❌ Превышен лимит приватных комнат."), 
                delete_after = 5, 
                ephemeral = True)
            
    @commands.slash_command(description = "Удаление текущей приватной комнаты.")
    @commands.has_role(798228559675916350)
    async def dpc(self, inter):        
        permchannelquery = self.bot.db_cursor.execute(f"SELECT member_id, channel_id FROM permanent_channels_{inter.guild.id} WHERE member_id = {inter.author.id}").fetchone()
        if permchannelquery != None:
            # Подтверждение удаления
            emb = disnake.Embed(description = "📛 Вы действительно хотите свою приватную комнату?")
            emb.set_footer(text = "Все настройки будут стёрты!")
            yes_button = disnake.ui.Button(style = disnake.ButtonStyle.green, label = "Да", custom_id = "yes_button")
            no_button = disnake.ui.Button(style = disnake.ButtonStyle.red, label = "Нет", custom_id = "no_button")
            await inter.send(embed = emb, ephemeral = True, components = [yes_button, no_button])
            try:
                interaction = await self.bot.wait_for("button_click", timeout = 20)

                if interaction.component.custom_id == "no_button": 
                    return
                elif interaction.component.custom_id == "yes_button":
                    try:
                        # Удаление приватной комнаты на сервере
                        await disnake.utils.get(inter.guild.channels, id = permchannelquery[1]).delete()

                        # Удаление приватной комнаты из БД
                        self.bot.db_cursor.execute(f"DELETE FROM permanent_channels_{inter.guild.id} WHERE channel_id = {permchannelquery[1]};")
                        self.bot.db_connection.commit()

                        await inter.send(
                            embed = disnake.Embed(description = f"✅ Приватная комната успешно удалена."), 
                            delete_after = 5, 
                            ephemeral = True)
                    except Exception as e:
                        await inter.send(
                            embed = disnake.Embed(description = f"❌ Ошибка удаления приватной комнаты."), 
                            delete_after = 5, 
                            ephemeral = True)
                        print(e)
            except Exception as e:
                print (e)
            finally:
                await inter.delete_original_response()
        else:
            await inter.send(
                embed = disnake.Embed(description = f"❌ Приватная комната ещё не создана."), 
                delete_after = 5, 
                ephemeral = True)
                

def setup(bot):
    bot.add_cog(PermanentChannels(bot))