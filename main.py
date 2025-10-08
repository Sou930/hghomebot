import os
import discord
from discord.ext import commands
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
async def setup(bot, db):
    # 🔹 Cog のインポート
    from program.admin.admin import Admin
    from program.currency.coin import Coin
    from program.currency.casino import Casino
    from program.currency.bank import Bank
    from program.top import Top
    from program.profile import Profile
    from program.search.search import Search
    from program.ticket import Ticket
    from program.search.youtube import Youtube
    from program.help import Help
    from program.currency.trade import Trade
    from program.admin.role import RoleManager


    # 🔹 Cog の追加（dbが必要なものは db も渡す）
    await bot.add_cog(Admin(bot))
    await bot.add_cog(Coin(bot, db))
    await bot.add_cog(Casino(bot, db))
    await bot.add_cog(Bank(bot)) 
    await bot.add_cog(Top(bot, db))
    await bot.add_cog(Profile(bot, db))
    await bot.add_cog(Search(bot))
    await bot.add_cog(Ticket(bot))
    await bot.add_cog(Youtube(bot))
    await bot.add_cog(Help(bot))
    await bot.add_cog(Trade(bot, db))
    await bot.add_cog(RoleManager(bot))


# 🔹 keep_alive がある場合は呼び出し（Renderで常時稼働用）
try:
    from keep_alive import keep_alive
    keep_alive()
except ImportError:
    pass

# 🔹 Bot 起動
async def main():
    # Cog登録に bot と db を渡す
    await setup(bot, db)
    # Bot起動
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())

