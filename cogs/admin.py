import discord
from discord.ext import commands
import importlib
import sys
from utils.checks import is_admin
from utils.menus import EmbedBuilder, LeaderboardBuilder, send_paginated_embed
import logging

logger = logging.getLogger(__name__)


class Admin(commands.Cog):
    """Administrative commands for bot management"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="reload", aliases=["r"])
    @is_admin()
    async def reload_commands(self, ctx):
        """Reload bot cogs and modules"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @reload_commands.command(name="all")
    @is_admin()
    async def reload_all(self, ctx):
        """Reload all cogs"""
        embed = EmbedBuilder.create_embed(
            title="🔄 Reloading All Cogs",
            description="Attempting to reload all loaded cogs...",
            color=discord.Color.orange(),
        )
        message = await ctx.send(embed=embed)

        success_cogs = []
        failed_cogs = []

        # Get list of currently loaded cogs
        cog_names = list(self.bot.cogs.keys())

        for cog_name in cog_names:
            try:
                # Convert cog name to module path
                module_name = f"cogs.{cog_name.lower()}"
                await self.bot.reload_extension(module_name)
                success_cogs.append(cog_name)
                logger.info("Reloaded %s", module_name)
            except Exception as e:
                failed_cogs.append(f"{cog_name}: {str(e)}")
                logger.error("Failed to reload %s: %s", cog_name, e)

        # Update embed with results
        if success_cogs and not failed_cogs:
            embed = EmbedBuilder.create_success_embed(
                title="✅ All Cogs Reloaded",
                description=f"Successfully reloaded {len(success_cogs)} cogs:\n"
                + "\n".join(f"• {cog}" for cog in success_cogs),
            )
        elif success_cogs and failed_cogs:
            embed = EmbedBuilder.create_warning_embed(
                title="⚠️ Partial Reload Success",
                description=f"**Successful ({len(success_cogs)}):**\n"
                + "\n".join(f"• {cog}" for cog in success_cogs)
                + f"\n\n**Failed ({len(failed_cogs)}):**\n"
                + "\n".join(f"• {cog}" for cog in failed_cogs[:5]),
            )
        else:
            embed = EmbedBuilder.create_error_embed(
                title="❌ Reload Failed",
                description="Failed to reload all cogs:\n"
                + "\n".join(f"• {cog}" for cog in failed_cogs[:5]),
            )

        await message.edit(embed=embed)

    @reload_commands.command()
    @is_admin()
    async def cog(self, ctx, cog_name: str):
        """Reload a specific cog"""
        try:
            module_name = f"cogs.{cog_name.lower()}"
            await self.bot.reload_extension(module_name)

            embed = EmbedBuilder.create_success_embed(
                title="✅ Cog Reloaded",
                description=f"Successfully reloaded `{cog_name}`",
            )
            await ctx.send(embed=embed)
            logger.info("Reloaded %s", module_name)
        except Exception as e:
            embed = EmbedBuilder.create_error_embed(
                title="❌ Reload Failed",
                description=f"Failed to reload `{cog_name}`: {str(e)}",
            )
            await ctx.send(embed=embed)
            logger.error("Failed to reload %s: %s", cog_name, e)

    @commands.command(name="load")
    @is_admin()
    async def load_cog(self, ctx, cog_name: str):
        """Load a cog"""
        try:
            module_name = f"cogs.{cog_name.lower()}"
            await self.bot.load_extension(module_name)

            embed = EmbedBuilder.create_success_embed(
                title="✅ Cog Loaded", description=f"Successfully loaded `{cog_name}`"
            )
            await ctx.send(embed=embed)
            logger.info("Loaded %s", module_name)
        except Exception as e:
            embed = EmbedBuilder.create_error_embed(
                title="❌ Load Failed",
                description=f"Failed to load `{cog_name}`: {str(e)}",
            )
            await ctx.send(embed=embed)
            logger.error("Failed to load %s: %s", cog_name, e)

    @commands.command(name="unload")
    @is_admin()
    async def unload_cog(self, ctx, cog_name: str):
        """Unload a cog"""
        try:
            module_name = f"cogs.{cog_name.lower()}"
            await self.bot.unload_extension(module_name)

            embed = EmbedBuilder.create_success_embed(
                title="✅ Cog Unloaded",
                description=f"Successfully unloaded `{cog_name}`",
            )
            await ctx.send(embed=embed)
            logger.info("Unloaded %s", module_name)
        except Exception as e:
            embed = EmbedBuilder.create_error_embed(
                title="❌ Unload Failed",
                description=f"Failed to unload `{cog_name}`: {str(e)}",
            )
            await ctx.send(embed=embed)
            logger.error("Failed to unload %s: %s", cog_name, e)

    @commands.command(name="cogs")
    @is_admin()
    async def list_cogs(self, ctx):
        """List all loaded cogs"""
        if not self.bot.cogs:
            embed = EmbedBuilder.create_warning_embed(
                title="No Cogs Loaded",
                description="There are currently no cogs loaded.",
            )
        else:
            cog_list = []
            for cog_name, cog in self.bot.cogs.items():
                command_count = len(
                    [cmd for cmd in cog.get_commands() if not cmd.hidden]
                )
                cog_list.append(f"• **{cog_name}** - {command_count} commands")

            embed = EmbedBuilder.create_info_embed(
                title=f"📦 Loaded Cogs ({len(self.bot.cogs)})",
                description="\n".join(cog_list),
            )

        await ctx.send(embed=embed)

    @commands.command(name="sync")
    @is_admin()
    async def sync_commands(self, ctx):
        """Sync application commands"""
        try:
            embed = EmbedBuilder.create_embed(
                title="🔄 Syncing Commands",
                description="Syncing application commands with Discord...",
                color=discord.Color.orange(),
            )
            message = await ctx.send(embed=embed)

            synced = await self.bot.tree.sync()

            embed = EmbedBuilder.create_success_embed(
                title="✅ Commands Synced",
                description=f"Successfully synced {len(synced)} application commands.",
            )
            await message.edit(embed=embed)
            logger.info("Synced %d application commands", len(synced))
        except Exception as e:
            embed = EmbedBuilder.create_error_embed(
                title="❌ Sync Failed", description=f"Failed to sync commands: {str(e)}"
            )
            await ctx.send(embed=embed)
            logger.error("Failed to sync commands: %s", e)

    @commands.command(name="shutdown", aliases=["stop", "quit"])
    @is_admin()
    async def shutdown_bot(self, ctx):
        """Shutdown the bot"""
        embed = EmbedBuilder.create_warning_embed(
            title="🔌 Shutting Down", description="Bot is shutting down... Goodbye! 👋"
        )
        await ctx.send(embed=embed)
        logger.info("Bot shutdown requested by %s", ctx.author)
        await self.bot.close()

    @commands.command(name="leaderboard", aliases=["lb", "top"])
    @is_admin()
    async def demo_leaderboard(self, ctx):
        """Demo leaderboard command showcasing the menu system"""
        # Create sample leaderboard data
        sample_data = [
            {"name": "Alice", "score": 9847, "emoji": "👑"},
            {"name": "Bob", "score": 8932, "emoji": "⚔️"},
            {"name": "Charlie", "score": 7651, "emoji": "🏹"},
            {"name": "Diana", "score": 7203, "emoji": "🛡️"},
            {"name": "Eve", "score": 6789, "emoji": "✨"},
            {"name": "Frank", "score": 6234, "emoji": "🔥"},
            {"name": "Grace", "score": 5987, "emoji": "❄️"},
            {"name": "Henry", "score": 5543, "emoji": "⚡"},
            {"name": "Ivy", "score": 5012, "emoji": "🌟"},
            {"name": "Jack", "score": 4876, "emoji": "🎯"},
            {"name": "Kate", "score": 4234, "emoji": "💎"},
            {"name": "Liam", "score": 3987, "emoji": "🏆"},
            {"name": "Maya", "score": 3654, "emoji": "🎪"},
            {"name": "Noah", "score": 3321, "emoji": "🎨"},
            {"name": "Olivia", "score": 2998, "emoji": "🎭"},
            {"name": "Peter", "score": 2765, "emoji": "🎪"},
            {"name": "Quinn", "score": 2432, "emoji": "🎵"},
            {"name": "Ruby", "score": 2198, "emoji": "💫"},
            {"name": "Sam", "score": 1987, "emoji": "🌙"},
            {"name": "Tina", "score": 1765, "emoji": "☀️"},
            {"name": "Uma", "score": 1543, "emoji": "🌈"},
            {"name": "Victor", "score": 1321, "emoji": "🦋"},
            {"name": "Wendy", "score": 1098, "emoji": "🌸"},
            {"name": "Xavier", "score": 876, "emoji": "🍀"},
            {"name": "Yara", "score": 654, "emoji": "🎀"},
        ]

        # Create leaderboard embeds
        embeds = LeaderboardBuilder.create_leaderboard(
            title="🏆 Demo Leaderboard",
            entries=sample_data,
            page_size=10,
            key_field="name",
            value_field="score",
            emoji_field="emoji",
            color=discord.Color.gold(),
            thumbnail="https://cdn.discordapp.com/emojis/1234567890.png",  # Optional
        )

        # Send paginated leaderboard
        await send_paginated_embed(ctx, embeds, user=ctx.author)

        # Log the action if database is available
        if self.bot.db:
            await self.bot.db.log_action(
                guild_id=ctx.guild.id if ctx.guild else 0,
                user_id=ctx.author.id,
                action="demo_leaderboard_viewed",
                details={"command": "leaderboard", "entries": len(sample_data)},
            )

    @commands.command(name="info")
    async def show_bot_info(self, ctx):
        """Display detailed bot information"""
        embed = discord.Embed(title="Bot Information", color=discord.Color.blue())

        embed.add_field(name="Bot Name", value=self.bot.user.name, inline=True)
        embed.add_field(name="Bot ID", value=self.bot.user.id, inline=True)
        embed.add_field(name="Guilds", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Users", value=len(self.bot.users), inline=True)
        embed.add_field(name="Cogs Loaded", value=len(self.bot.extensions), inline=True)
        embed.add_field(
            name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True
        )

        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f"Discord.py {discord.__version__}")

        await ctx.send(embed=embed)

    @commands.command(name="help")
    async def custom_help(self, ctx, command_name: str = None):
        """Display help information"""
        if command_name:
            command = self.bot.get_command(command_name)
            if command:
                embed = discord.Embed(
                    title=f"Help: {command.name}",
                    description=command.help or "No description available",
                    color=discord.Color.blue(),
                )
                embed.add_field(
                    name="Usage",
                    value=f"`!{command.name} {command.signature}`",
                    inline=False,
                )
                if command.aliases:
                    embed.add_field(
                        name="Aliases", value=", ".join(command.aliases), inline=False
                    )
            else:
                embed = discord.Embed(
                    title="Command Not Found",
                    description=f"Command `{command_name}` not found.",
                    color=discord.Color.red(),
                )
        else:
            embed = discord.Embed(
                title="Bot Commands",
                description="Use `!help <command>` for detailed information about a command.",
                color=discord.Color.blue(),
            )

            # Group commands by cog
            for cog_name, cog in self.bot.cogs.items():
                commands_list = [
                    cmd.name for cmd in cog.get_commands() if not cmd.hidden
                ]
                if commands_list:
                    embed.add_field(
                        name=cog_name, value=", ".join(commands_list), inline=False
                    )

        await ctx.send(embed=embed)

    # Error handling
    @reload_commands.error
    @load_cog.error
    @unload_cog.error
    @list_cogs.error
    @sync_commands.error
    @shutdown_bot.error
    async def admin_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("❌ You need administrator permissions to use this command!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Missing required argument!")


async def setup(bot):
    await bot.add_cog(Admin(bot))
