# 株を買うコマンド
import os
import discord
from discord import app_commands
from discord.ext import commands
from os.path import join, dirname
from dotenv import load_dotenv

# 環境変数の取得
dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)
guild_id = int(os.environ.get("GUILD_ID"))

class Buy(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        self.user_data = bot.user_data
        self.stock_prices = bot.stock_prices
        
    @app_commands.command(
        name="buy",
        description="株を購入します"
    )
    @app_commands.guilds(guild_id)
    async def buy(self, ctx:discord.Interaction, brand:str, amount:int):
        if ctx.user.id not in self.user_data:
            await ctx.response.send_message("まずはゲームに参加してください。", ephemeral=True)
        elif brand not in self.stock_prices:
            await ctx.response.send_message("その銘柄は存在しません。", ephemeral=True)
        elif amount <= 0:
            await ctx.response.send_message("1以上の数を入力してください。", ephemeral=True)
        elif self.user_data[ctx.user.id]["coins"] < amount * self.stock_prices:
            await ctx.response.send_message("コインが足りません。", ephemeral=True)
        else:
            self.user_data[ctx.user.id]["coins"] -= amount * self.stock_prices
            self.user_data[ctx.user.id]["stocks"] += amount
            await ctx.response.send_message(f"{amount}株購入しました。", ephemeral=True)
        return

async def setup(bot: commands.Bot):
    await bot.add_cog(Buy(bot))
