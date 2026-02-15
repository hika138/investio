"""ユーザーの資産状況を表示するコマンドを提供するCog"""
import os
import sqlite3
from os.path import join, dirname

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from libs import wrapper

# 環境変数の取得
dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)
guild_id = int(os.environ.get("GUILD_ID"))

class Show(commands.Cog):
    """ユーザーの資産状況を表示するコマンドを提供するCog"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database: sqlite3.Connection = bot.database
        self.sqlite_wrapper: wrapper.sqlite_wrapper = bot.sqlite_wrapper

    @app_commands.command(
        name="show",
        description="プレイヤーの情報と現在の株価を表示します"
    )
    @app_commands.guilds(guild_id)
    async def show(self, ctx: discord.Interaction, user: discord.User = None):
        """
        プレイヤーの情報と現在の株価を表示するコマンド
        """
        # ユーザー指定がある場合
        if user is not None:
            user_coins = self.sqlite_wrapper.get_user_coins(user.id)
            # ユーザーがゲームに参加していない場合はエラーメッセージを送信
            if user_coins is None:
                await ctx.response.send_message("そのユーザーはゲームに参加していません。", ephemeral=True)
                return
            user_stocks = self.sqlite_wrapper.get_all_user_stocks(user.id)
            stocks = self.sqlite_wrapper.get_all_stocks()
            msg = ""
            msg += f"{user.mention}の情報\n"
            msg += f"コイン: {user_coins:,}枚\n"
            msg += "\n持ち株\n"
            for brand, amount in user_stocks.items():
                msg += f"{brand}: {amount:,}株\n"
            msg += "\n株価\n"
            for brand, price in stocks:
                msg += f"{brand}: {price:,}コイン\n"
            await ctx.response.send_message(msg, ephemeral=True)
            return

        # ユーザー指定がない場合
        user_coins = self.sqlite_wrapper.get_user_coins(ctx.user.id)
        if user_coins is None:
            await ctx.response.send_message("まずはjoinコマンドで参加してください。", ephemeral=True)
            return
        user_stocks = self.sqlite_wrapper.get_all_user_stocks(ctx.user.id)
        stocks = self.sqlite_wrapper.get_all_stocks()
        msg = ""
        msg += "あなたの情報\n"
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
    """
    Cogをセットアップする関数
    """
    await bot.add_cog(Show(bot))
