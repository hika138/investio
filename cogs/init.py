"""データベースを初期化するためのCog"""

import os
from os.path import join, dirname
from dotenv import load_dotenv

import discord
from discord import app_commands
from discord.ext import commands
from libs import wrapper

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
guild_id = int(os.environ.get("GUILD_ID"))

class Init(commands.Cog):
    """データベースを初期化するためのCog"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.sqlite_wrapper: wrapper.SqliteWrapper = bot.sqlite_wrapper

    @app_commands.command(name="init", description="データベースを初期化します")
    @app_commands.guilds(guild_id)
    async def init(self, ctx: discord.Interaction) -> None:
        """データベースを初期化するコマンド"""
        if not ctx.user.guild_permissions.administrator:
            await ctx.response.send_message(
                "このコマンドを使用するには管理者権限が必要です。", ephemeral=True
            )
            return
        self.sqlite_wrapper.create_tables()
        await ctx.response.send_message("データベースを初期化しました。", ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    """Cogをセットアップする関数"""
    await bot.add_cog(Init(bot))
