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

class Reload(commands.Cog):
    """Cogを再読み込みするためのCog"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.sqlite_wrapper: wrapper.SqliteWrapper = bot.sqlite_wrapper

    @app_commands.command(name="reload", description="cogを再読み込みします")
    @app_commands.guilds(guild_id)
    async def reload(self, ctx: discord.Interaction):
        """Cogを再読み込みするコマンド"""
        if not ctx.user.guild_permissions.administrator:
            await ctx.response.send_message(
                "このコマンドを使用するには管理者権限が必要です。", ephemeral=True
            )
            return
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await self.bot.reload_extension(f"cogs.{filename[:-3]}")
        await ctx.response.send_message("cogを再読み込みしました。", ephemeral=True)

async def setup(bot: commands.Bot):
    """
    Cogをセットアップする関数
    """
    await bot.add_cog(Reload(bot))