import discord
from discord import app_commands
from discord.ext import commands
import json
from pathlib import Path
from datetime import datetime, timedelta

# 保存ファイルと設定
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
# Discord Bot スラッシュコマンド
# =====================

class Currency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="daily", description="20時間おきにログインボーナスを受け取る")
    async def daily(self, interaction: discord.Interaction):
        success, balance = claim_daily(interaction.user.id)
        if success:
            await interaction.response.send_message(
                f"🎉 {interaction.user.mention} ボーナス{DAILY_AMOUNT}を受け取りました！\n💰 現在の所持金: {balance}"
            )
        else:
            await interaction.response.send_message(
                f"⏳ {interaction.user.mention} まだボーナスを受け取れません。\n💰 現在の所持金: {balance}"
            )

    @app_commands.command(name="balance", description="現在の所持金を確認する")
    async def balance(self, interaction: discord.Interaction):
        balance = get_balance(interaction.user.id)
        await interaction.response.send_message(
            f"💰 {interaction.user.mention} の所持金: {balance}"
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Currency(bot))
