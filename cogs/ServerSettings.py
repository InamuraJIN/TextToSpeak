import discord
from discord import app_commands
from discord.ext import commands
import json
import os

DATA_FILE_PATH = os.path.join("data", "serversettings.json")

def load_server_settings() -> dict:
    """
    JSONファイルからサーバー設定を読み込んで返す。
    存在しない場合は空の辞書を返す。
    """
    if not os.path.exists(DATA_FILE_PATH):
        return {}
    with open(DATA_FILE_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_server_settings(data: dict):
    """
    サーバー設定をJSONファイルに保存する。
    """
    with open(DATA_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_guild_config(guild_id: int) -> dict:
    """
    指定ギルドIDの設定を取得。無ければ空のdictを返す。
    """
    settings = load_server_settings()
    return settings.get(str(guild_id), {})

def update_guild_config(guild_id: int, key: str, value: int):
    """
    指定ギルドIDの特定キーを更新し、JSONファイルへ保存。
    """
    settings = load_server_settings()
    guild_str = str(guild_id)
    if guild_str not in settings:
        settings[guild_str] = {}
    settings[guild_str][key] = value
    save_server_settings(settings)

class ServerSettings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="va", description="VC Auto Join のチャンネル設定")
    async def set_va(
        self, 
        interaction: discord.Interaction, 
        channel: discord.VoiceChannel
    ):
        """
        /va コマンド: VC Auto Join 用のVCチャンネルを設定
        """
        update_guild_config(interaction.guild_id, "auto_join_channel", channel.id)
        await interaction.response.send_message(
            f"VC Auto Joinチャンネルを {channel.mention} に設定しました。", 
            ephemeral=True
        )

    @app_commands.command(name="vl", description="VC Log のチャンネル設定")
    async def set_vl(
        self, 
        interaction: discord.Interaction, 
        channel: discord.TextChannel
    ):
        """
        /vl コマンド: VC Log 用のテキストチャンネルを設定
        """
        update_guild_config(interaction.guild_id, "vc_log_channel", channel.id)
        await interaction.response.send_message(
            f"VC Logチャンネルを {channel.mention} に設定しました。", 
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(ServerSettings(bot))
    print("✅ ServerSettings Cog をロードしました")
