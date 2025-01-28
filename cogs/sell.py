# 株を売るコマンド
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

class Sell(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database:sqlite3.Connection = bot.database
        
    @app_commands.command(
        name="sell",
        description="株を売却します"
    )
    @app_commands.guilds(guild_id)
    async def sell(self, ctx:discord.Interaction, brand:Literal["Rise", "Swing"], amount:int):
        # ユーザーデータの取得
        cursor = self.database.cursor()
        cursor.execute("SELECT * FROM user_coins WHERE user_id=?", (ctx.user.id,))
        if cursor.fetchone() is None:
            await ctx.response.send_message("まずはjoinコマンドで参加してください。", ephemeral=True)
            return
        # 売却数の確認
        if amount <= 0:
            await ctx.response.send_message("売却数は1以上で指定してください。", ephemeral=True)
            return
        # 株価の取得
        cursor.execute("SELECT price FROM stocks WHERE name = ?", (brand,))
        stock_price = cursor.fetchone()[0]
        if stock_price is None:
            await ctx.response.send_message("その銘柄は存在しません。", ephemeral=True)
            return
        # 所持株の確認
        cursor.execute("SELECT amount FROM user_stocks WHERE user_id=? and brand=?", (ctx.user.id, brand,))
        if cursor.fetchone()[0] < amount:
            await ctx.response.send_message("株が足りません。", ephemeral=True)
            return
        # 株の売却
        cursor.execute("UPDATE user_coins SET amount = amount + ? WHERE user_id=?", (stock_price * amount, ctx.user.id))
        cursor.execute("UPDATE user_stocks SET amount = amount - ? WHERE user_id=? and brand=?", (amount, ctx.user.id, brand))
        self.database.commit()
        await ctx.response.send_message(f"{brand}を{amount}株売却しました。", ephemeral=True)
        return

async def setup(bot: commands.Bot):
    await bot.add_cog(Sell(bot))
