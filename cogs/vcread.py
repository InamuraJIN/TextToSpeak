import discord
from discord.ext import commands
from gtts import gTTS
import os
import json
import re
import emoji

class VCRead(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None
        self.text_channel = None
        self.last_user = None

        dictionary_path = os.path.join(os.path.dirname(__file__), "../data/dictionary.json")
        ignore_prefix_path = os.path.join(os.path.dirname(__file__), "../data/ignoreprefix.json")

        with open(dictionary_path, encoding="utf-8") as f:
            self.word_dict = json.load(f)

        with open(ignore_prefix_path, encoding="utf-8") as f:
            self.ignore_prefix = set(f.read().strip().splitlines())

    async def speak_text(self, text):
        if not self.voice_client or not self.voice_client.is_connected():
            print("⚠️ Bot は VC に接続していません。読み上げをスキップします。")
            return
        
        tts = gTTS(text=text, lang="ja")
        file_path = "voice.mp3"
        tts.save(file_path)

        if not self.voice_client.is_playing():
            self.voice_client.play(discord.FFmpegPCMAudio(file_path))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not self.voice_client:
            return
        if self.text_channel is None or message.channel.id != self.text_channel.id:
            return
        if not self.is_user_in_vc(message.author):
            return

        text = message.content.strip()

        # 修正①: メンションを含む場合は記号スキップの対象外
        if not message.mentions and text and text[0] in self.ignore_prefix:
            print(f"⚠️ {message.author.display_name} のメッセージをスキップ: {text}")
            return

        # 絵文字を削除
        text = self.remove_emojis(text)

        text = await self.format_text(text)
        if message.author.id != self.last_user:
            text = f"{message.author.display_name}、{text}"
        self.last_user = message.author.id

        await self.speak_text(text)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return

        bot_voice_client = discord.utils.get(self.bot.voice_clients, guild=member.guild)

        if not bot_voice_client or not bot_voice_client.is_connected():
            return

        bot_channel = bot_voice_client.channel

        # 修正②: 入退室時の読み上げは記号スキップの対象外
        if after.channel == bot_channel and before.channel != bot_channel:
            await self.speak_text(f"{member.display_name}、やっほー")
        elif before.channel == bot_channel and (after.channel != bot_channel or after.channel is None):
            await self.speak_text(f"{member.display_name}、またね")

    def remove_emojis(self, text):
        return emoji.replace_emoji(text, replace="")

    async def format_text(self, text):
        text = text.lower()
        text = re.sub(r"[ｗw]{2,}", "わらわら", text)
        text = re.sub(r"[ｗw]", "わら", text)

        for key, value in self.word_dict.items():
            text = text.replace(key, value)

        text = "URL" if "http" in text else text
        text = "添付ファイル" if "添付" in text else text
        
        return text

    def is_user_in_vc(self, user):
        bot_voice_client = discord.utils.get(self.bot.voice_clients, guild=user.guild)
        if bot_voice_client and bot_voice_client.channel:
            return user in bot_voice_client.channel.members
        return False

    async def set_text_channel(self, channel):
        self.text_channel = channel

    async def set_voice_client(self, vc):
        self.voice_client = vc

async def setup(bot):
    await bot.add_cog(VCRead(bot))
