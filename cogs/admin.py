import discord
from discord.ext import commands
import importlib
import sys
from utils.checks import is_admin


class Admin(commands.Cog):
    """Administrative commands for bot management"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="reload")
    @is_admin()
    async def reload_cog(self, ctx, cog_name: str = None):
        """Reload a specific cog or all cogs"""
        if cog_name is None:
            await ctx.send(
                "❌ Please specify a cog name or use `reload all` to reload all cogs."
            )
            return

        if cog_name.lower() == "all":
            await self.reload_all_cogs(ctx)
            return

        # Add 'cogs.' prefix if not present
        if not cog_name.startswith("cogs."):
            cog_name = f"cogs.{cog_name}"

        try:
            await self.bot.reload_extension(cog_name)

            embed = discord.Embed(
                title="Cog Reloaded",
                description=f"Successfully reloaded `{cog_name}`",
                color=discord.Color.green(),
            )
            await ctx.send(embed=embed)

        except commands.ExtensionNotLoaded:
            await ctx.send(f"❌ Cog `{cog_name}` is not loaded!")
        except commands.ExtensionNotFound:
            await ctx.send(f"❌ Cog `{cog_name}` not found!")
        except Exception as e:
            await ctx.send(f"❌ Failed to reload `{cog_name}`: {e}")

    async def reload_all_cogs(self, ctx):
        """Reload all loaded cogs"""
        loaded_cogs = list(self.bot.extensions.keys())
        success_count = 0
        failed_cogs = []

        for cog_name in loaded_cogs:
            try:
                await self.bot.reload_extension(cog_name)
                success_count += 1
            except Exception as e:
                failed_cogs.append(f"{cog_name}: {e}")

        embed = discord.Embed(
            title="Bulk Cog Reload",
            color=discord.Color.green() if not failed_cogs else discord.Color.orange(),
        )

        embed.add_field(
            name="Success",
            value=f"Reloaded {success_count}/{len(loaded_cogs)} cogs",
            inline=False,
        )

        if failed_cogs:
            failed_text = "\n".join(failed_cogs[:5])  # Limit to first 5 failures
            if len(failed_cogs) > 5:
                failed_text += f"\n... and {len(failed_cogs) - 5} more"
            embed.add_field(name="Failures", value=f"```{failed_text}```", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="load")
    @is_admin()
    async def load_cog(self, ctx, cog_name: str):
        """Load a cog"""
        # Add 'cogs.' prefix if not present
        if not cog_name.startswith("cogs."):
            cog_name = f"cogs.{cog_name}"

        try:
            await self.bot.load_extension(cog_name)

            embed = discord.Embed(
                title="Cog Loaded",
                description=f"Successfully loaded `{cog_name}`",
                color=discord.Color.green(),
            )
            await ctx.send(embed=embed)

        except commands.ExtensionAlreadyLoaded:
            await ctx.send(f"❌ Cog `{cog_name}` is already loaded!")
        except commands.ExtensionNotFound:
            await ctx.send(f"❌ Cog `{cog_name}` not found!")
        except Exception as e:
            await ctx.send(f"❌ Failed to load `{cog_name}`: {e}")

    @commands.command(name="unload")
    @is_admin()
    async def unload_cog(self, ctx, cog_name: str):
        """Unload a cog"""
        # Add 'cogs.' prefix if not present
        if not cog_name.startswith("cogs."):
            cog_name = f"cogs.{cog_name}"

        # Prevent unloading the admin cog
        if cog_name == "cogs.admin":
            await ctx.send("❌ Cannot unload the admin cog!")
            return

        try:
            await self.bot.unload_extension(cog_name)

            embed = discord.Embed(
                title="Cog Unloaded",
                description=f"Successfully unloaded `{cog_name}`",
                color=discord.Color.orange(),
            )
            await ctx.send(embed=embed)

        except commands.ExtensionNotLoaded:
            await ctx.send(f"❌ Cog `{cog_name}` is not loaded!")
        except Exception as e:
            await ctx.send(f"❌ Failed to unload `{cog_name}`: {e}")

    @commands.command(name="cogs", aliases=["extensions"])
    @is_admin()
    async def list_cogs(self, ctx):
        """List all loaded cogs"""
        loaded_cogs = list(self.bot.extensions.keys())

        if not loaded_cogs:
            await ctx.send("No cogs are currently loaded.")
            return

        embed = discord.Embed(
            title="Loaded Cogs",
            description="\n".join([f"• `{cog}`" for cog in loaded_cogs]),
            color=discord.Color.blue(),
        )
        embed.set_footer(text=f"Total: {len(loaded_cogs)} cogs")

        await ctx.send(embed=embed)

    @commands.command(name="sync")
    @is_admin()
    async def sync_commands(self, ctx):
        """Sync slash commands (if using hybrid commands)"""
        try:
            synced = await self.bot.tree.sync()

            embed = discord.Embed(
                title="Commands Synced",
                description=f"Synced {len(synced)} command(s)",
                color=discord.Color.green(),
            )
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ Failed to sync commands: {e}")

    @commands.command(name="shutdown")
    @is_admin()
    async def shutdown_bot(self, ctx):
        """Shutdown the bot"""
        embed = discord.Embed(
            title="Bot Shutdown",
            description="Shutting down bot...",
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed)
        await self.bot.close()

    @commands.command(name="info")
    async def bot_info(self, ctx):
        """Display bot information"""
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
    @reload_cog.error
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
