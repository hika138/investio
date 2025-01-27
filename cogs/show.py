# プレイヤーの情報と現在の株価を表示するコマンド
    # コイン: xxxx枚
    # 持ち株
    # Rise: xx株
    # Swing: xx株
    # 株価
    # Rise: xxxxコイン
    # Swing: xxxxコイン
import os
import discord
import sqlite3
from discord import app_commands
from discord.ext import commands
from os.path import join, dirname
from dotenv import load_dotenv

# 環境変数の取得
dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)
guild_id = int(os.environ.get("GUILD_ID"))

class Show(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database:sqlite3.Connection = bot.database
        
    @app_commands.command(
        name="show",
        description="プレイヤーの情報と現在の株価を表示します"
    )
    @app_commands.guilds(guild_id)
    async def show(self, ctx:discord.Interaction, user:discord.User=None):
        cursor = self.database.cursor()
        # ユーザー指定がある場合
        if user is not None:
            cursor.execute("SELECT amount FROM user_coins WHERE user_id=?", (user.id,))
            user_coins = cursor.fetchone()
            if user_coins is None:
                await ctx.response.send_message("そのユーザーはゲームに参加していません。", ephemeral=True)
                return
            cursor.execute("SELECT brand, amount FROM user_stocks WHERE user_id=?", (user.id,))
            user_stocks = cursor.fetchall()
            cursor.execute("SELECT name, price FROM stocks")
            stocks = cursor.fetchall()
            msg = ""
            msg += f"{user.mention}の情報\n"
            msg += f"コイン: {user_coins[0]:,}枚\n"
            msg += "\n持ち株\n"
            for stock in user_stocks:
                msg += f"{stock[0]}: {stock[1]:,}株\n"
            msg += "\n株価\n"
            for stock in stocks:
                msg += f"{stock[0]}: {stock[1]:,}コイン\n"
            await ctx.response.send_message(msg, ephemeral=True)
            return
        
        # ユーザー指定がない場合
        else:
            cursor.execute("SELECT amount FROM user_coins WHERE user_id=?", (ctx.user.id,))
            user_coins = cursor.fetchone()
            if user_coins is None:
                await ctx.response.send_message("まずはjoinコマンドで参加してください。", ephemeral=True)
                return
            cursor.execute("SELECT brand, amount FROM user_stocks WHERE user_id=?", (ctx.user.id,))
            user_stocks = cursor.fetchall()
            cursor.execute("SELECT name, price FROM stocks")
            stocks = cursor.fetchall()
            msg = ""
            msg += f"あなたの情報\n"
            msg += f"コイン: {user_coins[0]:,}枚\n"
            msg += "\n持ち株\n"
            for stock in user_stocks:
                msg += f"{stock[0]}: {stock[1]:,}株\n"
            msg += "\n株価\n"
            for stock in stocks:
                msg += f"{stock[0]}: {stock[1]:,}コイン\n"
            await ctx.response.send_message(msg, ephemeral=True)
            return

async def setup(bot: commands.Bot):
    await bot.add_cog(Show(bot))
