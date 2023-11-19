import disnake
from disnake.ext import commands

class DropdownBlackList(disnake.ui.UserSelect):
    def __init__(self, channel_object):
        self.channel_object = channel_object

        super().__init__(
            placeholder = "Выберите пользователя...",
            min_values = 1,
            max_values = 1,
        )

    async def callback(self, inter: disnake.MessageInteraction):
        try:
            if self.values[0] != inter.author:
                if self.channel_object.permissions_for(self.values[0]).connect or not self.values[0] in self.channel_object.overwrites:
                    await self.channel_object.set_permissions(target = self.values[0], overwrite = disnake.PermissionOverwrite(connect = False))
                    if self.values[0] in self.channel_object.members:
                        await self.values[0].move_to(None)
                    await inter.response.edit_message(embed = disnake.Embed(description = f"✅ Пользователь успешно добавлен в черный список."), components = None)
                else:
                    await self.channel_object.set_permissions(target = self.values[0], overwrite = None)
                    await inter.response.edit_message(embed = disnake.Embed(description = f"✅ Пользователь успешно удален из черного списка."), components = None)
            else:
                await inter.response.edit_message(embed = disnake.Embed(description = f"❌ Вы не можете добавить себя в черный список."), components = None)
        except Exception as e:
            await inter.edit_message(embed = disnake.Embed(description = f"❌ Ошибка изменения прав пользователя."), components = None)
        await inter.delete_original_response(delay = 3)

class DropdownPermanentMenu(disnake.ui.StringSelect):
    def __init__(self):

        options = [
            disnake.SelectOption(
                label = "Создать", emoji = "⚰️", value = "create"
            ),
            disnake.SelectOption(
                label = "Открыть", emoji = "📭", value = "open"
            ),
            disnake.SelectOption(
                label = "Закрыть", emoji = "📪", value = "close"
            ),
            disnake.SelectOption(
                label = "Добавить/Удалить участника из черного списка", emoji = "👹", value = "set_bl"
            ),
            disnake.SelectOption(
                label = "Просмотреть черный список", emoji = "🚷", value = "print_bl"
            ),
        ]

        super().__init__(
            placeholder = "Выберите желаемое действие...",
            min_values = 1,
            max_values = 1,
            options = options,
        )

    async def callback(self, inter: disnake.MessageInteraction):
        permquery = inter.bot.db_cursor.execute(f"SELECT member_id, channel_id FROM permanent_channels WHERE member_id = {inter.author.id}").fetchone()
        member_role = disnake.utils.get(inter.guild.roles, id = 1167532972212240516)
        if self.values[0] == "create":
            # Проверка на существование канала для его создания
            if permquery == None or disnake.utils.get(inter.guild.channels, id = permquery[1]) == None:
                emb = disnake.Embed(description = "📛 Выберите предустановку доступа к комнате.")
                emb.set_footer(text = "Данную настройку можно изменить после создания.")
                open_button = disnake.ui.Button(style = disnake.ButtonStyle.green, label = "Открытая", custom_id = "open")
                close_button = disnake.ui.Button(style = disnake.ButtonStyle.red, label = "Закрытая", custom_id = "close")
                
                await inter.response.edit_message(embed = emb,  components = [open_button, close_button])

                try:
                    interaction = await inter.bot.wait_for("button_click", timeout = 20)
                    
                    # Задание первичных настроек канала
                    permcategory = disnake.utils.get(inter.guild.categories, id = 1173949858634272819)
                    if interaction.component.custom_id == "open": access = True
                    else: access = False
                    overwrites = {
                        member_role: disnake.PermissionOverwrite(connect = access),
                        inter.author: disnake.PermissionOverwrite(connect = True, manage_channels = True)
                    }

                    # Создание канала
                    permchannel = await inter.guild.create_voice_channel(name = f"{inter.author.display_name}\'s channel", category = permcategory, overwrites = overwrites)
                    
                    # Добавление канала в БД
                    inter.bot.db_cursor.execute(f"INSERT OR REPLACE INTO permanent_channels VALUES ({inter.author.id}, {permchannel.id})")
                    inter.bot.db_connection.commit()
                    
                    await inter.edit_original_response(embed = disnake.Embed(description = f"✅ Приватная комната успешно создана."), components = None)
                
                except Exception as e:
                    await inter.edit_original_response(embed = disnake.Embed(description = f"❌ Ошибка создания приватной комнаты."), components = None)
                    print(e)
            
            else:
                await inter.response.edit_message(embed = disnake.Embed(description = f"❌ Приватная комната уже существует."), components = None)

        # Проверка на существование канала для его изменения
        elif permquery != None and disnake.utils.get(inter.guild.channels, id = permquery[1]) != None:
            channel_object = disnake.utils.get(inter.guild.channels, id = permquery[1])
            try:
                # Открытие канала
                if self.values[0] == "open":
                    for overwrite in channel_object.overwrites:
                        if overwrite != inter.author and not isinstance(overwrite, disnake.Member):
                            await channel_object.set_permissions(target = overwrite, overwrite = None)

                # Закрытие канала
                elif self.values[0] == "close":
                    await channel_object.set_permissions(
                        overwrite = disnake.PermissionOverwrite(connect = False),
                        target = member_role
                    )
                    for member in channel_object.members:
                        await channel_object.set_permissions(
                            overwrite = disnake.PermissionOverwrite(connect = True),
                            target = member
                        )
                
                # Добавление/Удаление участника из черного списка
                elif self.values[0] == "set_bl":
                    view = disnake.ui.View()
                    view.add_item(DropdownBlackList(channel_object))
                    await inter.response.edit_message(view = view)
                    return

                # Вывод черного списка
                elif self.values[0] == "print_bl":
                    emb = disnake.Embed(title = "Пользователи в черном списке:")
                    users_info = ""
                    for overwrite in channel_object.overwrites:
                        # Проверяем, является ли overwrite разрешением для пользователя и запрещено ли ему подключаться
                        if isinstance(overwrite, disnake.Member) and not channel_object.permissions_for(overwrite).connect:
                            users_info += f"{overwrite.display_name} ({overwrite.name})\n"
                    emb.description = users_info
                    await inter.response.edit_message(embed = emb, components = None)
                    return
                
                await inter.response.edit_message(embed = disnake.Embed(description = f"✅ Параметры доступа приватной комнаты успешно изменены."), components = None)
            
            except Exception as e:
                await inter.response.edit_message(embed = disnake.Embed(description = f"❌ Ошибка изменения параметров доступа комнаты."), components = None)
                print(e)
        else:
            await inter.response.edit_message(embed = disnake.Embed(description = f"❌ Приватная комната ещё не создана."), components = None)
        await inter.delete_original_response(delay = 3)

