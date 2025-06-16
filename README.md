# Discord Bot Boilerplate

A comprehensive Discord bot boilerplate built with discord.py featuring modular cog architecture, hot reloading, essential moderation tools, background tasks, shared HTTP session management, and PostgreSQL database integration.

## Features

- 🔧 **Modular Architecture**: Organized cog system for easy feature management
- 🔄 **Hot Reloading**: Reload cogs without restarting the bot
- 🛡️ **Moderation Tools**: Comprehensive moderation commands (kick, ban, mute, purge, etc.)
- ⚡ **Admin Commands**: Bot management and debugging tools
- 🌟 **Aura System**: Complete gaming system with gambling, economy, leaderboards, and social features
- 🔐 **Permission System**: Role-based command access control
- 📝 **Logging**: Comprehensive logging for debugging and monitoring
- 🎨 **Rich Embeds**: Beautiful embedded messages for better UX
- 🎛️ **Interactive Menus**: Paginated embeds, dropdowns, and confirmation dialogs
- ❓ **Advanced Help System**: Interactive help menus with categorized commands
- 🛡️ **Global Error Handler**: Comprehensive error handling with user-friendly messages
- ⚡ **Hybrid Commands**: All commands work as both prefix commands (!) and slash commands (/)
- ⏰ **Background Tasks**: Looping tasks with start/stop control
- 🌐 **HTTP Session**: Shared aiohttp session for API requests
- 🔄 **Bot Lifecycle**: Proper startup and shutdown management
- ✅ **Environment Validation**: Automatic validation of configuration before startup
- 🚀 **Easy Setup**: Automated start scripts for all platforms
- 🗄️ **Database Integration**: PostgreSQL/Supabase support with connection pooling

## Project Structure

```
discord-bot/
├── main.py              # Bot entry point with lifecycle management
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (add your token here)
├── start.sh             # Unix/Linux/macOS start script
├── start.bat            # Windows start script
├── cogs/               # Bot modules
│   ├── __init__.py
│   ├── admin.py        # Admin commands (reload, load, unload, etc.)
│   ├── moderation.py   # Moderation commands (kick, ban, mute, etc.)
│   ├── aura.py         # Aura system (gambling, economy, leaderboards)
│   ├── tasks.py        # Background tasks and task management
│   └── database_demo.py # Database usage examples
├── assets/             # Images and media files
│   └── opticcat.txt    # Placeholder for OpticCat image
└── utils/              # Utility functions
    ├── __init__.py
    ├── checks.py       # Permission checks and helpers
    ├── http_utils.py   # HTTP request utilities
    └── database.py     # Database manager and utilities
```

## Quick Start

### 🚀 Easy Setup (Recommended)

The fastest way to get started is using the automated start scripts:

#### **Unix/Linux/macOS:**

```bash
chmod +x start.sh
./start.sh
```

#### **Windows:**

```cmd
start.bat
```

These scripts will automatically:

- ✅ Check for Python installation
- ✅ Create virtual environment if needed
- ✅ Install/update all dependencies
- ✅ Validate configuration files
- ✅ Start the bot

**Just make sure you have:**

1. Python 3.8+ installed
2. Created a `.env` file with your Discord token (and optionally database credentials)

### Manual Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- A Discord bot token
- PostgreSQL database (optional - for Supabase/database features)

### 2. Installation

1. **Clone or download** this project to your local machine

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your environment variables**:
   Create a `.env` file in the root directory with the following:

   ```env
   # Required
   DISCORD_TOKEN=your_bot_token_here

   # Optional - Database Configuration (for Supabase/PostgreSQL)
   DATABASE_HOST=your_database_host
   DATABASE_PORT=5432
   DATABASE_NAME=your_database_name
   DATABASE_USER=your_database_user
   DATABASE_PASSWORD=your_database_password
   DATABASE_SSL=require
   ```

4. **Environment Validation**:
   The bot automatically validates your environment configuration before starting. It will check for:

   - **Required variables**: `DISCORD_TOKEN` presence and basic format validation
   - **Database config**: If any database variables are set, all required ones must be present
   - **Format validation**: Port numbers, SSL modes, and other format-specific checks
   - **Common mistakes**: Quotes around tokens, missing .env file, formatting issues

   If validation fails, the bot will display helpful error messages and exit before attempting to start.

