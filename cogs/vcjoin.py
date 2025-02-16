import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv("GAPI.env")
AUTOJOIN_VC_ID = int(os.getenv("DISCORD_VC_AUTOJOIN01"))

class VCJoin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return

        guild = member.guild
        vc_channel = guild.get_channel(AUTOJOIN_VC_ID)

        if not vc_channel:
            print(f"⚠️ 指定された VC（ID: {AUTOJOIN_VC_ID}）が見つかりません")
            return

        bot_voice_client = discord.utils.get(self.bot.voice_clients, guild=guild)

        # VC の現在のメンバーリストを取得（Bot を除外）
        non_bot_members = [m for m in vc_channel.members if not m.bot]

        # ユーザーが VC に入ったとき
        if after.channel == vc_channel and before.channel != vc_channel:
            if bot_voice_client and bot_voice_client.is_connected():
                return  # すでに接続している場合は何もしない

            if len(non_bot_members) == 1:  # 最初のユーザーが入室した場合のみ接続
                try:
                    vc = await vc_channel.connect()
                    vcread_cog = self.bot.get_cog("VCRead")
                    if vcread_cog:
                        await vcread_cog.set_voice_client(vc)
                        await vcread_cog.set_text_channel(vc_channel)
                    print(f"✅ Bot が {vc_channel.name} に接続しました")
                except discord.errors.ClientException:
                    print(f"⚠️ Bot は既に VC に接続しています")

        # VC から最後のユーザーが退出したとき
        elif before.channel == vc_channel and after.channel != vc_channel:
            if bot_voice_client and len(non_bot_members) == 0:  # ユーザーがいなくなった場合
                await bot_voice_client.disconnect()
                vcread_cog = self.bot.get_cog("VCRead")
                if vcread_cog:
                    await vcread_cog.set_voice_client(None)
                    await vcread_cog.set_text_channel(None)
                print(f"🔇 Bot が {vc_channel.name} から退出しました")

async def setup(bot):
    await bot.add_cog(VCJoin(bot))
