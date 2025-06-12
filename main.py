import discord
from discord.ext import commands
import asyncio
import os
import logging
import aiohttp
from dotenv import load_dotenv
from utils.database import DatabaseManager
from utils.env_validator import validate_environment_or_exit

# Load environment variables from .env file
load_dotenv()

# Validate environment variables before proceeding
validate_environment_or_exit()

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(command_prefix="!", intents=intents, help_command=None)

        # Global aiohttp session
        self.session = None

        # Database manager
        self.db = None

    async def setup_hook(self):
        """Called when the bot is starting up"""
        logger.info("Bot is starting up...")

        # Initialize database
        await self.create_database_connection()

        # Initialize global aiohttp session
        await self.create_http_session()

        # Load cogs
        cogs_to_load = [
            "cogs.moderation",
            "cogs.admin",
            "cogs.tasks",
            "cogs.database_demo",
        ]

        for cog in cogs_to_load:
            try:
                await self.load_extension(cog)
                logger.info("Loaded %s", cog)
            except Exception as e:
                logger.error("Failed to load %s: %s", cog, e)

        logger.info("Bot setup completed!")

    async def create_database_connection(self):
        """Create database connection pool"""
        try:
            self.db = DatabaseManager(self)
            await self.db.initialize()
            logger.info("Database manager initialized")
        except Exception as e:
            logger.warning("Database initialization failed: %s", e)
            logger.warning("Bot will continue without database functionality")
            self.db = None

    async def create_http_session(self):
        """Create a global aiohttp session"""
        connector = aiohttp.TCPConnector(
            limit=100,  # Total connection limit
            limit_per_host=30,  # Per-host connection limit
            ttl_dns_cache=300,  # DNS cache TTL
            use_dns_cache=True,
        )

        timeout = aiohttp.ClientTimeout(total=30)  # 30 second timeout

        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                "User-Agent": f"Discord Bot {self.user.name if self.user else 'Unknown'}/1.0"
            },
        )
        logger.info("Global aiohttp session created")

    async def close_http_session(self):
        """Close the global aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("Global aiohttp session closed")

    async def close_database_connection(self):
        """Close database connection pool"""
        if self.db:
            await self.db.close()
            logger.info("Database connection closed")

    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info("%s has connected to Discord!", self.user)
        logger.info("Bot is in %d guilds", len(self.guilds))
        logger.info("Bot ID: %s", self.user.id)

        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, name="for !help"
            )
        )

        # Start any background tasks here if needed
        logger.info("Bot is ready and operational!")

    async def close(self):
        """Called when the bot is shutting down"""
        logger.info("Bot is shutting down...")

        # Close database connection
        await self.close_database_connection()

        # Close aiohttp session
        await self.close_http_session()

        # Call parent close method
        await super().close()

        logger.info("Bot shutdown completed!")


async def main():
    # Read token from environment variable
    token = os.getenv("DISCORD_TOKEN")

    if not token:
        logger.error(
            "DISCORD_TOKEN not found in environment variables! Please create a .env file and add DISCORD_TOKEN=your_bot_token_here"
        )
        return

    bot = DiscordBot()

    try:
        await bot.start(token)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error("Bot error: %s", e)
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
