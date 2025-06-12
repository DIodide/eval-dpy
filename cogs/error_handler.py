import discord
from discord.ext import commands
import logging
import traceback
import sys
from typing import Optional
from utils.menus import EmbedBuilder

logger = logging.getLogger(__name__)


class ErrorHandler(commands.Cog):
    """Global error handler for the Discord bot"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        """
        Global error handler for command errors
        Handles various types of command errors and provides user-friendly responses
        """

        # Don't handle errors that have already been handled locally
        if hasattr(ctx.command, "on_error"):
            return

        # Don't handle errors for commands that have local error handlers
        cog = ctx.cog
        if cog and cog.has_error_handler():
            return

        # Extract the original error from CommandInvokeError
        if isinstance(error, commands.CommandInvokeError):
            error = error.original

        # Don't interfere with KeyboardInterrupt - let it propagate to close the bot
        if isinstance(error, KeyboardInterrupt):
            logger.info("KeyboardInterrupt received, shutting down bot...")
            raise error

        # Handle specific error types
        embed = None
        send_to_user = True

        if isinstance(error, commands.CommandNotFound):
            # Silently ignore command not found errors
            send_to_user = False

        elif isinstance(error, commands.DisabledCommand):
            embed = EmbedBuilder.create_error_embed(
                "Command Disabled",
                f"The command `{ctx.command}` has been disabled and cannot be used.",
            )

        elif isinstance(error, commands.MissingRequiredArgument):
            embed = EmbedBuilder.create_error_embed(
                "Missing Required Argument",
                f"You're missing the required argument: `{error.param.name}`\n\n"
                f"**Usage:** `!{ctx.command.qualified_name} {ctx.command.signature}`\n"
                f"Use `!help {ctx.command.qualified_name}` for more information.",
            )

        elif isinstance(error, commands.BadArgument):
            embed = EmbedBuilder.create_error_embed(
                "Invalid Argument",
                f"Invalid argument provided: {str(error)}\n\n"
                f"**Usage:** `!{ctx.command.qualified_name} {ctx.command.signature}`\n"
                f"Use `!help {ctx.command.qualified_name}` for more information.",
            )

        elif isinstance(error, commands.TooManyArguments):
            embed = EmbedBuilder.create_error_embed(
                "Too Many Arguments",
                f"You provided too many arguments for this command.\n\n"
                f"**Usage:** `!{ctx.command.qualified_name} {ctx.command.signature}`\n"
                f"Use `!help {ctx.command.qualified_name}` for more information.",
            )

        elif isinstance(error, commands.MissingPermissions):
            perms = ", ".join(error.missing_permissions)
            embed = EmbedBuilder.create_error_embed(
                "Missing Permissions",
                f"You don't have the required permissions to use this command.\n\n"
                f"**Required permissions:** {perms}",
            )

        elif isinstance(error, commands.BotMissingPermissions):
            perms = ", ".join(error.missing_permissions)
            embed = EmbedBuilder.create_error_embed(
                "Bot Missing Permissions",
                f"I don't have the required permissions to execute this command.\n\n"
                f"**Required permissions:** {perms}\n"
                f"Please contact a server administrator to grant these permissions.",
            )

        elif isinstance(error, commands.CheckFailure):
            embed = EmbedBuilder.create_error_embed(
                "Check Failed", "You don't have permission to use this command."
            )

        elif isinstance(error, commands.CommandOnCooldown):
            embed = EmbedBuilder.create_error_embed(
                "Command On Cooldown",
                f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds.",
            )

        elif isinstance(error, commands.MaxConcurrencyReached):
            embed = EmbedBuilder.create_error_embed(
                "Command In Use",
                f"This command is already being used. Please wait for it to finish.",
            )

        elif isinstance(error, commands.NotOwner):
            embed = EmbedBuilder.create_error_embed(
                "Owner Only", "This command can only be used by the bot owner."
            )

        elif isinstance(error, commands.PrivateMessageOnly):
            embed = EmbedBuilder.create_error_embed(
                "DM Only", "This command can only be used in direct messages."
            )

        elif isinstance(error, commands.NoPrivateMessage):
            embed = EmbedBuilder.create_error_embed(
                "Server Only", "This command cannot be used in direct messages."
            )

        elif isinstance(error, discord.Forbidden):
            embed = EmbedBuilder.create_error_embed(
                "Permission Denied",
                "I don't have permission to perform this action. Please check my role permissions.",
            )

        elif isinstance(error, discord.NotFound):
            embed = EmbedBuilder.create_error_embed(
                "Not Found",
                "The requested resource could not be found. It may have been deleted or moved.",
            )

        elif isinstance(error, discord.HTTPException):
            if error.status == 429:  # Rate limited
                embed = EmbedBuilder.create_error_embed(
                    "Rate Limited",
                    "I'm being rate limited by Discord. Please try again in a few moments.",
                )
            else:
                embed = EmbedBuilder.create_error_embed(
                    "Discord Error", f"Discord returned an error: {error.text}"
                )

        elif isinstance(error, commands.ExtensionError):
            # Extension-related errors (for debugging)
            logger.error("Extension error in command %s: %s", ctx.command, error)
            embed = EmbedBuilder.create_error_embed(
                "Extension Error",
                "An error occurred with a bot extension. This has been logged.",
            )

        else:
            # Unknown/unexpected error
            logger.error("Unexpected error in command %s: %s", ctx.command, error)
            logger.error(
                "Full traceback: %s",
                traceback.format_exception(type(error), error, error.__traceback__),
            )

            embed = EmbedBuilder.create_error_embed(
                "Unexpected Error",
                "An unexpected error occurred while processing this command. "
                "This has been logged and will be investigated.",
            )

        # Send error message to user if applicable
        if send_to_user and embed:
            try:
                await ctx.send(embed=embed)
            except discord.HTTPException:
                # If we can't send embeds, try sending a simple message
                try:
                    await ctx.send(f"❌ Error: {embed.description}")
                except discord.HTTPException:
                    # If we can't send anything, log it
                    logger.error(
                        "Could not send error message to user in %s", ctx.channel
                    )

    @commands.Cog.listener()
    async def on_error(self, event: str, *args, **kwargs):
        """
        Global error handler for non-command errors
        Handles errors that occur outside of command processing
        """
        # Get the current exception
        exc_type, exc_value, exc_traceback = sys.exc_info()

        # Don't interfere with KeyboardInterrupt
        if exc_type is KeyboardInterrupt:
            logger.info(
                "KeyboardInterrupt received in event %s, shutting down bot...", event
            )
            raise exc_value

        # Log the error
        logger.error("Error in event %s: %s", event, exc_value)
        logger.error(
            "Full traceback: %s",
            traceback.format_exception(exc_type, exc_value, exc_traceback),
        )

        # Try to get more context about the error
        error_context = {
            "event": event,
            "args": str(args)[:200] if args else "None",
            "kwargs": str(kwargs)[:200] if kwargs else "None",
        }

        logger.error("Error context: %s", error_context)

    @commands.Cog.listener()
    async def on_command_completion(self, ctx: commands.Context):
        """
        Log successful command completions
        """
        # Only log if debug logging is enabled
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "Command completed: %s by %s in %s",
                ctx.command.qualified_name,
                ctx.author,
                ctx.guild.name if ctx.guild else "DM",
            )

    @commands.command(name="error", hidden=True)
    @commands.is_owner()
    async def test_error(self, ctx):
        """Test command to trigger an error (owner only)"""
        raise Exception("This is a test error!")

    async def cog_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        """
        Local error handler for this cog
        This will handle errors specific to error handler commands
        """
        if isinstance(error, commands.NotOwner):
            embed = EmbedBuilder.create_error_embed(
                "Owner Only",
                "Error testing commands can only be used by the bot owner.",
            )
            await ctx.send(embed=embed)


class ErrorLogging:
    """Utility class for error logging and reporting"""

    @staticmethod
    def setup_logging():
        """Setup enhanced logging for error tracking"""
        # Create a separate logger for errors
        error_logger = logging.getLogger("bot_errors")
        error_logger.setLevel(logging.ERROR)

        # Create file handler for errors if it doesn't exist
        if not error_logger.handlers:
            try:
                handler = logging.FileHandler("bot_errors.log", encoding="utf-8")
                formatter = logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
                handler.setFormatter(formatter)
                error_logger.addHandler(handler)
                logger.info("Error logging to file enabled")
            except Exception as e:
                logger.warning("Could not setup error file logging: %s", e)

    @staticmethod
    async def log_error_to_channel(bot, error: Exception, context: str = None):
        """
        Log error to a designated error channel (if configured)
        This can be used for important errors that need immediate attention
        """
        # This is a placeholder for error reporting to a Discord channel
        # You can implement this based on your needs
        error_channel_id = None  # Set this to your error logging channel ID

        if error_channel_id:
            try:
                channel = bot.get_channel(error_channel_id)
                if channel:
                    embed = EmbedBuilder.create_error_embed(
                        "Bot Error Detected",
                        f"**Context:** {context or 'Unknown'}\n"
                        f"**Error:** {str(error)[:1000]}\n"
                        f"**Type:** {type(error).__name__}",
                    )
                    await channel.send(embed=embed)
            except Exception as e:
                logger.error("Could not send error to logging channel: %s", e)


async def setup(bot):
    # Setup enhanced error logging
    ErrorLogging.setup_logging()

    # Add the error handler cog
    await bot.add_cog(ErrorHandler(bot))
    logger.info("Global error handler loaded")
