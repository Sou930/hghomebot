import discord
from discord.ext import commands
from discord import app_commands

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 🔹 管理者権限チェック
    async def cog_check(self, ctx):
        if isinstance(ctx, commands.Context):
            return ctx.author.guild_permissions.administrator
        elif isinstance(ctx, discord.Interaction):
            return ctx.user.guild_permissions.administrator
        return False

    # 🔹 Timeout コマンド
    @app_commands.command(name="timeout", description="指定したユーザーを一時的にミュートします")
    @app_commands.describe(user="ミュートするユーザー", duration="時間（分単位）")
    async def timeout(self, interaction: discord.Interaction, user: discord.Member, duration: int):
        if duration <= 0:
            await interaction.response.send_message("❌ 時間は1分以上指定してください。", ephemeral=True)
            return

        try:
            await user.timeout(discord.utils.utcnow() + discord.timedelta(minutes=duration))
            await interaction.response.send_message(f"⏱ {user.mention} を {duration} 分間ミュートしました。")
        except Exception as e:
            await interaction.response.send_message(f"❌ ミュートできませんでした: {e}", ephemeral=True)

    # 🔹 ロール付与コマンド（/giverole に変更）
    @app_commands.command(name="giverole", description="指定したユーザーにロールを付与します")
    @app_commands.describe(user="ロールを付与するユーザー", role="付与するロール")
    async def giverole(self, interaction: discord.Interaction, user: discord.Member, role: discord.Role):
        try:
            await user.add_roles(role)
            await interaction.response.send_message(f"✅ {user.mention} に {role.name} を付与しました。")
        except Exception as e:
            await interaction.response.send_message(f"❌ ロールを付与できませんでした: {e}", ephemeral=True)

# 🔹 Cog登録用
async def setup(bot):
    await bot.add_cog(Admin(bot))
