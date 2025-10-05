import discord
from discord.ext import commands
from discord import app_commands

class Status(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    def get_user_ref(self, user_id):
        return self.db.collection("users").document(str(user_id))

    async def get_user_data(self, user_id):
        doc = self.get_user_ref(user_id).get()
        if doc.exists:
            data = doc.to_dict()
            data.setdefault("coins", 0)
            data.setdefault("bank", 0)
            data.setdefault("work_level", 1)
            data.setdefault("exp", 0)
            return data
        else:
            return {"coins": 0, "bank": 0, "work_level": 1, "exp": 0}

    @app_commands.command(name="status", description="自分の職業レベルやコインを確認します")
    async def status(self, interaction: discord.Interaction):
        user = interaction.user
        data = await self.get_user_data(user.id)

        embed = discord.Embed(
            title=f"📊 {user.display_name} のステータス",
            color=discord.Color.blue()
        )
        embed.add_field(name="💰 所持コイン", value=f"{data['coins']} 枚", inline=True)
        embed.add_field(name="🏦 銀行残高", value=f"{data['bank']} 枚", inline=True)
        embed.add_field(name="⚒️ 労働レベル", value=f"{data['work_level']}", inline=True)
        embed.add_field(name="📈 経験値", value=f"{data['exp']}/{data['work_level']*100}", inline=True)
        await interaction.response.send_message(embed=embed)

async def setup(bot, db):
    await bot.add_cog(Status(bot, db))
