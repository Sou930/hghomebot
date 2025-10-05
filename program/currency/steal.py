import discord
from discord.ext import commands
from discord import app_commands
import random
from datetime import datetime, timedelta

class Steal(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    def get_user_ref(self, user_id):
        return self.db.collection("users").document(str(user_id))

    async def get_user_data(self, user_id):
        doc = self.get_user_ref(user_id).get()
        if doc.exists:
            data = doc.to_dict()
            data.setdefault("coins", 0)
            data.setdefault("work_ban_until", None)
            data.setdefault("steal_level", 1)
            return data
        else:
            return {"coins": 0, "steal_level": 1, "work_ban_until": None}

    async def set_user_data(self, user_id, data):
        self.get_user_ref(user_id).set(data, merge=True)

    @app_commands.command(name="steal", description="ランキング上位の人からコインを盗む！")
    async def steal(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        user_data = await self.get_user_data(user_id)

        # work_banチェック
        if user_data.get("work_ban_until"):
            ban_time = datetime.fromisoformat(user_data["work_ban_until"])
            if datetime.utcnow() < ban_time:
                remain = ban_time - datetime.utcnow()
                hours = int(remain.total_seconds() // 3600)
                minutes = int((remain.total_seconds() % 3600) // 60)
                await interaction.response.send_message(
                    f"🚫 盗み失敗の罰中です。あと {hours}時間 {minutes}分 で解除されます。",
                    ephemeral=True
                )
                return

        # 上位ユーザーリストから選ぶ
        users = self.db.collection("users").order_by("coins", direction="DESCENDING").limit(10).stream()
        targets = [u for u in users if u.id != str(user_id)]
        if not targets:
            await interaction.response.send_message("❌ 対象が見つかりませんでした。", ephemeral=True)
            return

        target_doc = random.choice(targets)
        target_id = target_doc.id
        target_data = target_doc.to_dict()

        steal_level = user_data.get("steal_level", 1)
        success_chance = min(30 + steal_level * 5, 90)
        success = random.randint(1, 100) <= success_chance

        if success and target_data["coins"] >= 50:
            stolen = random.randint(50, min(200, target_data["coins"]))
            # 更新
            self.get_user_ref(target_id).update({"coins": target_data["coins"] - stolen})
            self.get_user_ref(user_id).update({"coins": user_data["coins"] + stolen})
            await interaction.response.send_message(f"🕶️ 盗み成功！{stolen} コインを盗みました！")
        else:
            fine = random.randint(50, 150)
            ban_until = (datetime.utcnow() + timedelta(hours=4)).isoformat()
            new_coins = max(0, user_data["coins"] - fine)
            await self.set_user_data(user_id, {"coins": new_coins, "work_ban_until": ban_until})
            await interaction.response.send_message(f"🚨 盗み失敗！罰金 {fine} コインと4時間の労働禁止！")

async def setup(bot, db):
    await bot.add_cog(Steal(bot, db))
