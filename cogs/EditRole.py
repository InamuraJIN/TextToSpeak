import os
from discord.ext import commands
from discord import Member
from dotenv import load_dotenv

load_dotenv("GAPI.env")

TARGET_GUILD_IDS = [int(x.strip()) for x in os.getenv("DISCORD_GUILD_ID", "").split(",") if x.strip().isdigit()]
ENFORCED_ROLE_ID = int(os.getenv("DISCORD_ENFORCED_ROLE_ID", "0"))

class EditRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        if member.guild.id not in TARGET_GUILD_IDS:
            return
        role = member.guild.get_role(ENFORCED_ROLE_ID)
        if role is None:
            return
        if role in member.roles:
            await member.add_roles(role, reason="Enforced role on join")

async def setup(bot):
    await bot.add_cog(EditRole(bot))
