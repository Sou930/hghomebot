import discord
from discord.ext import commands
import aiohttp

class Youtube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # 提供された Invidious インスタンスリスト
        self.invidious_instances = [
            "https://nyc1.iv.ggtyler.dev",
            "https://invid-api.poketube.fun/",
            "https://cal1.iv.ggtyler.dev",
            "https://invidious.nikkosphere.com",
            "https://lekker.gay",
            "https://invidious.f5.si",
            "https://invidious.lunivers.trade",
            "https://invid-api.poketube.fun",
            "https://pol1.iv.ggtyler.dev",
            "https://eu-proxy.poketube.fun",
            "https://iv.melmac.space",
            "https://invidious.reallyaweso.me",
            "https://invidious.dhusch.de",
            "https://usa-proxy2.poketube.fun",
            "https://id.420129.xyz",
            "https://invidious.darkness.service",
            "https://iv.datura.network",
            "https://invidious.jing.rocks",
            "https://invidious.private.coffee",
            "https://youtube.mosesmang.com",
            "https://iv.duti.dev",
            "https://invidious.projectsegfau.lt",
            "https://invidious.perennialte.ch",
            "https://invidious.einfachzocken.eu",
            "https://invidious.adminforge.de",
            "https://inv.nadeko.net",
            "https://invidious.esmailelbob.xyz",
            "https://invidious.0011.lt",
            "https://invidious.ducks.party"
        ]

    @commands.hybrid_command(name="youtube", description="Youtube動画を検索します (Invidious)")
    async def youtube(self, ctx, *, query: str):
        data = None
        # 複数インスタンスを順番に試す
        timeout = aiohttp.ClientTimeout(total=5)  # 5秒でタイムアウト
        async with aiohttp.ClientSession(timeout=timeout) as session:
            for base_url in self.invidious_instances:
                try:
                    api_url = f"{base_url}/api/v1/search"
                    async with session.get(api_url, params={"q": query, "type": "video"}) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if data:
                                break
                except Exception:
                    continue

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
