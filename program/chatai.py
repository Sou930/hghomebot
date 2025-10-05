import discord
from discord.ext import commands
import aiohttp
import os

HF_TOKEN = os.environ.get("HF_API_KEY")  # Render環境変数に設定
MODEL_URL = "https://api-inference.huggingface.co/models/deepseek-ai/DeepSeek-V3.2-Exp"

class ChatAI(commands.Cog):
    """メンションされたときにDeepSeekで返答するCog"""

    def __init__(self, bot):
        self.bot = bot

    async def query_deepseek(self, prompt: str) -> str:
        """Hugging Face APIに問い合わせて返答を取得"""
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        payload = {"inputs": prompt}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(MODEL_URL, headers=headers, json=payload, timeout=60) as response:
                    if response.status != 200:
                        return f"⚠️ APIエラー {response.status}"
                    data = await response.json()
                    if isinstance(data, list) and "generated_text" in data[0]:
                        return data[0]["generated_text"]
                    return "⚠️ 返答を解析できませんでした。"
        except Exception as e:
            return f"💥 API接続エラー: {e}"

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Bot自身のメッセージは無視
        if message.author.bot:
            return

        # Botがメンションされた場合
        if self.bot.user.mentioned_in(message):
            prompt = message.content.replace(f"<@{self.bot.user.id}>", "").strip()
            if not prompt:
                await message.reply("こんにちは！話題を教えてください🤖")
                return

            await message.channel.trigger_typing()
            reply = await self.query_deepseek(prompt)
            # Discordメッセージ制限対策
            await message.reply(reply[:1900])

async def setup(bot):
    await bot.add_cog(ChatAI(bot))
