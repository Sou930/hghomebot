import discord
from discord.ext import commands
import aiohttp

class Youtube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
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
        timeout = aiohttp.ClientTimeout(total=5)
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

        results = data[:10]
        current = 0

        def create_embed(index):
            video = results[index]
            title = video.get("title")
            video_id = video.get("videoId")
            description = video.get("description", "説明なし")[:200]
            url = f"https://www.youtube.com/watch?v={video_id}"
            embed = discord.Embed(
                title=title,
                description=f"{description}\n\n[▶ YouTubeで見る]({url})",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"{index + 1} / {len(results)} 件目")
            if "videoThumbnails" in video and len(video["videoThumbnails"]) > 0:
                embed.set_thumbnail(url=video["videoThumbnails"][0]["url"])
            return embed

        class YoutubeView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=120)

            @discord.ui.button(label="◀ 前へ", style=discord.ButtonStyle.secondary)
            async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
                nonlocal current
                current = (current - 1) % len(results)
                await interaction.response.edit_message(embed=create_embed(current), view=self)

            @discord.ui.button(label="次へ ▶", style=discord.ButtonStyle.primary)
            async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
                nonlocal current
                current = (current + 1) % len(results)
                await interaction.response.edit_message(embed=create_embed(current), view=self)

        view = YoutubeView()
        await ctx.send(embed=create_embed(current), view=view)

async def setup(bot):
    await bot.add_cog(Youtube(bot))

