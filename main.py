import discord
import os
import sys
import random
import json
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
        self._user_init_stocks:dict = {"Rise": 0, 
                                       "Swing": 0,
                                    }
        
        # 株価
        self.stock_prices:dict = {"Rise": 1000, 
                                   "Swing": 1000,
                                }
        
        # ユーザーの情報を保存する辞書 
        # {discord.User.id: {"coins": int, "stocks": dict{"brand": int, "amount": int}}}
        self.user_data:dict= {}
        
        # cogs
        self.initial_extensions = [
            "cogs.join",
            "cogs.buy",
            "cogs.sell",
            "cogs.show",
            "cogs.save",
        ]
        
    async def setup_hook(self):
        for extension in self.initial_extensions:
            await self.load_extension(extension)
    
    async def on_ready(self):
        # セーブデータの読み込み
        if os.path.exists("./save/user_data.json"):
            with open("./save/user_data.json", "r") as f:
                self.user_data = json.load(f)
        if os.path.exists("./save/stock_prices.json"):
            with open("./save/stock_prices.json", "r") as f:
                self.stock_prices = json.load(f)
                
        self.guild = self.get_guild(guild_id)
        await self.tree.sync(guild=self.guild)
        
        print("get on ready!")
        sys.stdout.flush()
        self.fluctuation.start()
        return
    
    @tasks.loop(hours=1)
    async def fluctuation(self):
        for brand in self.stock_prices:
            if brand == "Rise":
                self.stock_prices[brand] += random.randint(-250, 500)
            elif brand == "Swing":
                self.stock_prices[brand] += random.randint(int(self.stock_prices[brand] * -0.5), int(self.stock_prices[brand] * 0.75))
            if self.stock_prices[brand] <= 100:
                self.stock_prices[brand] = 100
        return

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

token = os.environ.get("TOKEN")
guild_id = int(os.environ.get("GUILD_ID"))
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = investio()
bot.run(token)