"""
管理者がユーザーの所持コインを操作するためのコグ
"""

import os
from os.path import join, dirname
from dotenv import load_dotenv

import discord
from discord import app_commands
from discord.ext import commands

from libs import wrapper

env_path = join(dirname(__file__), "../.env")
load_dotenv(env_path)
guild_id = int(os.environ.get("GUILD_ID", "0"))

class SetCoins(commands.Cog):
    """管理者がユーザーの所持コインを操作するためのコグ"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.sqlite_wrapper: wrapper.SqliteWrapper = bot.sqlite_wrapper

    @app_commands.command(name="setcoins", description="ユーザーの所持コインを設定します")
    @app_commands.guilds(guild_id)
    async def setcoins(
        self, ctx: discord.Interaction, user: discord.User, amount: int
    ):
        """ユーザーの所持コインを設定するコマンド"""
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

        # 所持コインが0以上でない場合はエラーメッセージを送信
        if amount < 0:
            await ctx.response.send_message(
                "所持コインは0以上で指定してください。", ephemeral=True
            )
            return

        # 所持コインを設定
        self.sqlite_wrapper.set_user_coins(user.id, amount)
        await ctx.response.send_message(
            f"{user.mention}の所持コインを{amount}に設定しました。", ephemeral=True
        )

async def setup(bot: commands.Bot) -> None:
    """ 
    Cogをセットアップする関数
    """
    await bot.add_cog(SetCoins(bot))
