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

            # Categorize based on cog name
            if command.cog_name == "Moderation":
                categories["🛡️ Moderation"].append(command)
            elif command.cog_name == "Admin":
                categories["⚡ Admin"].append(command)
            elif command.cog_name == "Tasks":
                categories["🔄 Tasks"].append(command)
            elif command.cog_name == "DatabaseDemo":
                categories["🗄️ Database"].append(command)
            elif command.cog_name == "HelpCommand":
                categories["❓ Help"].append(command)
            else:
                categories["🔧 Utility"].append(command)

        # Remove empty categories
        return {k: v for k, v in categories.items() if v}

    def create_main_help_embed(self) -> discord.Embed:
        """Create the main help embed"""
        embed = EmbedBuilder.create_embed(
            title="🤖 Bot Help Menu",
            description=(
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
            ),
            color=discord.Color.blue(),
            thumbnail=self.bot.user.display_avatar.url if self.bot.user else None,
            timestamp=True,
        )

        # Add bot statistics
        guild_count = len(self.bot.guilds)
        user_count = sum(guild.member_count for guild in self.bot.guilds)
        command_count = len([cmd for cmd in self.bot.commands if not cmd.hidden])

        embed.add_field(
            name="📊 Bot Statistics",
            value=(
                f"**Servers:** {guild_count:,}\n"
                f"**Users:** {user_count:,}\n"
                f"**Commands:** {command_count}"
            ),
            inline=True,
        )

        # Add useful information
        embed.add_field(
            name="🔗 Useful Links",
            value=(
                "[Support Server](https://discord.gg/your-server)\n"
                "[Documentation](https://github.com/your-repo)\n"
                "[Invite Bot](https://discord.com/oauth2/authorize)"
            ),
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

        for command in commands_list:
            # Get command signature
            signature = f"!{command.qualified_name}"
            if command.signature:
                signature += f" {command.signature}"

            # Get short description
            description = command.short_doc or "No description available"

            embed.add_field(
                name=f"`{signature}`",
                value=description,
                inline=False,
            )

        embed.set_footer(
            text=f"Use !help <command> for detailed information • {len(commands_list)} commands"
        )
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

    @commands.command(name="help", aliases=["h", "commands"])
    async def help_command(self, ctx, *, command_or_category: str = None):
        """
        Show help information for commands and categories

        Usage:
        !help - Show the main help menu
        !help <command> - Show detailed help for a specific command
        !help <category> - Show commands in a category
        """
        try:
            if not command_or_category:
                # Show main help menu with dropdown
                embed = self.create_main_help_embed()
                categories = self.get_command_categories()

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
                    clean_name = " ".join(category_name.split()[1:])

                    options.append(
                        discord.SelectOption(
                            label=clean_name,
                            value=category_name,
                            description=f"View all {clean_name.lower()} commands",
                            emoji=emoji,
                        )
                    )

                await send_select_menu(
                    ctx,
                    embed,
                    options,
                    self.create_help_select_callback,
                    placeholder="🔍 Choose a category to explore...",
                    user=ctx.author,
                    timeout=300,
                )

            else:
                # Look for specific command
                command = self.bot.get_command(command_or_category.lower())
                if command and not command.hidden:
                    embed = self.create_command_embed(command)
                    await ctx.send(embed=embed)
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
                            await send_paginated_embed(ctx, embeds, user=ctx.author)
                        else:
                            embed = EmbedBuilder.create_warning_embed(
                                "No Commands", "No commands are currently available."
                            )
                            await ctx.send(embed=embed)
                    else:
                        category_name = category_shortcuts[lookup]
                        if category_name in categories:
                            embed = self.create_category_embed(
                                category_name, categories[category_name]
                            )
                            await ctx.send(embed=embed)
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

        except Exception as e:
            logger.error("Error in help command: %s", e)
            embed = EmbedBuilder.create_error_embed(
                "Help Error", "An error occurred while generating help information."
            )
            await ctx.send(embed=embed)

    @commands.command(name="about", aliases=["info", "botinfo"])
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
        user_count = sum(guild.member_count for guild in self.bot.guilds)
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
