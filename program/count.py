import discord
from discord.ext import commands
from discord import app_commands

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

    # ===== カウンティング =====
    @app_commands.command(name='start_counting', description='カウンティングを開始します')
    @app_commands.describe(start_number='開始する数字（デフォルト: 1）')
    async def start_counting(self, interaction, start_number=1):
        self.counting_channels[interaction.channel.id] = {
            'current': start_number - 1,
            'last_user': None,
            'start_number': start_number
        }
        await interaction.response.send_message(
            f'🔢 カウンティングを **{start_number}** から開始します！'
        )

    # ===== メッセージ監視 =====
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        channel_id = message.channel.id
        if channel_id not in self.counting_channels:
            return

        counting_data = self.counting_channels[channel_id]
        try:
            number = int(message.content.strip())

            if message.author.id == counting_data['last_user']:
                await message.add_reaction('❌')
                await message.channel.send(
                    f'{message.author.mention} 連続で数字を入力できません！\n'
                    f'カウンティングを **{counting_data["start_number"]}** からリセットします。'
                )
                counting_data['current'] = counting_data['start_number'] - 1
                counting_data['last_user'] = None
                return

            if number == counting_data['current'] + 1:
                counting_data['current'] = number
                counting_data['last_user'] = message.author.id
                await message.add_reaction('✅')
                if number % 100 == 0:
                    await message.channel.send(f'🎉 **{number}** に到達！')
            else:
                await message.add_reaction('❌')
                await message.channel.send(
                    f'間違いです！カウンティングを **{counting_data["start_number"]}** からリセットします。'
                )
                counting_data['current'] = counting_data['start_number'] - 1
                counting_data['last_user'] = None
        except ValueError:
            pass

    # ===== 進数変換 =====
    @app_commands.command(name='to_binary', description='10進数を2進数に変換')
    @app_commands.describe(number='変換する数字')
    async def to_binary(self, interaction, number):
        await interaction.response.send_message(f"{number} → 2進数: `{bin(int(number))[2:]}`")

    @app_commands.command(name='to_octal', description='10進数を8進数に変換')
    @app_commands.describe(number='変換する数字')
    async def to_octal(self, interaction, number):
        await interaction.response.send_message(f"{number} → 8進数: `{oct(int(number))[2:]}`")

    @app_commands.command(name='to_hex', description='10進数を16進数に変換')
    @app_commands.describe(number='変換する数字')
    async def to_hexadecimal(self, interaction, number):
        await interaction.response.send_message(f"{number} → 16進数: `{hex(int(number))[2:].upper()}`")

    @app_commands.command(name='convert_base', description='任意進数変換')
    @app_commands.describe(number='数字', from_base='元の進数', to_base='変換後の進数')
    async def convert_base(self, interaction, number, from_base, to_base):
        try:
            decimal_value = int(number, int(from_base))
            digits = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            if decimal_value == 0:
                result = '0'
            else:
                result = ''
                temp = abs(decimal_value)
                while temp > 0:
                    result = digits[temp % int(to_base)] + result
                    temp //= int(to_base)
                if decimal_value < 0:
                    result = '-' + result
            await interaction.response.send_message(f"{from_base}進数 `{number}` → {to_base}進数 `{result}`")
        except Exception:
            await interaction.response.send_message('❌ 有効な数字と進数を入力してください。')
