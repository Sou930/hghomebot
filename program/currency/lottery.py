import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord.ui import View, Button
from datetime import datetime, timedelta
import random

class LotteryButton(Button):
    def __init__(self, amount, db):
        super().__init__(label=f"{amount} コイン応募", style=discord.ButtonStyle.green)
        self.amount = amount
        self.db = db

    async def callback(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)

        # 所持金確認
        ref = self.db.collection("users").document(user_id)
        doc = ref.get()
        coins = doc.to_dict().get("coins", 0) if doc.exists else 0
        if coins < self.amount:
            await interaction.response.send_message("❌ コインが足りません。", ephemeral=True)
            return

        # 応募データ更新
        lottery_ref = self.db.collection("lottery").document("current")
        data = lottery_ref.get().to_dict() if lottery_ref.get().exists else {"entries": {}}
        entries = data.get("entries", {})
        entries[user_id] = entries.get(user_id, 0) + self.amount
        lottery_ref.set({"entries": entries})

        # 総応募額更新
        default_ref = self.db.collection("users").document("default")
        default_doc = default_ref.get()
        total = default_doc.to_dict().get("lottery_total", 0) + self.amount
        default_ref.set({"lottery_total": total}, merge=True)

        # コイン減算
        ref.set({"coins": coins - self.amount}, merge=True)
        await interaction.response.send_message(f"✅ {self.amount} コインで応募しました！", ephemeral=True)

class LotteryView(View):
    def __init__(self, db):
        super().__init__(timeout=None)
        self.db = db
        for amount in [50, 100, 200]:
            self.add_item(LotteryButton(amount, db))

class Lottery(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        self.lottery_task.start()
        self.bot.loop.create_task(self.init_defaults())

    # 🔹 users/default 初期化
    async def init_defaults(self):
        ref = self.db.collection("users").document("default")
        doc = ref.get()
        data = doc.to_dict() if doc.exists else {}
        data.setdefault("coins", 0)
        data.setdefault("bank", 0)
        data.setdefault("work_level", 1)
        data.setdefault("dollar", 0.0)
        data.setdefault("steal_level", 1)
        data.setdefault("steal_exp", 0)
        data.setdefault("lottery_channel", None)
        data.setdefault("lottery_total", 0)
        ref.set(data, merge=True)

    # 🔹 募集通知チャンネル取得
    async def get_lottery_channel(self):
        ref = self.db.collection("users").document("default")
        doc = ref.get()
        return doc.to_dict().get("lottery_channel") if doc.exists else None

    # 🔹 応募データ取得・保存
    async def get_lottery_entries(self):
        ref = self.db.collection("lottery").document("current")
        doc = ref.get()
        if doc.exists:
            return doc.to_dict().get("entries", {})
        else:
            ref.set({"entries": {}})
            return {}

    async def set_lottery_entries(self, entries):
        ref = self.db.collection("lottery").document("current")
        ref.set({"entries": entries})

    # 🔹 募集通知チャンネル設定
    @app_commands.command(name="set_channel", description="宝くじ募集通知チャンネルを設定")
    @app_commands.describe(type="設定種類", channel="チャンネル")
    async def set_channel(self, interaction: discord.Interaction, type: str, channel: discord.TextChannel):
        if type != "lottery":
            await interaction.response.send_message("❌ type は 'lottery' のみ対応", ephemeral=True)
            return
        ref = self.db.collection("users").document("default")
        ref.set({"lottery_channel": channel.id}, merge=True)
        await interaction.response.send_message(f"✅ 宝くじ募集通知チャンネルを {channel.mention} に設定しました。")

    # 🔹 募集通知メッセージ送信（18時）
    async def send_lottery_notification(self):
        channel_id = await self.get_lottery_channel()
        if not channel_id:
            return
        for guild in self.bot.guilds:
            channel = guild.get_channel(channel_id)
            if channel:
                embed = discord.Embed(
                    title="🎟 宝くじ募集開始 🎟",
                    description="ボタンを押して応募してください！\n応募期間: 18:00〜翌16:00",
                    color=discord.Color.gold()
                )
                await channel.send(embed=embed, view=LotteryView(self.db))

    # 🔹 自動抽選タスク（毎日17時）
    @tasks.loop(minutes=1)
    async def lottery_task(self):
        now = datetime.utcnow()
        # 募集開始通知 18時
        if now.hour == 18 and now.minute == 0:
            await self.send_lottery_notification()

        # 当選発表 17時
        if now.hour == 17 and now.minute == 0:
            entries = await self.get_lottery_entries()
            if not entries:
                return
            total = sum(entries.values())
            users = list(entries.keys())
            weights = [entries[u] for u in users]

            first = random.choices(users, weights=weights, k=1)[0]
            second = random.choices([u for u in users if u != first],
                                    weights=[entries[u] for u in users if u != first], k=1)[0]
            third = random.choices([u for u in users if u not in [first, second]],
                                   weights=[entries[u] for u in users if u not in [first, second]], k=1)[0]

            prizes = {
                first: int(total * 0.5),
                second: int(total * 0.3),
                third: int(total * 0.2)
            }

            # 配布
            for uid, prize in prizes.items():
                ref = self.db.collection("users").document(uid)
                doc = ref.get()
                coins = doc.to_dict().get("coins", 0) if doc.exists else 0
                ref.set({"coins": coins + prize}, merge=True)

            # 発表
            channel_id = await self.get_lottery_channel()
            if channel_id:
                for guild in self.bot.guilds:
                    channel = guild.get_channel(channel_id)
                    if channel:
                        embed = discord.Embed(
                            title="🎉 宝くじ当選発表 🎉",
                            description=f"総応募額: {total} コイン",
                            color=discord.Color.gold()
                        )
                        embed.add_field(name="🥇 1等", value=f"<@{first}> +{prizes[first]} コイン")
                        embed.add_field(name="🥈 2等", value=f"<@{second}> +{prizes[second]} コイン")
                        embed.add_field(name="🥉 3等", value=f"<@{third}> +{prizes[third]} コイン")
                        await channel.send(embed=embed)

            # リセット
            await self.set_lottery_entries({})
            default_ref = self.db.collection("users").document("default")
            default_ref.set({"lottery_total": 0}, merge=True)

    @lottery_task.before_loop
    async def before_lottery(self):
        await self.bot.wait_until_ready()

# 🔹 Cog 登録
async def setup(bot, db):
    await bot.add_cog(Lottery(bot, db))
