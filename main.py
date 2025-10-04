import os
import discord
from discord.ext import commands

from keep_alive import keep_alive

# Token は Render の環境変数から取得
TOKEN = os.environ.get("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True  # メッセージ内容の取得を有効化

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔗 Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"❌ Sync error: {e}")

async def main():
    # Cog がまだないので setup は不要
    keep_alive()  # Render サーバー維持用
    await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
