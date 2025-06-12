import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta
from utils.checks import is_admin, can_target_member, format_time


class Moderation(commands.Cog):
    """Moderation commands for server management"""

    def __init__(self, bot):
        self.bot = bot
        self.muted_members = {}  # Simple in-memory storage for muted members

    @commands.command(name="kick")
    @is_admin()
    async def kick_member(
        self, ctx, member: discord.Member, *, reason="No reason provided"
    ):
        """Kick a member from the server"""
        if not await can_target_member(ctx, member):
            await ctx.send("❌ You cannot target this member!")
            return

        try:
            await member.kick(reason=f"Kicked by {ctx.author}: {reason}")

            embed = discord.Embed(
                title="Member Kicked",
                description=f"**{member}** has been kicked from the server.",
                color=discord.Color.orange(),
                timestamp=datetime.utcnow(),
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            embed.set_thumbnail(url=member.display_avatar.url)

            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to kick this member!")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {e}")

    @commands.command(name="ban")
    @is_admin()
    async def ban_member(
        self, ctx, member: discord.Member, *, reason="No reason provided"
    ):
        """Ban a member from the server"""
        if not await can_target_member(ctx, member):
            await ctx.send("❌ You cannot target this member!")
            return

        try:
            await member.ban(reason=f"Banned by {ctx.author}: {reason}")

            embed = discord.Embed(
                title="Member Banned",
                description=f"**{member}** has been banned from the server.",
                color=discord.Color.red(),
                timestamp=datetime.utcnow(),
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            embed.set_thumbnail(url=member.display_avatar.url)

            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to ban this member!")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {e}")

    @commands.command(name="unban")
    @is_admin()
    async def unban_member(self, ctx, *, member):
        """Unban a member from the server"""
        banned_users = [entry async for entry in ctx.guild.bans()]

        member_name, member_discriminator = member.split("#")

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                try:
                    await ctx.guild.unban(user)

                    embed = discord.Embed(
                        title="Member Unbanned",
                        description=f"**{user}** has been unbanned from the server.",
                        color=discord.Color.green(),
                        timestamp=datetime.utcnow(),
                    )
                    embed.add_field(
                        name="Moderator", value=ctx.author.mention, inline=True
                    )

                    await ctx.send(embed=embed)
                    return

                except discord.Forbidden:
                    await ctx.send("❌ I don't have permission to unban members!")
                    return
                except Exception as e:
                    await ctx.send(f"❌ An error occurred: {e}")
                    return

        await ctx.send("❌ Member not found in ban list!")

    @commands.command(name="mute")
    @is_admin()
    async def mute_member(
        self,
        ctx,
        member: discord.Member,
        duration: int = 0,
        *,
        reason="No reason provided",
    ):
        """Mute a member (timeout) for a specified duration in minutes"""
        if not await can_target_member(ctx, member):
            await ctx.send("❌ You cannot target this member!")
            return

        if duration <= 0:
            await ctx.send("❌ Duration must be a positive number of minutes!")
            return

        if duration > 40320:  # 28 days max
            await ctx.send("❌ Duration cannot exceed 28 days (40320 minutes)!")
            return

        try:
            timeout_until = datetime.utcnow() + timedelta(minutes=duration)
            await member.timeout(
                timeout_until, reason=f"Muted by {ctx.author}: {reason}"
            )

            embed = discord.Embed(
                title="Member Muted",
                description=f"**{member}** has been muted for {format_time(duration * 60)}.",
                color=discord.Color.orange(),
                timestamp=datetime.utcnow(),
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(
                name="Duration", value=format_time(duration * 60), inline=True
            )
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            embed.set_thumbnail(url=member.display_avatar.url)

            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to timeout this member!")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {e}")

    @commands.command(name="unmute")
    @is_admin()
    async def unmute_member(self, ctx, member: discord.Member):
        """Unmute a member (remove timeout)"""
        try:
            await member.timeout(None, reason=f"Unmuted by {ctx.author}")

            embed = discord.Embed(
                title="Member Unmuted",
                description=f"**{member}** has been unmuted.",
                color=discord.Color.green(),
                timestamp=datetime.utcnow(),
            )
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            embed.set_thumbnail(url=member.display_avatar.url)

            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send(
                "❌ I don't have permission to remove timeout from this member!"
            )
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {e}")

    @commands.command(name="purge", aliases=["clear"])
    @is_admin()
    async def purge_messages(self, ctx, amount: int):
        """Delete a specified number of messages"""
        if amount <= 0:
            await ctx.send("❌ Amount must be a positive number!")
            return

        if amount > 100:
            await ctx.send("❌ Cannot delete more than 100 messages at once!")
            return

        try:
            deleted = await ctx.channel.purge(
                limit=amount + 1
            )  # +1 to include the command message

            embed = discord.Embed(
                title="Messages Purged",
                description=f"Successfully deleted {len(deleted) - 1} messages.",
                color=discord.Color.green(),
                timestamp=datetime.utcnow(),
            )
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            embed.add_field(name="Channel", value=ctx.channel.mention, inline=True)

            # Send confirmation message that will auto-delete
            confirmation = await ctx.send(embed=embed)
            await asyncio.sleep(5)  # Wait 5 seconds
            await confirmation.delete()

        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to manage messages!")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {e}")

    @commands.command(name="slowmode")
    @is_admin()
    async def set_slowmode(self, ctx, seconds: int):
        """Set slowmode for the current channel"""
        if seconds < 0 or seconds > 21600:
            await ctx.send("❌ Slowmode must be between 0 and 21600 seconds (6 hours)!")
            return

        try:
            await ctx.channel.edit(slowmode_delay=seconds)

            if seconds == 0:
                embed = discord.Embed(
                    title="Slowmode Disabled",
                    description=f"Slowmode has been disabled in {ctx.channel.mention}.",
                    color=discord.Color.green(),
                    timestamp=datetime.utcnow(),
                )
            else:
                embed = discord.Embed(
                    title="Slowmode Enabled",
                    description=f"Slowmode set to {format_time(seconds)} in {ctx.channel.mention}.",
                    color=discord.Color.orange(),
                    timestamp=datetime.utcnow(),
                )

            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to manage this channel!")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {e}")

    @commands.command(name="warn")
    @is_admin()
    async def warn_member(
        self, ctx, member: discord.Member, *, reason="No reason provided"
    ):
        """Warn a member"""
        if not await can_target_member(ctx, member):
            await ctx.send("❌ You cannot target this member!")
            return

        embed = discord.Embed(
            title="Member Warned",
            description=f"**{member}** has been warned.",
            color=discord.Color.yellow(),
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        embed.set_thumbnail(url=member.display_avatar.url)

        await ctx.send(embed=embed)

        # Try to DM the user
        try:
            dm_embed = discord.Embed(
                title=f"Warning in {ctx.guild.name}",
                description=f"You have been warned by **{ctx.author}**.",
                color=discord.Color.yellow(),
                timestamp=datetime.utcnow(),
            )
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            await member.send(embed=dm_embed)
        except discord.Forbidden:
            pass  # User has DMs disabled

    # Error handling for missing permissions
    @kick_member.error
    @ban_member.error
    @unban_member.error
    @mute_member.error
    @unmute_member.error
    @purge_messages.error
    @set_slowmode.error
    @warn_member.error
    async def moderation_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("❌ You need administrator permissions to use this command!")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("❌ Member not found!")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Invalid argument provided!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Missing required argument!")


async def setup(bot):
    await bot.add_cog(Moderation(bot))
