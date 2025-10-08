import discord
from discord import app_commands
from discord.ext import commands
import os
import aiohttp

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CX = os.getenv("GOOGLE_CX")

class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="search",
        description="Google Custom SearchでWebまたは画像検索を行います"
    )
    @app_commands.describe(
        type="検索タイプを選択してください",
        query="検索キーワード"
    )
    @app_commands.choices(
        type=[
            app_commands.Choice(name="🌐 Web検索", value="web"),
            app_commands.Choice(name="🖼 画像検索", value="image")
        ]
    )
    async def search(self, interaction: discord.Interaction, type: app_commands.Choice[str], query: str):
        await interaction.response.defer(thinking=True)

        if not GOOGLE_API_KEY or not GOOGLE_CX:
            await interaction.followup.send("⚠ Google APIキーまたはCXが設定されていません。管理者に連絡してください。")
            return

        search_type = type.value
        params = {
            "key": GOOGLE_API_KEY,
            "cx": GOOGLE_CX,
            "q": query,
            "num": 5
        }
        if search_type == "image":
            params["searchType"] = "image"

        async with aiohttp.ClientSession() as session:
            async with session.get("https://www.googleapis.com/customsearch/v1", params=params) as resp:
                if resp.status != 200:
                    await interaction.followup.send(f"❌ 検索中にエラーが発生しました。ステータスコード: {resp.status}")
                    return
                data = await resp.json()

        items = data.get("items", [])
        if not items:
            await interaction.followup.send("🔍 検索結果が見つかりませんでした。")
            return

        current_index = 0

        def create_embed(index):
            item = items[index]
            title = item.get("title", "タイトルなし")
            url = item.get("link", "")
            snippet = item.get("snippet", "")[:200]
            embed = discord.Embed(
                title=f"{type.name}検索結果：{query}",
                color=discord.Color.blue()
            )
            if search_type == "image":
                embed.add_field(name=title, value=f"[🖼 画像リンク]({url})", inline=False)
                embed.set_image(url=url)
            else:
                embed.add_field(name=title, value=f"{snippet}\n[🔗 リンク]({url})", inline=False)
            embed.set_footer(text=f"{index + 1} / {len(items)} 件目")
            return embed

        class SearchView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=120)

            @discord.ui.button(label="◀ 前へ", style=discord.ButtonStyle.secondary)
            async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
                nonlocal current_index
                current_index = (current_index - 1) % len(items)
                await interaction.response.edit_message(embed=create_embed(current_index), view=self)

            @discord.ui.button(label="次へ ▶", style=discord.ButtonStyle.primary)
            async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
                nonlocal current_index
                current_index = (current_index + 1) % len(items)
                await interaction.response.edit_message(embed=create_embed(current_index), view=self)

        view = SearchView()
        await interaction.followup.send(embed=create_embed(current_index), view=view)

async def setup(bot):
    await bot.add_cog(Search(bot))
