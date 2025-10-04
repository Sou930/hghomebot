import discord
from discord import app_commands
from discord.ext import commands
import random
from DATA.firebase_db import get_user_balance, set_user_balance, db
from datetime import datetime

class Casino(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="casino", description="カジノで増やそう！")
    @app_commands.describe(
        type="遊びを選択",
        bet="賭け金を入力"
    )
    async def casino(self, interaction: discord.Interaction, type: str, bet: int):
        user_id = str(interaction.user.id)

        # Firestoreから残高取得
        balance = get_user_balance(user_id)

        # 入力チェック
        if bet <= 0:
            await interaction.response.send_message("⚠️ 賭け金は1以上にしてください！", ephemeral=True)
            return
        if bet > balance:
            await interaction.response.send_message("💸 所持金が足りません！", ephemeral=True)
            return

        result_text = ""
        win_amount = 0

        # === SLOT ===
        if type == "slot":
            symbols = ["🍒", "🍋", "🔔", "💎", "7️⃣"]
            roll = [random.choice(symbols) for _ in range(3)]
            result_text = " | ".join(roll)

            if len(set(roll)) == 1:  # 3つ揃い
                win_amount = bet * 5
                result_message = f"💎 ジャックポット！ {win_amount} コイン獲得！"
            else:
                win_amount = -bet
                result_message = f"😢 はずれ！ {bet} コイン失いました。"

        # === COIN TOSS ===
        elif type == "cointoss":
            coin = random.choice(["表", "裏"])
            player_choice = random.choice(["表", "裏"])  # ランダム勝負にする
            win = (coin == player_choice)
            result_text = f"🪙 コイントス結果: **{coin}**（あなたの選択: {player_choice}）"

            if win:
                win_amount = bet
                result_message = f"🎉 勝利！ {bet} コイン獲得！"
            else:
                win_amount = -bet
                result_message = f"😢 残念！ {bet} コイン失いました。"

        else:
            await interaction.response.send_message("⚠️ `type` は `slot` または `cointoss` のみ使用できます。", ephemeral=True)
            return

        # 所持金更新
        new_balance = max(balance + win_amount, 0)
        set_user_balance(user_id, new_balance)

        embed = discord.Embed(
            title="🎰 カジノ結果",
            description=f"{interaction.user.mention}\n\n{result_text}\n\n{result_message}\n💰 現在の所持金: {new_balance} コイン",
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed)

    # --- オートコンプリート ---
    @casino.autocomplete("type")
    async def casino_type_autocomplete(self, interaction: discord.Interaction, current: str):
        types = ["slot", "cointoss"]
        return [
            app_commands.Choice(name=t, value=t)
            for t in types
            if current.lower() in t.lower()
        ]


async def setup(bot):
    await bot.add_cog(Casino(bot))
