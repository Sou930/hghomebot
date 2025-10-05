import os
import discord
from discord.ext import commands
import asyncio
import threading

# Firebase
from data.firebase_init import init_firebase
db = init_firebase()

# Bot設定
TOKEN = os.environ.get("DISCORD_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# keep_aliveをスレッドで起動
try:
    from keep_alive import keep_alive
    threading.Thread(target=keep_alive).start()
except Exception as e:
    print(f"⚠️ keep_alive error: {e}")

# Bot起動後にCog登録
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

    try:
        from program.currency.coin import Coin
        from program.currency.casino import Casino
        from program.top import Top
        from program.search import Search
        from program.ticket import Ticket
        from program.youtube import Youtube 
        from program.currency.steal import Steal
        from program.currency.bank import Bank
        from program.status import Status

        await bot.add_cog(Coin(bot, db))
        await bot.add_cog(Casino(bot, db))
        await bot.add_cog(Top(bot, db))
        await bot.add_cog(Search(bot))
        await bot.add_cog(Ticket(bot))
        await bot.add_cog(Youtube(bot))
        await bot.add_cog(Steal(bot, db))
        await bot.add_cog(Bank(bot, db))
        await bot.add_cog(Status(bot, db))

        synced = await bot.tree.sync()
        print(f"🔗 Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"❌ Setup error: {e}")

# Bot起動
async def main():
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
