import discord
from discord.ext import commands
from discord import app_commands

class CountCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.last_number = 0
        self.last_user = None

    @app_commands.command(name="count", description="次の数字を入力します")
    async def count(self, interaction: discord.Interaction, number: int):
        # 同じ人が連続入力 → リセット
        if self.last_user == interaction.user.id:
            self.last_number = 0
            self.last_user = None
            await interaction.response.send_message("⚠️ 同じ人が連続してカウントしました！1にリセットされてしまいました...")
            return

        # 正しい次の数字か判定
        if number == self.last_number + 1:
            self.last_number = number
            self.last_user = interaction.user.id
            await interaction.response.send_message(f"✅ {number}！")
        else:
            self.last_number = 0
            self.last_user = None
            await interaction.response.send_message("❌ ミスです！1にリセットされてしまいました...")
