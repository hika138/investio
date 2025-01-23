import discord
import os
import sys
import random
import json
import datetime
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
        # {str(discord.User.id): {"coins": int, "stocks": dict{"brand": int, "amount": int}}}
        self.user_data:dict= {}
        
        # cogs
        self.initial_extensions = [
            # ユーザー用
            "cogs.join",
            "cogs.buy",
            "cogs.sell",
            "cogs.show",
            # 管理用
            "cogs.save",
            "cogs.load",
        ]
        
    async def setup_hook(self):
        # セーブデータの読み込み
        if os.path.exists("./save/userdata.json"):
            with open("./save/userdata.json", "r") as f:
                self.user_data = json.load(f)
        if os.path.exists("./save/stock_prices.json"):
            with open("./save/stock_prices.json", "r") as f:
                self.stock_prices = json.load(f)
        
        for extension in self.initial_extensions:
            await self.load_extension(extension)
    
    async def on_ready(self):
        self.guild = self.get_guild(guild_id)
        await self.tree.sync(guild=self.guild)
        
        print("get on ready!")
        await self.guild.get_channel(notify_channel_id).send("起動しました！")
        sys.stdout.flush()
        self.fluctuation.start()
        return
    
    @tasks.loop(minutes=1)
    async def fluctuation(self):
        if datetime.datetime.now().minute == 0:
            for brand in self.stock_prices:
                if brand == "Rise":
                    self.stock_prices[brand] += random.randint(-250, 500)
                elif brand == "Swing":
                    self.stock_prices[brand] += random.randint(int(self.stock_prices[brand] * -0.5), int(self.stock_prices[brand] * 0.5))
                if self.stock_prices[brand] <= 100:
                    self.stock_prices[brand] = 100
            await self.guild.get_channel(update_channel_id).send("株価が更新されました！")
            
            # 通知用のEmbedを作成
            stock_info = ""
            for brand in self.stock_prices:
                stock_info += f"{brand}: {self.stock_prices[brand]:,}\n"
            
            user_info = ""
            for user_id in self.user_data:
                user = self.guild.get_member(int(user_id))
                user_info += f"{user.display_name}: {self.user_data[user_id]['coins']:,}\n"
            
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