class PermanentChannels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description = "Управление приватными комнатами.")
    async def menu(self, inter):
        # Проверка на присутствие роли бустера
        premium_role = inter.guild.premium_subscriber_role
        if not premium_role in inter.author.roles: raise commands.MissingRole(premium_role)

        view = disnake.ui.View()
        view.add_item(DropdownPermanentMenu())
        
        await inter.send(view = view, ephemeral = True)         
            
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        removed_roles = set(before.roles) - set(after.roles)
        if before.guild.get_role(798228559675916350) in removed_roles:
            permquery = self.bot.db_cursor.execute(f"SELECT channel_id FROM permanent_channels WHERE member_id = {before.id}").fetchone()
            if permquery != None:
                try:
                    channel = before.guild.get_channel(permquery[0])
                    if channel: await channel.delete()
                    
                    self.bot.db_cursor.execute(f"DELETE FROM permanent_channels WHERE channel_id = {permquery[0]}")
                    self.bot.db_connection.commit()
                except Exception as e:
                    print(e)                                
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        permquery = self.bot.db_cursor.execute(f"SELECT channel_id FROM permanent_channels WHERE member_id = {member.id}").fetchone()
        if  permquery != None:
            channel = member.guild.get_channel(permquery[0])
            if channel: await channel.delete()
            self.bot.db_cursor.execute(f"DELETE FROM permanent_channels WHERE member_id = {member.id}")
            self.bot.db_connection.commit()
            
def setup(bot):
    bot.add_cog(PermanentChannels(bot))