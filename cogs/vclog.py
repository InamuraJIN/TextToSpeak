import discord
from discord.ext import commands
import os
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta

TIMEOUT_SECONDS = 60  #タイムアウト（秒）

load_dotenv("GAPI.env")
VC_LOG_CHANNEL_ID = int(os.getenv("DISCORD_VC_LOG"))

class VCLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
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
        if str(member.id) in self.ignore_users:
            return False
        if any(str(role.id) in self.ignore_roles for role in member.roles):
            return False
        if str(channel_id) in self.ignore_vcs:
            return False
        return True

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return

        if before.channel is None and after.channel:
            if not self.should_log(member, after.channel.id):
                return

            now = datetime.utcnow()
            last_time = self.last_join_time.get(member.id)

            if last_time and now - last_time < timedelta(seconds=TIMEOUT_SECONDS):
                return

            self.last_join_time[member.id] = now
            channel = self.bot.get_channel(VC_LOG_CHANNEL_ID)

            if channel:
                vc_invite = await after.channel.create_invite(max_age=0, max_uses=0, unique=False)
                display_name = f"{member.mention}（{member.display_name}）"
                vc_name_link = f"[{after.channel.name}]({vc_invite.url})"
                embed = discord.Embed(
                    description=f"{display_name} が {vc_name_link} に参加しました",
                    color=discord.Color.green()
                )
                embed.set_footer(text=f"ユーザーID: {member.id}")
                await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(VCLog(bot))
