import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import random

class Coin(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    def get_user_ref(self, user_id):
        return self.db.collection("users").document(str(user_id))

    async def get_user_data(self, user_id):
        doc = self.get_user_ref(user_id).get()
        if doc.exists:
            return doc.to_dict()
        else:
            return {"coins": 0, "work_level": 1, "last_work": None}

    async def set_user_data(self, user_id, data):
        self.get_user_ref(user_id).set(data, merge=True)

    async def add_coins(self, user_id, amount):
        data = await self.get_user_data(user_id)
        coins = data.get("coins", 0) + amount
        data["coins"] = coins
        await self.set_user_data(user_id, data)
        return coins

    # 🔹 /work コマンド
    @app_commands.command(name="work", description="仕事をしてコインを稼ぐ（4時間ごと）")
    async def work(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        data = await self.get_user_data(user_id)

        now = datetime.utcnow()
        last_work = data.get("last_work")
        if last_work:
            last_time = datetime.fromisoformat(last_work)
            if now - last_time < timedelta(hours=4):
                remaining = timedelta(hours=4) - (now - last_time)
                hours, remainder = divmod(int(remaining.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                await interaction.response.send_message(
                    f"⏳ まだ働けません。あと {hours}時間 {minutes}分 {seconds}秒 待ってください。",
                    ephemeral=True
                )
                return

        # 労働レベルに応じた報酬
        level = data.get("work_level", 1)
        base_reward = random.randint(50, 100)  # 基本額
        reward = base_reward * level

        # コイン追加と最後の労働時間更新
        await self.add_coins(user_id, reward)
        data["last_work"] = now.isoformat()
        await self.set_user_data(user_id, data)

        await interaction.response.send_message(
            f"💼 仕事をしました！労働レベル {level} で {reward} コインを獲得！"
        )

# Cog登録用
async def setup(bot, db):
    from .coin import Coin
    await bot.add_cog(Coin(bot, db))
