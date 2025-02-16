import discord
from discord import app_commands
from discord.ext import commands

class SlashCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="jv", description="VC に参加する")
    async def join_vc(self, interaction: discord.Interaction):
        if not interaction.user.voice or not interaction.user.voice.channel:
            embed = discord.Embed(title="⚠️ VCに参加してね", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        channel = interaction.user.voice.channel
        vc = await channel.connect()

        vcread_cog = self.bot.get_cog("VCRead")
        if vcread_cog:
            await vcread_cog.set_text_channel(interaction.channel)
            await vcread_cog.set_voice_client(vc)

        embed = discord.Embed(title="おじゃましまーす", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="dv", description="VC から退出する")
    async def leave_vc(self, interaction: discord.Interaction):
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
            embed = discord.Embed(title="おとされるううう", color=discord.Color.orange())
            await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(SlashCommand(bot))
