import discord
from discord import app_commands
from discord.ext import commands
import os
import aiohttp

# Tavily APIキー（Renderの環境変数に設定しておく）
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="search", description="Tavilyでインターネット検索を行います")
    async def search(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer(thinking=True)

        # APIキーが設定されていない場合
        if not TAVILY_API_KEY:
            await interaction.followup.send("⚠ Tavily APIキーが設定されていません。管理者に連絡してください。")
            return

        # Tavily APIにリクエスト送信
        async with aiohttp.ClientSession() as session:
            url = "https://api.tavily.com/search"
            headers = {"Content-Type": "application/json"}
            json_data = {
                "api_key": TAVILY_API_KEY,
                "query": query,
                "num_results": 3
            }

            async with session.post(url, json=json_data, headers=headers) as resp:
                if resp.status != 200:
                    await interaction.followup.send("❌ 検索中にエラーが発生しました。")
                    return

                data = await resp.json()

        # 結果がない場合
        results = data.get("results", [])
        if not results:
            await interaction.followup.send("🔍 検索結果が見つかりませんでした。")
            return

        # 結果をEmbedで送信
        embed = discord.Embed(
            title=f"🔎 検索結果：{query}",
            color=0x3498db
        )

        for result in results:
            title = result.get("title", "タイトルなし")
            url = result.get("url", "")
            summary = result.get("content", "")
            if len(summary) > 150:
                summary = summary[:150] + "..."
            embed.add_field(name=title, value=f"{summary}\n[🔗 リンク]({url})", inline=False)

        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Search(bot))
