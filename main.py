import os
import discord
from discord.ext import commands
from discord import app_commands
import asyncio

# 🔹 Firebase 初期化
from data.firebase_init import init_firebase
db = init_firebase()

# 🔹 Bot 初期化
TOKEN = os.environ.get("DISCORD_TOKEN")  # Render環境変数

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 🔹 Ready イベント
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔗 Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"❌ Sync error: {e}")

# 🔹 Cog登録
async def setup():
    from program.currency.coin import Coin
    from program.currency.casino import Casino
    from program.top import Top
    from program.search import Search

    await bot.add_cog(Coin(bot, db))
    await bot.add_cog(Casino(bot, db))
    await bot.add_cog(Top(bot, db))
    await bot.add_cog(Search(bot))

# 🔹 keep_alive がある場合は呼び出し
try:
    from keep_alive import keep_alive
    keep_alive()
except:
    pass

# 🔹 Bot 起動
async def main():
    await setup()
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
