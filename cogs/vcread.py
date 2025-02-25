import discord
from discord.ext import commands
from gtts import gTTS
import os
import json
import re
import emoji
import asyncio

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

        # Google TTS の音声設定
        self.speaking_rate = 1.2  
        self.pitch = 0.0 
        self.volume_gain_db = 0.0  

        self.read_queue = asyncio.Queue()
        self.read_task = self.bot.loop.create_task(self.read_loop())

    async def cog_unload(self):
        self.read_task.cancel()

    async def read_loop(self):
        while True:
            try:
                text = await self.read_queue.get()
                if text.strip() == "":
                    self.read_queue.task_done()
                    continue
                await self._speak_text(text)
                self.read_queue.task_done()
            except asyncio.CancelledError:
                break

    async def _speak_text(self, text: str):
        if not self.voice_client or not self.voice_client.is_connected():
            return
        try:
            tts = gTTS(text=text, lang="ja")
        except AssertionError:
            return
        file_path = "voice.mp3"
        tts.save(file_path)
        while self.voice_client.is_playing():
            await asyncio.sleep(0.3)
        self.voice_client.play(discord.FFmpegPCMAudio(file_path))
        while self.voice_client.is_playing():
            await asyncio.sleep(0.3)

    async def speak_text(self, text: str):
        if text.strip() == "":
            return
        await self.read_queue.put(text)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not self.voice_client:
            return
        if self.text_channel is None or message.channel.id != self.text_channel.id:
            return
        if not self.is_user_in_vc(message.author):
            return

        text = message.content.strip()
        if not message.mentions and text and text[0] in self.ignore_prefix:
            return
        
        # 添付ファイルがある場合は「添付ファイル」とする
        if message.attachments:
            text = "添付ファイル"
        else:
            text = emoji.replace_emoji(text, replace="")
            for ch in self.ignore_prefix:
                text = text.replace(ch, "")
            text = await self.format_text(text)


        # メンションをサーバーニックネームに置換
        for mention in message.mentions:
            text = text.replace(f"<@{mention.id}>", mention.display_name)
            text = text.replace(f"<@!{mention.id}>", mention.display_name)

        text = emoji.replace_emoji(text, replace="")
        for ch in self.ignore_prefix:
            text = text.replace(ch, "")
        text = await self.format_text(text)
        if message.author.id != self.last_user:
            text = f"{message.author.display_name}、{text}"
        self.last_user = message.author.id

        await self.speak_text(text)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot or not self.voice_client:
            return
        bot_voice_client = discord.utils.get(self.bot.voice_clients, guild=member.guild)
        if not bot_voice_client or not bot_voice_client.is_connected():
            return
        bot_channel = bot_voice_client.channel
        if after.channel == bot_channel and before.channel != bot_channel:
            await self.speak_text(f"{member.display_name}、やっほー")
        elif before.channel == bot_channel and (after.channel != bot_channel or after.channel is None):
            await self.speak_text(f"{member.display_name}、またね")

    async def format_text(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"[ｗw]{2,}", "わらわら", text)
        text = re.sub(r"[ｗw]", "わら", text)
        for key, value in self.word_dict.items():
            text = text.replace(key, value)
        if "http" in text:
            return "URL"
        return text

    def is_user_in_vc(self, user: discord.Member):
        bot_voice_client = discord.utils.get(self.bot.voice_clients, guild=user.guild)
        if bot_voice_client and bot_voice_client.channel:
            return user in bot_voice_client.channel.members
        return False

    async def set_text_channel(self, channel: discord.abc.Messageable):
        self.text_channel = channel

    async def set_voice_client(self, vc: discord.VoiceClient):
        self.voice_client = vc

async def setup(bot):
    await bot.add_cog(VCRead(bot))
    print("✅ vcread をロードしました")
