import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from data.firebase_init import init_firebase

db = init_firebase()

class Bank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 🔹 ユーザーデータ取得
    async def get_user_data(self, user_id: int):
        ref = db.collection("users").document(str(user_id))
        doc = ref.get()
        if doc.exists:
            return doc.to_dict()
        else:
            data = {"coins": 0, "bank": 0}
            ref.set(data)
            return data

    # 🔹 ユーザーデータ更新
    async def set_user_data(self, user_id: int, new_data: dict):
        ref = db.collection("users").document(str(user_id))
        ref.set(new_data, merge=True)

    # 🔹 /bank コマンド
    @app_commands.command(name="bank", description="銀行操作（預け入れ・引き出し・残高確認）")
    @app_commands.describe(
        type="操作の種類を選択（deposit=預け入れ、withdraw=引き出し、balance=残高確認）",
        amount="金額を指定（例: 100 または all）"
    )
    @app_commands.choices(
        type=[
            app_commands.Choice(name="deposit（預け入れ）", value="deposit"),
            app_commands.Choice(name="withdraw（引き出し）", value="withdraw"),
            app_commands.Choice(name="balance（残高確認）", value="balance"),
        ]
    )
    async def bank(self, interaction: discord.Interaction, type: app_commands.Choice[str], amount: str = None):
        user_id = interaction.user.id
        data = await self.get_user_data(user_id)
        coins = data.get("coins", 0)
        bank = data.get("bank", 0)

        # --- 残高確認 ---
        if type.value == "balance" or amount is None:
            embed = discord.Embed(
                title=f"💳 {interaction.user.display_name} の残高情報",
                color=discord.Color.green()
            )
            embed.add_field(name="💰 所持金", value=f"{coins} コイン")
            embed.add_field(name="🏦 銀行残高", value=f"{bank} コイン")
            embed.add_field(name="💵 合計資産", value=f"{coins + bank} コイン")
            await interaction.response.send_message(embed=embed)
            return

        # --- 金額チェック ---
        if amount.lower() == "all":
            amount = coins if type.value == "deposit" else bank
        else:
            try:
                amount = int(amount)
            except ValueError:
                await interaction.response.send_message("❌ 金額は数値または 'all' を指定してください。", ephemeral=True)
                return

        if amount <= 0:
            await interaction.response.send_message("❌ 金額は1以上を指定してください。", ephemeral=True)
            return

        # --- 預け入れ処理 ---
        if type.value == "deposit":
            if coins < amount:
                await interaction.response.send_message("💸 所持金が足りません。", ephemeral=True)
                return
            coins -= amount
            bank += amount
            await self.set_user_data(user_id, {"coins": coins, "bank": bank})
            await interaction.response.send_message(f"🏦 {amount} コインを銀行に預けました！\n💰 残高: {bank} コイン")

        # --- 引き出し処理（5%手数料） ---
        elif type.value == "withdraw":
            fee = int(amount * 0.05)  # 手数料5%
            total_deduction = amount + fee  # 実際に銀行から引かれる額

            if bank < total_deduction:
                await interaction.response.send_message(
                    f"🏦 銀行残高が足りません。\n必要額: {total_deduction} コイン（内手数料 {fee} コイン）",
                    ephemeral=True
                )
                return

            bank -= total_deduction
            coins += amount

            await self.set_user_data(user_id, {"coins": coins, "bank": bank})
            await interaction.response.send_message(
                f"💵 {amount} コインを引き出しました！（手数料 {fee} コイン）\n"
                f"🏦 残り銀行残高: {bank} コイン"
            )

async def setup(bot):
    await bot.add_cog(Bank(bot))
