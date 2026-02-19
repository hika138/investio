"""joinコマンドを提供するCog"""

import os
from os.path import dirname, join
from dotenv import load_dotenv

import discord
from discord import app_commands
from discord.ext import commands
from libs import wrapper

# 環境変数の取得
dotenv_path = join(dirname(__file__), "../.env")
load_dotenv(dotenv_path)
guild_id = int(os.environ.get("GUILD_ID"))


class Join(commands.Cog):
    """joinコマンドを提供するCog"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.sqlite_wrapper: wrapper.sqlite_wrapper = bot.sqlite_wrapper

        self._user_init_coins: int = bot._user_init_coins
        self._user_init_stocks: dict = bot._user_init_stocks

    @app_commands.command(name="join", description="ゲームに参加します")
    @app_commands.guilds(guild_id)
    async def join(self, ctx: discord.Interaction):
        """ゲームに参加するコマンド"""
        # ユーザーがすでにゲームに参加しているか確認
        user_coins = self.sqlite_wrapper.get_user_coins(ctx.user.id)
        if user_coins is None:
            # ユーザーの所持金と株数を初期化
            self.sqlite_wrapper.set_user_coins(ctx.user.id, self._user_init_coins)
            for brand, amount in self._user_init_stocks.items():
                self.sqlite_wrapper.set_user_stocks(ctx.user.id, brand, amount)
            await ctx.response.send_message(
                "ゲームに参加しました！", ephemeral=True
            )
        else:
            await ctx.response.send_message("あなたはすでにゲームに参加しています。", ephemeral=True)


async def setup(bot: commands.Bot):
    """
    Cogをセットアップする関数
    """
    await bot.add_cog(Join(bot))
