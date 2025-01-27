# ゲームに参加するコマンド
import os
import discord
import sqlite3
from discord import app_commands
from discord.ext import commands
from os.path import join, dirname
from dotenv import load_dotenv

# 環境変数の取得
dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)
guild_id = int(os.environ.get("GUILD_ID"))

class Join(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        self.database:sqlite3.Connection = bot.database
        self._user_init_coins:int = bot._user_init_coins
        self._user_init_stocks:dict = bot._user_init_stocks
                    
    @app_commands.command(
        name="join",
        description="ゲームに参加します"
    )
    @app_commands.guilds(guild_id)
    async def join(self, ctx:discord.Interaction):
        cursor = self.database.cursor()
        cursor.execute("SELECT * FROM user_coins WHERE user_id=?", (ctx.user.id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO user_coins (user_id, amount) VALUES (?, ?)", (ctx.user.id, self._user_init_coins))
            for brand, amount in self._user_init_stocks.items():
                cursor.execute("INSERT INTO user_stocks (user_id, brand, amount) VALUES (?, ?, ?)", (ctx.user.id, brand, amount))
            self.database.commit()
            await ctx.response.send_message("ゲームに参加しました！", ephemeral=True)
            return
        else:
            await ctx.response.send_message("あなたはすでにゲームに参加しています。", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Join(bot))
