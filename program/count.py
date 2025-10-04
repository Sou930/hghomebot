import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from DATA.firebase_db import get_channel_state, set_channel_state, delete_channel_state

class CountCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.count_channels: set[int] = set()
        self.channel_states: dict[int, dict] = {}

    # --- /startcount ---
    @app_commands.command(name="startcount", description="このチャンネルをカウント専用に設定します")
    async def startcount(self, interaction: discord.Interaction):
        ch_id = interaction.channel.id
        self.count_channels.add(ch_id)

        state = get_channel_state(ch_id)
        state.update({"last_number": 0, "last_user": None, "lock": asyncio.Lock()})
        self.channel_states[ch_id] = state
        set_channel_state(ch_id, state)

        await interaction.response.send_message("✅ このチャンネルをカウントチャンネルに設定しました。1から始めてください。")

    # --- /stopcount ---
    @app_commands.command(name="stopcount", description="このチャンネルをカウントチャンネルから解除します")
    async def stopcount(self, interaction: discord.Interaction):
        ch_id = interaction.channel.id
        self.count_channels.discard(ch_id)
        self.channel_states.pop(ch_id, None)
        delete_channel_state(ch_id)
        await interaction.response.send_message("🔕 このチャンネルをカウントチャンネルから解除しました。")

    # --- /count_statistics ---
    @app_commands.command(name="count_statistics", description="このチャンネルのカウント統計を表示します")
    async def count_statistics(self, interaction: discord.Interaction):
        ch_id = interaction.channel.id
        state = get_channel_state(ch_id)
        if not state:
            await interaction.response.send_message("📊 このチャンネルではカウントがまだ開始されていません。")
            return

        embed = discord.Embed(title="📊 カウント統計", color=discord.Color.blue())
        embed.add_field(name="現在のカウント", value=str(state["last_number"]), inline=False)
        embed.add_field(name="成功数", value=str(state["success"]), inline=True)
        embed.add_field(name="失敗数", value=str(state["fails"]), inline=True)
        embed.add_field(name="リセット回数", value=str(state["resets"]), inline=True)
        await interaction.response.send_message(embed=embed)

    # --- on_message ---
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        ch_id = message.channel.id
        if ch_id not in self.count_channels:
            return

        state = self.channel_states.setdefault(ch_id, get_channel_state(ch_id))
        state.setdefault("lock", asyncio.Lock())

        async with state["lock"]:
            try:
                number = int(message.content.strip())
            except Exception:
                return

            last_num = state.get("last_number", 0)
            last_user = state.get("last_user")

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

            set_channel_state(ch_id, state)
