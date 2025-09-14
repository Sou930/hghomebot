import discord
from discord.ext import commands
from discord import app_commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import aiohttp

class WeatherCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.notify_channels = {}  # guild_id -> { "weather": channel_id }

        # 毎日6時に天気予報を送信
        self.scheduler.add_job(self.send_weather_all, "cron", hour=6, minute=0)
        self.scheduler.start()

    # --- /set_channel コマンド ---
    @app_commands.command(name="set_channel", description="通知チャンネルを設定します（例: 天気予報）")
    async def set_channel(self, interaction: discord.Interaction, type: str):
        guild_id = interaction.guild.id
        if type.lower() not in ["weather"]:
            await interaction.response.send_message("⚠️ 現在サポートしているのは `weather` のみです。")
            return

        if guild_id not in self.notify_channels:
            self.notify_channels[guild_id] = {}

        self.notify_channels[guild_id][type.lower()] = interaction.channel.id
        await interaction.response.send_message(f"✅ このチャンネルが `{type}` 通知チャンネルに設定されました。")

    # --- 天気を全サーバーに送信 ---
    async def send_weather_all(self):
        for guild_id, types in self.notify_channels.items():
            channel_id = types.get("weather")
            if channel_id:
                channel = self.bot.get_channel(channel_id)
                if channel:
                    weather = await self.get_weather()
                    if weather:
                        await channel.send(f"☀️ おはようございます！今日の天気予報:\n{weather}")
                    else:
                        await channel.send("⚠️ 天気情報の取得に失敗しました。")

    # --- 天気取得 (Tsukumijima API利用) ---
    async def get_weather(self) -> str | None:
        url = "https://weather.tsukumijima.net/api/forecast/city/340010"  # 広島県広島市
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return None
                    data = await resp.json()

            title = data.get("title", "天気予報")
            forecasts = data.get("forecasts", [])

            if forecasts:
                today = forecasts[0]
                date_label = today.get("dateLabel", "今日")
                telop = today.get("telop", "不明")
                temps = today.get("temperature", {})
                min_temp = temps.get("min", {}).get("celsius", "-")
                max_temp = temps.get("max", {}).get("celsius", "-")
                return f"{title} ({date_label})\n天気: {telop}\n最高気温: {max_temp}℃ / 最低気温: {min_temp}℃"
            return None
        except Exception as e:
            print(f"Weather API error: {e}")
            return None
