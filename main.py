import discord
import os
import random
import math
import datetime
import sqlite3
from discord.ext import commands, tasks
from os.path import join, dirname
from dotenv import load_dotenv

class investio(commands.Bot):
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
                
        # cogs
        self.initial_extensions = [
            # ユーザー用
            "cogs.join",
            "cogs.buy",
            "cogs.sell",
            "cogs.show",
            
            # 管理者用
            "cogs.set",
        ]
        
    async def setup_hook(self):
        self.database = sqlite3.connect("./save/save.db")
        for extension in self.initial_extensions:
            await self.load_extension(extension)
    
    async def on_ready(self):
        self.guild = self.get_guild(guild_id)
        await self.tree.sync(guild=self.guild)
        
        # 開始通知
        print("get on ready!")
        await self.guild.get_channel(notify_channel_id).send("起動しました！")
        
        # テーブルの作成
        cursor = self.database.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS user_coins (user_id INTEGER, amount INTEGER)")
        cursor.execute("CREATE TABLE IF NOT EXISTS user_stocks (user_id INTEGER, brand TEXT, amount INTEGER)")
        cursor.execute("CREATE TABLE IF NOT EXISTS stocks (brand TEXT PRIMARY KEY, price INTEGER)")
        cursor.execute("CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY AUTOINCREMENT, brand TEXT, price INTEGER, time TEXT)")
        self.database.commit()
        # 銘柄の初期化
        cursor.execute("DELETE FROM stocks")
        for brand in self.stock_brands:
            cursor.execute("INSERT INTO stocks VALUES (?, ?)", (brand, 1000))
            
        # 履歴の初期化
        cursor.execute("DELETE FROM history")
        self.database.commit()
        
        # 株価の変動を開始
        self.fluctuation.start()
        return
    
    @tasks.loop(minutes=1)
    async def fluctuation(self):
        if datetime.datetime.now().minute == 0:
            cursor = self.database.cursor()
            for brand in self.stock_brands:
                increase = 0
                if brand == "Rise":
                    increase = random.randint(-50, 100)
                    cursor.execute("UPDATE stocks SET price=price+? WHERE brand=?", (increase, brand))
                elif brand == "Swing":
                    stock_price = cursor.execute("SELECT price FROM stocks WHERE brand=?", (brand,)).fetchone()[0]
                    increase = int(1000*(math.sin((datetime.datetime.now().hour+random.randint(-6, 6))/6*math.pi) + 0.5*random.randint(-1, 1))) - stock_price//1000
                    cursor.execute("UPDATE stocks SET price=price+? WHERE brand=?", (stock_price, brand))
                if cursor.execute("SELECT price FROM stocks WHERE brand=?", (brand,)).fetchone()[0] < 100:
                    cursor.execute("UPDATE stocks SET price=100 WHERE brand=?", (brand,))
                cursor.execute("INSERT INTO history VALUES (?, ?, ?, ?)", (None, brand, increase, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            self.database.commit()
                
            if (9 <= datetime.datetime.now().hour <= 21):
                await self.guild.get_channel(update_channel_id).send("株価が更新されました！")
                
                # 通知用のEmbedを作成
                stock_info = ""
                
                cursor.execute("SELECT * FROM stocks")
                for row in cursor.fetchall():
                    stock_info += f"{row[0]}: {row[1]:,}\n"
                
                user_info = ""
                cursor.execute("SELECT * FROM user_coins")
                for row in cursor.fetchall():
                    print(row[1])
                    user_info += f"{self.guild.get_member(row[0])}: {row[1]:,}\n"
                
                cursor.execute("SELECT * FROM user_coins")
                
                embed = discord.Embed(title="Infomation",
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

bot = investio()
bot.run(token)