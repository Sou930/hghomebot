import os
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from keep_alive import keep_alive  # Flask keep-alive

# ----- 環境変数からトークン取得 -----
TOKEN = os.environ.get("DISCORD_TOKEN")
if TOKEN is None:
    raise ValueError("⚠️ 環境変数 DISCORD_TOKEN が設定されていません！")

# Bot設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

# Cogを追加
async def setup_bot():
    from program.count import MathBot  # 移動したCogをインポート
    await bot.add_cog(MathBot(bot))

async def main():
    print("🔄 setup_bot 実行中")  # デバッグ
    await setup_bot()
    print("🚀 bot.start 実行前")  # デバッグ
    await bot.start(TOKEN)
    print("✅ bot.start 実行後")  # デバッグ（ここには通常来ない）


# ----- Render + UptimeRobot 用の起動 -----
if __name__ == "__main__":
    keep_alive()        # Flask を立ち上げて HTTP ping に対応
    asyncio.run(main()) # Bot を起動
