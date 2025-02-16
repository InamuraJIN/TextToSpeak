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

        if after.channel == vc_channel:
            if bot_voice_client and bot_voice_client.is_connected():
                return  
            
            try:
                vc = await vc_channel.connect()
                vcread_cog = self.bot.get_cog("VCRead")
                if vcread_cog:
                    await vcread_cog.set_voice_client(vc)

                    # VC に紐づいたテキストチャット（ボイスチャンネルのメッセージ機能）を取得
                    if vc_channel.permissions_for(guild.me).read_messages:
                        text_channel = vc_channel
                        await vcread_cog.set_text_channel(text_channel)
                        print(f"📝 読み上げ対象チャンネルを VCテキスト ({vc_channel.name}) に設定しました")
                    else:
                        print("⚠️ VCテキストチャンネルの権限がない、または存在しません")

                print(f"✅ Bot が {vc_channel.name} に接続しました")
            except discord.errors.ClientException:
                print(f"⚠️ Bot は既に VC に接続しています")

        elif before.channel == vc_channel and after.channel != vc_channel:
            if bot_voice_client and len(vc_channel.members) == 1:
                await bot_voice_client.disconnect()
                vcread_cog = self.bot.get_cog("VCRead")
                if vcread_cog:
                    await vcread_cog.set_voice_client(None)
                    await vcread_cog.set_text_channel(None)
                print(f"🔇 Bot が {vc_channel.name} から退出しました")

async def setup(bot):
    await bot.add_cog(VCJoin(bot))
