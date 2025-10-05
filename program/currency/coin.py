import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import random

class Coin(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    # 🔹 Firebaseのユーザードキュメント参照
    def get_user_ref(self, user_id):
        return self.db.collection("users").document(str(user_id))

    # 🔹 ユーザーデータ取得
    async def get_user_data(self, user_id):
        doc = self.get_user_ref(user_id).get()
        if doc.exists:
            data = doc.to_dict()
            data.setdefault("coins", 0)
            data.setdefault("work_level", 1)
            data.setdefault("last_work", None)
            data.setdefault("exp", 0)
            return data
        else:
            return {"coins": 0, "work_level": 1, "last_work": None, "exp": 0}

    # 🔹 データ保存
    async def set_user_data(self, user_id, data):
        self.get_user_ref(user_id).set(data, merge=True)

    # 🔹 コイン操作
    async def add_coins(self, user_id, amount):
        ref = self.get_user_ref(user_id)
        doc = ref.get()
        coins = (doc.to_dict().get("coins", 0) if doc.exists else 0) + amount
        ref.set({"coins": coins}, merge=True)
        return coins

    async def remove_coins(self, user_id, amount):
        ref = self.get_user_ref(user_id)
        doc = ref.get()
        coins = doc.to_dict().get("coins", 0) if doc.exists else 0
        if coins < amount:
            return False
        ref.set({"coins": coins - amount}, merge=True)
        return True

    # 🔹 /daily コマンド
    @app_commands.command(name="daily", description="毎日のログインボーナス")
    async def daily(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        data = await self.get_user_data(user_id)

        now = datetime.utcnow()
        last_claim = data.get("last_daily")
        if last_claim:
            last_time = datetime.fromisoformat(last_claim)
            if now - last_time < timedelta(hours=20):
                remaining = timedelta(hours=20) - (now - last_time)
                hours, remainder = divmod(int(remaining.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                await interaction.response.send_message(
                    f"⏳ まだ daily を受け取れません。あと {hours}時間 {minutes}分 {seconds}秒 待ってください。",
                    ephemeral=True
                )
                return

        reward = 100
        await self.add_coins(user_id, reward)
        await self.set_user_data(user_id, {"last_daily": now.isoformat()})

        await interaction.response.send_message(f"🎁 daily ボーナス {reward} コインを獲得！")

    # 🔹 /give_coin コマンド
    @app_commands.command(name="give_coin", description="指定ユーザーにコインを渡す")
    @app_commands.describe(user="受け取るユーザー", price="渡すコイン数")
    async def give_coin(self, interaction: discord.Interaction, user: discord.Member, price: int):
        if price <= 0:
            await interaction.response.send_message("❌ 1以上の値を指定してください。", ephemeral=True)
            return

        can_send = await self.remove_coins(interaction.user.id, price)
        if not can_send:
            await interaction.response.send_message("❌ コインが不足しています。", ephemeral=True)
            return

        await self.add_coins(user.id, price)
        await interaction.response.send_message(f"✅ {user.display_name} に {price} コインを渡しました！")

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

        # 🔸 労働報酬（レベル依存）
        level = data.get("work_level", 1)
        base_reward = random.randint(50, 100)
        reward = base_reward * level

        # 🔸 経験値とレベルアップ処理
        exp_gain = random.randint(5, 15)
        exp = data.get("exp", 0) + exp_gain
        next_level_req = level * 100  # 次レベルに必要な経験値

        leveled_up = False
        if exp >= next_level_req:
            exp -= next_level_req
            level += 1
            leveled_up = True

        # 🔸 保存
        await self.add_coins(user_id, reward)
        await self.set_user_data(user_id, {
            "last_work": now.isoformat(),
            "exp": exp,
            "work_level": level
        })

        # 🔸 結果表示
        msg = f"💼 仕事をしました！労働レベル {level} で {reward} コインを獲得！（+{exp_gain}EXP）"
        if leveled_up:
            msg += "\n🎉 労働レベルが上がりました！"

        await interaction.response.send_message(msg)

# 🔹 Cog 登録
async def setup(bot, db):
    await bot.add_cog(Coin(bot, db))