### 3. Getting a Discord Bot Token

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section in the sidebar
4. Click "Add Bot"
5. Under "Token", click "Copy" to copy your bot token
6. Add this token to your `.env` file as shown above

### 4. Database Setup (Optional)

#### Using Supabase (Recommended)

1. **Create a Supabase project** at [supabase.com](https://supabase.com)
2. **Get your database credentials**:
   - Go to Settings → Database
   - Copy the connection string details
3. **Add to your `.env` file**:
   ```env
   DATABASE_HOST=db.your-project-ref.supabase.co
   DATABASE_PORT=5432
   DATABASE_NAME=postgres
   DATABASE_USER=postgres
   DATABASE_PASSWORD=your_password
   DATABASE_SSL=require
   ```

#### Using Local PostgreSQL

1. **Install PostgreSQL** on your system
2. **Create a database** for your bot
3. **Add credentials to `.env`**:
   ```env
   DATABASE_HOST=localhost
   DATABASE_PORT=5432
   DATABASE_NAME=discord_bot
   DATABASE_USER=your_user
   DATABASE_PASSWORD=your_password
   DATABASE_SSL=prefer
   ```

**Note**: The bot will work without a database, but database-related commands will be unavailable.

### 5. Bot Permissions

When inviting your bot to a server, make sure it has these permissions:

- Send Messages
- Embed Links
- Read Message History
- Manage Messages (for purge command)
- Kick Members
- Ban Members
- Moderate Members (for timeout/mute)
- Manage Channels (for slowmode)

### 6. Running the Bot

#### Using Start Scripts (Recommended):

```bash
# Unix/Linux/macOS
./start.sh

# Windows
start.bat
```

#### Manual Start:

```bash
python main.py
```

## Commands

**Note**: All commands work as both traditional prefix commands (e.g., `!help`) and modern slash commands (e.g., `/help`). Slash commands provide better autocomplete and parameter validation.

### Admin Commands (Administrator only)

- `!reload <cog_name>` / `/reload cog:<cog_name>` - Reload a specific cog
- `!reload all` / `/reload all` - Reload all cogs
- `!load <cog_name>` / `/load cog_name:<cog_name>` - Load a cog
- `!unload <cog_name>` / `/unload cog_name:<cog_name>` - Unload a cog
- `!cogs` / `/cogs` - List all loaded cogs
- `!sync` / `/sync` - Sync slash commands
- `!shutdown` / `/shutdown` - Shutdown the bot
- `!leaderboard` / `/leaderboard` - Demo paginated leaderboard (showcases menu system)

### Help Commands (Everyone)

- `!help` / `/help` - Interactive help menu with dropdown categories
- `!help <command>` / `/help command_or_category:<command>` - Detailed help for a specific command
- `!help <category>` / `/help command_or_category:<category>` - Show commands in a category (e.g., `!help mod`)
- `!help commands` / `/help command_or_category:commands` - View all commands in paginated format
- `!about` / `/about` - Detailed bot information and statistics (aliases: `!info`, `!botinfo`)

### Moderation Commands (Administrator only)

- `!kick <member> [reason]` / `/kick member:<member> reason:[reason]` - Kick a member
- `!ban <member> [reason]` / `/ban member:<member> reason:[reason]` - Ban a member
- `!unban <user> [reason]` / `/unban user:<user> reason:[reason]` - Unban a user
- `!mute <member> <minutes> [reason]` / `/mute member:<member> duration:<minutes> reason:[reason]` - Timeout a member
- `!unmute <member> [reason]` / `/unmute member:<member> reason:[reason]` - Remove timeout from a member
- `!purge <amount>` / `/purge amount:<amount>` - Delete messages (max 100)
- `!slowmode <seconds>` / `/slowmode seconds:<seconds>` - Set channel slowmode (0-21600 seconds)
- `!warn <member> [reason]` / `/warn member:<member> reason:[reason]` - Warn a member

### Task Management Commands (Administrator only)

- `!task` / `/task` - List all available tasks and their status
- `!task start <task_name>` / `/task start task_name:<task_name>` - Start a specific background task
- `!task stop <task_name>` / `/task stop task_name:<task_name>` - Stop a running background task
- `!task restart <task_name>` / `/task restart task_name:<task_name>` - Restart a background task
- `!task stopall` / `/task stopall` - Stop all running background tasks

#### Available Tasks

- **example_task_1**: Simple periodic task (runs every 5 minutes)
- **example_task_2**: Status updater task (runs every 10 minutes)
- **api_monitor_task**: API monitoring task (runs every hour)

### Database Commands (Administrator only)

**Note**: Only available when database is configured

- `!db` / `/db` - Show database connection status
- `!db prefix [new_prefix]` / `/db prefix new_prefix:[prefix]` - Get or set guild command prefix
- `!db userdata <member> [key] [value]` / `/db userdata member:<member> key:[key] value:[value]` - Manage user data
- `!db logs [limit]` / `/db logs limit:[limit]` - View recent bot action logs
- `!db tasks` / `/db tasks` - View task status from database
- `!db query <SELECT_query>` / `/db query query:<query>` - Execute read-only SQL queries

## Features in Detail

### Database Integration

The bot includes a robust PostgreSQL database system with:

- **Connection Pooling**: Efficient connection management with asyncpg
- **Supabase Compatible**: Works seamlessly with Supabase and pgbouncer
- **Auto-Migration**: Automatically creates required tables on startup
- **Built-in Tables**: Guild settings, user data, bot logs, task status
- **Easy Integration**: Simple methods for common database operations

#### Database Tables

1. **guild_settings**: Per-guild configuration and custom prefixes
2. **user_data**: User-specific data storage with JSONB support
3. **bot_logs**: Action logging for moderation and bot events
4. **task_status**: Background task monitoring and error tracking

#### Using Database in Your Code

```python
# In a cog or command
async def my_command(self, ctx):
    # Check if database is available
    if not self.bot.db:
        await ctx.send("Database not available!")
        return

    # Get user data
    user_data = await self.bot.db.get_user_data(ctx.author.id, ctx.guild.id)

    # Set user data
    await self.bot.db.set_user_data(ctx.author.id, {"points": 100}, ctx.guild.id)

    # Log an action
    await self.bot.db.log_action(
        guild_id=ctx.guild.id,
        user_id=ctx.author.id,
        action="command_used",
        details={"command": "my_command"}
    )

    # Execute custom query
    result = await self.bot.db.fetch("SELECT * FROM user_data WHERE guild_id = $1", ctx.guild.id)
```

### Background Tasks System

The bot includes a comprehensive background tasks system with:

- **Looping Tasks**: Use discord.py's `@tasks.loop()` decorator
- **Task Management**: Start, stop, restart, and monitor tasks
- **Error Handling**: Automatic error recovery and logging
- **Bot Integration**: Tasks wait for bot to be ready before starting
- **Database Logging**: Task status tracked in database

#### Creating New Tasks

```python
@tasks.loop(minutes=30)
async def my_custom_task(self):
    """Your custom task that runs every 30 minutes"""
    try:
        # Your task logic here
        logger.info("Custom task is running!")

        # Update task status in database
        if self.bot.db:
            await self.bot.db.update_task_status("my_custom_task", True)

    except Exception as e:
        logger.error("Error in custom task: %s", e)
        if self.bot.db:
            await self.bot.db.update_task_status("my_custom_task", False, str(e))

@my_custom_task.before_loop
async def before_my_custom_task(self):
    await self.bot.wait_until_ready()
```

### Interactive Menu System

The bot includes a powerful menu system for creating beautiful, interactive Discord interfaces:

#### **Menu Types Available:**

1. **Paginated Embeds**: Navigate through multiple pages with buttons
2. **Select Menus**: Dropdown menus for category selection
3. **Confirmation Dialogs**: Yes/No prompts for important actions
4. **Leaderboards**: Automatically formatted, paginated leaderboards

#### **Using the Menu System:**

```python
from utils.menus import (
    EmbedBuilder,
    LeaderboardBuilder,
    send_paginated_embed,
    send_confirmation
)

# Create beautiful embeds
embed = EmbedBuilder.create_success_embed(
    title="Success",
    description="Operation completed successfully!"
)

# Create paginated leaderboard
leaderboard_data = [
    {"name": "Player1", "score": 1000, "emoji": "👑"},
    {"name": "Player2", "score": 850, "emoji": "⚔️"},
    # ... more entries
]

embeds = LeaderboardBuilder.create_leaderboard(
    title="🏆 Top Players",
    entries=leaderboard_data,
    key_field="name",
    value_field="score",
    emoji_field="emoji"
)

# Send with navigation buttons
await send_paginated_embed(ctx, embeds)

# Confirmation dialog
result = await send_confirmation(ctx, embed)
if result:
    await ctx.send("Confirmed!")
```

#### **Menu Features:**

- ✅ **User-specific interactions** - Only the command user can interact
- ✅ **Automatic timeout** - Menus disable after inactivity
- ✅ **Permission checks** - Built-in interaction validation
- ✅ **Error handling** - Graceful handling of Discord API errors
- ✅ **Customizable styling** - Colors, emojis, and formatting options

### Error Handling System

The bot includes a comprehensive global error handler that:

#### **Features:**

- 🔍 **Intelligent Error Detection** - Identifies specific error types
- 💬 **User-Friendly Messages** - Clear explanations instead of technical errors
- 📝 **Comprehensive Logging** - Detailed error logs for debugging
- 🔄 **Graceful Recovery** - Bot continues running after most errors
- ⚡ **Fast Response** - Quick error message delivery

#### **Error Types Handled:**

- **Command Errors**: Missing arguments, invalid permissions, cooldowns
- **Discord API Errors**: Rate limits, permission issues, not found errors
- **Bot Errors**: Extension loading issues, database connection problems
- **User Errors**: Invalid input, missing permissions, command not found

#### **KeyboardInterrupt Protection:**

The error handler specifically allows `KeyboardInterrupt` to pass through, ensuring you can always stop the bot with Ctrl+C while catching all other errors gracefully.

### Global HTTP Session

The bot includes a shared aiohttp session for efficient HTTP requests:

```python
# In any cog, access the global session
async with self.bot.session.get('https://api.example.com') as response:
    data = await response.json()

# Or use the utility functions
from utils.http_utils import get_json
data = await get_json(self.bot, 'https://api.example.com')
```

#### HTTP Utilities Available

- `get_json(bot, url)` - GET request returning JSON
- `post_json(bot, url, data)` - POST request returning JSON
- `get_text(bot, url)` - GET request returning text
- `download_file(bot, url)` - Download file with size limits
- `check_url(bot, url)` - Check URL status code

### Bot Lifecycle Management

The bot properly handles startup and shutdown:

- **Startup Hook**: Initialize database, HTTP session, load cogs
- **Ready Event**: Set status, start tasks
- **Shutdown Hook**: Clean up resources, close connections

## Configuration

### Changing the Command Prefix

Edit `main.py` and change the `command_prefix` parameter:

```python
super().__init__(
    command_prefix='your_prefix_here',  # Change this
    intents=intents,
    help_command=None
)
```

Or use the database to set per-guild prefixes:

```bash
!db prefix $    # Set prefix to $
```

### Adding More Cogs

1. Create a new Python file in the `cogs/` directory
2. Follow the cog template structure
3. Add the cog to the `cogs_to_load` list in `main.py`

### Example Cog Template

```python
import discord
from discord.ext import commands
from utils.checks import is_admin

class YourCogName(commands.Cog):
    """Description of your cog"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='your_command')
    async def your_command(self, ctx):
        """Command description"""
        await ctx.send("Hello World!")

        # Log the action if database is available
        if self.bot.db:
            await self.bot.db.log_action(
                guild_id=ctx.guild.id,
                user_id=ctx.author.id,
                action="your_command_used"
            )

async def setup(bot):
    await bot.add_cog(YourCogName(bot))
```

### Aura System Commands

The bot includes a comprehensive aura gaming system with economy features:

- `!aura` / `/aura` - Check your aura amount and statistics
- `!aura check @user` - Check another user's aura
- `!aura slots [bet]` - Play slot machine with EVAL characters (🔥⚡💎🌟👑🎯🚀💀🌙☄️)
- `!aura flip [bet] [heads/tails]` - Coin flip gambling
- `!aura roll [bet] [target]` - Dice roll with multipliers
- `!aura daily` - Claim daily aura bonus with cosmic events
- `!aura donate @user [amount]` - Give aura to another user
- `!aura drain @user` - Risky command to steal aura (can backfire!)
- `!aura leaderboard` - View server aura rankings
- `!aura titles` - See all available aura titles and requirements
- `!aura shop` - Browse purchasable items (shields, multipliers, bombs)
- `!aura shop [item]` - Purchase a shop item
- `!erika` - Special tribute command for Erika
- `!opticcat` - Hidden mega aura command (not in help)

**Features:**

- 🎰 Multiple gambling games with different odds and strategies
- 💰 Economy system with items and effects
- 🏆 Progressive title system from "Aura Seeker" to "Aura God"
- 🛡️ Protection items (shields) and enhancement items (multipliers)
- 📊 Detailed statistics tracking and leaderboards
- 🎨 Beautiful color-coded embeds based on aura level
- 🔒 Cooldown system to prevent spam
- 💾 Full database persistence

For detailed documentation, see [AURA_COMMANDS.md](AURA_COMMANDS.md)

## Troubleshooting

### Common Issues

1. **Import Errors**: Use the start scripts or install dependencies: `pip install -r requirements.txt`
2. **Token Issues**: Ensure your token is correctly placed in `.env` file as `DISCORD_TOKEN=your_token_here`
3. **Environment Validation Errors**: The bot will display specific validation errors before startup - follow the error messages to fix configuration issues
4. **Database Connection**: Check your database credentials in `.env` file
5. **Permission Errors**: Make sure the bot has the necessary permissions in your Discord server
6. **Cog Loading Errors**: Check the console for specific error messages when cogs fail to load
7. **Environment Variable Issues**: Make sure `.env` file is in the same directory as `main.py`
8. **Task Errors**: Check console logs for task-specific error messages
9. **Python Version**: Ensure you have Python 3.8 or higher installed

### Database Troubleshooting

- **Connection Timeout**: Check if your database host and port are correct
- **SSL Errors**: Try changing `DATABASE_SSL` to `disable` for local databases
- **Permission Denied**: Verify your database user has the required permissions
- **Table Errors**: The bot automatically creates tables, but check database logs for issues

### Using Start Scripts

The automated start scripts will check for most common issues and provide helpful error messages:

- ✅ **Python Installation**: Verifies Python 3 is installed
- ✅ **Environment File**: Checks for `.env` file existence
- ✅ **Dependencies**: Automatically installs/updates requirements
- ✅ **File Structure**: Validates required files exist

### Getting Help

- Check the console output for error messages
- Ensure all dependencies are installed
- Verify your bot token is valid and properly set in `.env` file
- Make sure the bot has proper permissions in your server
- Review the logs for HTTP session or task-related issues
- For database issues, check the PostgreSQL/Supabase logs

## Development

### Adding Utility Functions

Add new utility functions to `utils/checks.py` or create new files in the `utils/` directory.

### Custom Permission Checks

Create custom permission decorators in `utils/checks.py`:

```python
def has_role(role_name):
    def predicate(ctx):
        return any(role.name == role_name for role in ctx.author.roles)
    return commands.check(predicate)
```

### Working with HTTP Requests

Use the shared session for efficient HTTP requests:

```python
from utils.http_utils import HTTPHelper

# In a cog
helper = HTTPHelper(self.bot)
data = await helper.get('https://api.example.com/data')
```

### Creating Background Tasks

Add new tasks to the `Tasks` cog following the pattern:

```python
@tasks.loop(hours=6)
async def cleanup_task(self):
    """Cleanup task that runs every 6 hours"""
    # Your cleanup logic here

    # Update task status in database
    if self.bot.db:
        await self.bot.db.update_task_status("cleanup_task", True)
```

### Database Schema Extensions

To add new tables or modify existing ones:

1. **Create migration scripts** or modify `_create_default_tables()` in `utils/database.py`
2. **Add helper methods** to `DatabaseManager` class for new operations
3. **Test thoroughly** with both local and Supabase databases

## Dependencies

- **discord.py**: Discord API wrapper
- **python-dotenv**: Environment variable management
- **aiohttp**: Async HTTP client/server
- **asyncpg**: PostgreSQL async driver

## License

This project is open source and available under the MIT License.
