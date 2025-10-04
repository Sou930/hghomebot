import discord
from discord.ext import commands
from discord import app_commands
from firebase_admin import firestore

class Coin(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    def get_user_ref(self, user_id):
        return self.db.collection("users").document(str(user_id))

    async def add_coins(self, user_id, amount):
        ref = self.get_user_ref(user_id)
        doc = ref.get()
        if doc.exists:
            coins = doc.to_dict().get("coins", 0) + amount
        else:
            coins = amount
        ref.set({"coins": coins}, merge=True)
        return coins

    # 🔹 /daily コマンド
    @app_commands.command(name="daily", description="毎日ログインボーナスを受け取る")
    async def daily(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        coins_added = 100  # 基本100コイン
        new_total = await self.add_coins(user_id, coins_added)
        await interaction.response.send_message(f"💰 {coins_added} コインを受け取りました！ 現在の所持: {new_total} コイン")

    # 🔹 /give_coin コマンド
    @app_commands.command(name="give_coin", description="指定ユーザーにコインを渡す")
    @app_commands.describe(user="コインを渡す相手", price="渡すコインの量")
    async def give_coin(self, interaction: discord.Interaction, user: discord.Member, price: int):
        if price <= 0:
            await interaction.response.send_message("❌ 1以上の値を指定してください。", ephemeral=True)
            return
        new_total = await self.add_coins(user.id, price)
        await interaction.response.send_message(f"✅ {user.mention} に {price} コインを渡しました！ 現在の所持: {new_total} コイン")

# 🔹 Cog登録用
async def setup(bot, db):
    await bot.add_cog(Coin(bot, db))
