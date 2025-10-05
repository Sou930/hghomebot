import discord
from discord.ext import commands

class TicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="チケットを作成", style=discord.ButtonStyle.green, custom_id="ticket_create")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user

        # 既存チャンネルチェック
        existing = discord.utils.get(guild.channels, name=f"ticket-{user.name}")
        if existing:
            await interaction.response.send_message("すでにチケットがあります。", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True)
        }
        channel = await guild.create_text_channel(f"ticket-{user.name}", overwrites=overwrites)
        await channel.send(f"{user.mention} チケットが作成されました。サポート担当者をお待ちください。")
        await interaction.response.send_message(f"チケットを作成しました: {channel.mention}", ephemeral=True)

class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ticket_announce", description="チケット案内メッセージを送信")
    async def ticket_announce(self, ctx):
        embed = discord.Embed(
            title="🎫 チケット案内",
            description="質問・提案・報告がある場合はこちらから個別のチャンネルを作成してお知らせください。",
            color=discord.Color.blurple()
        )
        embed.set_footer(text="チケットを作成するには下のボタンを押してください。")
        view = TicketButton()
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Ticket(bot))
