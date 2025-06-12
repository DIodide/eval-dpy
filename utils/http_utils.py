import aiohttp
import asyncio
import logging
from typing import Optional, Dict, Any, Union

logger = logging.getLogger(__name__)


class HTTPHelper:
    """Helper class for making HTTP requests using the bot's shared session"""

    def __init__(self, bot):
        self.bot = bot

    @property
    def session(self) -> Optional[aiohttp.ClientSession]:
        """Get the bot's shared aiohttp session"""
        return getattr(self.bot, "session", None)

    async def get(self, url: str, **kwargs) -> Optional[Dict[Any, Any]]:
        """Make a GET request and return JSON response"""
        if not self.session:
            logger.error("No HTTP session available")
            return None

        try:
            async with self.session.get(url, **kwargs) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning(
                        "GET request to %s returned status %d", url, response.status
                    )
                    return None
        except aiohttp.ClientError as e:
            logger.error("HTTP GET error for %s: %s", url, e)
            return None
        except Exception as e:
            logger.error("Unexpected error in GET request to %s: %s", url, e)
            return None

    async def post(
        self,
        url: str,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
        **kwargs,
    ) -> Optional[Dict[Any, Any]]:
        """Make a POST request and return JSON response"""
        if not self.session:
            logger.error("No HTTP session available")
            return None

        try:
            async with self.session.post(
                url, data=data, json=json, **kwargs
            ) as response:
                if response.status in (200, 201):
                    return await response.json()
                else:
                    logger.warning(
                        "POST request to %s returned status %d", url, response.status
                    )
                    return None
        except aiohttp.ClientError as e:
            logger.error("HTTP POST error for %s: %s", url, e)
            return None
        except Exception as e:
            logger.error("Unexpected error in POST request to %s: %s", url, e)
            return None

    async def get_text(self, url: str, **kwargs) -> Optional[str]:
        """Make a GET request and return text response"""
        if not self.session:
            logger.error("No HTTP session available")
            return None

        try:
            async with self.session.get(url, **kwargs) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(
                        "GET request to %s returned status %d", url, response.status
                    )
                    return None
        except aiohttp.ClientError as e:
            logger.error("HTTP GET error for %s: %s", url, e)
            return None
        except Exception as e:
            logger.error("Unexpected error in GET request to %s: %s", url, e)
            return None

    async def download_file(
        self, url: str, max_size: int = 10 * 1024 * 1024
    ) -> Optional[bytes]:
        """Download a file with size limit (default 10MB)"""
        if not self.session:
            logger.error("No HTTP session available")
            return None

        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.warning(
                        "Download request to %s returned status %d",
                        url,
                        response.status,
                    )
                    return None

                content_length = response.headers.get("content-length")
                if content_length and int(content_length) > max_size:
                    logger.warning(
                        "File at %s is too large (%s bytes)", url, content_length
                    )
                    return None

                content = bytearray()
                async for chunk in response.content.iter_chunked(8192):
                    content.extend(chunk)
                    if len(content) > max_size:
                        logger.warning(
                            "File at %s exceeded size limit during download", url
                        )
                        return None

                return bytes(content)

        except aiohttp.ClientError as e:
            logger.error("HTTP download error for %s: %s", url, e)
            return None
        except Exception as e:
            logger.error("Unexpected error downloading from %s: %s", url, e)
            return None

    async def check_url_status(self, url: str) -> Optional[int]:
        """Check if a URL is accessible and return status code"""
        if not self.session:
            logger.error("No HTTP session available")
            return None

        try:
            async with self.session.head(url) as response:
                return response.status
        except aiohttp.ClientError as e:
            logger.error("HTTP HEAD error for %s: %s", url, e)
            return None
        except Exception as e:
            logger.error("Unexpected error checking %s: %s", url, e)
            return None


# Utility functions for easy access
async def get_json(bot, url: str, **kwargs) -> Optional[Dict[Any, Any]]:
    """Convenience function to make a GET request and return JSON"""
    helper = HTTPHelper(bot)
    return await helper.get(url, **kwargs)


async def post_json(
    bot, url: str, data: Optional[Dict] = None, json: Optional[Dict] = None, **kwargs
) -> Optional[Dict[Any, Any]]:
    """Convenience function to make a POST request and return JSON"""
    helper = HTTPHelper(bot)
    return await helper.post(url, data=data, json=json, **kwargs)


async def get_text(bot, url: str, **kwargs) -> Optional[str]:
    """Convenience function to make a GET request and return text"""
    helper = HTTPHelper(bot)
    return await helper.get_text(url, **kwargs)


async def download_file(
    bot, url: str, max_size: int = 10 * 1024 * 1024
) -> Optional[bytes]:
    """Convenience function to download a file"""
    helper = HTTPHelper(bot)
    return await helper.download_file(url, max_size)


async def check_url(bot, url: str) -> Optional[int]:
    """Convenience function to check URL status"""
    helper = HTTPHelper(bot)
    return await helper.check_url_status(url)
