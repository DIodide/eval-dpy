import discord
from discord.ext import commands
from typing import Union


def is_admin():
    """Check if user has administrator permissions"""

    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator

    return commands.check(predicate)


def is_mod_or_admin():
    """Check if user has moderation permissions (manage messages, kick members, or admin)"""

    async def predicate(ctx):
        perms = ctx.author.guild_permissions
        return any(
            [
                perms.administrator,
                perms.manage_messages,
                perms.kick_members,
                perms.ban_members,
            ]
        )

    return commands.check(predicate)


async def can_target_member(ctx, target: discord.Member) -> bool:
    """Check if the command author can target the specified member"""
    if target == ctx.author:
        return False

    if target == ctx.guild.owner:
        return False

    if ctx.author.top_role <= target.top_role and ctx.author != ctx.guild.owner:
        return False

    return True


def format_time(seconds: int) -> str:
    """Format seconds into a readable time string"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    elif seconds < 86400:
        return f"{seconds // 3600}h {(seconds % 3600) // 60}m"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}d {hours}h"
