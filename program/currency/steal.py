import discord
from discord import app_commands
from discord.ext import commands
import random
from datetime import datetime, timedelta

class Steal(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db  # 🔹 dbを引数として受け取る
        self.cooldowns = {}  # ユーザーごとのクールダウン管理

    # 🔹 ユーザーデータ取得
    async def get_user_data(self, user_id: int):
        ref = self.db.collection("users").document(str(user_id))
        doc = ref.get()
        if doc.exists:
            return doc.to_dict()
        else:
            data = {
                "coins": 0,
                "steal_exp": 0,
                "steal_level": 1,
                "work_locked_until": None
            }
            ref.set(data)
            return data

    # 🔹 ユーザーデータ更新
    async def set_user_data(self, user_id: int, new_data: dict):
        ref = self.db.collection("users").document(str(user_id))
        ref.set(new_data, merge=True)

    # 🔹 レベルアップ判定
    def check_level_up(self, exp: int, level: int):
        next_exp = level * 50  # 次レベルに必要な経験値
        leveled_up = False
        while exp >= next_exp:
            exp -= next_exp
            level += 1
            leveled_up = True
            next_exp = level * 50
        return exp, level, leveled_up

    # 🔹 /steal コマンド
    @app_commands.command(name="steal", description="他のユーザーからコインを盗もう！(失敗のリスクあり)")
    @app_commands.describe(user="盗む対象のユーザー")
    async def steal(self, interaction: discord.Interaction, user: discord.User):
        thief_id = interaction.user.id
        target_id = user.id

        if thief_id == target_id:
            await interaction.response.send_message("❌ 自分自身からは盗めません。", ephemeral=True)
            return

        # 🔸 クールダウン（6時間）
        now = datetime.utcnow()
        if thief_id in self.cooldowns and self.cooldowns[thief_id] > now:
            remaining = self.cooldowns[thief_id] - now
            hours = remaining.seconds // 3600
            minutes = (remaining.seconds % 3600) // 60
            await interaction.response.send_message(
                f"⏳ もう少し待って！あと **{hours}時間 {minutes}分** 後に再挑戦できます。",
                ephemeral=True
            )
            return
        self.cooldowns[thief_id] = now + timedelta(hours=6)

        # 🔸 データ取得
        thief_data = await self.get_user_data(thief_id)
        target_data = await self.get_user_data(target_id)

        thief_coins = thief_data.get("coins", 0)
        target_coins = target_data.get("coins", 0)
        steal_exp = thief_data.get("steal_exp", 0)
        steal_level = thief_data.get("steal_level", 1)

        if target_coins < 10:
            await interaction.response.send_message("😅 相手はほとんどお金を持っていません！", ephemeral=True)
            return

        # 🔸 成功率（基本40% + レベル×2%）
        success_chance = 0.4 + (steal_level * 0.02)
        success_chance = min(success_chance, 0.9)

        # --- 成功 ---
        if random.random() < success_chance:
            stolen = random.randint(5, int(target_coins * 0.3))
            target_coins -= stolen
            thief_coins += stolen

            # 経験値 +10
            steal_exp += 10
            steal_exp, steal_level, leveled_up = self.check_level_up(steal_exp, steal_level)

            await self.set_user_data(target_id, {"coins": target_coins})
            await self.set_user_data(thief_id, {
                "coins": thief_coins,
                "steal_exp": steal_exp,
                "steal_level": steal_level
            })

            msg = f"💀 {interaction.user.mention} は {user.mention} から **{stolen} コイン** を盗みました！"
            if leveled_up:
                msg += f"\n📈 窃盗レベルが **Lv.{steal_level}** に上がった！"
            await interaction.response.send_message(msg)

        # --- 失敗 ---
        else:
            fine = random.randint(10, 30)
            thief_coins = max(0, thief_coins - fine)
            # 失敗でも経験値 +3
            steal_exp += 3
            steal_exp, steal_level, leveled_up = self.check_level_up(steal_exp, steal_level)

            # 🔒 /work を1日ロック
            work_locked_until = datetime.utcnow() + timedelta(days=1)

            await self.set_user_data(thief_id, {
                "coins": thief_coins,
                "steal_exp": steal_exp,
                "steal_level": steal_level,
                "work_locked_until": work_locked_until.isoformat()
            })

            msg = f"🚨 {interaction.user.mention} は盗みに失敗！警備に捕まり **{fine} コイン** の罰金！\n" \
                  f"⏳ 1日間 `/work` が使用できません。"
            if leveled_up:
                msg += f"\n📈 でも経験で学び、窃盗レベルが **Lv.{steal_level}** に上がった！"
            await interaction.response.send_message(msg)

# 🔹 setup
async def setup(bot, db):
    await bot.add_cog(Steal(bot, db))
