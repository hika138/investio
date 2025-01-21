# ゲームに参加するコマンド
import os
import discord
import copy
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
        
        self.user_data:dict = bot.user_data
        self._user_init_coins:int = bot._user_init_coins
        self._user_init_stocks:dict = copy.deepcopy(bot._user_init_stocks)
                    
    @app_commands.command(
        name="join",
        description="ゲームに参加します"
    )
    @app_commands.guilds(guild_id)
    async def join(self, ctx:discord.Interaction):
        if ctx.user.id not in self.user_data:
            self.user_data[ctx.user.id] = {"coins":self._user_init_coins, "stocks":self._user_init_stocks}
            await ctx.response.send_message("ゲームに参加しました！", ephemeral=True)
        else:
            await ctx.response.send_message("あなたはすでにゲームに参加しています。", ephemeral=True)
        return

async def setup(bot: commands.Bot):
    await bot.add_cog(Join(bot))
