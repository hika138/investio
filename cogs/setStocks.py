"""
管理者が株数を操作するためのコグ
"""

from typing import Literal
import discord
from discord import app_commands
from discord.ext import commands

from libs import wrapper

class SetStocks(commands.Cog):
    """管理者が株数を操作するためのコグ"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.sqlite_wrapper: wrapper.sqlite_wrapper = bot.sqlite_wrapper

    @app_commands.command(name="setStocks", description="ユーザーの株数を設定します")
    async def setstocks(
        self, ctx: discord.Interaction, user: discord.User, brand: Literal["Rise"], amount: int
    ):
        """ユーザーの株数を設定するコマンド"""
        # ユーザーがゲームに参加していない場合はエラーメッセージを送信
        user_coins = self.sqlite_wrapper.get_user_coins(user.id)
        if user_coins is None:
            await ctx.response.send_message(
                "そのユーザーはゲームに参加していません。", ephemeral=True
            )
            return

        # 株数が0以上でない場合はエラーメッセージを送信
        if amount < 0:
            await ctx.response.send_message(
                "株数は0以上で指定してください。", ephemeral=True
            )
            return

        # 銘柄が存在しない場合はエラーメッセージを送信
        stocks = self.sqlite_wrapper.get_all_stocks()
        if brand not in stocks:
            await ctx.response.send_message("その銘柄は存在しません。", ephemeral=True)
            return

        # 株数を設定
        self.sqlite_wrapper.set_user_stocks(user.id, brand, amount)
        await ctx.response.send_message(
            f"{user.mention}の{brand}の株数を{amount}に設定しました。", ephemeral=True
        )
