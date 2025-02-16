import asyncio
import discord
from discord.ext import commands
import os
import glob
from dotenv import load_dotenv

load_dotenv("GAPI.env")

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix="/", intents=intents)

async def load_extensions():
    for file in glob.glob("cogs/*.py"):
        cog_name = file.replace("/", ".").replace("\\", ".").replace(".py", "")
        try:
            await bot.load_extension(cog_name)
            print(f"✅ {cog_name} をロードしました")
        except Exception as e:
            print(f"⚠️ {cog_name} のロードに失敗: {e}")

@bot.event
async def on_ready():
    print("✅ Discord Botが起動しました")

@bot.event
async def on_error(event, *args, **kwargs):
    import traceback
    print(f"⚠️ エラーが発生しました: {event}")
    print(traceback.format_exc())

async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

asyncio.run(main())
