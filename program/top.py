import discord
from discord.ext import commands
from discord import app_commands

COIN_TO_JPY = 10  # 1コイン = 10円
JPY_TO_USD = 1 / 150  # 仮に1ドル=150円（必要に応じて変更）

class Top(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    # 🔹 /top コマンド
    @app_commands.command(name="top", description="ランキングを表示します")
    @app_commands.describe(type="ランキングの種類を選択してください")
    @app_commands.choices(
        type=[
            app_commands.Choice(name="💰 所持金ランキング", value="coin"),
            app_commands.Choice(name="🏦 銀行残高ランキング", value="bank"),
            app_commands.Choice(name="💼 職業レベルランキング", value="work_level"),
            app_commands.Choice(name="💵 合計資産ランキング", value="total"),
            app_commands.Choice(name="💲 ドル換算ランキング", value="usd")
        ]
    )
    async def top(self, interaction: discord.Interaction, type: app_commands.Choice[str]):
        ranking_type = type.value
        users_ref = self.db.collection("users")
        docs = users_ref.stream()

        ranking = []
        for doc in docs:
            data = doc.to_dict()
            coins = data.get("coins", 0)
            bank = data.get("bank", 0)
            work_level = data.get("work_level", 0)

            if ranking_type == "coin":
                value = coins
            elif ranking_type == "bank":
                value = bank
            elif ranking_type == "work_level":
                value = work_level
            elif ranking_type == "total":
                value = coins + bank
            elif ranking_type == "usd":
                total_jpy = (coins + bank) * COIN_TO_JPY
                value = round(total_jpy * JPY_TO_USD, 2)
            ranking.append((doc.id, value))

        # 🔹 降順ソート（上位10人）
        ranking.sort(key=lambda x: x[1], reverse=True)
        top_10 = ranking[:10]

        # 🔹 埋め込み作成
        embed = discord.Embed(
            title=f"🏆 {type.name}",
            color=discord.Color.gold()
        )

        if not top_10:
            embed.description = "データがありません。"
        else:
            for i, (user_id, value) in enumerate(top_10, start=1):
                try:
                    user = await self.bot.fetch_user(int(user_id))
                    name = user.display_name
                except:
                    name = "不明なユーザー"
                embed.add_field(
                    name=f"#{i} {name}",
                    value=f"{value:,}",
                    inline=False
                )

        await interaction.response.send_message(embed=embed)

# 🔹 Cog登録
async def setup(bot, db):
    await bot.add_cog(Top(bot, db))
