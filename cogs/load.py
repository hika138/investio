# ゲーム状況をロードするコマンド
import os
import discord
from discord import app_commands
from discord.ext import commands
from os.path import join, dirname
from dotenv import load_dotenv
import json

# 環境変数の取得
dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)
guild_id = int(os.environ.get("GUILD_ID"))

class Load(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.user_data = bot.user_data
        self.stock_prices = bot.stock_prices
        
    @app_commands.command(
        name="load",
        description="ゲーム状況をロードします"
    )
    @app_commands.guilds(guild_id)
    async def load(self, ctx:discord.Interaction):
        # 株価とプレイヤーの情報を
        msg = ""
        if os.path.exists("./save/userdata.json"):
            with open("./save/userdata.json", "r") as f:
                self.user_data = json.load(f)
            msg += "ユーザーデータをロードしました。\n"
        else:
            msg += "userdata.jsonが見つかりませんでした。\n"
        if os.path.exists("./save/stock_prices.json"):
            with open("./save/stock_prices.json", "r") as f:
                self.stock_prices = json.load(f)
            msg += "株価をロードしました。"
        else:
            msg += "stock_prices.jsonが見つかりませんでした。"
        
        if msg != "":
            await ctx.response.send_message(msg, ephemeral=True)
        else:
            await ctx.response.send_message("stock_prices.jsonが見つかりませんでした。", ephemeral=True)
        return
        
        
async def setup(bot: commands.Bot):
    await bot.add_cog(Load(bot))