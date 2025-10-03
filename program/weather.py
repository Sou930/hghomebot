import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import aiohttp
from bs4 import BeautifulSoup

class EarthquakeCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.last_eq_time = None  # 最後に検知した地震の発生時刻
        self.channel_id = None    # 通知先チャンネルID

        # 30秒ごとにチェック
        self.scheduler.add_job(self.check_earthquake, "interval", seconds=30)
        self.scheduler.start()

    @commands.command(name="set_eq_channel")
    async def set_eq_channel(self, ctx: commands.Context):
        """地震速報の通知チャンネルを設定"""
        self.channel_id = ctx.channel.id
        await ctx.send("✅ このチャンネルを地震速報の通知先に設定しました")

    async def fetch_page(self):
        url = "https://typhoon.yahoo.co.jp/weather/jp/earthquake/"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None
                return await resp.text()

    async def check_earthquake(self):
        html = await self.fetch_page()
        if not html:
            return

        soup = BeautifulSoup(html, "html.parser")
        eq_table = soup.select_one("#eqinfdtl .yjw_table")
        if not eq_table:
            return

        # 発生時刻
        time_row = eq_table.select_one("tr:nth-of-type(1) td:nth-of-type(2) small")
        eq_time = time_row.get_text(strip=True) if time_row else None

        if not eq_time or eq_time == self.last_eq_time:
            return  # 新しい地震なし

        self.last_eq_time = eq_time  # 更新

        # 情報抽出
        rows = eq_table.select("tr")
        info = {}
        keys = ["発生時刻", "震源地", "最大震度", "マグニチュード", "深さ", "緯度/経度", "情報"]

        for i, key in enumerate(keys, start=1):
            td = rows[i].select_one("td:nth-of-type(2) small")
            info[key] = td.get_text(strip=True) if td else "-"

        # 画像URL
        eq_img = soup.select_one("#earthquake-01 img")
        img_url = eq_img["src"] if eq_img else None

        # Discordに送信
        if self.channel_id:
            channel = self.bot.get_channel(self.channel_id)
            if channel:
                embed = discord.Embed(
                    title="地震速報",
                    description=f"**発生時刻:** {info['発生時刻']}\n"
                                f"**震源地:** {info['震源地']}\n"
                                f"**最大震度:** {info['最大震度']}\n"
                                f"**M:** {info['マグニチュード']} / 深さ: {info['深さ']}\n"
                                f"**緯度/経度:** {info['緯度/経度']}\n"
                                f"{info['情報']}",
                    color=discord.Color.red()
                )
                if img_url:
                    embed.set_image(url=img_url)

                await channel.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(EarthquakeCog(bot))
