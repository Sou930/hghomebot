import random
import discord
from discord import app_commands
from discord.ext import commands

class Casino(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    @app_commands.command(name="cointoss", description="コイントスでコインを賭けます（50%の確率で2倍）")
    @app_commands.describe(bet="賭けるコインの枚数")
    async def cointoss(self, interaction: discord.Interaction, bet: int):
        if bet <= 0:
            await interaction.response.send_message("❌ 賭け額は1以上で入力してください。")
            return

        user_id = str(interaction.user.id)
        user_ref = self.db.collection("users").document(user_id)
        user_data = user_ref.get().to_dict() or {"coins": 0}
        coins = user_data.get("coins", 0)

        if coins < bet:
            await interaction.response.send_message("❌ コインが足りません！")
            return

        result = random.choice(["表", "裏"])
        win = random.choice([True, False])

        if win:
            coins += bet
            msg = f"🎉 {result}！ あなたの勝ち！ {bet}コイン獲得！"
        else:
            coins -= bet
            msg = f"💀 {result}！ 残念、負けです… {bet}コイン失いました。"

        user_ref.set({ "coins": coins }, merge=True)

        await interaction.response.send_message(
            f"{msg}\n現在の所持金: **{coins}** コイン"
        )
