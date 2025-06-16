import discord
from discord.ext import commands, tasks
import asyncio
import aiohttp
from datetime import datetime
import logging
from utils.checks import is_admin

logger = logging.getLogger(__name__)


class Tasks(commands.Cog):
    """Background tasks and task management commands"""

    def __init__(self, bot):
        self.bot = bot
        self.running_tasks = {}  # Keep track of running tasks

        # Example tasks - these won't start automatically
        self.example_task_1.add_exception_type(Exception)
        self.example_task_2.add_exception_type(Exception)
        self.api_monitor_task.add_exception_type(Exception)

        #self.example_task_1.start()

    async def cog_unload(self):
        """Stop all tasks when the cog is unloaded"""
        logger.info("Stopping all tasks before unloading...")
        stopped_tasks = []

        tasks_to_stop = [
            ("example_task_1", self.example_task_1),
            ("example_task_2", self.example_task_2),
            ("api_monitor_task", self.api_monitor_task),
        ]

        for task_name, task in tasks_to_stop:
            if task.is_running():
                task.cancel()
                stopped_tasks.append(task_name)
                logger.info("Stopped %s", task_name)

        if stopped_tasks:
            logger.info("Stopped tasks: %s", ", ".join(stopped_tasks))
        else:
            logger.info("No running tasks to stop")

    # Example Task 1: Simple periodic message
    @tasks.loop(minutes=5)
    async def example_task_1(self):
        """Example task that runs every 5 minutes"""
        try:
            logger.info("Example Task 1 is running...")
            # Your task logic here
            # Example: Send a message to a specific channel

            # Uncomment and modify as needed:
            # channel = self.bot.get_channel(CHANNEL_ID)
            # if channel:
            #     await channel.send("🤖 Periodic message from Example Task 1!")

        except Exception as e:
            logger.error("Error in example_task_1: %s", e)

    @example_task_1.before_loop
    async def before_example_task_1(self):
        """Wait for bot to be ready before starting task"""
        await self.bot.wait_until_ready()
        logger.info("Example Task 1 is ready to start")

    @example_task_1.error
    async def example_task_1_error(self, error):
        """Handle errors in example task 1"""
        logger.error("Example Task 1 encountered an error: %s", error)

    # Example Task 2: Status updater
    @tasks.loop(minutes=10)
    async def example_task_2(self):
        """Example task that updates bot status every 10 minutes"""
        try:
            statuses = [
                "for !help",
                f"over {len(self.bot.guilds)} servers",
                f"with {len(self.bot.users)} users",
                "for new commands",
            ]

            # Cycle through different statuses
            import random

            status = random.choice(statuses)

            await self.bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching, name=status
                )
            )
            logger.info("Updated bot status to: %s", status)

        except Exception as e:
            logger.error("Error in example_task_2: %s", e)

    @example_task_2.before_loop
    async def before_example_task_2(self):
        """Wait for bot to be ready before starting task"""
        await self.bot.wait_until_ready()
        logger.info("Example Task 2 is ready to start")

    @example_task_2.error
    async def example_task_2_error(self, error):
        """Handle errors in example task 2"""
        logger.error("Example Task 2 encountered an error: %s", error)

    # Example Task 3: API monitoring
    @tasks.loop(hours=1)
    async def api_monitor_task(self):
        """Example task that monitors an API every hour"""
        try:
            if not self.bot.session:
                logger.warning("No HTTP session available for API monitoring")
                return

            # Example API call using the global session
            async with self.bot.session.get("https://httpbin.org/get") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(
                        "API monitor: Status OK, Origin: %s",
                        data.get("origin", "Unknown"),
                    )
                else:
                    logger.warning("API monitor: Status %d", response.status)

        except aiohttp.ClientError as e:
            logger.error("API monitor network error: %s", e)
        except Exception as e:
            logger.error("Error in api_monitor_task: %s", e)

    @api_monitor_task.before_loop
    async def before_api_monitor_task(self):
        """Wait for bot to be ready before starting task"""
        await self.bot.wait_until_ready()
        logger.info("API Monitor Task is ready to start")

    @api_monitor_task.error
    async def api_monitor_task_error(self, error):
        """Handle errors in API monitor task"""
        logger.error("API Monitor Task encountered an error: %s", error)

    # Task Management Commands
    @commands.hybrid_group(name="task")
    @is_admin()
    async def task_commands(self, ctx):
        """Background task management commands"""
        if ctx.invoked_subcommand is None:
            await self.list_tasks(ctx)

    @task_commands.command(name="list")
    @is_admin()
    async def list_tasks(self, ctx):
        """List all available background tasks and their status"""
        tasks_info = [
            ("example_task_1", self.example_task_1, "Simple periodic task (5 min)"),
            ("example_task_2", self.example_task_2, "Status updater task (10 min)"),
            ("api_monitor_task", self.api_monitor_task, "API monitoring task (1 hour)"),
        ]

        embed = discord.Embed(
            title="🔄 Available Tasks",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow(),
        )

        for name, task, description in tasks_info:
            status = "🟢 Running" if task.is_running() else "🔴 Stopped"
            embed.add_field(
                name=f"{name}", value=f"{description}\nStatus: {status}", inline=False
            )

        embed.set_footer(text="Use !task start/stop <task_name> to control tasks")
        await ctx.send(embed=embed)

    @task_commands.command(name="start")
    @is_admin()
    async def start_task(self, ctx, task_name: str):
        """
        Start a specific background task

        Parameters
        ----------
        task_name : str
            The name of the task to start
        """
        task_map = {
            "example_task_1": self.example_task_1,
            "example_task_2": self.example_task_2,
            "api_monitor_task": self.api_monitor_task,
        }

        if task_name not in task_map:
            await ctx.send(
                f"❌ Task `{task_name}` not found! Use `!task list` to see available tasks."
            )
            return

        task = task_map[task_name]

        if task.is_running():
            await ctx.send(f"⚠️ Task `{task_name}` is already running!")
            return

        try:
            task.start()

            embed = discord.Embed(
                title="✅ Task Started",
                description=f"Successfully started task `{task_name}`",
                color=discord.Color.green(),
                timestamp=datetime.utcnow(),
            )
            embed.add_field(name="Started by", value=ctx.author.mention, inline=True)

            await ctx.send(embed=embed)
            logger.info("Task %s started by %s", task_name, ctx.author)

        except Exception as e:
            await ctx.send(f"❌ Failed to start task `{task_name}`: {e}")
            logger.error("Failed to start task %s: %s", task_name, e)

    @task_commands.command(name="stop")
    @is_admin()
    async def stop_task(self, ctx, task_name: str):
        """
        Stop a specific background task

        Parameters
        ----------
        task_name : str
            The name of the task to stop
        """
        task_map = {
            "example_task_1": self.example_task_1,
            "example_task_2": self.example_task_2,
            "api_monitor_task": self.api_monitor_task,
        }

        if task_name not in task_map:
            await ctx.send(
                f"❌ Task `{task_name}` not found! Use `!task list` to see available tasks."
            )
            return

        task = task_map[task_name]

        if not task.is_running():
            await ctx.send(f"⚠️ Task `{task_name}` is not running!")
            return

        try:
            task.cancel()

            embed = discord.Embed(
                title="🛑 Task Stopped",
                description=f"Successfully stopped task `{task_name}`",
                color=discord.Color.orange(),
                timestamp=datetime.utcnow(),
            )
            embed.add_field(name="Stopped by", value=ctx.author.mention, inline=True)

            await ctx.send(embed=embed)
            logger.info("Task %s stopped by %s", task_name, ctx.author)

        except Exception as e:
            await ctx.send(f"❌ Failed to stop task `{task_name}`: {e}")
            logger.error("Failed to stop task %s: %s", task_name, e)

    @task_commands.command(name="restart")
    @is_admin()
    async def restart_task(self, ctx, task_name: str):
        """
        Restart a specific background task

        Parameters
        ----------
        task_name : str
            The name of the task to restart
        """
        task_map = {
            "example_task_1": self.example_task_1,
            "example_task_2": self.example_task_2,
            "api_monitor_task": self.api_monitor_task,
        }

        if task_name not in task_map:
            await ctx.send(
                f"❌ Task `{task_name}` not found! Use `!task list` to see available tasks."
            )
            return

        task = task_map[task_name]

        try:
            # Stop if running
            if task.is_running():
                task.cancel()
                await asyncio.sleep(1)  # Give it a moment to stop

            # Start the task
            task.start()

            embed = discord.Embed(
                title="🔄 Task Restarted",
                description=f"Successfully restarted task `{task_name}`",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow(),
            )
            embed.add_field(name="Restarted by", value=ctx.author.mention, inline=True)

            await ctx.send(embed=embed)
            logger.info("Task %s restarted by %s", task_name, ctx.author)

        except Exception as e:
            await ctx.send(f"❌ Failed to restart task `{task_name}`: {e}")
            logger.error("Failed to restart task %s: %s", task_name, e)

    @task_commands.command(name="stopall")
    @is_admin()
    async def stop_all_tasks(self, ctx):
        """Stop all running background tasks"""
        stopped_tasks = []

        tasks_to_stop = [
            ("example_task_1", self.example_task_1),
            ("example_task_2", self.example_task_2),
            ("api_monitor_task", self.api_monitor_task),
        ]

        for task_name, task in tasks_to_stop:
            if task.is_running():
                task.cancel()
                stopped_tasks.append(task_name)
                logger.info("Stopped %s", task_name)

                # Update database status if available
                if self.bot.db:
                    await self.bot.db.update_task_status(
                        task_name, False, "Manually stopped"
                    )

        if stopped_tasks:
            embed = discord.Embed(
                title="✅ Tasks Stopped",
                description=f"Successfully stopped {len(stopped_tasks)} tasks:\n"
                + "\n".join(f"• {task}" for task in stopped_tasks),
                color=discord.Color.green(),
            )
        else:
            embed = discord.Embed(
                title="ℹ️ No Tasks Running",
                description="No tasks were running.",
                color=discord.Color.blue(),
            )

        await ctx.send(embed=embed)

    # Error handling for task commands
    @task_commands.error
    async def task_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("❌ You need administrator permissions to manage tasks!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "❌ Missing required argument! Use `!task list` to see available tasks."
            )


async def setup(bot):
    await bot.add_cog(Tasks(bot))
