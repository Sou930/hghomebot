import discord
from discord.ext import commands
from discord import app_commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Botのコマンド一覧を表示します")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📢 HGHomeBot コマンド一覧",
            color=discord.Color.green()
        )

        embed.add_field(
            name="💰 通貨システム",
            value=(
                "/daily … 20時間おきにログインボーナスを受け取る\n"
                "/top type: … 所持金・銀行残高・職業レベル・合計資産のランキングを表示\n"
                "/give_coin user: price: … 指定ユーザーにコインを渡す\n"
                "/bank type: amount: … 銀行に入金/出金（deposit/withdraw）\n"
                "/profile … 自分の所持金・銀行残高・職業レベルを確認\n"
                "/dollar … コインとドルのレート表示"
            ),
            inline=False
        )

        embed.add_field(
            name="🎰 カジノ機能",
            value=(
                "/cointoss bet: … コイントス\n"
                "/slot bet: … スロットマシンで遊ぶ\n"
                "/dice bet: … ダイスで遊ぶ"
            ),
            inline=False
        )

        embed.add_field(
            name="🔍 検索機能",
            value=(
                "/search type: query: … Web検索/画像検索（ボタンで切替）\n"
                "/youtube query: … Youtube動画検索（Invidious）"
            ),
            inline=False
        )

        embed.add_field(
            name="🛠 管理者機能",
            value=(
                "/timeout user: duration: … 指定ユーザーを一時ミュート\n"
                "/giverole user: role: … 指定ユーザーにロールを付与\n"
                "/ticket_button … チケット案内ボタンを作成"
            ),
            inline=False
        )

        embed.set_footer(text="HGHomeBot v0.3 - 最新機能対応")

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))
