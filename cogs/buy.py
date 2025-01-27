# 株を買うコマンド
import os
import discord
import sqlite3
from typing import Literal
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
        self.database:sqlite3.Connection = bot.database
                
    @app_commands.command(
        name="buy",
        description="株を購入します"
    )
    @app_commands.guilds(guild_id)
    async def buy(self, ctx:discord.Interaction, brand:Literal["Rise", "Swing"], amount:int):
        # ユーザーデータの取得
        cursor = self.database.cursor()
        cursor.execute("SELECT * FROM user_coins WHERE user_id=?", (ctx.user.id,))
        if cursor.fetchone() is None:
            await ctx.response.send_message("まずはjoinコマンドで参加してください。", ephemeral=True)
            return
        
        if amount <= 0:
            await ctx.response.send_message("購入数は1以上で指定してください。", ephemeral=True)
        
        # 株価の取得
        cursor.execute("SELECT price FROM stocks WHERE name=?", (brand,))
        stock_price = cursor.fetchone()[0]
        if stock_price is None:
            await ctx.response.send_message("その銘柄は存在しません。", ephemeral=True)
            return
        # 所持金の取得
        cursor.execute("SELECT amount FROM user_coins WHERE user_id=?", (ctx.user.id,))
        coins = cursor.fetchone()[0]
        if coins < stock_price * amount:
            await ctx.response.send_message("コインが足りません。", ephemeral=True)
            return
        # 株の購入
        if cursor.execute("SELECT * FROM user_stocks WHERE user_id=? and brand=?", (ctx.user.id, brand)).fetchone() is None:
            cursor.execute("INSERT INTO user_stocks (user_id, brand, amount) VALUES (?, ?, 0)", (ctx.user.id, brand))
        cursor.execute("UPDATE user_coins SET amount=amount - ? WHERE user_id=?", (stock_price * amount, ctx.user.id))
        cursor.execute("UPDATE user_stocks SET amount=amount + ? WHERE user_id=? and brand=?", (amount, ctx.user.id, brand))
        self.database.commit()
        await ctx.response.send_message(f"{brand}を{amount}株購入しました。", ephemeral=True)
        return

async def setup(bot: commands.Bot):
    await bot.add_cog(Buy(bot))
