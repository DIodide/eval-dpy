import os
import logging
import re
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger(__name__)


class EnvironmentValidationError(Exception):
    """Raised when environment validation fails"""

    pass


class EnvironmentValidator:
    """Environment variables validator for Discord bot"""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """
        Validate all environment variables
        Returns: (is_valid, errors, warnings)
        """
        self.errors.clear()
        self.warnings.clear()

        # Validate required variables
        self._validate_discord_token()

        # Validate optional database variables
        self._validate_database_config()

        # Validate other optional variables
        self._validate_optional_vars()

        return len(self.errors) == 0, self.errors.copy(), self.warnings.copy()

    def _validate_discord_token(self):
        """Validate Discord bot token"""
        token = os.getenv("DISCORD_TOKEN")

        if not token:
            self.errors.append(
                "DISCORD_TOKEN is required! Please add it to your .env file:\n"
                "  DISCORD_TOKEN=your_bot_token_here"
            )
            return

        # Basic Discord token format validation
        # Discord tokens typically follow patterns like:
        # - Bot tokens: start with bot id (numbers), then a dot, then base64-like string
        # - Should be at least 50 characters long
        if len(token) < 50:
            self.warnings.append(
                "DISCORD_TOKEN appears to be too short. Discord tokens are typically 59+ characters."
            )

        # Check if it looks like a valid token format
        # Discord bot tokens usually have this pattern: numbers.base64.base64
        if not re.match(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$", token):
            self.warnings.append(
                "DISCORD_TOKEN format appears invalid. Expected format: numbers.string.string"
            )

        # Check for common mistakes
        if token.startswith('"') and token.endswith('"'):
            self.errors.append(
                "DISCORD_TOKEN should not be wrapped in quotes in the .env file"
            )

        if token.lower().startswith("bot "):
            self.errors.append(
                "DISCORD_TOKEN should not include 'Bot ' prefix in the .env file"
            )

    def _validate_database_config(self):
        """Validate database configuration (optional but if one is set, others should be too)"""
        db_vars = {
            "DATABASE_HOST": os.getenv("DATABASE_HOST"),
            "DATABASE_PORT": os.getenv("DATABASE_PORT"),
            "DATABASE_NAME": os.getenv("DATABASE_NAME"),
            "DATABASE_USER": os.getenv("DATABASE_USER"),
            "DATABASE_PASSWORD": os.getenv("DATABASE_PASSWORD"),
        }

        # Check if any database variables are set
        set_vars = {k: v for k, v in db_vars.items() if v is not None}

        if not set_vars:
            # No database config - that's fine, database is optional
            self.warnings.append(
                "No database configuration found. Database features will be disabled.\n"
                "  To enable database features, add these variables to your .env file:\n"
                "  DATABASE_HOST=your_host\n"
                "  DATABASE_PORT=5432\n"
                "  DATABASE_NAME=your_database\n"
                "  DATABASE_USER=your_user\n"
                "  DATABASE_PASSWORD=your_password"
            )
            return

        # If some are set, all required ones should be set
        required_db_vars = [
            "DATABASE_HOST",
            "DATABASE_NAME",
            "DATABASE_USER",
            "DATABASE_PASSWORD",
        ]
        missing_vars = [var for var in required_db_vars if not db_vars[var]]

        if missing_vars:
            self.errors.append(
                f"Incomplete database configuration. Missing: {', '.join(missing_vars)}\n"
                "  Either remove all database variables or provide all required ones."
            )

        # Validate DATABASE_PORT if provided
        port = db_vars["DATABASE_PORT"]
        if port:
            try:
                port_num = int(port)
                if not (1 <= port_num <= 65535):
                    self.errors.append(
                        f"DATABASE_PORT must be between 1 and 65535, got: {port}"
                    )
            except ValueError:
                self.errors.append(f"DATABASE_PORT must be a number, got: {port}")

        # Validate DATABASE_SSL if provided
        ssl = os.getenv("DATABASE_SSL")
        if ssl:
            valid_ssl_modes = [
                "disable",
                "allow",
                "prefer",
                "require",
                "verify-ca",
                "verify-full",
            ]
            if ssl not in valid_ssl_modes:
                self.warnings.append(
                    f"DATABASE_SSL value '{ssl}' is not a standard PostgreSQL SSL mode.\n"
                    f"  Valid values: {', '.join(valid_ssl_modes)}"
                )

    def _validate_optional_vars(self):
        """Validate other optional environment variables"""
        # Validate LOG_LEVEL if provided
        log_level = os.getenv("LOG_LEVEL")
        if log_level:
            valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            if log_level.upper() not in valid_levels:
                self.warnings.append(
                    f"LOG_LEVEL '{log_level}' is not a standard logging level.\n"
                    f"  Valid values: {', '.join(valid_levels)}"
                )

        # Check for common .env file mistakes
        self._check_common_mistakes()

    def _check_common_mistakes(self):
        """Check for common .env file formatting mistakes"""
        env_file_path = ".env"
        if not os.path.exists(env_file_path):
            self.warnings.append(
                ".env file not found. Make sure it exists in the same directory as main.py"
            )
            return

        try:
            with open(env_file_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.splitlines()
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                # Check for spaces around = sign
                if "=" in line and (" = " in line or "= " in line or " =" in line):
                    self.warnings.append(
                        f".env file line {i}: Avoid spaces around '=' sign. "
                        f"Use 'KEY=value' not 'KEY = value'"
                    )

                # Check for missing values
                if line.endswith("="):
                    var_name = line[:-1]
                    self.warnings.append(
                        f".env file line {i}: Variable '{var_name}' has no value"
                    )

        except Exception as e:
            self.warnings.append(f"Could not read .env file: {e}")

    def print_validation_results(self, errors: List[str], warnings: List[str]):
        """Print validation results in a user-friendly format"""
        if errors:
            print("\n❌ Environment Validation Errors:")
            print("=" * 50)
            for i, error in enumerate(errors, 1):
                print(f"{i}. {error}")
                print()

        if warnings:
            print("\n⚠️  Environment Validation Warnings:")
            print("=" * 50)
            for i, warning in enumerate(warnings, 1):
                print(f"{i}. {warning}")
                print()

        if not errors and not warnings:
            print("✅ Environment validation passed!")


def validate_environment() -> bool:
    """
    Validate environment variables before bot startup
    Returns True if validation passes, False if there are errors
    """
    validator = EnvironmentValidator()
    is_valid, errors, warnings = validator.validate_all()

    # Always print results
    validator.print_validation_results(errors, warnings)

    if not is_valid:
        print("\n🚫 Bot startup cancelled due to environment validation errors.")
        print("Please fix the errors above and try again.")
        return False

    if warnings:
        print("\n⚠️  Bot will start despite warnings, but you may want to address them.")

    return True


def validate_environment_or_exit():
    """
    Validate environment variables and exit if validation fails
    This is a convenience function for use in main()
    """
    if not validate_environment():
        exit(1)
