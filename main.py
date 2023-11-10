import disnake
from disnake.ext import commands

import os

from keep_alive import keep_alive
keep_alive()

bot = commands.Bot(command_prefix='meow/', help_command= None, intents = disnake.Intents.all())

# Подключение и проверка
@bot.event
async def on_ready():
    print(f"Бот «{bot.user.name}» успешно запущен.")
    await bot.change_presence(status = disnake.Status.dnd, activity = disnake.Activity(type = disnake.ActivityType.listening, name = "Spotify"))

# Загрузка когов
if os.path.isdir("cogs"):
    for filename in os.listdir("cogs"):
        if filename.endswith(".py"):
            bot.load_extension(f"cogs.{filename[:-3]}")

token = os.environ['TOKEN']
bot.run(token)