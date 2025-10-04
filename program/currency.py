import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from DATA.firebase_db import get_user_balance, set_user_balance
from DATA.firebase_db import db  # Firestoreクライアント

class Currency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- /daily ---
    @app_commands.command(name="daily", description="20時間おきにログインボーナスを受け取る")
    async def daily(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        now = datetime.utcnow()

        # Firestoreからユーザーデータ取得
        doc_ref = db.collection("users").document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            user_data = doc.to_dict()
            last_claim = datetime.fromisoformat(user_data.get("last_daily", "2000-01-01T00:00:00"))
            balance = user_data.get("balance", 0)
        else:
            last_claim = datetime(2000, 1, 1)
            balance = 0
            doc_ref.set({"balance": balance, "last_daily": last_claim.isoformat()})

        if now - last_claim < timedelta(hours=20):
            remaining = timedelta(hours=20) - (now - last_claim)
            await interaction.response.send_message(
                f"⏳ 次のログインボーナスまで {remaining.seconds // 3600}時間{(remaining.seconds % 3600) // 60}分 です。",
                ephemeral=True
            )
            return

        reward = 500
        balance += reward
        doc_ref.update({"balance": balance, "last_daily": now.isoformat()})

        await interaction.response.send_message(f"🎉 {reward}コインを受け取りました！")

    # --- /balance ---
    @app_commands.command(name="balance", description="自分の所持金を確認する")
    async def balance(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        balance = get_user_balance(user_id)
        await interaction.response.send_message(f"💰 現在の所持金: {balance} コイン")

    # --- /top ---
    @app_commands.command(name="top", description="ランキングを表示する")
    @app_commands.describe(type="ランキングの種類を選択 (balanceのみ対応)")
    async def top(self, interaction: discord.Interaction, type: str):
        users_ref = db.collection("users")
        docs = users_ref.stream()
        data = {doc.id: doc.to_dict() for doc in docs}

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
