import disnake
from disnake.ext import commands
import os
import sqlite3

# Поддержка работы
from keep_alive import keep_alive
keep_alive()

bot = commands.Bot(command_prefix ='meow/', help_command = None, intents = disnake.Intents.all())

#Подключение к БД
connection = sqlite3.connect('tyan.db')
bot.db_cursor = connection.cursor()

# Загрузка когов
if os.path.isdir("cogs"):
    for filename in os.listdir("cogs"):
        if filename.endswith(".py"):
            bot.load_extension(f"cogs.{filename[:-3]}")

# Подтверждение подключения и изменение статуса
@bot.event
async def on_ready():
    print(f"Бот «{bot.user.name}» успешно запущен.")

    await bot.change_presence(status = disnake.Status.dnd, activity = disnake.Activity(type = disnake.ActivityType.listening, name = "Spotify"))

token = os.environ['TOKEN']
bot.run(token)