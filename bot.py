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
loaded_cogs = set()

async def load_extensions():
    files = sorted(set(glob.glob("cogs/*.py")), key=str.lower)
    for path in files:
        filename = os.path.basename(path)
        if filename.startswith("__"):
            continue
        cog_name = f"cogs.{filename[:-3]}"
        if cog_name in loaded_cogs:
            continue
        try:
            await bot.load_extension(cog_name)
            loaded_cogs.add(cog_name)
        except Exception as e:
            print(f"⚠️ {filename[:-3]} のロードに失敗: {e}")

@bot.event
async def on_ready():
    print("✅ Discord Botが起動しました")
    try:
        bot.tree.copy_global_to(guild=discord.Object(id=GUILD_ID))
        await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print("✅ スラッシュコマンドを同期しました")
    except Exception as e:
        print(f"⚠️ スラッシュコマンドの同期に失敗しました: {e}")

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
