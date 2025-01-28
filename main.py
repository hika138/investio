import discord
import os
import random
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
        
        # 株価の変動を開始
        self.fluctuation.start()
        return
    
    @tasks.loop(minutes=1)
    async def fluctuation(self):
        if datetime.datetime.now().minute == 0:
            cursor = self.database.cursor()
            for brand in self.stock_brands:
                if brand == "Rise":
                    cursor.execute("UPDATE stocks SET price = price + ? WHERE name = ?", (random.randint(-250, 500), brand))
                elif brand == "Swing":
                    stock_price = cursor.execute("SELECT price FROM stocks WHERE name = ?", (brand,)).fetchone()[0]
                    cursor.execute("UPDATE stocks SET price = price + ? WHERE name = ?", (-random.randint(int(stock_price)/2, int(stock_price))/2, brand)) 
                if cursor.execute("SELECT price FROM stocks WHERE name = ?", (brand,)).fetchone()[0] < 100:
                    cursor.execute("UPDATE stocks SET price = 100 WHERE name = ?", (brand,))
            self.database.commit()
            
            if (9 <= datetime.datetime.now().hour <= 21):
                await self.guild.get_channel(update_channel_id).send("株価が更新されました！")
                
                # 通知用のEmbedを作成
                stock_info = ""
                
                cursor.execute("SELECT * FROM stocks")
                for row in cursor.fetchall():
                    stock_info += f"{row[1]}: {row[2]:,}\n"
                
                user_info = ""
                cursor.execute("SELECT * FROM user_coins")
                for row in cursor.fetchall():
                    user_info += f"{row[0]}: {row[1]:,}\n"
                
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