import discord
from discord.ext import commands
import aiohttp

class Youtube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # 複数の Invidious インスタンス
        self.invidious_instances = [
            "https://invidious.snopyta.org/api/v1/search",
            "https://invidious.kavin.rocks/api/v1/search",
            "https://invidious.namazso.eu/api/v1/search",
            "https://invidious.fdn.fr/api/v1/search",
            "https://invidious.tiekoetter.com/api/v1/search"
        ]

    @commands.hybrid_command(name="youtube", description="Youtube動画を検索します (Invidious)")
    async def youtube(self, ctx, *, query: str):
        data = None
        # インスタンスを順に試す
        async with aiohttp.ClientSession() as session:
            for url in self.invidious_instances:
                try:
                    async with session.get(url, params={"q": query, "type": "video"}, timeout=5) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if data:
                                break  # 成功したらループを抜ける
                except Exception:
                    continue  # 応答なしの場合は次のインスタンスへ

        if not data:
            await ctx.send("全ての Invidious インスタンスで検索に失敗しました。")
            return

        # 上位5件を表示
        embed = discord.Embed(title=f"Youtube検索結果: {query}", color=discord.Color.red())
        for item in data[:5]:
            title = item.get("title")
            url = f"https://www.youtube.com/watch?v={item.get('videoId')}"
            embed.add_field(name=title, value=url, inline=False)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Youtube(bot))
