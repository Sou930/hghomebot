import discord
from discord.ext import commands
from discord import app_commands

class MathBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.counting_channels = {}  # チャンネルごとのカウンティング情報

    # -----------------------
    # カウンティング機能
    # -----------------------
    @app_commands.command(name='start_counting', description='カウンティングを開始します')
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

                # 連続入力チェック
                if message.author.id == counting_data['last_user']:
                    await message.add_reaction('❌')
                    await message.channel.send(f'{message.author.mention} 連続で数字を入力することはできません！')
                    return
                
                # 正しい数字チェック
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

    # -----------------------
    # 進数変換機能
    # -----------------------
    @app_commands.command(name='to_binary', description='10進数を2進数に変換します')
    async def to_binary(self, interaction: discord.Interaction, number: str):
        try:
            number_int = int(number)
            await interaction.response.send_message(f"`{number}` → 2進数: `{bin(number_int)[2:]}`")
        except ValueError:
            await interaction.response.send_message('❌ 有効な整数を入力してください。')

    @app_commands.command(name='to_octal', description='10進数を8進数に変換します')
    async def to_octal(self, interaction: discord.Interaction, number: str):
        try:
            number_int = int(number)
            await interaction.response.send_message(f"`{number}` → 8進数: `{oct(number_int)[2:]}`")
        except ValueError:
            await interaction.response.send_message('❌ 有効な整数を入力してください。')

    @app_commands.command(name='to_hex', description='10進数を16進数に変換します')
    async def to_hexadecimal(self, interaction: discord.Interaction, number: str):
        try:
            number_int = int(number)
            await interaction.response.send_message(f"`{number}` → 16進数: `{hex(number_int)[2:].upper()}`")
        except ValueError:
            await interaction.response.send_message('❌ 有効な整数を入力してください。')

    @app_commands.command(
        name='convert_base',
        description='任意進数変換を行います (2~36)'
    )
    async def convert_base(self, interaction: discord.Interaction, number: str, from_base: int, to_base: int):
        try:
            from_base_int = int(from_base)
            to_base_int = int(to_base)
            if not (2 <= from_base_int <= 36) or not (2 <= to_base_int <= 36):
                raise ValueError("進数は2から36の範囲で指定してください")
            
            decimal_value = int(str(number), from_base_int)
            digits = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            if decimal_value == 0:
                result = '0'
            else:
                result = ''
                temp = abs(decimal_value)
                while temp > 0:
                    result = digits[temp % to_base_int] + result
                    temp //= to_base_int
                if decimal_value < 0:
                    result = '-' + result

            await interaction.response.send_message(f"{from_base_int}進数 `{number}` → {to_base_int}進数 `{result}`")
        except Exception:
            await interaction.response.send_message('❌ 有効な数字と進数を入力してください。')

    # デバッグ用メソッド
    def reset_counting(self, counting_data):
        """カウンティングをリセットする"""
        counting_data['mistakes'] = counting_data.get('mistakes', 0) + 1
        counting_data['current'] = 0  # 次に期待する数字が1になる
        counting_data['last_user'] = None
        logger.info(f"リセット実行: current={counting_data['current']}")
