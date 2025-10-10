import discord
from discord.ext import commands
from datetime import datetime, timedelta

class TitleManager(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    # 🔹 ユーザーデータ取得
    async def get_user_data(self, user_id: int):
        ref = self.db.collection("users").document(str(user_id))
        doc = ref.get()
        if doc.exists:
            data = doc.to_dict()
            # 欠けている値を補完
            data.setdefault("coins", 0)
            data.setdefault("bank", 0)
            data.setdefault("streak", 0)
            data.setdefault("titles", [])
            return data
        return {"coins": 0, "bank": 0, "streak": 0, "titles": []}

    # 🔹 称号判定
    async def check_titles(self, user_id: int):
        data = await self.get_user_data(user_id)
        titles = data.get("titles", [])

        # 条件に応じて称号を追加
        new_titles = []

        # 連続ログイン
streak = data.get("streak", 0)
if streak >= 7 and "暇人" not in titles:
    new_titles.append("暇人")     # 7日連続ログイン
if streak >= 30 and "ぼっち" not in titles:
    new_titles.append("ぼっち")   # 30日連続ログイン
if streak >= 60 and "ニート" not in titles:
    new_titles.append("ニート")   # 60日連続ログイン

# 所持資産称号
total_coins = data.get("coins", 0) + data.get("bank", 0)
if total_coins >= 100_000 and "富豪" not in titles:
    new_titles.append("富豪")         # 資産10万コイン突破
if total_coins >= 1_000_000 and "大富豪" not in titles:
    new_titles.append("大富豪")       # 資産100万コイン突破


        if new_titles:
            titles.extend(new_titles)
            # データ更新
            self.db.collection("users").document(str(user_id)).update({"titles": titles})
        return new_titles

    # 🔹 /titles コマンドで表示
    @commands.hybrid_command(name="titles", description="自分の獲得称号を表示します")
    async def titles(self, ctx):
        user_id = ctx.author.id
        await self.check_titles(user_id)  # 最新の称号をチェック
        data = await self.get_user_data(user_id)
        titles = data.get("titles", [])

        if not titles:
            msg = "まだ称号はありません。"
        else:
            msg = "\n".join([f"🏅 {t}" for t in titles])

        embed = discord.Embed(
            title=f"👑 {ctx.author.display_name} の称号",
            description=msg,
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)

# 🔹 Cog 登録
async def setup(bot, db):
    await bot.add_cog(TitleManager(bot, db))

