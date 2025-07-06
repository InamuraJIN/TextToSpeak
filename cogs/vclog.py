import discord
from discord.ext import commands
import os
import json
from datetime import datetime, timedelta

# ◆ここは残す：タイムアウト秒などの既存機能は維持
TIMEOUT_SECONDS = 60  # タイムアウト（秒）

# ◆環境変数は使わないので削除
# from dotenv import load_dotenv
# load_dotenv("GAPI.env")
# VC_LOG_CHANNEL_ID = int(os.getenv("DISCORD_VC_LOG"))

# ◆serversettings.jsonを参照するための関数をインポート（ServerSettings.py から）
#   例: cogsフォルダ内のServerSettings.pyで定義している場合
#   from .ServerSettings import get_guild_config

# 「cogs」直下にない場合は、インポートパスを調整してください。
from .ServerSettings import get_guild_config

class VCLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # 既存機能の変数はそのまま
        self.last_join_time = {}
        self.ignore_users = set()
        self.ignore_roles = set()
        self.ignore_vcs = set()
        self.load_ignore_list()

    def load_ignore_list(self):
        if os.path.exists("Ignorelog.json"):
            with open("Ignorelog.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self.ignore_users = set(data.get("users", []))
                self.ignore_roles = set(data.get("roles", []))
                self.ignore_vcs = set(data.get("vcs", []))

    def should_log(self, member, channel_id):
        # 既存のignoreロジックを保持
        if str(member.id) in self.ignore_users:
            return False
        if any(str(role.id) in self.ignore_roles for role in member.roles):
            return False
        if str(channel_id) in self.ignore_vcs:
            return False
        return True

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # Botの場合は除外
        if member.bot:
            return

        # 「VCに入った」イベントをフック (before.channel==None, after.channel!=None)
        if before.channel is None and after.channel:
            # 無視対象ならログを出さない
            if not self.should_log(member, after.channel.id):
                return

            now = datetime.utcnow()
            last_time = self.last_join_time.get(member.id)

            # 一定時間以内の再入室はログに出さない (既存機能のTIMEOUT_SECONDS)
            if last_time and now - last_time < timedelta(seconds=TIMEOUT_SECONDS):
                return

            self.last_join_time[member.id] = now

            # ◆serversettings.jsonから 「vc_log_channel」を取得
            guild_config = get_guild_config(member.guild.id)
            vc_log_channel_id = guild_config.get("vc_log_channel")
            if not vc_log_channel_id:
                # 未設定ならログを出さずにスキップ
                return

            # 実際にテキストチャンネルを取得
            channel = self.bot.get_channel(vc_log_channel_id)
            if not channel:
                # 既に削除済みなどで存在しなければスキップ
                return

            # 以下、ログEmbedを送る既存の処理
            vc_invite = await after.channel.create_invite(max_age=0, max_uses=0, unique=False)
            avatar_url = member.display_avatar.url if member.display_avatar else None
            nickname = member.display_name
            user_mention = member.mention
            vc_name_link = f"[{after.channel.name}]({vc_invite.url})"

            embed = discord.Embed(
                description=f"{user_mention} が {vc_name_link} に参加しました",
                color=discord.Color.green(),
            )
            embed.set_footer(text=f"ユーザーID: {member.id}")

            embed.add_field(name=f"{nickname}", value="\u200b", inline=False)
            if avatar_url:
                embed.set_thumbnail(url=avatar_url)

            await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(VCLog(bot))
    print("✅ vclog をロードしました")
