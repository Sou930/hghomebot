import os
import discord
from discord.ext import commands
from discord import app_commands

from keep_alive import keep_alive
from program.count import CountCog
from program.base import BaseCog
from program.weather import EarthquakeCog
from program.currency import Currency

TOKEN = os.environ.get("DISCORD_TOKEN")  # Renderの環境変数で設定する

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔗 Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"❌ Sync error: {e}")

# Cogを登録
async def setup():
    await bot.add_cog(CountCog(bot))
    await bot.add_cog(BaseCog(bot))
    await bot.add_cog(EarthquakeCog(bot))
    await bot.add_cog(Currency(bot))
    
async def main():
    await setup()
    keep_alive()
    await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
