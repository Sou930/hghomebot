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
            name="💰 通貨・報酬システム",
            value=(
                "/daily … 20時間おきにログインボーナスを受け取る\n"
                "/give_coin user: price: … 指定ユーザーにコインを渡す\n"
                "/work … 仕事をしてコインと経験値を獲得（4時間ごと）\n"
                "/bank withdraw amount: … 銀行から出金（手数料あり）\n"
                "/profile … 所持金・銀行残高・職業レベルを確認\n"
                "/dollar … コインとドルのレート表示、交換可能"
            ),
            inline=False
        )

        embed.add_field(
            name="💀 窃盗機能",
            value=(
                "/steal user: … 他ユーザーからコインを盗む（失敗リスクあり）\n"
                "成功率は窃盗レベルに依存\n"
                "失敗すると罰金＋/workが1日使用不可"
            ),
            inline=False
        )

        embed.add_field(
            name="👑 称号機能",
            value=(
                "/titles … 獲得した称号を確認\n"
                "例: 暇人 / ぼっち / ニート / 富豪 / 大富豪"
            ),
            inline=False
        )

        embed.add_field(
            name="🔍 検索機能",
            value=(
                "/search type: query: … Web検索/画像検索（ボタンで切替）\n"
                "/youtube query: … YouTube動画検索（Invidious）"
            ),
            inline=False
        )

        embed.set_footer(text="HGHomeBot v0.3.2 - 最新機能対応")

        await interaction.response.send_message(embed=embed)

# 🔹 Cog 登録
async def setup(bot):
    await bot.add_cog(Help(bot))

