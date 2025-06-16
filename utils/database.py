import asyncpg
import asyncio
import logging
import os
import sqlite3
import aiosqlite
import json
from typing import Optional, List, Dict, Any, Union
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class SQLiteManager:
    """SQLite database manager as fallback when PostgreSQL is not available"""

    def __init__(self, bot=None, db_path: str = "data/bot.db"):
        self.bot = bot
        self.db_path = db_path
        self._ensure_directory()

    def _ensure_directory(self):
        """Ensure the database directory exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    async def initialize(self):
        """Initialize SQLite database"""
        try:
            # Create database file and tables
            await self._create_default_tables()
            logger.info("SQLite database initialized at %s", self.db_path)
        except Exception as e:
            logger.error("Failed to initialize SQLite database: %s", e)
            raise

    async def _create_default_tables(self):
        """Create default tables for bot functionality"""
        create_tables_sql = """
        -- Guild settings table
        CREATE TABLE IF NOT EXISTS guild_settings (
            guild_id INTEGER PRIMARY KEY,
            prefix TEXT DEFAULT '!',
            settings TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- User data table
        CREATE TABLE IF NOT EXISTS user_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            guild_id INTEGER,
            data TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, guild_id)
        );
        
        -- Bot logs table
        CREATE TABLE IF NOT EXISTS bot_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER,
            user_id INTEGER,
            action TEXT,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Task status table
        CREATE TABLE IF NOT EXISTS task_status (
            task_name TEXT PRIMARY KEY,
            is_running BOOLEAN DEFAULT 0,
            last_run TIMESTAMP,
            last_error TEXT,
            run_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_user_data_guild_id ON user_data(guild_id);
        CREATE INDEX IF NOT EXISTS idx_user_data_user_id ON user_data(user_id);
        CREATE INDEX IF NOT EXISTS idx_bot_logs_guild_id ON bot_logs(guild_id);
        CREATE INDEX IF NOT EXISTS idx_bot_logs_created_at ON bot_logs(created_at);
        """

        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript(create_tables_sql)
            await db.commit()
            logger.info("SQLite database tables created")

    async def close(self):
        """Close database connections (no persistent connections in SQLite)"""
        logger.info("SQLite database connections closed")

    # Utility methods for common operations
    async def execute(self, query: str, *args) -> str:
        """Execute a query that doesn't return data"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(query, args)
            await db.commit()
            return f"Executed: {cursor.rowcount} rows affected"

    async def fetch(self, query: str, *args) -> List[Dict[str, Any]]:
        """Fetch multiple rows"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, args)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def fetchrow(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """Fetch a single row"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, args)
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def fetchval(self, query: str, *args) -> Any:
        """Fetch a single value"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(query, args)
            row = await cursor.fetchone()
            return row[0] if row else None

    # Guild settings methods
    async def get_guild_settings(self, guild_id: int) -> Dict[str, Any]:
        """Get guild settings"""
        row = await self.fetchrow(
            "SELECT settings FROM guild_settings WHERE guild_id = ?", guild_id
        )
        if row and row["settings"]:
            try:
                return json.loads(row["settings"])
            except json.JSONDecodeError:
                return {}
        return {}

    async def set_guild_setting(self, guild_id: int, key: str, value: Any):
        """Set a specific guild setting"""
        # Get existing settings
        settings = await self.get_guild_settings(guild_id)
        settings[key] = value

        await self.execute(
            """
            INSERT OR REPLACE INTO guild_settings (guild_id, settings, updated_at) 
            VALUES (?, ?, CURRENT_TIMESTAMP)
            """,
            guild_id,
            json.dumps(settings),
        )

    async def get_guild_prefix(self, guild_id: int) -> str:
        """Get guild command prefix"""
        row = await self.fetchrow(
            "SELECT prefix FROM guild_settings WHERE guild_id = ?", guild_id
        )
        return row["prefix"] if row else "!"

    async def set_guild_prefix(self, guild_id: int, prefix: str):
        """Set guild command prefix"""
        await self.execute(
            """
            INSERT OR REPLACE INTO guild_settings (guild_id, prefix, updated_at) 
            VALUES (?, ?, CURRENT_TIMESTAMP)
            """,
            guild_id,
            prefix,
        )

    # User data methods
    async def get_user_data(self, user_id: int, guild_id: int = None) -> Dict[str, Any]:
        """Get user data"""
        if guild_id:
            row = await self.fetchrow(
                "SELECT data FROM user_data WHERE user_id = ? AND guild_id = ?",
                user_id,
                guild_id,
            )
        else:
            row = await self.fetchrow(
                "SELECT data FROM user_data WHERE user_id = ? AND guild_id IS NULL",
                user_id,
            )

        if row and row["data"]:
            try:
                return json.loads(row["data"])
            except json.JSONDecodeError:
                return {}
        return {}

    async def set_user_data(
        self, user_id: int, data: Dict[str, Any], guild_id: int = None
    ):
        """Set user data"""
        # Get existing data and merge
        existing_data = await self.get_user_data(user_id, guild_id)
        existing_data.update(data)

        await self.execute(
            """
            INSERT OR REPLACE INTO user_data (user_id, guild_id, data, updated_at) 
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """,
            user_id,
            guild_id,
            json.dumps(existing_data),
        )

    # Logging methods
    async def log_action(
        self, guild_id: int, user_id: int, action: str, details: Dict[str, Any] = None
    ):
        """Log a bot action"""
        await self.execute(
            "INSERT INTO bot_logs (guild_id, user_id, action, details) VALUES (?, ?, ?, ?)",
            guild_id,
            user_id,
            action,
            json.dumps(details or {}),
        )

    async def get_recent_logs(
        self, guild_id: int, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get recent bot logs for a guild"""
        return await self.fetch(
            """
            SELECT * FROM bot_logs 
            WHERE guild_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
            """,
            guild_id,
            limit,
        )

    # Task status methods
    async def update_task_status(
        self, task_name: str, is_running: bool, error: str = None
    ):
        """Update task status"""
        # Get existing count
        existing = await self.fetchrow(
            "SELECT run_count FROM task_status WHERE task_name = ?", task_name
        )
        count = (existing["run_count"] if existing else 0) + 1

        await self.execute(
            """
            INSERT OR REPLACE INTO task_status 
            (task_name, is_running, last_run, last_error, run_count, updated_at) 
            VALUES (?, ?, CURRENT_TIMESTAMP, ?, ?, CURRENT_TIMESTAMP)
            """,
            task_name,
            int(is_running),
            error,
            count,
        )

    async def get_task_status(self, task_name: str) -> Optional[Dict[str, Any]]:
        """Get task status"""
        return await self.fetchrow(
            "SELECT * FROM task_status WHERE task_name = ?", task_name
        )

    async def get_all_task_statuses(self) -> List[Dict[str, Any]]:
        """Get all task statuses"""
        return await self.fetch("SELECT * FROM task_status ORDER BY task_name")


class DatabaseManager:
    """PostgreSQL database manager with connection pooling for Supabase/pgbouncer"""

    def __init__(self, bot=None):
        self.bot = bot
        self.pool: Optional[asyncpg.Pool] = None
        self._connection_config = {}

    async def initialize(self):
        """Initialize database connection pool"""
        try:
            # Load database configuration from environment
            self._load_config()

            # Create connection pool
            self.pool = await asyncpg.create_pool(
                **self._connection_config,
                min_size=2,  # Minimum connections in pool
                max_size=10,  # Maximum connections in pool
                command_timeout=30,  # Command timeout in seconds
                server_settings={
                    "jit": "off",  # Disable JIT for better compatibility with pgbouncer
                    "application_name": "discord_bot",
                },
            )

            # Test connection
            async with self.pool.acquire() as conn:
                version = await conn.fetchval("SELECT version()")
                logger.info("Database connected successfully")
                logger.info("PostgreSQL version: %s", version.split()[1])

            # Create default tables if they don't exist
            await self._create_default_tables()

        except Exception as e:
            logger.error("Failed to initialize database: %s", e)
            raise

    def _load_config(self):
        """Load database configuration from environment variables"""
        # Required environment variables
        host = os.getenv("DATABASE_HOST")
        port = int(os.getenv("DATABASE_PORT", 5432))
        database = os.getenv("DATABASE_NAME")
        user = os.getenv("DATABASE_USER")
        password = os.getenv("DATABASE_PASSWORD")

        # Optional SSL configuration (recommended for Supabase)
        ssl = os.getenv("DATABASE_SSL", "require")

        if not all([host, database, user, password]):
            raise ValueError(
                "Missing required database environment variables. Please check DATABASE_HOST, DATABASE_NAME, DATABASE_USER, and DATABASE_PASSWORD"
            )

        self._connection_config = {
            "host": host,
            "port": port,
            "database": database,
            "user": user,
            "password": password,
            "ssl": ssl,
        }

        logger.info(
            "Database configuration loaded for %s@%s:%d/%s", user, host, port, database
        )

    async def _create_default_tables(self):
        """Create default tables for bot functionality"""
        create_tables_sql = """
        -- Guild settings table
        CREATE TABLE IF NOT EXISTS guild_settings (
            guild_id BIGINT PRIMARY KEY,
            prefix VARCHAR(10) DEFAULT '!',
            settings JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- User data table
        CREATE TABLE IF NOT EXISTS user_data (
            user_id BIGINT PRIMARY KEY,
            guild_id BIGINT,
            data JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Bot logs table
        CREATE TABLE IF NOT EXISTS bot_logs (
            id SERIAL PRIMARY KEY,
            guild_id BIGINT,
            user_id BIGINT,
            action VARCHAR(100),
            details JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Task status table
        CREATE TABLE IF NOT EXISTS task_status (
            task_name VARCHAR(100) PRIMARY KEY,
            is_running BOOLEAN DEFAULT FALSE,
            last_run TIMESTAMP WITH TIME ZONE,
            last_error TEXT,
            run_count INTEGER DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_user_data_guild_id ON user_data(guild_id);
        CREATE INDEX IF NOT EXISTS idx_bot_logs_guild_id ON bot_logs(guild_id);
        CREATE INDEX IF NOT EXISTS idx_bot_logs_created_at ON bot_logs(created_at);
        """

        async with self.pool.acquire() as conn:
            await conn.execute(create_tables_sql)
            logger.info("Default database tables ensured")

    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")

    @asynccontextmanager
    async def acquire(self):
        """Context manager for acquiring database connections"""
        if not self.pool:
            raise RuntimeError("Database not initialized")

        async with self.pool.acquire() as conn:
            yield conn

    # Utility methods for common operations
    async def execute(self, query: str, *args) -> str:
        """Execute a query that doesn't return data"""
        async with self.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args) -> List[asyncpg.Record]:
        """Fetch multiple rows"""
        async with self.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args) -> Optional[asyncpg.Record]:
        """Fetch a single row"""
        async with self.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetchval(self, query: str, *args) -> Any:
        """Fetch a single value"""
        async with self.acquire() as conn:
            return await conn.fetchval(query, *args)

    # Guild settings methods
    async def get_guild_settings(self, guild_id: int) -> Dict[str, Any]:
        """Get guild settings"""
        row = await self.fetchrow(
            "SELECT settings FROM guild_settings WHERE guild_id = $1", guild_id
        )
        return row["settings"] if row else {}

    async def set_guild_setting(self, guild_id: int, key: str, value: Any):
        """Set a specific guild setting"""
        await self.execute(
            """
            INSERT INTO guild_settings (guild_id, settings) 
            VALUES ($1, $2) 
            ON CONFLICT (guild_id) 
            DO UPDATE SET 
                settings = guild_settings.settings || $2,
                updated_at = NOW()
        """,
            guild_id,
            {key: value},
        )

    async def get_guild_prefix(self, guild_id: int) -> str:
        """Get guild command prefix"""
        row = await self.fetchrow(
            "SELECT prefix FROM guild_settings WHERE guild_id = $1", guild_id
        )
        return row["prefix"] if row else "!"

    async def set_guild_prefix(self, guild_id: int, prefix: str):
        """Set guild command prefix"""
        await self.execute(
            """
            INSERT INTO guild_settings (guild_id, prefix) 
            VALUES ($1, $2) 
            ON CONFLICT (guild_id) 
            DO UPDATE SET 
                prefix = $2,
                updated_at = NOW()
        """,
            guild_id,
            prefix,
        )

    # User data methods
    async def get_user_data(self, user_id: int, guild_id: int = None) -> Dict[str, Any]:
        """Get user data"""
        if guild_id:
            row = await self.fetchrow(
                "SELECT data FROM user_data WHERE user_id = $1 AND guild_id = $2",
                user_id,
                guild_id,
            )
        else:
            row = await self.fetchrow(
                "SELECT data FROM user_data WHERE user_id = $1", user_id
            )
        return row["data"] if row else {}

    async def set_user_data(
        self, user_id: int, data: Dict[str, Any], guild_id: int = None
    ):
        """Set user data"""
        await self.execute(
            """
            INSERT INTO user_data (user_id, guild_id, data) 
            VALUES ($1, $2, $3) 
            ON CONFLICT (user_id) 
            DO UPDATE SET 
                data = user_data.data || $3,
                updated_at = NOW()
        """,
            user_id,
            guild_id,
            data,
        )

    # Logging methods
    async def log_action(
        self, guild_id: int, user_id: int, action: str, details: Dict[str, Any] = None
    ):
        """Log a bot action"""
        await self.execute(
            "INSERT INTO bot_logs (guild_id, user_id, action, details) VALUES ($1, $2, $3, $4)",
            guild_id,
            user_id,
            action,
            details or {},
        )

    async def get_recent_logs(
        self, guild_id: int, limit: int = 100
    ) -> List[asyncpg.Record]:
        """Get recent bot logs for a guild"""
        return await self.fetch(
            """
            SELECT * FROM bot_logs 
            WHERE guild_id = $1 
            ORDER BY created_at DESC 
            LIMIT $2
        """,
            guild_id,
            limit,
        )

    # Task status methods
    async def update_task_status(
        self, task_name: str, is_running: bool, error: str = None
    ):
        """Update task status"""
        await self.execute(
            """
            INSERT INTO task_status (task_name, is_running, last_run, last_error, run_count) 
            VALUES ($1, $2, NOW(), $3, 1) 
            ON CONFLICT (task_name) 
            DO UPDATE SET 
                is_running = $2,
                last_run = NOW(),
                last_error = $3,
                run_count = task_status.run_count + 1,
                updated_at = NOW()
        """,
            task_name,
            is_running,
            error,
        )

    async def get_task_status(self, task_name: str) -> Optional[asyncpg.Record]:
        """Get task status"""
        return await self.fetchrow(
            "SELECT * FROM task_status WHERE task_name = $1", task_name
        )

    async def get_all_task_statuses(self) -> List[asyncpg.Record]:
        """Get all task statuses"""
        return await self.fetch("SELECT * FROM task_status ORDER BY task_name")


# Convenience functions for easy access
def get_db(bot) -> Union[DatabaseManager, SQLiteManager]:
    """Get the database manager from bot instance (synchronous)"""
    if not hasattr(bot, "db") or not bot.db:
        raise RuntimeError("Database not initialized")
    return bot.db


async def execute_query(bot, query: str, *args) -> str:
    """Execute a database query"""
    db = get_db(bot)
    return await db.execute(query, *args)


async def fetch_query(
    bot, query: str, *args
) -> List[Union[asyncpg.Record, Dict[str, Any]]]:
    """Fetch multiple rows from database"""
    db = get_db(bot)
    return await db.fetch(query, *args)


async def fetchrow_query(
    bot, query: str, *args
) -> Optional[Union[asyncpg.Record, Dict[str, Any]]]:
    """Fetch a single row from database"""
    db = get_db(bot)
    return await db.fetchrow(query, *args)


async def fetchval_query(bot, query: str, *args) -> Any:
    """Fetch a single value from database"""
    db = get_db(bot)
    return await db.fetchval(query, *args)
