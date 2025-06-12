import discord
from discord.ext import commands, tasks
from datetime import datetime
import logging
from utils.checks import is_admin
from utils.database import get_db

logger = logging.getLogger(__name__)


class DatabaseDemo(commands.Cog):
    """Demo cog showing database integration with commands and tasks"""

    def __init__(self, bot):
        self.bot = bot

        # Start the database demo task
        # self.database_demo_task.start()  # Uncomment to auto-start

    async def cog_unload(self):
        """Clean up when cog is unloaded"""
        if self.database_demo_task.is_running():
            self.database_demo_task.cancel()

    # Database Demo Task
    @tasks.loop(minutes=30)
    async def database_demo_task(self):
        """Demo task that interacts with the database"""
        try:
            if not self.bot.db:
                logger.warning("Database not available for demo task")
                return

            # Update task status in database
            await self.bot.db.update_task_status("database_demo_task", True)

            # Log the task run
            await self.bot.db.log_action(
                guild_id=0,  # 0 for bot-level actions
                user_id=self.bot.user.id,
                action="database_demo_task_run",
                details={"timestamp": datetime.utcnow().isoformat()},
            )

            logger.info("Database demo task completed successfully")

        except Exception as e:
            logger.error("Error in database_demo_task: %s", e)
            if self.bot.db:
                await self.bot.db.update_task_status(
                    "database_demo_task", False, str(e)
                )

    @database_demo_task.before_loop
    async def before_database_demo_task(self):
        """Wait for bot to be ready before starting task"""
        await self.bot.wait_until_ready()
        logger.info("Database Demo Task is ready to start")

    @database_demo_task.error
    async def database_demo_task_error(self, error):
        """Handle errors in database demo task"""
        logger.error("Database Demo Task encountered an error: %s", error)

    # Database Commands
    @commands.hybrid_group(name="db", aliases=["database"])
    @is_admin()
    async def database_commands(self, ctx):
        """Database management and demo commands"""
        if ctx.invoked_subcommand is None:
            await self.database_status(ctx)

    @database_commands.command(name="status")
    @is_admin()
    async def database_status(self, ctx):
        """Show database connection status"""
        if not self.bot.db:
            embed = discord.Embed(
                title="❌ Database Status",
                description="Database is not connected",
                color=discord.Color.red(),
            )
        else:
            try:
                # Test database connection
                version = await self.bot.db.fetchval("SELECT version()")

                embed = discord.Embed(
                    title="✅ Database Status",
                    description="Database is connected and operational",
                    color=discord.Color.green(),
                    timestamp=datetime.utcnow(),
                )
                embed.add_field(
                    name="PostgreSQL Version",
                    value=version.split()[1] if version else "Unknown",
                    inline=True,
                )
                embed.add_field(
                    name="Pool Status",
                    value=f"Min: {self.bot.db.pool.get_min_size()}, Max: {self.bot.db.pool.get_max_size()}",
                    inline=True,
                )

            except Exception as e:
                embed = discord.Embed(
                    title="⚠️ Database Status",
                    description=f"Database connection error: {e}",
                    color=discord.Color.orange(),
                )

        await ctx.send(embed=embed)

    @database_commands.command(name="prefix")
    @is_admin()
    async def manage_prefix(self, ctx, new_prefix: str = None):
        """
        Get or set the guild prefix

        Parameters
        ----------
        new_prefix : str, optional
            The new prefix to set
        """
        if not self.bot.db:
            await ctx.send("❌ Database not available!")
            return

        try:
            if new_prefix is None:
                # Get current prefix
                current_prefix = await self.bot.db.get_guild_prefix(ctx.guild.id)
                embed = discord.Embed(
                    title="Current Guild Prefix",
                    description=f"Current prefix: `{current_prefix}`",
                    color=discord.Color.blue(),
                )
            else:
                # Set new prefix
                await self.bot.db.set_guild_prefix(ctx.guild.id, new_prefix)

                # Log the action
                await self.bot.db.log_action(
                    guild_id=ctx.guild.id,
                    user_id=ctx.author.id,
                    action="prefix_changed",
                    details={"old_prefix": "!", "new_prefix": new_prefix},
                )

                embed = discord.Embed(
                    title="✅ Prefix Updated",
                    description=f"Guild prefix set to: `{new_prefix}`",
                    color=discord.Color.green(),
                )

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ Database error: {e}")

    @database_commands.command(name="userdata")
    @is_admin()
    async def manage_user_data(
        self, ctx, member: discord.Member, key: str = None, value: str = None
    ):
        """
        Get or set user data

        Parameters
        ----------
        member : discord.Member
            The member to manage data for
        key : str, optional
            The data key to get/set
        value : str, optional
            The value to set for the key
        """
        if not self.bot.db:
            await ctx.send("❌ Database not available!")
            return

        try:
            if key is None:
                # Get all user data
                data = await self.bot.db.get_user_data(member.id, ctx.guild.id)

                embed = discord.Embed(
                    title=f"User Data for {member.display_name}",
                    color=discord.Color.blue(),
                )

                if data:
                    for k, v in data.items():
                        embed.add_field(name=k, value=str(v), inline=True)
                else:
                    embed.description = "No data found for this user"

            elif value is None:
                # Get specific key
                data = await self.bot.db.get_user_data(member.id, ctx.guild.id)
                value = data.get(key, "Not found")

                embed = discord.Embed(
                    title=f"User Data: {key}",
                    description=f"Value: `{value}`",
                    color=discord.Color.blue(),
                )
            else:
                # Set key-value pair
                await self.bot.db.set_user_data(member.id, {key: value}, ctx.guild.id)

                # Log the action
                await self.bot.db.log_action(
                    guild_id=ctx.guild.id,
                    user_id=ctx.author.id,
                    action="user_data_updated",
                    details={"target_user": member.id, "key": key, "value": value},
                )

                embed = discord.Embed(
                    title="✅ User Data Updated",
                    description=f"Set `{key}` = `{value}` for {member.mention}",
                    color=discord.Color.green(),
                )

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ Database error: {e}")

    @database_commands.command(name="logs")
    @is_admin()
    async def view_logs(self, ctx, limit: int = 10):
        """
        View recent bot logs for this guild

        Parameters
        ----------
        limit : int, optional
            Number of logs to show (max 50)
        """
        if not self.bot.db:
            await ctx.send("❌ Database not available!")
            return

        try:
            if limit > 50:
                limit = 50  # Cap at 50 for performance

            logs = await self.bot.db.get_recent_logs(ctx.guild.id, limit)

            if not logs:
                embed = discord.Embed(
                    title="📝 Bot Logs",
                    description="No logs found for this guild",
                    color=discord.Color.blue(),
                )
            else:
                embed = discord.Embed(
                    title=f"📝 Recent Bot Logs ({len(logs)} entries)",
                    color=discord.Color.blue(),
                    timestamp=datetime.utcnow(),
                )

                for log in logs[:10]:  # Show max 10 in embed
                    user = self.bot.get_user(log["user_id"])
                    user_name = user.name if user else f"User {log['user_id']}"

                    embed.add_field(
                        name=f"{log['action']} - {user_name}",
                        value=f"<t:{int(log['created_at'].timestamp())}:R>",
                        inline=False,
                    )

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ Database error: {e}")

    @database_commands.command(name="tasks")
    @is_admin()
    async def view_task_status(self, ctx):
        """View task status from database"""
        if not self.bot.db:
            await ctx.send("❌ Database not available!")
            return

        try:
            task_statuses = await self.bot.db.get_all_task_statuses()

            embed = discord.Embed(
                title="🔄 Task Status (Database)",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow(),
            )

            if not task_statuses:
                embed.description = "No task status records found"
            else:
                for task in task_statuses:
                    status_emoji = "🟢" if task["is_running"] else "🔴"
                    status_text = "Running" if task["is_running"] else "Stopped"

                    last_run = "Never"
                    if task["last_run"]:
                        last_run = f"<t:{int(task['last_run'].timestamp())}:R>"

                    value = f"Status: {status_emoji} {status_text}\n"
                    value += f"Last Run: {last_run}\n"
                    value += f"Run Count: {task['run_count']}"

                    if task["last_error"]:
                        value += f"\nLast Error: `{task['last_error'][:100]}...`"

                    embed.add_field(name=task["task_name"], value=value, inline=False)

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ Database error: {e}")

    @database_commands.command(name="query")
    @is_admin()
    async def execute_query(self, ctx, *, query: str):
        """
        Execute a raw SQL query (SELECT only)

        Parameters
        ----------
        query : str
            The SQL query to execute (SELECT statements only)
        """
        if not self.bot.db:
            await ctx.send("❌ Database not available!")
            return

        # Security check - only allow SELECT statements
        if not query.strip().upper().startswith("SELECT"):
            await ctx.send("❌ Only SELECT queries are allowed for security!")
            return

        try:
            result = await self.bot.db.fetch(query)

            if not result:
                embed = discord.Embed(
                    title="Query Result",
                    description="No results returned",
                    color=discord.Color.blue(),
                )
            else:
                # Format results (limit to first 10 rows)
                rows = result[:10]

                embed = discord.Embed(
                    title=f"Query Result ({len(result)} rows)",
                    color=discord.Color.green(),
                    timestamp=datetime.utcnow(),
                )

                # Convert rows to readable format
                result_text = "```\n"
                for i, row in enumerate(rows):
                    result_text += f"Row {i + 1}: {dict(row)}\n"
                result_text += "```"

                if len(result_text) > 1024:
                    result_text = result_text[:1020] + "...```"

                embed.add_field(name="Results", value=result_text, inline=False)

                if len(result) > 10:
                    embed.set_footer(text=f"Showing first 10 of {len(result)} rows")

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ Query error: {e}")

    # Error handling
    @database_commands.error
    async def database_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(
                "❌ You need administrator permissions to use database commands!"
            )
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Missing required argument!")


async def setup(bot):
    await bot.add_cog(DatabaseDemo(bot))
