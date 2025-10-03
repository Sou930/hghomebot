import discord
from discord.ext import commands
import json
from pathlib import Path
from datetime import datetime, timedelta

# 保存先ファイル
DATA_FILE = Path("Data/currency.json")
BONUS_HOURS = 20      # ログインボーナス間隔（20時間）
DAILY_AMOUNT = 100    # ボーナス額

def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_currency(user_id, amount):
    """ユーザーに通貨を加算"""
    data = load_data()
    user = data.get(str(user_id), {"balance": 0, "last_daily": None})
    user["balance"] += amount
    data[str(user_id)] = user
    save_data(data)
    return user["balance"]

def can_receive_daily(user_id):
    """ログインボーナスを受け取れるか判定"""
    data = load_data()
    user = data.get(str(user_id))
    if not user or not user.get("last_daily"):
        return True
    last_claim = datetime.fromisoformat(user["last_daily"])
    return (datetime.utcnow() - last_claim) >= timedelta(hours=BONUS_HOURS)

def claim_daily(user_id):
    """ログインボーナスを受け取る処理"""
    data = load_data()
    user = data.get(str(user_id), {"balance": 0, "last_daily": None})

    if can_receive_daily(user_id):
        user["balance"] += DAILY_AMOUNT
        user["last_daily"] = datetime.utcnow().isoformat()
        data[str(user_id)] = user
        save_data(data)
        return True, user["balance"]
    else:
        return False, user["balance"]

def get_balance(user_id):
    """所持金を取得"""
    data = load_data()
    user = data.get(str(user_id), {"balance": 0})
    return user["balance"]

# =====================
# Discord Bot コマンド
# =====================

class Currency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def daily(self, ctx):
        """20時間おきにログインボーナスを受け取る"""
        success, balance = claim_daily(ctx.author.id)
        if success:
            await ctx.send(f"🎉 {ctx.author.mention} ボーナス{DAILY_AMOUNT}を受け取りました！\n💰 現在の所持金: {balance}")
        else:
            await ctx.send(f"⏳ {ctx.author.mention} まだボーナスを受け取れません。\n💰 現在の所持金: {balance}")

    @commands.command()
    async def balance(self, ctx):
        """現在の所持金を確認"""
        balance = get_balance(ctx.author.id)
        await ctx.send(f"💰 {ctx.author.mention} の所持金: {balance}")

async def setup(bot):
    await bot.add_cog(Currency(bot))
