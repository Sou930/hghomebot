# program/count.py
import discord
from discord.ext import commands
from discord import app_commands
import ast
import asyncio
import logging
import json
import os

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

DATA_DIR = "./Data"
COUNT_FILE = os.path.join(DATA_DIR, "count.json")


def safe_eval_int(expr: str) -> int | None:
    """式を安全に整数として評価"""
    try:
        node = ast.parse(expr, mode="eval")
        allowed_nodes = (
            ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
            ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod,
            ast.Pow, ast.UAdd, ast.USub, ast.Load
        )

        for n in ast.walk(node):
            if not isinstance(n, allowed_nodes):
                return None

        val = eval(compile(node, "<eval>", "eval"), {"__builtins__": {}}, {})
        if isinstance(val, int):
            return val
        if isinstance(val, float) and val.is_integer():
            return int(val)
        return None
    except Exception:
        return None


class CountCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.count_channels: set[int] = set()
        self.channel_states: dict[int, dict] = {}
        self._load_data()

    # --- JSON読み込み/保存 ---
    def _load_data(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        if not os.path.exists(COUNT_FILE):
            with open(COUNT_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
        with open(COUNT_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
        for ch_id, state in data.items():
            self.channel_states[int(ch_id)] = {
                "last_number": state.get("last_number", 0),
                "last_user": state.get("last_user"),
                "success": state.get("success", 0),
                "fails": state.get("fails", 0),
                "resets": state.get("resets", 0),
                "lock": asyncio.Lock()
            }

    def _save_data(self):
        data = {}
        for ch_id, state in self.channel_states.items():
            d = state.copy()
            d.pop("lock", None)
            data[str(ch_id)] = d
        with open(COUNT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # --- コマンド ---
    @app_commands.command(name="startcount", description="このチャンネルをカウント専用に設定します")
    async def startcount(self, interaction: discord.Interaction):
        ch_id = interaction.channel.id
        self.count_channels.add(ch_id)
        if ch_id not in self.channel_states:
            self.channel_states[ch_id] = {
                "last_number": 0,
                "last_user": None,
                "success": 0,
                "fails": 0,
                "resets": 0,
                "lock": asyncio.Lock()
            }
        else:
            self.channel_states[ch_id].update({
                "last_number": 0,
                "last_user": None
            })
        self._save_data()
        await interaction.response.send_message("✅ このチャンネルをカウントチャンネルに設定しました。1から始めてください。")

    @app_commands.command(name="stopcount", description="このチャンネルをカウントチャンネルから解除します")
    async def stopcount(self, interaction: discord.Interaction):
        ch_id = interaction.channel.id
        self.count_channels.discard(ch_id)
        self.channel_states.pop(ch_id, None)
        self._save_data()
        await interaction.response.send_message("🔕 このチャンネルをカウントチャンネルから解除しました。")

    @app_commands.command(name="count_statistics", description="このチャンネルのカウント統計を表示します")
    async def count_statistics(self, interaction: discord.Interaction):
        ch_id = interaction.channel.id
        state = self.channel_states.get(ch_id)
        if not state:
            await interaction.response.send_message("📊 このチャンネルではカウントがまだ開始されていません。")
            return

        embed = discord.Embed(title="📊 カウント統計", color=discord.Color.blue())
        embed.add_field(name="現在のカウント", value=str(state["last_number"]), inline=False)
        embed.add_field(name="成功数", value=str(state["success"]), inline=True)
        embed.add_field(name="失敗数", value=str(state["fails"]), inline=True)
        embed.add_field(name="リセット回数", value=str(state["resets"]), inline=True)

        await interaction.response.send_message(embed=embed)

    # --- on_message 処理 ---
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if message.guild is None or message.channel is None:
            return

        ch_id = message.channel.id
        if ch_id not in self.count_channels:
            return

        state = self.channel_states.setdefault(ch_id, {
            "last_number": 0,
            "last_user": None,
            "success": 0,
            "fails": 0,
            "resets": 0,
            "lock": asyncio.Lock()
        })

        async with state["lock"]:
            number = None
            try:
                number = int(message.content.strip())
            except Exception:
                number = safe_eval_int(message.content.strip())

            if number is None:
                return

            last_num = state["last_number"]
            last_user = state["last_user"]

            if last_user == message.author.id:
                state.update({"last_number": 0, "last_user": None})
                state["resets"] += 1
                await message.channel.send("⚠️ 同じ人が連続入力しました。リセットします。1からやり直してください。")
            elif number == last_num + 1:
                state.update({"last_number": number, "last_user": message.author.id})
                state["success"] += 1
                try:
                    await message.add_reaction("✅")
                except Exception:
                    pass
            else:
                state.update({"last_number": 0, "last_user": None})
                state["fails"] += 1
                await message.channel.send(f"❌ {number} は正しい次の数値ではありません。リセットします。")

            self._save_data()
