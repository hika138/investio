# プレイヤーの情報と現在の株価を表示するコマンド
    # コイン: xxxx枚
    # 持ち株
    # Rise: xx株
    # Swing: xx株
    # 株価
    # Rise: xxxxコイン
    # Swing: xxxxコイン
import os
import discord
from discord import app_commands
from discord.ext import commands
from os.path import join, dirname
from dotenv import load_dotenv

# 環境変数の取得
dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)
guild_id = int(os.environ.get("GUILD_ID"))

class Show(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.user_data:dict = bot.user_data
        self.stock_prices:dict = bot.stock_prices
        
    @app_commands.command(
        name="show",
        description="プレイヤーの情報と現在の株価を表示します"
    )
    @app_commands.guilds(guild_id)
    async def show(self, ctx:discord.Interaction, user:discord.User=None):
        # ユーザー指定がある場合
        if user is not None:
            if str(user.id) not in self.user_data:
                await ctx.response.send_message("そのユーザーはゲームに参加していません。", ephemeral=True)
            else:
                msg = f"コイン: {self.user_data[str(user.id)]['coins']:,}枚\n"
                msg += "持ち株\n"
                for brand, amount in self.user_data[str(user.id)]["stocks"].items():
                    msg += f"{brand}: {amount:,}株\n"
                await ctx.response.send_message(msg, ephemeral=True)
                return
        
        # ユーザー指定がない場合
        if str(ctx.user.id) not in self.user_data:
            await ctx.response.send_message("まずはゲームに参加してください。\n`/join`で参加できます。", ephemeral=True)
        else:
            msg = f"コイン: {self.user_data[str(ctx.user.id)]['coins']:,}枚\n"
            msg += "持ち株\n"
            for brand, amount in self.user_data[str(ctx.user.id)]["stocks"].items():
                msg += f"{brand}: {amount:,}株\n"
            msg += "株価\n"
            for brand, price in self.stock_prices.items():
                msg += f"{brand}: {price:,}コイン\n"
            
            await ctx.response.send_message(msg, ephemeral=True)
        return

async def setup(bot: commands.Bot):
    await bot.add_cog(Show(bot))
