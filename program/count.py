import discord
from discord.ext import commands
from discord import app_commands
import ast

def safe_eval(expr: str) -> int | None:
    """
    数式を安全に評価する（+, -, *, /, () のみ対応）
    """
    try:
        node = ast.parse(expr, mode="eval")

        # 許可するノード型
        allowed_nodes = (ast.Expression, ast.BinOp, ast.UnaryOp,
                         ast.Num, ast.Add, ast.Sub, ast.Mult, ast.Div,
                         ast.Pow, ast.Mod, ast.FloorDiv,
                         ast.USub, ast.UAdd, ast.Constant, ast.Load)

        def check_node(n):
            if not isinstance(n, allowed_nodes):
                raise ValueError("不正な式")
            for child in ast.iter_child_nodes(n):
                check_node(child)

        check_node(node)
        return int(eval(compile(node, "<expr>", "eval")))
    except Exception:
        return None


class CountCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.count_channels = {}  # guild_id -> channel_id
        self.last_number = {}     # guild_id -> last number
        self.last_user = {}       # guild_id -> last user id

    # --- /startcount コマンド ---
    @app_commands.command(name="startcount", description="このチャンネルをカウント専用に設定します")
    async def startcount(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        self.count_channels[guild_id] = interaction.channel.id
        self.last_number[guild_id] = 0
        self.last_user[guild_id] = None
        await interaction.response.send_message("✅ このチャンネルがカウントチャンネルに設定されました！1からスタートです。")

    # --- メッセージ監視 ---
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        guild_id = message.guild.id if message.guild else None
        if guild_id is None:
            return

        # カウントチャンネルでなければ無視
        if self.count_channels.get(guild_id) != message.channel.id:
            return

        # 数字 or 式を判定
        content = message.content.strip()
        try:
            number = int(content)
        except ValueError:
            number = safe_eval(content)

        if number is None:
            await message.delete()
            return

        last_num = self.last_number.get(guild_id, 0)
        last_user = self.last_user.get(guild_id, None)

        # 同じ人が連続 → リセット
        if last_user == message.author.id:
            self.last_number[guild_id] = 0
            self.last_user[guild_id] = None
            await message.channel.send("⚠️ 同じ人が連続してカウントしました！1にリセットされてしまいました...何を四天王!?")
            return

        # 正しい次の数か
        if number == last_num + 1:
            self.last_number[guild_id] = number
            self.last_user[guild_id] = message.author.id
            await message.add_reaction("✅")
        else:
            self.last_number[guild_id] = 0
            self.last_user[guild_id] = None
            await message.channel.send("❌ ミスです！1にリセットされてしまいました...")
