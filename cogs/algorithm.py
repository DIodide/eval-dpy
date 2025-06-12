import discord
from discord.ext import commands
from utils.checks import is_admin
from utils.menus import EmbedBuilder, LeaderboardBuilder, send_paginated_embed
import logging
from utils.analytics import SSBUPlayer

logger = logging.getLogger(__name__)


class Algorithm(commands.Cog):
    """Administrative commands for bot management"""

    def __init__(self, bot):
        self.bot = bot
        self.riotKey = self.bot.riotKey
        self.startggKey = self.bot.startggKey
        self.ballchasingKey = self.bot.ballchasingKey

    @commands.command(name="getSmashStats")
    async def getSmashStats(self, ctx, id):
        print("change made 23 dguioahfguahufghau")
        mango = SSBUPlayer.SSBUPlayer(id, self.startggKey, self.bot.session)
        await mango.fetch_data()
        await mango.fetch_rankings()
        await mango.fetch_standings()
        await mango.fetch_sets()
        await mango.fetch_mains()
        await mango.fetch_extreme_matchups()
        await mango.fetch_extreme_stages()
        await mango.fetch_win_rates()
        x = await mango.get_stats()
        await ctx.send(x)
        
    


        
    # Error handling
    
    # Whenever you add a command add a decorator
    # @<functionname>.error
    # example
    # @getOverwatchStats.error
    async def admin_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("❌ You need administrator permissions to use this command!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Missing required argument!")


async def setup(bot):
    await bot.add_cog(Algorithm(bot))