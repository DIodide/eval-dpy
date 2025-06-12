import discord
from discord.ext import commands
from typing import List, Dict, Any, Optional, Callable, Union
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class MenuView(discord.ui.View):
    """Base class for interactive Discord menus with pagination and buttons"""

    def __init__(
        self,
        *,
        timeout: float = 180.0,
        user: Optional[discord.User] = None,
        delete_after: bool = False,
    ):
        super().__init__(timeout=timeout)
        self.user = user
        self.delete_after = delete_after
        self.message: Optional[discord.Message] = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check if the user can interact with this menu"""
        if self.user and interaction.user != self.user:
            await interaction.response.send_message(
                "❌ You cannot interact with this menu!", ephemeral=True
            )
            return False
        return True

    async def on_timeout(self) -> None:
        """Called when the view times out"""
        if self.message:
            try:
                if self.delete_after:
                    await self.message.delete()
                else:
                    # Disable all buttons
                    for item in self.children:
                        item.disabled = True
                    await self.message.edit(view=self)
            except discord.HTTPException:
                pass  # Message might already be deleted


class PaginatedEmbed(MenuView):
    """Paginated embed menu with navigation buttons"""

    def __init__(
        self,
        embeds: List[discord.Embed],
        *,
        timeout: float = 180.0,
        user: Optional[discord.User] = None,
        delete_after: bool = False,
        show_page_count: bool = True,
    ):
        super().__init__(timeout=timeout, user=user, delete_after=delete_after)
        self.embeds = embeds
        self.current_page = 0
        self.show_page_count = show_page_count

        # Update embed footers with page numbers if requested
        if show_page_count and len(embeds) > 1:
            self._update_embed_footers()

        # Only show navigation if there are multiple pages
        if len(embeds) <= 1:
            self.clear_items()

    def _update_embed_footers(self):
        """Add page numbers to embed footers"""
        for i, embed in enumerate(self.embeds):
            page_text = f"Page {i + 1} of {len(self.embeds)}"
            if embed.footer.text:
                embed.set_footer(text=f"{embed.footer.text} • {page_text}")
            else:
                embed.set_footer(text=page_text)

    @discord.ui.button(emoji="⏮️", style=discord.ButtonStyle.secondary)
    async def first_page(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """Go to first page"""
        self.current_page = 0
        await interaction.response.edit_message(
            embed=self.embeds[self.current_page], view=self
        )

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.primary)
    async def previous_page(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """Go to previous page"""
        self.current_page = (self.current_page - 1) % len(self.embeds)
        await interaction.response.edit_message(
            embed=self.embeds[self.current_page], view=self
        )

    @discord.ui.button(emoji="🗑️", style=discord.ButtonStyle.danger)
    async def delete_menu(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """Delete the menu"""
        await interaction.response.defer()
        await interaction.delete_original_response()

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.primary)
    async def next_page(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """Go to next page"""
        self.current_page = (self.current_page + 1) % len(self.embeds)
        await interaction.response.edit_message(
            embed=self.embeds[self.current_page], view=self
        )

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary)
    async def last_page(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """Go to last page"""
        self.current_page = len(self.embeds) - 1
        await interaction.response.edit_message(
            embed=self.embeds[self.current_page], view=self
        )


class SelectMenu(MenuView):
    """Menu with a select dropdown"""

    def __init__(
        self,
        options: List[discord.SelectOption],
        callback: Callable[[discord.Interaction, str], Any],
        *,
        placeholder: str = "Choose an option...",
        timeout: float = 180.0,
        user: Optional[discord.User] = None,
        delete_after: bool = False,
    ):
        super().__init__(timeout=timeout, user=user, delete_after=delete_after)
        self.callback_func = callback
        self.add_item(
            discord.ui.Select(
                placeholder=placeholder, options=options, custom_id="select_menu"
            )
        )

    @discord.ui.select(placeholder="Choose an option...")
    async def select_callback(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        """Handle select menu interaction"""
        await self.callback_func(interaction, select.values[0])


class ConfirmationMenu(MenuView):
    """Simple confirmation menu with Yes/No buttons"""

    def __init__(
        self,
        *,
        timeout: float = 60.0,
        user: Optional[discord.User] = None,
        delete_after: bool = True,
    ):
        super().__init__(timeout=timeout, user=user, delete_after=delete_after)
        self.result: Optional[bool] = None

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.success, emoji="✅")
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """Confirm button"""
        self.result = True
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="No", style=discord.ButtonStyle.danger, emoji="❌")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Cancel button"""
        self.result = False
        self.stop()
        await interaction.response.defer()


