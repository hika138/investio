"""
株式投資ゲーム「Investio」のDiscord Botです。
ユーザーは株を購入・売却して資産を増やすことが目的です。株価は定期的に変動し、ユーザーの資産も変動します。
ユーザーは以下のコマンドを使用できます。
- `/join`: ゲームに参加します。初期資金と株を受け取ります。
- `/buy <銘柄> <数量>`: 指定した銘柄の株を指定した数量購入します。
- `/sell <銘柄> <数量>`: 指定した銘柄の株を指定した数量売却します。
- `/show`: 自分の資産状況を表示します。
管理者は以下のコマンドを使用できます。
- `/set <銘柄> <価格>`: 指定した銘柄の株価を手動で設定します。
"""

from os.path import join, dirname
import math
import datetime
import sqlite3
import os
import random
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks

from libs import wrapper

class Investio(commands.Bot):
    """
    Discord Botのメインクラス
    """
    def __init__(self):
        super().__init__(
            intents=intents,
            help_command=None,
            command_prefix='h!'
        )
        # 初期値
        self._user_init_coins:int = 10000
        self._user_init_stocks:dict = {
            "Rise": 0, 
            "Swing": 0,
        }
        self.stock_brands:list = ["Rise", "Swing"]
        self.database:sqlite3.Connection = None
        self.sqlite_wrapper = wrapper.sqlite_wrapper(self.database)
        self.guild:discord.Guild = None

        # cogs
        self.initial_extensions = [
            # ユーザー用
            "cogs.join",
            "cogs.buy",
            "cogs.sell",
            "cogs.show",

            # 管理者用
            #"cogs.set",
        ]

    async def setup_hook(self):
        """Botのセットアップ処理"""
        self.database = sqlite3.connect("./save/save.db")
        for extension in self.initial_extensions:
            await self.load_extension(extension)

    async def on_ready(self):
        """Botが起動したときの処理"""
        self.guild = self.get_guild(guild_id)
        await self.tree.sync(guild=self.guild)

        # 開始通知
        print("get on ready!")
        await self.guild.get_channel(notify_channel_id).send("起動しました！")

        # テーブルの作成
        self.sqlite_wrapper.create_tables()
        # 銘柄の初期化
        self.sqlite_wrapper.initialize_brands(self.stock_brands)

        # 履歴の初期化
        self.sqlite_wrapper.initialize_history()

        # 株価の変動を開始
        self.fluctuation.start()
        return

    @tasks.loop(time=datetime.time(hour=6, minute=0, second=0, tzinfo=datetime.timezone(datetime.timedelta(hours=9))))
    @tasks.loop(time=datetime.time(hour=18, minute=0, second=0, tzinfo=datetime.timezone(datetime.timedelta(hours=9))))
    async def fluctuation(self):
        """
        株価の変動を定期的に行うタスク
        
        :param self: Investioクラスのインスタンス
        """
        # 株価の変動
        for brand in self.stock_brands:
            if brand == "Rise":
                pass
            elif brand == "Swing":
                pass

            # 通知
            await self.guild.get_channel(update_channel_id).send("株価が更新されました！")

            # 通知用のEmbedを作成
            # 株価の情報を取得して表示
            stock_info = ""
            for brand in self.stock_brands:
                price = self.sqlite_wrapper.get_stock_price(brand)
                stock_info += f"{brand}: {price:,}\n"

            # プレイヤーの情報を取得して表示
            user_info = ""
            for user in self.sqlite_wrapper.get_users():
                coins = self.sqlite_wrapper.get_user_coins(user)
                member = self.guild.get_member(user)
                if member:
                    user_info += f"{member.display_name}: {coins:,}\n"
                else:
                    user_info += f"Unknown User: {coins:,}\n"

            embed = discord.Embed(title="Information",
                    description="株価とプレイヤー情報を通知します。",
                    colour=0x00b0f4,
                    timestamp=datetime.datetime.now())
            embed.add_field(name="株価",
                            value=stock_info,
                            inline=True)
            embed.add_field(name="プレイヤー",
                            value=user_info,
                            inline=True)
            await self.guild.get_channel(update_channel_id).send(embed=embed)
        return

# 環境変数の取得
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
token = os.environ.get("TOKEN")
guild_id = int(os.environ.get("GUILD_ID"))
notify_channel_id = int(os.environ.get("NOTIFY_CHANNEL_ID"))
update_channel_id = int(os.environ.get("UPDATE_CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = Investio()
bot.run(token)
