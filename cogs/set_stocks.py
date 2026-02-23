"""
管理者が株数を操作するためのコグ
"""
import os
from os.path import join, dirname
from typing import Literal
from dotenv import load_dotenv


import discord
from discord import app_commands
from discord.ext import commands

from libs import wrapper


env_path = join(dirname(__file__), "../.env")
load_dotenv(env_path)
guild_id = int(os.environ.get("GUILD_ID", "0"))

class SetStocks(commands.Cog):
    """管理者が株数を操作するためのコグ"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.sqlite_wrapper: wrapper.SqliteWrapper = bot.sqlite_wrapper

    @app_commands.command(name="setstocks", description="ユーザーの株数を設定します")
    @app_commands.guilds(guild_id)
    async def set_stocks(
        self, ctx: discord.Interaction, user: discord.User, brand: Literal["Rise"], amount: int
    ):
        """ユーザーの株数を設定するコマンド"""
        if not ctx.user.guild_permissions.administrator:
            await ctx.response.send_message(
                "このコマンドを使用するには管理者権限が必要です。", ephemeral=True
            )
            return
        # ユーザーがゲームに参加していない場合はエラーメッセージを送信
        if not self.sqlite_wrapper.is_exist_user(user.id):
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

async def setup(bot: commands.Bot) -> None:
    """ 
    Cogをセットアップする関数
    """
    await bot.add_cog(SetStocks(bot))
