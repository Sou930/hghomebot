import discord
from discord.ext import commands
import aiohttp

class Youtube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Invidious インスタンス URL
        self.invidious_base = "https://invidious.snopyta.org/api/v1/search"

    @commands.hybrid_command(name="youtube", description="Youtube動画を検索します (Invidious)")
    async def youtube(self, ctx, *, query: str):
        params = {"q": query, "type": "video"}  # 動画のみ取得

        async with aiohttp.ClientSession() as session:
            async with session.get(self.invidious_base, params=params) as resp:
                if resp.status != 200:
                    await ctx.send("検索に失敗しました。")
                    return
                data = await resp.json()

        if not data:
            await ctx.send("検索結果が見つかりませんでした。")
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
