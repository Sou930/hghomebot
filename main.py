import os
import discord
from discord.ext import commands
import asyncio
from keep_alive import keep_alive

# ===== Bot 設定 =====
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 起動時イベント
@bot.event
async def on_ready():
    print(f"✅ Bot is ready! Logged in as {bot.user}")

# メイン処理
async def main():
    keep_alive()  # Flaskサーバー起動
    TOKEN = os.environ.get("DISCORD_TOKEN")
    if TOKEN is None:
        raise ValueError("⚠️ 環境変数 DISCORD_TOKEN が設定されていません")
    await bot.start(TOKEN)

# エントリーポイント
if __name__ == "__main__":
    asyncio.run(main())
