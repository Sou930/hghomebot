import os
import discord
from discord.ext import commands
from discord import app_commands
import asyncio

# ----- 環境変数からトークン取得 -----
TOKEN = os.environ.get("DISCORD_TOKEN")
if TOKEN is None:
    raise ValueError("⚠️ 環境変数 DISCORD_TOKEN が設定されていません！")

# Bot設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

# ----- MathBot Cog の定義 -----
class MathBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.counting_channels = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user} がログインしました！')
        print(f'Bot ID: {self.bot.user.id}')
        try:
            synced = await self.bot.tree.sync()
            print(f'{len(synced)} 個のスラッシュコマンドを同期しました')
        except Exception as e:
            print(f'コマンド同期エラー: {e}')
        print('------')
    
    # カウンティング機能
    @app_commands.command(name='start_counting', description='カウンティングを開始します')
    @app_commands.describe(start_number='開始する数字（デフォルト: 1）')
    async def start_counting(self, interaction: discord.Interaction, start_number: int = 1):
        self.counting_channels[interaction.channel.id] = {
            'current': start_number - 1,
            'last_user': None
        }
        await interaction.response.send_message(
            f'🔢 カウンティングを **{start_number}** から開始します！\n次の数字を入力してください。'
        )
    
    @app_commands.command(name='stop_counting', description='カウンティングを停止します')
    async def stop_counting(self, interaction: discord.Interaction):
        if interaction.channel.id in self.counting_channels:
            del self.counting_channels[interaction.channel.id]
            await interaction.response.send_message('⏹️ カウンティングを停止しました。')
        else:
            await interaction.response.send_message('❌ このチャンネルでカウンティングは開始されていません。')
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        channel_id = message.channel.id
        if channel_id in self.counting_channels:
            try:
                number = int(message.content.strip())
                counting_data = self.counting_channels[channel_id]
                
                if message.author.id == counting_data['last_user']:
                    await message.add_reaction('❌')
                    await message.channel.send(f'{message.author.mention} 連続で数字を入力することはできません！')
                    return
                
                if number == counting_data['current'] + 1:
                    counting_data['current'] = number
                    counting_data['last_user'] = message.author.id
                    await message.add_reaction('✅')
                    
                    if number % 100 == 0:
                        await message.channel.send(f'🎉 **{number}** に到達しました！おめでとうございます！')
                else:
                    await message.add_reaction('❌')
                    await message.channel.send(f'間違いです！次の数字は **{counting_data["current"] + 1}** です。')
                    
            except ValueError:
                pass  # 数字でない場合は無視
    
    # 進数変換
    @app_commands.command(name='to_binary', description='10進数を2進数に変換します')
    @app_commands.describe(number='変換する10進数')
    async def to_binary(self, interaction: discord.Interaction, number: int):
        result = bin(number)[2:]
        await interaction.response.send_message(f"`{number}` → 2進数: `{result}`")
    
    @app_commands.command(name='to_octal', description='10進数を8進数に変換します')
    @app_commands.describe(number='変換する10進数')
    async def to_octal(self, interaction: discord.Interaction, number: int):
        result = oct(number)[2:]
        await interaction.response.send_message(f"`{number}` → 8進数: `{result}`")
    
    @app_commands.command(name='to_hex', description='10進数を16進数に変換します')
    @app_commands.describe(number='変換する10進数')
    async def to_hexadecimal(self, interaction: discord.Interaction, number: int):
        result = hex(number)[2:].upper()
        await interaction.response.send_message(f"`{number}` → 16進数: `{result}`")
    
    @app_commands.command(name='convert_base', description='任意進数変換を行います')
    @app_commands.describe(number='変換する数字', from_base='変換前の進数 (2-36)', to_base='変換後の進数 (2-36)')
    async def convert_base(self, interaction: discord.Interaction, number: str, from_base: int, to_base: int):
        try:
            decimal_value = int(number, from_base)
            digits = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            if decimal_value == 0:
                result = '0'
            else:
                result = ''
                temp = abs(decimal_value)
                while temp > 0:
                    result = digits[temp % to_base] + result
                    temp //= to_base
                if decimal_value < 0:
                    result = '-' + result
            await interaction.response.send_message(f"{from_base}進数 `{number}` → {to_base}進数 `{result}`")
        except Exception:
            await interaction.response.send_message('❌ 有効な数字と進数を入力してください。')

# Cogを追加
async def setup_bot():
    await bot.add_cog(MathBot(bot))

async def main():
    await setup_bot()
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
