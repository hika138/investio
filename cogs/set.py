# ユーザデータや株価を設定するコマンド
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

class Set(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database:sqlite3.Connection = bot.database

    @app_commands.command(
        name="set",
        description="ユーザデータや株価を設定します"
    )
    @app_commands.guilds(guild_id)
    async def set(self, ctx:discord.Interaction, target:Literal["user_coins", "user_stocks", "stocks"], user:discord.User=None, brand:Literal["Rise", "Swing"]=None, value:int=None):
        cursor = self.database.cursor()
        if target == "user_coins":
            if user is None or value is None:
                await ctx.response.send_message(
                f"userとvalueを指定してください。\n```user: ユーザー\nvalue: コインの枚数```", 
                ephemeral=True)
                return
            cursor.execute("SELECT * FROM user_coins WHERE user_id=?", (user.id,))
            if cursor.fetchone() is None:
                await ctx.response.send_message(f"{user}はゲームに参加していません。", ephemeral=True)
                return
            cursor.execute("UPDATE user_coins SET amount=? WHERE user_id=?", (value, user.id))
            self.database.commit()
            await ctx.response.send_message(f"{user}のコインを{value}に設定しました。", ephemeral=True)
            
        elif target == "user_stocks":
            if user is None or brand is None or value is None:
                await ctx.response.send_message(f"userとbrandとvalueを指定してください。\n```user: ユーザー\nbrand: 銘柄名\nvalue: 株の数```", 
                                                ephemeral=True)
                return
            cursor.execute("SELECT * FROM user_coins WHERE user_id=?", (user.id,))
            if cursor.fetchone() is None:
                await ctx.response.send_message(f"{user}はゲームに参加していません。", ephemeral=True)
                return
            cursor.execute("UPDATE user_stocks SET amount=? WHERE user_id=? and brand=?", (value, user.id, brand))
            self.database.commit()
            await ctx.response.send_message(f"{user}の{brand}の株を{value}に設定しました。", ephemeral=True)
            
        elif target == "stocks":
            if brand is None or value is None:
                await ctx.response.send_message(f"brandとvalueを指定してください。\n```brand: 銘柄名\nvalue: 株価```", 
                                                ephemeral=True)
                return
            cursor.execute("SELECT * FROM stocks WHERE name=?", (brand,))
            if cursor.fetchone() is None:
                await ctx.response.send_message(f"{brand}は存在しません。", ephemeral=True)
                return
            cursor.execute("UPDATE stocks SET price=? WHERE name=?", (value, brand))
            self.database.commit()
            await ctx.response.send_message(f"{brand}の株価を{value}に設定しました。", ephemeral=True)
        return

async def setup(bot: commands.Bot):
    await bot.add_cog(Set(bot))
