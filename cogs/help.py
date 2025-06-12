import discord
from discord.ext import commands
from typing import Dict, List, Optional
import logging
from utils.menus import (
    EmbedBuilder,
    PaginatedEmbed,
    SelectMenu,
    send_paginated_embed,
    send_select_menu,
)
from utils.checks import is_admin

logger = logging.getLogger(__name__)


class HelpCommand(commands.Cog):
    """Interactive help command with beautiful menus"""

    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")  # Remove default help command

    def get_command_categories(self) -> Dict[str, List[commands.Command]]:
        """Get commands organized by category"""
        categories = {
            "🛡️ Moderation": [],
            "⚡ Admin": [],
            "🔄 Tasks": [],
            "🗄️ Database": [],
            "❓ Help": [],
            "🔧 Utility": [],
        }

        for command in self.bot.commands:
            # Skip hidden commands
            if command.hidden:
                continue

            # Skip if command has no cog (shouldn't happen but safety check)
            if not hasattr(command, "cog") or not command.cog:
                categories["🔧 Utility"].append(command)
                continue

            # Get cog name safely
            cog_name = command.cog.__class__.__name__ if command.cog else "Unknown"

            # Categorize based on cog name
            if cog_name == "Moderation":
                categories["🛡️ Moderation"].append(command)
            elif cog_name == "Admin":
                categories["⚡ Admin"].append(command)
            elif cog_name == "Tasks":
                categories["🔄 Tasks"].append(command)
            elif cog_name == "DatabaseDemo":
                categories["🗄️ Database"].append(command)
            elif cog_name == "HelpCommand":
                categories["❓ Help"].append(command)
            else:
                categories["🔧 Utility"].append(command)

        # Remove empty categories and return
        return {k: v for k, v in categories.items() if v}

    def create_main_help_embed(self) -> discord.Embed:
        """Create the main help embed"""
        description = (
            "Welcome to the help system! This bot features modular commands "
            "organized into different categories.\n\n"
            "**Navigation:**\n"
            "• Use the dropdown menu below to browse categories\n"
            "• Click on category names for detailed command lists\n"
            "• Use `!help <command>` for specific command help\n\n"
            "**Quick Links:**\n"
            "• `!help commands` - View all commands\n"
            "• `!help admin` - Admin-only commands\n"
            "• `!help mod` - Moderation commands"
        )

        embed = EmbedBuilder.create_embed(
            title="🤖 Bot Help Menu",
            description=description,
            color=discord.Color.blue(),
            thumbnail=self.bot.user.display_avatar.url if self.bot.user else None,
            timestamp=True,
        )

        # Add bot statistics
        guild_count = len(self.bot.guilds)
        user_count = sum(guild.member_count or 0 for guild in self.bot.guilds)
        command_count = len([cmd for cmd in self.bot.commands if not cmd.hidden])

        stats_value = (
            f"**Servers:** {guild_count:,}\n"
            f"**Users:** {user_count:,}\n"
            f"**Commands:** {command_count}"
        )

        embed.add_field(
            name="📊 Bot Statistics",
            value=stats_value,
            inline=True,
        )

        # Add useful information - make this shorter to avoid limits
        links_value = (
            "[Support](https://discord.gg/support)\n"
            "[Docs](https://github.com/repo)\n"
            "[Invite](https://discord.com/invite)"
        )

        embed.add_field(
            name="🔗 Links",
            value=links_value,
            inline=True,
        )

        embed.set_footer(text="Use the dropdown menu below to explore commands")
        return embed

    def create_category_embed(
        self, category_name: str, commands_list: List[commands.Command]
    ) -> discord.Embed:
        """Create an embed for a specific category"""
        embed = EmbedBuilder.create_embed(
            title=f"{category_name} Commands",
            description=f"Here are all the commands in the **{category_name}** category:",
            color=discord.Color.green(),
            timestamp=True,
        )

        # Discord limits:
        # - Embed description: 4096 characters
        # - Field value: 1024 characters
        # - Total embed: 6000 characters
        # - Max 25 fields per embed

        field_count = 0
        for command in commands_list:
            if field_count >= 25:  # Discord's field limit
                break

            # Get command signature
            signature = f"!{command.qualified_name}"
            if command.signature:
                signature += f" {command.signature}"

            # Truncate signature if too long
            if len(signature) > 256:  # Field name limit
                signature = signature[:253] + "..."

            # Get short description and truncate if needed
            description = command.short_doc or "No description available"
            if len(description) > 1020:  # Leave room for formatting
                description = description[:1017] + "..."

            embed.add_field(
                name=f"`{signature}`",
                value=description,
                inline=False,
            )
            field_count += 1

        # Truncate footer if needed
        footer_text = f"Use !help <command> for detailed information • {len(commands_list)} commands"
        if len(footer_text) > 2048:  # Footer text limit
            footer_text = footer_text[:2045] + "..."

        embed.set_footer(text=footer_text)
        return embed

    def create_command_embed(self, command: commands.Command) -> discord.Embed:
        """Create a detailed embed for a specific command"""
        # Determine color based on command category
        color = discord.Color.blue()
        if command.cog_name == "Moderation":
            color = discord.Color.red()
        elif command.cog_name == "Admin":
            color = discord.Color.orange()
        elif command.cog_name == "Tasks":
            color = discord.Color.purple()

        embed = EmbedBuilder.create_embed(
            title=f"Command: {command.qualified_name}",
            description=command.help or "No detailed description available.",
            color=color,
            timestamp=True,
        )

        # Command signature
        signature = f"!{command.qualified_name}"
        if command.signature:
            signature += f" {command.signature}"

        embed.add_field(name="📝 Usage", value=f"`{signature}`", inline=False)

        # Command aliases
        if command.aliases:
            aliases = ", ".join(f"`{alias}`" for alias in command.aliases)
            embed.add_field(name="🔄 Aliases", value=aliases, inline=True)

        # Required permissions
        if hasattr(command, "checks") and command.checks:
            perms = []
            for check in command.checks:
                if "admin" in str(check):
                    perms.append("Administrator")
                elif "mod" in str(check):
                    perms.append("Moderator")

            if perms:
                embed.add_field(
                    name="🔒 Required Permissions",
                    value=", ".join(perms),
                    inline=True,
                )

        # Category
        if command.cog_name:
            embed.add_field(name="📂 Category", value=command.cog_name, inline=True)

        embed.set_footer(text="Arguments in <> are required, [] are optional")
        return embed

    async def create_help_select_callback(
        self, interaction: discord.Interaction, selected_value: str
    ):
        """Handle help category selection"""
        try:
            categories = self.get_command_categories()

            if selected_value == "main":
                embed = self.create_main_help_embed()
                await interaction.response.edit_message(embed=embed)
            elif selected_value in categories:
                embed = self.create_category_embed(
                    selected_value, categories[selected_value]
                )
                await interaction.response.edit_message(embed=embed)
            else:
                embed = EmbedBuilder.create_error_embed(
                    "Category Not Found", "The selected category was not found."
                )
                await interaction.response.edit_message(embed=embed)

        except Exception as e:
            logger.error("Error in help select callback: %s", e)
            embed = EmbedBuilder.create_error_embed(
                "Error", "An error occurred while processing your selection."
            )
            await interaction.response.edit_message(embed=embed)

    @commands.hybrid_command(name="help", aliases=["h", "commands"])
    async def help_command(self, ctx, *, command_or_category: str = None):
        """
        Show help information for commands and categories

        Parameters
        ----------
        command_or_category : str, optional
            The command or category to get help for
        """
        try:
            if not command_or_category:
                # Show main help menu with dropdown
                embed = self.create_main_help_embed()
                categories = self.get_command_categories()

                # Only create select menu if we have categories
                if not categories:
                    # No categories available, show simple message
                    await ctx.send("❌ No commands are currently available.")
                    return

                # Create select options
                options = [
                    discord.SelectOption(
                        label="Main Menu",
                        value="main",
                        description="Return to the main help menu",
                        emoji="🏠",
                    )
                ]

                for category_name in categories.keys():
                    # Extract emoji from category name
                    emoji = category_name.split()[0] if category_name else "📁"
                    clean_name = (
                        " ".join(category_name.split()[1:])
                        if len(category_name.split()) > 1
                        else category_name
                    )

                    # Ensure we have a valid clean name
                    if not clean_name:
                        clean_name = "Unknown"

                    # Truncate label if too long (Discord limit is 100 chars)
                    if len(clean_name) > 95:
                        clean_name = clean_name[:92] + "..."

                    # Truncate description if too long (Discord limit is 100 chars)
                    description = f"View all {clean_name.lower()} commands"
                    if len(description) > 95:
                        description = description[:92] + "..."

                    options.append(
                        discord.SelectOption(
                            label=clean_name,
                            value=category_name,
                            description=description,
                            emoji=emoji,
                        )
                    )

                # Ensure we have at least one option besides main menu
                if len(options) <= 1:
                    await ctx.send("❌ No command categories are currently available.")
                    return

                # Limit to 25 options (Discord's limit)
                if len(options) > 25:
                    options = options[:25]

                try:
                    await send_select_menu(
                        ctx,
                        embed,
                        options,
                        self.create_help_select_callback,
                        placeholder="🔍 Choose a category to explore...",
                        user=ctx.author,
                        timeout=300,
                    )
                except discord.HTTPException as e:
                    logger.error("Failed to send select menu: %s", e)
                    # Fallback: send simple embed without select menu
                    await ctx.send(embed=embed)

            else:
                # Look for specific command
                command = self.bot.get_command(command_or_category.lower())
                if command and not command.hidden:
                    embed = self.create_command_embed(command)
                    try:
                        await ctx.send(embed=embed)
                    except discord.HTTPException as e:
                        # Fallback for embed issues
                        await ctx.send(
                            f"**{command.qualified_name}**: {command.short_doc or 'No description'}"
                        )
                    return

                # Look for category shortcuts
                categories = self.get_command_categories()
                category_shortcuts = {
                    "mod": "🛡️ Moderation",
                    "moderation": "🛡️ Moderation",
                    "admin": "⚡ Admin",
                    "administrator": "⚡ Admin",
                    "task": "🔄 Tasks",
                    "tasks": "🔄 Tasks",
                    "db": "🗄️ Database",
                    "database": "🗄️ Database",
                    "util": "🔧 Utility",
                    "utility": "🔧 Utility",
                    "commands": "all",
                }

                lookup = command_or_category.lower()
                if lookup in category_shortcuts:
                    if category_shortcuts[lookup] == "all":
                        # Show all commands in paginated format
                        embeds = []
                        for category_name, commands_list in categories.items():
                            if commands_list:
                                embed = self.create_category_embed(
                                    category_name, commands_list
                                )
                                embeds.append(embed)

                        if embeds:
                            try:
                                await send_paginated_embed(ctx, embeds, user=ctx.author)
                            except discord.HTTPException:
                                # Fallback: send simple text list
                                command_list = []
                                for commands_list in categories.values():
                                    for cmd in commands_list:
                                        command_list.append(
                                            f"`!{cmd.qualified_name}` - {cmd.short_doc or 'No description'}"
                                        )

                                # Split into chunks to avoid message length limits
                                chunks = []
                                current_chunk = ""
                                for cmd_info in command_list:
                                    if (
                                        len(current_chunk) + len(cmd_info) + 1 > 1900
                                    ):  # Leave room for formatting
                                        chunks.append(current_chunk)
                                        current_chunk = cmd_info
                                    else:
                                        current_chunk += (
                                            "\n" + cmd_info
                                            if current_chunk
                                            else cmd_info
                                        )

                                if current_chunk:
                                    chunks.append(current_chunk)

                                for i, chunk in enumerate(chunks):
                                    await ctx.send(
                                        f"**Commands (Part {i + 1}/{len(chunks)}):**\n{chunk}"
                                    )
                        else:
                            await ctx.send("⚠️ No commands are currently available.")
                    else:
                        category_name = category_shortcuts[lookup]
                        if category_name in categories:
                            embed = self.create_category_embed(
                                category_name, categories[category_name]
                            )
                            try:
                                await ctx.send(embed=embed)
                            except discord.HTTPException:
                                # Fallback: send simple text list
                                command_list = []
                                for cmd in categories[category_name]:
                                    command_list.append(
                                        f"`!{cmd.qualified_name}` - {cmd.short_doc or 'No description'}"
                                    )

                                await ctx.send(
                                    f"**{category_name} Commands:**\n"
                                    + "\n".join(command_list[:20])
                                )  # Limit to 20 commands
                        else:
                            embed = EmbedBuilder.create_error_embed(
                                "Category Not Found",
                                f"The category `{command_or_category}` was not found.",
                            )
                            await ctx.send(embed=embed)
                else:
                    # Not found
                    embed = EmbedBuilder.create_error_embed(
                        "Command Not Found",
                        f"No command or category named `{command_or_category}` was found.\n\n"
                        "Use `!help` to see all available commands and categories.",
                    )
                    await ctx.send(embed=embed)

        except discord.HTTPException as e:
            logger.error("Discord API error in help command: %s", e)
            await ctx.send(
                "❌ There was an issue displaying the help menu. Please try again or use `!help <command>` for specific command help."
            )
        except Exception as e:
            logger.error("Error in help command: %s", e)
            embed = EmbedBuilder.create_error_embed(
                "Help Error", "An error occurred while generating help information."
            )
            try:
                await ctx.send(embed=embed)
            except discord.HTTPException:
                await ctx.send(
                    "❌ An error occurred while generating help information."
                )

    @commands.hybrid_command(name="about", aliases=["info", "botinfo"])
    async def about_command(self, ctx):
        """Show detailed information about the bot"""
        embed = EmbedBuilder.create_embed(
            title="🤖 About This Bot",
            description=(
                "A comprehensive Discord bot built with discord.py featuring "
                "modular architecture, database integration, and modern UI components."
            ),
            color=discord.Color.blue(),
            thumbnail=self.bot.user.display_avatar.url if self.bot.user else None,
            timestamp=True,
        )

        # Bot information
        app_info = await self.bot.application_info()
        embed.add_field(name="👑 Bot Owner", value=app_info.owner.mention, inline=True)

        embed.add_field(
            name="🐍 Python Version",
            value=f"{self.bot.user.name} v1.0.0",
            inline=True,
        )

        embed.add_field(
            name="📚 discord.py Version", value=discord.__version__, inline=True
        )

        # Statistics
        guild_count = len(self.bot.guilds)
        user_count = sum(guild.member_count or 0 for guild in self.bot.guilds)
        command_count = len([cmd for cmd in self.bot.commands if not cmd.hidden])

        embed.add_field(
            name="📊 Statistics",
            value=(
                f"**Servers:** {guild_count:,}\n"
                f"**Users:** {user_count:,}\n"
                f"**Commands:** {command_count}\n"
                f"**Cogs:** {len(self.bot.cogs)}"
            ),
            inline=True,
        )

        # Features
        features = [
            "🛡️ Moderation Tools",
            "⚡ Admin Commands",
            "🔄 Background Tasks",
            "🗄️ Database Integration",
            "🌐 HTTP Session Management",
            "📝 Comprehensive Logging",
            "🎨 Interactive Menus",
            "✅ Environment Validation",
        ]

        embed.add_field(name="✨ Features", value="\n".join(features), inline=True)

        # Links
        embed.add_field(
            name="🔗 Links",
            value=(
                "[GitHub Repository](https://github.com/your-repo)\n"
                "[Support Server](https://discord.gg/your-server)\n"
                "[Invite Bot](https://discord.com/oauth2/authorize)"
            ),
            inline=True,
        )

        embed.set_footer(text="Made with ❤️ using discord.py")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
