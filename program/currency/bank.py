import discord
from discord.ext import commands
from discord import app_commands

class Bank(commands.Cog):
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
            return data
        else:
            return {"coins": 0, "bank": 0, "work_level": 1}

    async def set_user_data(self, user_id, data):
        self.get_user_ref(user_id).set(data, merge=True)

    # 🔹 /deposit 預け入れ
    @app_commands.command(name="deposit", description="銀行にコインを預けます")
    @app_commands.describe(amount="預ける金額")
    async def deposit(self, interaction: discord.Interaction, amount: int):
        if amount <= 0:
            await interaction.response.send_message("❌ 1以上の金額を指定してください。", ephemeral=True)
            return

        user_id = interaction.user.id
        data = await self.get_user_data(user_id)

        if data["coins"] < amount:
            await interaction.response.send_message("💰 手持ちのコインが足りません。", ephemeral=True)
            return

        limit = data["work_level"] * 500
        if data["bank"] + amount > limit:
            await interaction.response.send_message(f"🏦 預けられる上限は {limit} コインです。", ephemeral=True)
            return

        data["coins"] -= amount
        data["bank"] += amount
        await self.set_user_data(user_id, data)
        await interaction.response.send_message(f"✅ 銀行に {amount} コイン預けました。現在の預金：{data['bank']}")

    # 🔹 /withdraw 引き出し
    @app_commands.command(name="withdraw", description="銀行からコインを引き出します")
    @app_commands.describe(amount="引き出す金額")
    async def withdraw(self, interaction: discord.Interaction, amount: int):
        if amount <= 0:
            await interaction.response.send_message("❌ 1以上の金額を指定してください。", ephemeral=True)
            return

        user_id = interaction.user.id
        data = await self.get_user_data(user_id)

        if data["bank"] < amount:
            await interaction.response.send_message("💰 銀行に十分な預金がありません。", ephemeral=True)
            return

        data["coins"] += amount
        data["bank"] -= amount
        await self.set_user_data(user_id, data)
        await interaction.response.send_message(f"💸 銀行から {amount} コイン引き出しました。手持ち：{data['coins']}")

async def setup(bot, db):
    await bot.add_cog(Bank(bot, db))
