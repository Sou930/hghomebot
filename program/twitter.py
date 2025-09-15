import discord
from discord.ext import commands
from discord import app_commands
import os
from twikit import Client

class TwitterCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client = None
        self.logged_in = False

    async def login(self):
        """Render環境変数からログイン"""
        if self.logged_in:
            return

        username = os.getenv("TWITTER_USERNAME")
        email = os.getenv("TWITTER_EMAIL")
        password = os.getenv("TWITTER_PASSWORD")

        if not username or not password:
            print("⚠️ Twitterの環境変数が設定されていません。")
            return

        self.client = Client("ja")  # 日本語
        await self.client.login(auth_info_1=username, auth_info_2=email, password=password)
        self.logged_in = True
        print("✅ Twitterにログイン成功")

    @app_commands.command(name="twitter_trend", description="日本のTwitterトレンドを表示します")
    async def twitter_trend(self, interaction: discord.Interaction):
        # ログイン処理
        if not self.logged_in:
            await self.login()
            if not self.logged_in:
                await interaction.response.send_message("⚠️ Twitterクライアントが準備できませんでした。")
                return

        # 日本のトレンド取得（WOEID=23424856）
        try:
            trends = await self.client.get_trends("23424856")
        except Exception as e:
            await interaction.response.send_message(f"⚠️ トレンド取得中にエラーが発生しました: {e}")
            return

        top_trends = trends[:10]  # 上位10件

        embed = discord.Embed(title="🇯🇵 日本のTwitterトレンド", color=discord.Color.blue())
        for t in top_trends:
            embed.add_field(name=t.name, value=f"ツイート数: {t.tweet_volume or '不明'}", inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="twitter_search", description="Twitterで検索します")
    async def twitter_search(self, interaction: discord.Interaction, keyword: str):
        if not self.logged_in:
            await self.login()
            if not self.logged_in:
                await interaction.response.send_message("⚠️ Twitterクライアントが準備できませんでした。")
                return

        try:
            posts = await self.client.search_tweet(keyword, "Latest")
        except Exception as e:
            await interaction.response.send_message(f"⚠️ 検索中にエラーが発生しました: {e}")
            return

        top_posts = posts[:5]

        embed = discord.Embed(title=f"🔎 Twitter検索: {keyword}", color=discord.Color.green())
        for p in top_posts:
            text = (p.text[:150] + "...") if len(p.text) > 150 else p.text
            url = f"https://x.com/{p.user.screen_name}/status/{p.id}"
            embed.add_field(name=f"@{p.user.screen_name}", value=f"{text}\n[リンク]({url})", inline=False)

        await interaction.response.send_message(embed=embed)
