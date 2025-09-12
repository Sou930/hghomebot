import os
import discord
from discord.ext import commands
import asyncio
from keep_alive import keep_alive  # Flask keep-alive
from program.count import MathBot  # Cogをインポート

# ===== Bot設定 =====
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

# Cogを非同期で追加
async def setup_bot():
    await bot.add_cog(MathBot(bot))

# 起動時イベント
@bot.event
async def on_ready():
    print(f"✅ Bot がログインしました: {bot.user}")
    print(f"Bot ID: {bot.user.id}")
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} 個のスラッシュコマンドを同期しました")
    except Exception as e:
        print(f"⚠️ コマンド同期エラー: {e}")
    print('------')

# ----- Discord Bot を起動する async 関数 -----
async def main():
    print("🔄 keep_alive 起動中")
    keep_alive()  # Flaskサーバーを立ち上げて ping 対応
    TOKEN = os.environ.get("DISCORD_TOKEN")
    if TOKEN is None:
        raise ValueError("⚠️ DISCORD_TOKEN が設定されていません！")
    print("🔧 Cog をセットアップ中")
    await setup_bot()  # 非同期で実行
    print("🚀 Bot 起動中")
    await bot.start(TOKEN)

# ----- エントリーポイント -----
if __name__ == "__main__":
    asyncio.run(main())
