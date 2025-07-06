import asyncio
import discord
from discord.ext import commands
import os
import glob
from dotenv import load_dotenv

load_dotenv("GAPI.env")

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# ◆ カンマ区切りの文字列を分割してリスト化
raw_ids = os.getenv("DISCORD_GUILD_ID", "")  # 例: "123456789012345678,987654321098765432"
TARGET_GUILD_IDS = []
for s in raw_ids.split(","):
    s = s.strip()
    if s.isdigit():
        TARGET_GUILD_IDS.append(int(s))

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
    print("✅ Botが起動しました")

    # ◆ 複数ギルドに順次同期
    try:
        for guild_id in TARGET_GUILD_IDS:
            guild_obj = discord.Object(id=guild_id)
            # ローカルに登録済みのコマンドをコピー＆同期
            bot.tree.copy_global_to(guild=guild_obj)
            await bot.tree.sync(guild=guild_obj)
        print("✅ 複数サーバーのスラッシュコマンドを同期しました")
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
