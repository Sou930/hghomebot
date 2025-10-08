import discord
from discord.ext import commands
from discord import app_commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="コマンド一覧を表示します")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📖 HGHomeBot コマンド一覧",
            color=discord.Color.blurple()
        )

        # 💰 通貨システム
        embed.add_field(
            name="💰 通貨システム",
            value=(
                "`/daily` - 20時間ごとにボーナスを受け取る\n"
                "`/give_coin user: price:` - 指定ユーザーにコインを渡す\n"
                "`/bank type: amount:` - 銀行へ入金・出金する\n"
                "`/profile` - ユーザー情報を確認"
            ),
            inline=False
        )

        # 🏆 ランキング
        embed.add_field(
            name="🏆 ランキング",
            value=(
                "`/top type:` - ランキングを表示\n"
                "　・coin → 所持金\n"
                "　・bank → 銀行残高\n"
                "　・work_level → 職業レベル\n"
                "　・total → 合計資産"
            ),
            inline=False
        )

        # 💼 労働
        embed.add_field(
            name="💼 労働",
            value="`/work` - 4時間ごとに働いてコインを獲得",
            inline=False
        )

        # 🎰 カジノ
        embed.add_field(
            name="🎰 カジノ",
            value=(
                "`/cointoss bet:` - コイントス\n"
                "`/slot bet:` - スロットマシン\n"
                "`/dice bet:` - ダイスゲーム"
            ),
            inline=False
        )

        # 🔍 検索
        embed.add_field(
            name="🔍 検索",
            value="`/search query:` - Web検索を実行",
            inline=False
        )

        # 🛠 管理者機能
        embed.add_field(
            name="🛠 管理者機能",
            value=(
                "`/timeout user: duration:` - 一時ミュート\n"
                "`/giverole user: role:` - ロール付与\n"
                "`/ticket_button` - チケット案内を追加"
            ),
            inline=False
        )

        # バージョン情報
        embed.set_footer(text="HGHomeBot v0.3 | Developed by Sou930")

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Help(bot))
