"""ユーザーの資産状況を表示するコマンドを提供するCog"""
import os
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
        self.sqlite_wrapper: wrapper.SqliteWrapper = bot.sqlite_wrapper

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
            if not self.sqlite_wrapper.is_exist_user(user.id):
                await ctx.response.send_message("そのユーザーはゲームに参加していません。", ephemeral=True)
                return
            user_stocks = self.sqlite_wrapper.get_all_user_stocks(user.id)
            stocks = self.sqlite_wrapper.get_all_stock_prices()
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
        if not self.sqlite_wrapper.is_exist_user(ctx.user.id):
            await ctx.response.send_message("まずはjoinコマンドで参加してください。", ephemeral=True)
            return
        user_coins = self.sqlite_wrapper.get_user_coins(ctx.user.id)
        user_stocks = self.sqlite_wrapper.get_all_user_stocks(ctx.user.id)
        stocks = self.sqlite_wrapper.get_all_stock_prices()
        msg = ""
        msg += "あなたの情報\n"
        msg += f"コイン: {user_coins:,}枚\n"
        msg += "\n持ち株\n"
        for brand, amount in user_stocks.items():
            msg += f"{brand}: {amount:,}株\n"
        msg += "\n株価\n"
        for brand, price in stocks:
            msg += f"{brand}: {price:,}コイン\n"
        await ctx.response.send_message(msg, ephemeral=True)
        return

async def setup(bot: commands.Bot):
    """
    Cogをセットアップする関数
    """
    await bot.add_cog(Show(bot))
