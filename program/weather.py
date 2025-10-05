# program/weather.py
import discord
from discord.ext import commands, tasks
from discord import app_commands
import requests
import os
import asyncio
from firebase_admin import firestore
import firebase_admin
import json

# --- 設定値 ---
# 利用するAPIのURL (広島: 340010)
WEATHER_API_URL = "https://weather.tsukumijima.net/api/forecast/city/340010"

# スケジュール実行時刻: 毎日 UTC 21:00 (日本時間 6:00) に実行
TARGET_TIME_UTC = discord.Time(hour=21, minute=0, tzinfo=discord.app_commands.transformers.tz_reference.utc)

# Firebase Firestore参照
# main.pyでfirebase_admin.initialize_app()が完了していることを前提とします
SCHEDULE_DOC_REF = None
if firebase_admin._apps:
    try:
        db = firestore.client()
        # スケジュール設定を保存するFirestoreのドキュメント参照
        SCHEDULE_DOC_REF = db.collection('schedules').document('weather_hiroshima')
    except ValueError:
        print("WARNING: Firestore client could not be initialized. Check Firebase initialization.")
# --------------------------------------------------------------------------------

class Weather(commands.Cog):
    """天気予報およびスケジュール関連のコマンドを管理するクラス"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        # Botの起動時にタスクを開始
        if SCHEDULE_DOC_REF:
            self.daily_weather_task.start()
        else:
            print("Daily weather task not started due to Firebase reference failure.")

    def cog_unload(self):
        """Cogがアンロードされる際にタスクを停止します"""
        self.daily_weather_task.cancel()

    # --- ヘルパー関数 ---
    def _get_hiroshima_forecast(self):
        """広島の今日の天気データをAPIから取得し、必要な情報を抽出する (同期処理)"""
        
        response = requests.get(WEATHER_API_URL)
        response.raise_for_status() # HTTPエラーをチェック
        data = response.json()
        
        # APIが返すデータ構造から、今日（forecasts[0]）のデータを抽出
        today_forecast = data['forecasts'][0]
        
        city_name = data['title'].split('の')[0] 
        date_label = today_forecast['dateLabel']
        telop = today_forecast['telop']
        detail = today_forecast['detail']['weather'].strip().replace('\n', ' ')
        temperature = today_forecast['temperature']['max']['celsius']
        
        return {
            "city": city_name,
            "date": date_label,
            "telop": telop,
            "detail": detail,
            "max_temp": temperature if temperature else "不明" # 最高気温がない場合
        }

    def _create_forecast_embed(self, forecast_data, title_prefix="☀️ 今日の天気予報"):
        """天気データからDiscord Embedを作成する"""
        
        embed = discord.Embed(
            title=f"{title_prefix}: {forecast_data['city']} ({forecast_data['date']})",
            description=f"**{forecast_data['telop']}**",
            color=0xFFA500 # オレンジ色
        )
        embed.add_field(name="詳細", value=forecast_data['detail'], inline=False)
        embed.add_field(name="🌡️ 最高気温", value=f"{forecast_data['max_temp']}℃", inline=True)
        embed.set_footer(text="情報提供: 気象庁API / データは午前5時頃に更新されます")
        return embed

    # --- スケジュール実行タスク ---
    
    @tasks.loop(time=TARGET_TIME_UTC) 
    async def daily_weather_task(self):
        """毎日6:00 JSTに広島の今日の天気予報を送信する非同期タスク"""
        
        if not SCHEDULE_DOC_REF:
            return 
            
        print("Daily weather check started for Hiroshima (JST 6:00).")
        
        # 1. チャンネルIDをFirebaseから取得
        try:
            doc = SCHEDULE_DOC_REF.get()
            if not doc.exists or 'channel_id' not in doc.to_dict():
                return 

            channel_id = doc.to_dict()['channel_id']
            # get_channelでキャッシュから取得できない場合、fetch_channelでAPIから取得を試みる
            target_channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(channel_id)

        except Exception as e:
            print(f"Error retrieving schedule from Firebase or fetching channel: {e}")
            return
        
        # 2. 広島の天気データを取得し、チャンネルに送信
        try:
            # 同期処理を非同期で実行
            forecast_data = await self.bot.loop.run_in_executor(
                None, self._get_hiroshima_forecast
            )
            embed = self._create_forecast_embed(forecast_data)
            
            await target_channel.send(embed=embed)
            print(f"広島の天気予報をチャンネル {channel_id} に送信しました。")

        except Exception as e:
            print(f"Daily weather task failed (API or sending error): {e}")

    # Botが完全に準備できてからタスクを開始
    @daily_weather_task.before_loop
    async def before_daily_weather_task(self):
        await self.bot.wait_until_ready()

    # --- アプリケーションコマンド ---
    
    @app_commands.command(name="weather", description="広島の今日の天気情報を即時表示します。")
    async def weather_command(self, interaction: discord.Interaction):
        await interaction.response.defer() # ephemeral=True を削除し、公開で応答
        
        try:
            forecast_data = await self.bot.loop.run_in_executor(
                None, self._get_hiroshima_forecast
            )
            embed = self._create_forecast_embed(forecast_data, title_prefix="☀️ 【即時表示】今日の天気予報")
            await interaction.followup.send(embed=embed)
            
        except requests.exceptions.HTTPError as e:
            await interaction.followup.send("天気APIとの通信に失敗しました。時間をおいてお試しください。", ephemeral=True)
            print(f"Weather command HTTP Error: {e}")
        except Exception as e:
            await interaction.followup.send("天気情報の取得中に予期せぬエラーが発生しました。", ephemeral=True)
            print(f"Weather command error: {e}")


    @app_commands.command(name="set_channel", description="毎朝6時(JST)に広島の天気予報を送信するチャンネルを設定します。")
    @app_commands.describe(channel="天気予報を送信するテキストチャンネル")
    async def set_weather_schedule(self, interaction: discord.Interaction, channel: discord.TextChannel):
        
        # 管理者権限チェック (Botの管理者の意図を尊重し、管理者のみに制限)
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("このコマンドは**管理者**のみが実行できます。", ephemeral=True)
            return
        
        if not SCHEDULE_DOC_REF:
             await interaction.response.send_message("❌ Firebaseが初期化されていません。開発者に確認してください。", ephemeral=True)
             return

        # Botがそのチャンネルにメッセージを送信する権限チェック
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
    # setup() 関数が呼び出された時点で、Botのモジュールとして登録
    await bot.add_cog(Weather(bot))
