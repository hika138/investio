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

import os
from os.path import join, dirname
import datetime
import random
from typing import List, Dict

from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks

from libs import wrapper
from libs import weekday

INIT_PRICE_MIN:int = 90
INIT_PRICE_MAX:int = 110
MAX_PRICE:int = 660
MIN_PRICE:int = 6
patterns:list = [
    [0, -1, 2, -2, 2, -3, 3], # ジグザグ型
    [0, -4, 8, -8, 16, -16, 32], # ジグザグ型（大きな変動）
    [0, 1, 4, 9, 16, 25, 110], # 急上昇型
    [0, 1, 2, 4, 8, 16, 32], # 上昇型
    [0, -1, -2, -3, -4, -5, -6], # 下降型
    [0, -1, -2, -4, -8, -8, -16] # 急下降型
]

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
        self._user_init_coins:int = 1000
        self._user_init_stocks:Dict[str, int] = {
            "Rise": 0, 
        }
        self.stock_brands:List[str] = ["Rise"]
        self.database:str = "./save/save.db"
        self.sqlite_wrapper = wrapper.SqliteWrapper(self.database)
        self.guild:discord.Guild = None
        # 株価の変動のパターン

        self.pattern = random.choice(patterns) # 初期の変動パターンをランダムに選択

        # cogs
        self.initial_extensions = [
            # ユーザー用
            "cogs.join",
            "cogs.buy",
            "cogs.sell",
            "cogs.show",

            # 管理者用
            "cogs.set_coins",
            "cogs.set_stocks",
            "cogs.init",
        ]


    async def setup_hook(self):
        """Botのセットアップ処理"""
        for extension in self.initial_extensions:
            await self.load_extension(extension)


    async def on_ready(self):
        """Botが起動したときの処理"""
        self.guild = self.get_guild(guild_id)
        await self.tree.sync(guild=self.guild)

        # テーブルの作成
        self.sqlite_wrapper.create_tables()
        # 銘柄の初期化
        self.sqlite_wrapper.initialize_brands(self.stock_brands)

        # 履歴の初期化
        self.sqlite_wrapper.initialize_history()

        # 株価の変動を開始
        self.fluctuation.start()

        # 開始通知
        print("get on ready!")
        await self.guild.get_channel(notify_channel_id).send("起動しました！")


    def change_stock_price(self, day:int, stock_price:int) -> int:
        """
        株価の変動を行う関数
        
        :param self: Investioクラスのインスタンス
        :param day: 現在の曜日(0:日曜日, 1:月曜日, ..., 6:土曜日)
        :type day: int
        :param stock_price: 現在の株価
        :type stock_price: int
        :return: 変動後の株価
        :rtype: int
        """
        # 日曜日の場合、変動パターンを選択して初期株価を設定
        if day == 0:
            stock_price = random.randint(INIT_PRICE_MIN, INIT_PRICE_MAX)
            # 先週が上昇系だった場合、次は下降系を選ぶ確率を高くする
            if patterns.index(self.pattern) in [2, 3]: # 上昇系
                self.pattern = random.choices(patterns, weights=
                                         [1, 1, 0.1, 0.1, 10, 10]
                                        )[0]

            # 先週が下降系だった場合、次はジグザグ系を選ぶ確率を高くする
            if patterns.index(self.pattern) in [4, 5]: # 下降系
                self.pattern = random.choices(patterns, weights=
                                         [10, 10, 1, 1, 0.1, 0.1]
                                        )[0]

            # 先週がジグザグ型だった場合、次は上昇系を選ぶ確率を高くする
            if patterns.index(self.pattern) in [0, 1]: # ジグザグ型
                self.pattern = random.choices(patterns, weights=
                                         [0.1, 0.1, 1, 1, 10, 10]
                                        )[0]
            self.pattern = random.choice(patterns)
        # 1日ごとにランダムな変動を加える
        else:
            stock_price += self.pattern[day % len(self.pattern)]*random.randint(1, 4)-int(self.pattern[day % len(self.pattern)]*random.random())
            if day % 7 > 3: # 週の後半
                if random.random() < 0.05: # 5%の確率で急下降
                    stock_price -= stock_price * int(random.uniform(0.5, 0.75)) # 50%から75%の範囲で急下降
            stock_price = min(stock_price, MAX_PRICE) # 株価の上限
            stock_price = max(stock_price, MIN_PRICE)  # 株価の下限
        return stock_price


    @tasks.loop(time=datetime.time(hour=6, minute=0, second=0, tzinfo=datetime.timezone(datetime.timedelta(hours=9))))
    async def fluctuation(self):
        """
        株価の変動を定期的に行うタスク
        
        :param self: Investioクラスのインスタンス
        """
        # 株価の変動
        for brand in self.stock_brands:
            if brand == "Rise":
                today_weekday = weekday.get_current_weekday()
                new_price = self.change_stock_price(today_weekday, self.sqlite_wrapper.get_stock_price(brand))
                self.sqlite_wrapper.set_stock_price(brand, new_price)
                if today_weekday == 0: # 日曜日ならユーザーの持ち株をリセット
                    for user in self.sqlite_wrapper.get_users():
                        self.sqlite_wrapper.set_user_stocks(user, brand, self._user_init_stocks[brand])

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
