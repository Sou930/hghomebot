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
async def setup_extensions():
    from program.currency.coin import setup as coin_setup
    from program.currency.casino import setup as casino_setup
    from program.top import setup as top_setup
    from program.search import setup as search_setup
    from program.ticket import setup as ticket_setup
    from program.youtube import setup as youtube_setup
    from program.bank import setup as bank_setup
    from program.profile import setup as profile_setup

    await coin_setup(bot, db)
    await casino_setup(bot, db)
    await bank_setup(bot, db)
    await top_setup(bot, db)
    await profile_setup(bot, db)
    await search_setup(bot)
    await ticket_setup(bot)
    await youtube_setup(bot)
    
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
