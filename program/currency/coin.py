import datetime
import discord
from discord import app_commands
from discord.ext import commands

class Coin(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    @app_commands.command(name="daily", description="1日1回コインを受け取ります（連続ログインでボーナスアップ）")
    async def daily(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        user_ref = self.db.collection("users").document(user_id)
        user_data = user_ref.get().to_dict() or {}

        now = datetime.datetime.utcnow().date()
        last_claim = user_data.get("last_daily")
        streak = user_data.get("streak", 0)
        coins = user_data.get("coins", 0)

        # 連続ログイン判定
        if last_claim:
            last_date = datetime.datetime.strptime(last_claim, "%Y-%m-%d").date()
            if now == last_date:
                await interaction.response.send_message("❌ 今日の報酬はすでに受け取っています！")
                return
            elif now - last_date == datetime.timedelta(days=1):
                streak += 1
            else:
                streak = 1
        else:
            streak = 1

        reward = 100 + (streak - 1) * 20
        coins += reward

        user_ref.set({
            "coins": coins,
            "last_daily": now.strftime("%Y-%m-%d"),
            "streak": streak
        })

        await interaction.response.send_message(
            f"💰 {reward}コインを受け取りました！\n"
            f"現在の所持金: **{coins}** コイン\n"
            f"連続ログイン: **{streak}日**"
        )
