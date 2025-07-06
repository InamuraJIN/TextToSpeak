import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv("GAPI.env")

intents = discord.Intents.default()
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'ログインしました: {bot.user}')
    print('参加しているサーバー一覧:')
    for guild in bot.guilds:
        print(f'- {guild.name} (ID: {guild.id})')

bot.run(os.getenv("DISCORD_BOT_TOKEN"))
