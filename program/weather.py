# program/weather.py (修正・追加)
import discord
from discord import app_commands
from discord.ext import commands, tasks
import requests
import os
from firebase_admin import firestore
import firebase_admin
import asyncio

# --- 設定値 ---
# 利用するAPIのURL (広島: 340010)
WEATHER_API_URL = "https://weather.tsukumijima.net/api/forecast/city/340010"

# 実行時刻: 毎日 UTC 21:00 (日本時間 6:00) に実行
# discord.Time(hour=21, minute=0, tzinfo=discord.app_commands.transformers.tz_reference.utc)
TARGET_TIME_UTC = discord.Time(hour=21, minute=0)

# Firebase Firestore参照
# main.pyでfirebase_admin.initialize_app()が完了している必要があります
try:
    db = firestore.client()
    SCHEDULE_DOC_REF = db.collection('schedules').document('weather_hiroshima')
except ValueError:
    # Firebaseが初期化されていない場合の対処
    SCHEDULE_DOC_REF = None
    print("WARNING: Firestore client could not be initialized. Check Firebase initialization in main.py.")
# --------------------------------------------------------------------------------

class Weather(commands.Cog):
    """天気予報およびスケジュール関連のコマンドを管理するクラス"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Botの起動時にタスクを開始
        if SCHEDULE_DOC_REF:
            self.daily_weather_task.start()
        else:
            print("Daily weather task not started due to Firebase initialization failure.")

    def cog_unload(self):
        # Botのシャットダウン時にタスクを停止
        self.daily_weather_task.cancel()

    # --- ヘルパー関数 ---
    def _get_hiroshima_forecast(self):
        """広島の今日の天気データをAPIから取得し、必要な情報を抽出する (同期処理)"""
        
        response = requests.get(WEATHER_API_URL)
        response.raise_for_status()
        data = response.json()
        
        # 今日（forecasts[0]）のデータを取得
        today_forecast = data['forecasts'][0]
        
        city_name = data['title'].split('の')[0] # 例: '広島'の天気予報 -> '広島'
        date_label = today_forecast['dateLabel'] # '今日'
        telop = today_forecast['telop']
        detail = today_forecast['detail']['weather']
        temperature = today_forecast['temperature']['max']['celsius'] # 最高気温
        
        return {
            "city": city_name,
            "date": date_label,
            "telop": telop,
            "detail": detail.strip(),
            "max_temp": temperature if temperature else "不明" # 最高気温がない場合は'不明'
        }

    def _create_forecast_embed(self, forecast_data):
        """天気データからDiscord Embedを作成する"""
        
        embed = discord.Embed(
            title=f"☀️ 【{forecast_data['date']}】{forecast_data['city']}の天気予報",
            description=f"**{forecast_data['telop']}**",
            color=0xFFA500 # オレンジ色
        )
        embed.add_field(name="詳細", value=forecast_data['detail'], inline=False)
        embed.add_field(name="🌡️ 最高気温", value=f"{forecast_data['max_temp']}℃", inline=True)
        embed.set_footer(text="情報提供: 気象庁API / データは午前5時頃に更新されます")
        return embed

    # --- スケジュール実行タスク ---
    
    # 毎日 UTC 21:00 (日本時間 6:00) に実行
    @tasks.loop(time=TARGET_TIME_UTC) 
    async def daily_weather_task(self):
        """毎日6:00 JSTに広島の今日の天気予報を送信する非同期タスク"""
        
        # Firebase参照が有効かチェック
        if not SCHEDULE_DOC_REF:
            print("ERROR: daily_weather_task failed: Firebase is not initialized.")
            return
            
        # 1. チャンネルIDをFirebaseから取得
        try:
            doc = SCHEDULE_DOC_REF.get()
            if not doc.exists or 'channel_id' not in doc.to_dict():
                return # 設定がなければスキップ

            channel_id = doc.to_dict()['channel_id']
            target_channel = self.bot.get_channel(channel_id)
            if not target_channel:
                target_channel = await self.bot.fetch_channel(channel_id)
        except Exception as e:
            print(f"Error retrieving schedule from Firebase: {e}")
            return
        
        # 2. 広島の天気データを取得
        try:
            # requestsは同期ライブラリなので、asyncio.to_threadで非同期に実行
            # Python 3.9+ であれば asyncio.to_thread, それ以下であれば run_in_executor
            forecast_data = await self.bot.loop.run_in_executor(
                None, self._get_hiroshima_forecast
            )
            embed = self._create_forecast_embed(forecast_data)
            
            # 3. チャンネルに送信
            await target_channel.send(embed=embed)
            print(f"広島の天気予報をチャンネル {channel_id} に送信しました。")

        except Exception as e:
            # エラー発生時はログに記録
            print(f"Daily weather task failed (Hiroshima API error): {e}")

    # Botが完全に準備できてからタスクを開始
    @daily_weather_task.before_loop
    async def before_daily_weather_task(self):
        await self.bot.wait_until_ready()

    # --- アプリケーションコマンド ---
    
    @app_commands.command(name="set_channel", description="毎朝6時(JST)に広島の天気予報を送信するチャンネルを設定します。")
    @app_commands.describe(channel="天気予報を送信するテキストチャンネル")
    async def set_weather_schedule(self, interaction: discord.Interaction, channel: discord.TextChannel):
        
        # 権限チェック (Botの管理者権限を持つユーザーのみ実行可能と仮定)
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("このコマンドは**管理者**のみが実行できます。", ephemeral=True)
            return
        
        if not SCHEDULE_DOC_REF:
             await interaction.response.send_message("❌ Firebaseが初期化されていません。開発者に確認してください。", ephemeral=True)
             return

        # チャンネル権限チェック (Botがそのチャンネルにメッセージを送信できるか)
        if not channel.permissions_for(interaction.guild.me).send_messages:
            await interaction.response.send_message(
                f"Botはチャンネル {channel.mention} にメッセージを送信する権限がありません。",
                ephemeral=True
            )
            return

        try:
            # チャンネルIDをFirebaseに保存
            SCHEDULE_DOC_REF.set({'channel_id': channel.id})

            await interaction.response.send_message(
                f"✅ 毎朝6時(JST)に、広島の天気予報をチャンネル {channel.mention} に送信するように設定しました。",
                ephemeral=True
            )
        except Exception as e:
            print(f"Error saving schedule to Firebase: {e}")
            await interaction.response.send_message(
                "スケジュールの保存中にエラーが発生しました。Firebaseの接続を確認してください。",
                ephemeral=True
            )

# Cog/Extensionとしてロードするためのエントリポイント
async def setup(bot):
    await bot.add_cog(Weather(bot))
