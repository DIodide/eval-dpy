# Utils package for Discord bot
# This package contains utility functions and helpers

from .checks import is_admin, is_mod_or_admin, can_target_member, format_time
from .http_utils import (
    HTTPHelper,
    get_json,
    post_json,
    get_text,
    download_file,
    check_url,
)
from .database import (
    DatabaseManager,
    get_db,
    execute_query,
    fetch_query,
    fetchrow_query,
    fetchval_query,
)
from .env_validator import (
    EnvironmentValidator,
    validate_environment,
    validate_environment_or_exit,
    EnvironmentValidationError,
)

__all__ = [
    # Permission checks
    "is_admin",
    "is_mod_or_admin",
    "can_target_member",
    "format_time",
    # HTTP utilities
    "HTTPHelper",
    "get_json",
    "post_json",
    "get_text",
    "download_file",
    "check_url",
    # Database utilities
    "DatabaseManager",
    "get_db",
    "execute_query",
    "fetch_query",
    "fetchrow_query",
    "fetchval_query",
    # Environment validation
    "EnvironmentValidator",
    "validate_environment",
    "validate_environment_or_exit",
    "EnvironmentValidationError",
]
