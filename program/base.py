import discord
from discord.ext import commands
from discord import app_commands

class BaseCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="baseconversion",
        description="数字を指定した進数に変換します（2進数〜16進数対応）"
    )
    async def baseconversion(self, interaction: discord.Interaction, base: int, number: int):
        # base が範囲外ならエラー
        if base < 2 or base > 16:
            await interaction.response.send_message("⚠️ 変換できるのは **2進数〜16進数** のみです！")
            return

        # number を base に変換
        digits = "0123456789ABCDEF"
        result = ""

        n = number
        if n == 0:
            result = "0"
        else:
            while n > 0:
                result = digits[n % base] + result
                n //= base

        await interaction.response.send_message(
            f"🔢 **{number} (10進数)** を **{base}進数** に変換すると → `{result}`"
        )
