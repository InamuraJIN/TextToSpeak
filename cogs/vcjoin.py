import discord
from discord.ext import commands
import asyncio
from datetime import datetime
from .ServerSettings import get_guild_config

class VCJoin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """Bot起動時に既存のVCユーザーがいる場合は自動接続する"""
        await self.check_and_rejoin_voice_channels()

    async def check_and_rejoin_voice_channels(self):
        """全ギルドの自動参加設定チャンネルをチェックし、ユーザーがいる場合は接続する"""
        for guild in self.bot.guilds:
            guild_config = get_guild_config(guild.id)
            autojoin_vc_id = guild_config.get("auto_join_channel")
            if not autojoin_vc_id:
                continue

            vc_channel = guild.get_channel(autojoin_vc_id)
            if not vc_channel:
                continue

            # 既にBotが接続中か確認
            already_connected = False
            for vc_client in self.bot.voice_clients:
                if vc_client.guild == guild and vc_client.channel == vc_channel and vc_client.is_connected():
                    already_connected = True
                    break
            
            if already_connected:
                continue

            # 非Botユーザーがいるかチェック
            non_bot_members = [m for m in vc_channel.members if not m.bot]
            if not non_bot_members:
                continue

            # 接続を試行
            try:
                vc = await vc_channel.connect(timeout=10.0)
                print(f"✅ 起動時に {guild.name} の {vc_channel.name} に自動接続しました")
                
                vcread = self.bot.get_cog("VCRead")
                if vcread:
                    await vcread.set_voice_client(vc)
                    # テキストチャンネルを設定
                    attached_text_channel = discord.utils.get(guild.channels, id=vc_channel.id, type=discord.ChannelType.text)
                    if attached_text_channel is None:
                        attached_text_channel = discord.utils.get(guild.channels, type=discord.ChannelType.text)
                    await vcread.set_text_channel(attached_text_channel)
            except Exception as e:
                print(f"⚠️ 起動時の自動接続に失敗 ({guild.name}): {e}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return

        guild_config = get_guild_config(member.guild.id)
        autojoin_vc_id = guild_config.get("auto_join_channel")
        if not autojoin_vc_id:
            return

        vc_channel = member.guild.get_channel(autojoin_vc_id)
        if not vc_channel:
            return

        # ユーザーがVCから退出したときの処理
        if before.channel == vc_channel and after.channel != vc_channel:
            for vc_client in self.bot.voice_clients:
                if vc_client.guild == member.guild and vc_client.channel == vc_channel:
                    # メンバーリスト更新待ち
                    await asyncio.sleep(0.5)
                    non_bot_members = [m for m in vc_channel.members if not m.bot]
                    if not non_bot_members:
                        await vc_client.disconnect()
                        vcread = self.bot.get_cog("VCRead")
                        if vcread:
                            await vcread.set_voice_client(None)
                            await vcread.set_text_channel(None)
                    break
            return

        # ユーザーがVCに入室したときの処理
        if after.channel == vc_channel and before.channel != vc_channel:
            # 既にBotが接続中か確認
            for vc_client in self.bot.voice_clients:
                if vc_client.guild == member.guild and vc_client.channel == vc_channel and vc_client.is_connected():
                    return
            # 接続リトライ
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
                # Find appropriate text channel (same logic as SlashCommand.py)
                attached_text_channel = discord.utils.get(member.guild.channels, id=vc_channel.id, type=discord.ChannelType.text)
                if attached_text_channel is None:
                    # Fallback to first available text channel in the guild
                    attached_text_channel = discord.utils.get(member.guild.channels, type=discord.ChannelType.text)
                await vcread.set_text_channel(attached_text_channel)

async def setup(bot):
    await bot.add_cog(VCJoin(bot))
