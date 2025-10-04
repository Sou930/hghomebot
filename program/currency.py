import discord
from discord import app_commands
from discord.ext import commands
import json
from datetime import datetime, timedelta
import os

DATA_FILE = "Data/currency.json"

class Currency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=4)

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            return {}
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}

    def save_data(self, data):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    # --- /daily ---
    @app_commands.command(name="daily", description="20時間おきにログインボーナスを受け取る")
    async def daily(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        data = self.load_data()
        now = datetime.utcnow()

        if user_id not in data:
            data[user_id] = {"balance": 0, "last_daily": "2000-01-01T00:00:00"}

        last_claim = datetime.fromisoformat(data[user_id]["last_daily"])
        if now - last_claim < timedelta(hours=20):
            remaining = timedelta(hours=20) - (now - last_claim)
            await interaction.response.send_message(
                f"⏳ 次のログインボーナスまで {remaining.seconds // 3600}時間{(remaining.seconds % 3600) // 60}分 です。",
                ephemeral=True
            )
            return

        reward = 500
        data[user_id]["balance"] += reward
        data[user_id]["last_daily"] = now.isoformat()
        self.save_data(data)

        await interaction.response.send_message(f"🎉 {reward}コインを受け取りました！")

    # --- /balance ---
    @app_commands.command(name="balance", description="自分の所持金を確認する")
    async def balance(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        data = self.load_data()
        balance = data.get(user_id, {}).get("balance", 0)
        await interaction.response.send_message(f"💰 現在の所持金: {balance} コイン")

    # --- /top ---
    @app_commands.command(name="top", description="ランキングを表示する")
    @app_commands.describe(type="ランキングの種類を選択 (balanceのみ対応)")
    async def top(self, interaction: discord.Interaction, type: str):
        data = self.load_data()
        if not data or all("balance" not in v for v in data.values()):
            await interaction.response.send_message("📂 まだデータがありません。ログインボーナスを受け取ってみてね！")
            return

        if type != "balance":
            await interaction.response.send_message("⚠️ 現在は `type: balance` のみ対応しています。")
            return

        sorted_data = sorted(
            data.items(),
            key=lambda x: x[1].get("balance", 0),
            reverse=True
        )

        desc = ""
        for rank, (uid, info) in enumerate(sorted_data[:10], start=1):
            try:
                user = await self.bot.fetch_user(int(uid))
                name = user.name
            except Exception:
                name = f"Unknown({uid})"
            desc += f"**#{rank}** {name} — 💰 {info['balance']} コイン\n"

        embed = discord.Embed(
            title="🏆 所持金ランキング",
            description=desc or "データがありません。",
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed)

    # --- オートコンプリート対応 ---
    @top.autocomplete("type")
    async def type_autocomplete(self, interaction: discord.Interaction, current: str):
        types = ["balance"]
        return [
            app_commands.Choice(name=t, value=t)
            for t in types
            if current.lower() in t.lower()
        ]


async def setup(bot):
    await bot.add_cog(Currency(bot))
