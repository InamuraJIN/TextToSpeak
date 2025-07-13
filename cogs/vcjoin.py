import discord
from discord.ext import commands
import asyncio
from datetime import datetime
from .ServerSettings import get_guild_config
import os

class VCJoin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.check_and_rejoin_voice_channels()

    async def get_text_channel_for_vc(self, vc_channel):
        vc_id = os.getenv("DISCORD_VC_AUTOJOIN01")
        if str(vc_channel.id) == vc_id:
            return vc_channel
        return None

    async def check_and_rejoin_voice_channels(self):
        for guild in self.bot.guilds:
            vc_id = os.getenv("DISCORD_VC_AUTOJOIN01")
            if not vc_id or not vc_id.isdigit():
                continue

            vc_channel = guild.get_channel(int(vc_id))
            if not vc_channel:
                continue

            already_connected = any(
                vc_client.guild == guild and vc_client.channel == vc_channel and vc_client.is_connected()
                for vc_client in self.bot.voice_clients
            )
            if already_connected:
                continue

            non_bot_members = [m for m in vc_channel.members if not m.bot]
            if not non_bot_members:
                continue

            try:
                vc = await vc_channel.connect(timeout=10.0)
                vcread = self.bot.get_cog("VCRead")
                if vcread:
                    await vcread.set_voice_client(vc)
                    await vcread.set_text_channel(vc_channel)
                    await vcread.restart_read_loop()
            except Exception as e:
                print(f"⚠️ 起動時の自動接続に失敗 ({guild.name}): {e}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return

        vc_id = os.getenv("DISCORD_VC_AUTOJOIN01")
        if not vc_id or not vc_id.isdigit():
            return

        vc_channel = member.guild.get_channel(int(vc_id))
        if not vc_channel:
            return

        if before.channel == vc_channel and after.channel != vc_channel:
            for vc_client in self.bot.voice_clients:
                if vc_client.guild == member.guild and vc_client.channel == vc_channel:
                    await asyncio.sleep(0.5)
                    non_bot_members = [m for m in vc_channel.members if not m.bot]
                    if not non_bot_members:
                        await vc_client.disconnect()
                        vcread = self.bot.get_cog("VCRead")
                        if vcread:
                            await vcread.set_voice_client(None)
                            await vcread.set_text_channel(None)
                            await vcread.restart_read_loop()
                    break
            return

        if after.channel == vc_channel and before.channel != vc_channel:
            for vc_client in self.bot.voice_clients:
                if vc_client.guild == member.guild and vc_client.channel == vc_channel and vc_client.is_connected():
                    return
            for i in range(3):
                try:
                    vc = await vc_channel.connect(timeout=10.0)
                    break
                except IndexError:
                    await asyncio.sleep(2)
                except Exception as e:
                    now = datetime.now().strftime('%m/%d %H:%M')
                    print(f"⚠️ {now} その他エラー: {e}")
                    return
            else:
                now = datetime.now().strftime('%m/%d %H:%M')
                print(f"❌ {now} 接続再試行に失敗しました")
                return

            vcread = self.bot.get_cog("VCRead")
            if vcread:
                await vcread.set_voice_client(vc)
                await vcread.set_text_channel(vc_channel)
                await vcread.restart_read_loop()

async def setup(bot):
    await bot.add_cog(VCJoin(bot))