class EmbedBuilder:
    """Helper class for building beautiful embeds"""

    @staticmethod
    def create_embed(
        title: str = None,
        description: str = None,
        color: discord.Color = None,
        *,
        author: discord.User = None,
        thumbnail: str = None,
        image: str = None,
        footer: str = None,
        timestamp: bool = False,
    ) -> discord.Embed:
        """Create a formatted embed with common styling"""
        if color is None:
            color = discord.Color.blue()

        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.utcnow() if timestamp else None,
        )

        if author:
            embed.set_author(
                name=author.display_name, icon_url=author.display_avatar.url
            )

        if thumbnail:
            embed.set_thumbnail(url=thumbnail)

        if image:
            embed.set_image(url=image)

        if footer:
            embed.set_footer(text=footer)

        return embed

    @staticmethod
    def create_error_embed(
        title: str = "Error",
        description: str = "An error occurred",
        *,
        footer: str = None,
    ) -> discord.Embed:
        """Create an error embed"""
        return EmbedBuilder.create_embed(
            title=f"❌ {title}",
            description=description,
            color=discord.Color.red(),
            footer=footer,
            timestamp=True,
        )

    @staticmethod
    def create_success_embed(
        title: str = "Success",
        description: str = "Operation completed successfully",
        *,
        footer: str = None,
    ) -> discord.Embed:
        """Create a success embed"""
        return EmbedBuilder.create_embed(
            title=f"✅ {title}",
            description=description,
            color=discord.Color.green(),
            footer=footer,
            timestamp=True,
        )

    @staticmethod
    def create_warning_embed(
        title: str = "Warning",
        description: str = "Please review this information",
        *,
        footer: str = None,
    ) -> discord.Embed:
        """Create a warning embed"""
        return EmbedBuilder.create_embed(
            title=f"⚠️ {title}",
            description=description,
            color=discord.Color.orange(),
            footer=footer,
            timestamp=True,
        )

    @staticmethod
    def create_info_embed(
        title: str = "Information",
        description: str = "Here's some information",
        *,
        footer: str = None,
    ) -> discord.Embed:
        """Create an info embed"""
        return EmbedBuilder.create_embed(
            title=f"ℹ️ {title}",
            description=description,
            color=discord.Color.blue(),
            footer=footer,
            timestamp=True,
        )


class LeaderboardBuilder:
    """Helper class for building leaderboard embeds"""

    @staticmethod
    def create_leaderboard(
        title: str,
        entries: List[Dict[str, Any]],
        *,
        page_size: int = 10,
        key_field: str = "name",
        value_field: str = "value",
        emoji_field: str = None,
        color: discord.Color = None,
        thumbnail: str = None,
    ) -> List[discord.Embed]:
        """
        Create paginated leaderboard embeds

        Args:
            title: Leaderboard title
            entries: List of dicts with leaderboard data
            page_size: Number of entries per page
            key_field: Field name for the main identifier
            value_field: Field name for the value to display
            emoji_field: Optional field name for emoji
            color: Embed color
            thumbnail: Thumbnail URL
        """
        if not entries:
            embed = EmbedBuilder.create_embed(
                title=title,
                description="No entries found.",
                color=color or discord.Color.blue(),
                thumbnail=thumbnail,
            )
            return [embed]

        embeds = []
        total_pages = (len(entries) + page_size - 1) // page_size

        for page in range(total_pages):
            start_idx = page * page_size
            end_idx = min(start_idx + page_size, len(entries))
            page_entries = entries[start_idx:end_idx]

            embed = EmbedBuilder.create_embed(
                title=title,
                color=color or discord.Color.blue(),
                thumbnail=thumbnail,
                timestamp=True,
            )

            leaderboard_text = ""
            for i, entry in enumerate(page_entries, start=start_idx + 1):
                # Get medal emoji for top 3
                if i == 1:
                    medal = "🥇"
                elif i == 2:
                    medal = "🥈"
                elif i == 3:
                    medal = "🥉"
                else:
                    medal = f"`{i:2d}.`"

                # Get custom emoji if provided
                custom_emoji = ""
                if emoji_field and emoji_field in entry:
                    custom_emoji = f" {entry[emoji_field]}"

                name = entry.get(key_field, "Unknown")
                value = entry.get(value_field, 0)

                leaderboard_text += f"{medal} **{name}**{custom_emoji} - `{value:,}`\n"

            embed.description = leaderboard_text

            if total_pages > 1:
                embed.set_footer(text=f"Page {page + 1} of {total_pages}")

            embeds.append(embed)

        return embeds


# Utility functions for easy menu creation
async def send_paginated_embed(
    ctx: commands.Context,
    embeds: List[discord.Embed],
    *,
    user: Optional[discord.User] = None,
    delete_after: bool = False,
) -> discord.Message:
    """Send a paginated embed menu"""
    view = PaginatedEmbed(embeds, user=user or ctx.author, delete_after=delete_after)
    message = await ctx.send(embed=embeds[0], view=view)
    view.message = message
    return message


async def send_confirmation(
    ctx: commands.Context,
    embed: discord.Embed,
    *,
    user: Optional[discord.User] = None,
    timeout: float = 60.0,
) -> Optional[bool]:
    """Send a confirmation menu and return the result"""
    view = ConfirmationMenu(timeout=timeout, user=user or ctx.author)
    message = await ctx.send(embed=embed, view=view)
    view.message = message

    await view.wait()
    return view.result


async def send_select_menu(
    ctx: commands.Context,
    embed: discord.Embed,
    options: List[discord.SelectOption],
    callback: Callable[[discord.Interaction, str], Any],
    *,
    placeholder: str = "Choose an option...",
    user: Optional[discord.User] = None,
    timeout: float = 180.0,
) -> discord.Message:
    """Send a select menu"""
    view = SelectMenu(
        options,
        callback,
        placeholder=placeholder,
        user=user or ctx.author,
        timeout=timeout,
    )
    message = await ctx.send(embed=embed, view=view)
    view.message = message
    return message
