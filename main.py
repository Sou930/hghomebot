import os
import discord
from discord.ext import commands

from keep_alive import keep_alive
from data.firebase_init import init_firebase

# 🔹 Firebase 初期化
db = init_firebase()

# 🔹 Discord Bot設定
TOKEN = os.environ.get("DISCORD_TOKEN")  # Renderの環境変数から取得

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 🔹 起動時イベント
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔗 Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"❌ Sync error: {e}")

# 🔹 Cogを登録
async def setup():
    from program.currency.coin import Coin
    from program.currency.casino import Casino
    from program.top import Top

    await bot.add_cog(Coin(bot, db))
    await bot.add_cog(Casino(bot, db))
    await bot.add_cog(Top(bot, db))

# 🔹 メイン関数
async def main():
    await setup()
    keep_alive()  # Renderでの維持
    await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
