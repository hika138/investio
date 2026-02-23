"""buyコマンドを提供するCog"""
import os
from os.path import join, dirname
from typing import Literal
from dotenv import load_dotenv

import discord
from discord import app_commands
from discord.ext import commands

from libs import wrapper
from libs import weekday

# 環境変数の取得
dotenv_path = join(dirname(__file__), "../.env")
load_dotenv(dotenv_path)
guild_id = int(os.environ.get("GUILD_ID"))


class Buy(commands.Cog):
    """ユーザーが株を購入するコマンドを提供するCog"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.sqlite_wrapper: wrapper.SqliteWrapper = bot.sqlite_wrapper

    @app_commands.command(name="buy", description="株を購入します")
    @app_commands.guilds(guild_id)
    async def buy(
        self, ctx: discord.Interaction, brand: Literal["Rise"], amount: int
    ):
        """株を購入するコマンド"""
        # ユーザーがゲームに参加していない場合はエラーメッセージを送信
        user_coins = self.sqlite_wrapper.get_user_coins(ctx.user.id)
        if not self.sqlite_wrapper.is_exist_user(ctx.user.id):
            await ctx.response.send_message(
                "まずはjoinコマンドで参加してください。", ephemeral=True
            )
            return

        if weekday.get_current_weekday() != 0:
            await ctx.response.send_message("株の購入は日曜日に限られます。", ephemeral=True)
            return

        # 購入数が1以上でない場合はエラーメッセージを送信
        if amount <= 0:
            await ctx.response.send_message(
                "購入数は1以上で指定してください。", ephemeral=True
            )
            return

        # 銘柄が存在しない場合はエラーメッセージを送信
        stocks = self.sqlite_wrapper.get_all_stocks()
        if brand not in stocks:
            await ctx.response.send_message("その銘柄は存在しません。", ephemeral=True)
            return
        stock_price = self.sqlite_wrapper.get_stock_price(brand)

        # ユーザーの所持金が足りない場合はエラーメッセージを送信
        if user_coins < stock_price * amount:
            await ctx.response.send_message("コインが足りません。", ephemeral=True)
            return

        # 株の購入
        # ユーザーの所持株数を取得し、存在しない場合は初期化
        if self.sqlite_wrapper.get_user_stocks(ctx.user.id, brand) is None:
            self.sqlite_wrapper.set_user_stocks(ctx.user.id, brand, 0)
        self.sqlite_wrapper.set_user_coins(ctx.user.id, user_coins - stock_price * amount)
        new_stocks = self.sqlite_wrapper.get_user_stocks(ctx.user.id, brand) + amount
        self.sqlite_wrapper.set_user_stocks(ctx.user.id, brand, new_stocks)
        await ctx.response.send_message(
            f"{brand}を{amount}株購入しました。", ephemeral=True
        )


async def setup(bot: commands.Bot):
    """
    Cogをセットアップする関数
    """
    await bot.add_cog(Buy(bot))
