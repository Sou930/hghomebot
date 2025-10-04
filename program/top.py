import discord
from discord import app_commands
from discord.ext import commands

class Top(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    @app_commands.command(name="top", description="ランキングを表示します")
    @app_commands.describe(type="表示するランキングの種類 (例: coin)")
    async def top(self, interaction: discord.Interaction, type: str):
        if type.lower() != "coin":
            await interaction.response.send_message("❌ 現在利用できるのは `coin` のみです。")
            return

        users = self.db.collection("users").stream()
        ranking = sorted(
            [(u.id, u.to_dict().get("coins", 0)) for u in users],
            key=lambda x: x[1],
            reverse=True
        )

        if not ranking:
            await interaction.response.send_message("📭 まだ誰もコインを持っていません。")
            return

        embed = discord.Embed(title="💰 コインランキング", color=discord.Color.gold())
        for i, (uid, coins) in enumerate(ranking[:10], start=1):
            user = await self.bot.fetch_user(uid)
            embed.add_field(
                name=f"{i}位: {user.name}",
                value=f"{coins} コイン",
                inline=False
            )

        await interaction.response.send_message(embed=embed)
