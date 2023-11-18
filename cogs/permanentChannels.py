import disnake
from disnake.ext import commands

class Dropdown(disnake.ui.StringSelect):
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
        ]

        super().__init__(
            placeholder = "Выберите желаемое действие",
            min_values = 1,
            max_values = 1,
            options = options,
        )

    async def callback(self, inter: disnake.MessageInteraction):
        if self.values[0] == "create":
            # Проверка на существование канала
            permquery = inter.bot.db_cursor.execute(f"SELECT member_id, channel_id FROM permanent_channels_{inter.guild.id} WHERE member_id = {inter.author.id}").fetchone()
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
                        disnake.utils.get(inter.guild.roles, id = 1167532972212240516): disnake.PermissionOverwrite(connect = access),
                        inter.author: disnake.PermissionOverwrite(connect = True, manage_channels = True)
                    }

                    # Создание канала
                    permchannel = await inter.guild.create_voice_channel(name = f"{inter.author.display_name}\'s channel", category = permcategory, overwrites = overwrites)
                    
                    # Добавление канала в БД
                    inter.bot.db_cursor.execute(f"INSERT OR REPLACE INTO permanent_channels_{inter.guild.id} VALUES ({inter.author.id}, {permchannel.id})")
                    inter.bot.db_connection.commit()
                    
                    await inter.edit_original_response(embed = disnake.Embed(description = f"✅ Приватная комната успешно создана."), components = None)
                except Exception as e:
                    await inter.edit_original_response(embed = disnake.Embed(description = f"❌ Ошибка создания приватной комнаты."), components = None)
                    print(e)
            else:
                await inter.response.edit_message(embed = disnake.Embed(description = f"❌ Приватная комната уже существует."), components = None)
        elif self.values[0] == "open":
            pass
        elif self.values[0] == "close":
            pass
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
        view.add_item(Dropdown())
        await inter.send(view = view, ephemeral = True)         
            
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        removed_roles = set(before.roles) - set(after.roles)
        if before.guild.get_role(798228559675916350) in removed_roles:
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