import discord
from discord.ext import commands
from discord import app_commands

class RoleManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 🔹 /giverole コマンド
    @app_commands.command(name="giverole", description="指定ユーザーにロールを付与します（管理者専用）")
    @app_commands.describe(user="ロールを付与するユーザー", role="付与するロール")
    async def giverole(self, interaction: discord.Interaction, user: discord.Member, role: discord.Role):
        # 管理者チェック
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ あなたにはこのコマンドを使う権限がありません。", ephemeral=True)
            return

        try:
            await user.add_roles(role)
            await interaction.response.send_message(f"✅ {user.mention} にロール `{role.name}` を付与しました。")
        except Exception as e:
            await interaction.response.send_message(f"❌ ロールの付与に失敗しました: {e}")

# 🔹 Cog 登録
async def setup(bot):
    await bot.add_cog(RoleManager(bot))
