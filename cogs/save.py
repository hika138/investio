# ゲーム状況を保存するコマンド
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

class Save(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.user_data = bot.user_data
        self.stock_prices = bot.stock_prices
        
    @app_commands.command(
        name="save",
        description="ゲーム状況を保存します"
    )
    @app_commands.guilds(guild_id)
    async def save(self, ctx:discord.Interaction):
        # 株価とプレイヤーの情報を保存
        with open("./save/userdata.json", "w") as f:
            json.dump(self.user_data, f)
        with open("./save/stock_prices.json", "w") as f:
            json.dump(self.stock_prices, f)
        await ctx.response.send_message("ゲーム状況を保存しました。", ephemeral=True)
        
async def setup(bot: commands.Bot):
    await bot.add_cog(Save(bot))