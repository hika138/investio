"""ユーザーが株を売却するコマンドを提供するCog"""
import os
import importlib
from typing import Literal
from os.path import join, dirname

import discord
from discord import app_commands
from discord.ext import commands

from libs import wrapper

# Load .env if available (use importlib to avoid identifier named "dotenv")
_dotenv_mod = importlib.import_module("dotenv")
_load_dotenv = getattr(_dotenv_mod, "load_dotenv")

env_path = join(dirname(__file__), "../.env")
_load_dotenv(env_path)
guild_id = int(os.environ.get("GUILD_ID", "0"))


class Sell(commands.Cog):
    """ユーザーが株を売却するコマンドを提供するCog"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.sqlite_wrapper: wrapper.sqlite_wrapper = bot.sqlite_wrapper

    @app_commands.command(name="sell", description="株を売却します")
    @app_commands.guilds(guild_id)
    async def sell(
        self, ctx: discord.Interaction, brand: Literal["Rise"], amount: int
    ) -> None:
        """株を売却するコマンド"""

        # ユーザーの所持金と株数を取得
        # ユーザーがゲームに参加していない場合はエラーメッセージを送信
        user_coins = self.sqlite_wrapper.get_user_coins(ctx.user.id)
        if user_coins is None:
            await ctx.response.send_message(
                "まずはjoinコマンドで参加してください。", ephemeral=True
            )
            return

        # 売却数が1以上でない場合はエラーメッセージを送信
        if amount <= 0:
            await ctx.response.send_message(
                "売却数は1以上で指定してください。", ephemeral=True
            )
            return
        # 銘柄が存在しない場合はエラーメッセージを送信
        stocks = self.sqlite_wrapper.get_all_stocks()
        if brand not in stocks:
            await ctx.response.send_message("その銘柄は存在しません。", ephemeral=True)
            return
        stock_price = self.sqlite_wrapper.get_stock_price(brand)

        # ユーザーの所持株数を取得
        user_stocks = self.sqlite_wrapper.get_user_stocks(ctx.user.id, brand)
        if user_stocks < amount:
            await ctx.response.send_message("株が足りません。", ephemeral=True)
            return

        # 売却処理
        self.sqlite_wrapper.set_user_coins(ctx.user.id, user_coins + stock_price * amount)
        self.sqlite_wrapper.set_user_stocks(ctx.user.id, brand, user_stocks - amount)
        await ctx.response.send_message(
            f"{brand}を{amount}株売却しました。", ephemeral=True
        )


async def setup(bot: commands.Bot) -> None:
    """ 
    Cogをセットアップする関数
    """
    await bot.add_cog(Sell(bot))
