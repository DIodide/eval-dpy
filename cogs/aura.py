"""
Aura System Cog

A comprehensive gaming and social system that allows users to gain, lose, and compete
with "aura" - a mystical power measurement. Features gambling, economy, leaderboards,
and social interactions.
"""

import asyncio
import logging
import os
import random
from datetime import datetime, timedelta
from typing import Dict, Any

import discord
from discord.ext import commands

from utils.menus import EmbedBuilder, LeaderboardBuilder, send_paginated_embed
from utils.database import get_db, SQLiteManager

logger = logging.getLogger(__name__)

# EVAL characters for slots
EVAL_CHARACTERS = ["🔥", "⚡", "💎", "🌟", "👑", "🎯", "🚀", "💀", "🌙", "☄️"]

# Aura titles based on aura amount
AURA_TITLES = {
    1000000: "Aura God",
    500000: "Aura Overlord",
    100000: "Aura Master",
    50000: "Aura Legend",
    25000: "Aura Virtuoso",
    10000: "Aura Expert",
    5000: "Aura Adept",
    2500: "Aura Scholar",
    1000: "Aura Apprentice",
    500: "Aura Novice",
    100: "Aura Initiate",
    0: "Aura Seeker",
    -500: "Aura Deficit",
    -1000: "Aura Debtor",
    -5000: "Aura Thief",
    -10000: "Aura Void",
    -25000: "Aura Banished",
}

# Daily rewards
DAILY_MESSAGES = [
    "✨ The universe smiles upon you!",
    "🌟 Your aura radiates with cosmic energy!",
    "💫 Fortune favors the bold!",
    "🔮 The stars align in your favor!",
    "⚡ Lightning strikes your soul with power!",
    "🌈 You've been blessed by the rainbow gods!",
    "🎭 The cosmic theater applauds your presence!",
    "🎪 The carnival of destiny rewards you!",
    "🎨 Your aura paints the sky with brilliance!",
    "🎯 Bullseye! Cosmic accuracy achieved!",
]

# Shop items
AURA_SHOP = {
    "shield": {
        "name": "🛡️ Aura Shield",
        "cost": 1000,
        "description": "Protects against 50% drain damage for 24 hours",
        "duration": 24 * 60 * 60,
    },
    "multiplier": {
        "name": "⚡ Aura Multiplier",
        "cost": 2500,
        "description": "2x aura gains for 12 hours",
        "duration": 12 * 60 * 60,
    },
    "bomb": {
        "name": "💣 Aura Bomb",
        "cost": 5000,
        "description": "Instantly deal 2000 damage to target (ignores shields)",
        "duration": 0,
    },
}


class Aura(commands.Cog):
    """Aura system - The ultimate power measurement"""

    def __init__(self, bot):
        self.bot = bot
        self.duel_requests = {}

    async def get_user_aura_data(
        self, user_id: int, guild_id: int = None
    ) -> Dict[str, Any]:
        """Get user's aura data from database"""
        db = get_db(self.bot)
        data = await db.get_user_data(user_id, guild_id)

        if "aura" not in data:
            data["aura"] = {
                "amount": 100,
                "daily_last": None,
                "shield_expires": None,
                "multiplier_expires": None,
                "items": [],
                "cooldowns": {},
                "stats": {
                    "duels_won": 0,
                    "duels_lost": 0,
                    "total_gained": 0,
                    "total_lost": 0,
                    "biggest_win": 0,
                    "biggest_loss": 0,
                },
            }

        return data["aura"]

    async def update_user_aura_data(
        self, user_id: int, aura_data: Dict[str, Any], guild_id: int = None
    ):
        """Update user's aura data in database"""
        db = get_db(self.bot)
        user_data = await db.get_user_data(user_id, guild_id)
        user_data["aura"] = aura_data
        await db.set_user_data(user_id, user_data, guild_id)

    async def modify_aura(
        self, user_id: int, amount: int, guild_id: int = None, reason: str = None
    ) -> int:
        """Modify user's aura amount and return new total"""
        aura_data = await self.get_user_aura_data(user_id, guild_id)

        # Apply multiplier if active
        if (
            aura_data.get("multiplier_expires")
            and datetime.now().timestamp() < aura_data["multiplier_expires"]
        ):
            if amount > 0:
                amount *= 2

        old_amount = aura_data["amount"]
        aura_data["amount"] += amount

        # Update stats
        if amount > 0:
            aura_data["stats"]["total_gained"] += amount
            if amount > aura_data["stats"]["biggest_win"]:
                aura_data["stats"]["biggest_win"] = amount
        else:
            aura_data["stats"]["total_lost"] += abs(amount)
            if abs(amount) > aura_data["stats"]["biggest_loss"]:
                aura_data["stats"]["biggest_loss"] = abs(amount)

        await self.update_user_aura_data(user_id, aura_data, guild_id)

        # Log the action
        db = get_db(self.bot)
        await db.log_action(
            guild_id,
            user_id,
            "aura_change",
            {
                "old_amount": old_amount,
                "new_amount": aura_data["amount"],
                "change": amount,
                "reason": reason or "Unknown",
            },
        )

        return aura_data["amount"]

    def get_aura_title(self, amount: int) -> str:
        """Get title based on aura amount"""
        for threshold in sorted(AURA_TITLES.keys(), reverse=True):
            if amount >= threshold:
                return AURA_TITLES[threshold]
        return "Aura Banished"

    def create_aura_embed(
        self, user: discord.Member, aura_data: Dict[str, Any]
    ) -> discord.Embed:
        """Create a beautiful aura display embed"""
        amount = aura_data["amount"]
        title = self.get_aura_title(amount)

        # Color based on aura amount
        if amount >= 100000:
            color = discord.Color.gold()
        elif amount >= 10000:
            color = discord.Color.purple()
        elif amount >= 1000:
            color = discord.Color.blue()
        elif amount >= 0:
            color = discord.Color.green()
        else:
            color = discord.Color.red()

        embed = discord.Embed(title=f"✨ {user.display_name}'s Aura", color=color)

        embed.add_field(
            name="💫 Aura Amount", value=f"```{amount:,} ✨```", inline=True
        )

        embed.add_field(name="👑 Title", value=f"**{title}**", inline=True)

        # Active effects
        effects = []
        now = datetime.now().timestamp()

        if aura_data.get("shield_expires") and now < aura_data["shield_expires"]:
            remaining = int(aura_data["shield_expires"] - now)
            effects.append(
                f"🛡️ Shield ({remaining // 3600}h {(remaining % 3600) // 60}m)"
            )

        if (
            aura_data.get("multiplier_expires")
            and now < aura_data["multiplier_expires"]
        ):
            remaining = int(aura_data["multiplier_expires"] - now)
            effects.append(
                f"⚡ 2x Multiplier ({remaining // 3600}h {(remaining % 3600) // 60}m)"
            )

        if effects:
            embed.add_field(
                name="🌟 Active Effects", value="\n".join(effects), inline=False
            )

        # Stats
        stats = aura_data.get("stats", {})
        embed.add_field(
            name="📈 Statistics",
            value=(
                f"**Duels:** {stats.get('duels_won', 0)}W / "
                f"{stats.get('duels_lost', 0)}L\n"
                f"**Biggest Win:** {stats.get('biggest_win', 0):,} ✨\n"
                f"**Biggest Loss:** {stats.get('biggest_loss', 0):,} ✨"
            ),
            inline=True,
        )

        embed.set_thumbnail(url=user.display_avatar.url)
        return embed

    @commands.hybrid_group(name="aura", description="Aura system commands")
    async def aura(self, ctx):
        """Main aura command group"""
        if ctx.invoked_subcommand is None:
            aura_data = await self.get_user_aura_data(ctx.author.id, ctx.guild.id)
            embed = self.create_aura_embed(ctx.author, aura_data)
            await ctx.send(embed=embed)

    @aura.command(name="check", description="Check someone's aura")
    async def aura_check(self, ctx, user: discord.Member = None):
        """Check aura amount for yourself or another user"""
        target = user or ctx.author
        aura_data = await self.get_user_aura_data(target.id, ctx.guild.id)
        embed = self.create_aura_embed(target, aura_data)
        await ctx.send(embed=embed)

    @aura.command(name="slots", description="Aura slot machine")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def aura_slots(self, ctx, bet: int = 50):
        """Play the aura slot machine"""
        if bet < 10:
            await ctx.send("❌ Minimum bet is 10 aura!")
            return

        aura_data = await self.get_user_aura_data(ctx.author.id, ctx.guild.id)

        if aura_data["amount"] < bet:
            await ctx.send("❌ Insufficient aura! You need more cosmic energy.")
            return

        # Generate slots
        slots = [random.choice(EVAL_CHARACTERS) for _ in range(3)]

        # Calculate winnings
        multiplier = 0
        if slots[0] == slots[1] == slots[2]:  # Triple match
            if slots[0] == "💎":  # Diamond jackpot
                multiplier = 50
            elif slots[0] == "👑":  # Crown mega win
                multiplier = 25
            elif slots[0] == "🔥":  # Fire big win
                multiplier = 10
            else:  # Other triples
                multiplier = 5
        elif (
            slots[0] == slots[1] or slots[1] == slots[2] or slots[0] == slots[2]
        ):  # Double match
            multiplier = 2

        winnings = int(bet * multiplier) - bet

        # Create animated embed
        embed = discord.Embed(
            title="🎰 AURA SLOTS",
            description="```🎲 🎲 🎲```\nSpinning...",
            color=discord.Color.orange(),
        )
        message = await ctx.send(embed=embed)

        await asyncio.sleep(1)

        # Show result
        result_color = (
            discord.Color.green()
            if winnings > 0
            else discord.Color.red()
            if winnings < 0
            else discord.Color.orange()
        )
        embed = discord.Embed(
            title="🎰 AURA SLOTS",
            description=f"```{slots[0]} {slots[1]} {slots[2]}```",
            color=result_color,
        )

        if winnings > 0:
            embed.add_field(
                name="🎉 WINNER!", value=f"You won **{winnings:,} aura**!", inline=False
            )
            await self.modify_aura(ctx.author.id, winnings, ctx.guild.id, "slots_win")
        elif winnings < 0:
            embed.add_field(
                name="💸 Better luck next time!",
                value=f"You lost **{bet:,} aura**",
                inline=False,
            )
            await self.modify_aura(ctx.author.id, -bet, ctx.guild.id, "slots_loss")
        else:
            embed.add_field(
                name="😐 No win, no loss",
                value="Your aura remains unchanged",
                inline=False,
            )

        await message.edit(embed=embed)

    @aura.command(name="flip", description="Flip a coin for aura")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def aura_flip(self, ctx, bet: int = 25, choice: str = "heads"):
        """Flip a coin to win or lose aura"""
        if bet < 5:
            await ctx.send("❌ Minimum bet is 5 aura!")
            return

        if choice.lower() not in ["heads", "tails", "h", "t"]:
            await ctx.send("❌ Choose 'heads' or 'tails'!")
            return

        aura_data = await self.get_user_aura_data(ctx.author.id, ctx.guild.id)

        if aura_data["amount"] < bet:
            await ctx.send("❌ Insufficient aura!")
            return

        # Normalize choice
        user_choice = "heads" if choice.lower() in ["heads", "h"] else "tails"
        result = random.choice(["heads", "tails"])

        embed = discord.Embed(title="🪙 Aura Coin Flip", color=discord.Color.orange())
        embed.description = "Flipping..."
        message = await ctx.send(embed=embed)

        await asyncio.sleep(2)

        coin_emoji = "🟡" if result == "heads" else "⚪"

        if user_choice == result:
            winnings = bet
            embed = EmbedBuilder.create_success_embed(
                title=f"🪙 {coin_emoji} {result.title()}!",
                description=f"🎉 You won **{winnings:,} aura**!",
            )
            await self.modify_aura(
                ctx.author.id, winnings, ctx.guild.id, "coinflip_win"
            )
        else:
            embed = EmbedBuilder.create_error_embed(
                title=f"🪙 {coin_emoji} {result.title()}!",
                description=f"💸 You lost **{bet:,} aura**",
            )
            await self.modify_aura(ctx.author.id, -bet, ctx.guild.id, "coinflip_loss")

        await message.edit(embed=embed)

    @aura.command(name="roll", description="Roll dice for aura")
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def aura_roll(self, ctx, bet: int = 30, target: int = 6):
        """Roll a dice - match the target to win big!"""
        if bet < 10:
            await ctx.send("❌ Minimum bet is 10 aura!")
            return

        if target < 1 or target > 6:
            await ctx.send("❌ Target must be between 1-6!")
            return

        aura_data = await self.get_user_aura_data(ctx.author.id, ctx.guild.id)

        if aura_data["amount"] < bet:
            await ctx.send("❌ Insufficient aura!")
            return

        roll = random.randint(1, 6)
        dice_emojis = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]

        embed = discord.Embed(title="🎲 Aura Dice Roll", color=discord.Color.orange())
        embed.description = "Rolling..."
        message = await ctx.send(embed=embed)

        await asyncio.sleep(2)

        if roll == target:
            winnings = bet * 5  # 5x multiplier for exact match
            embed = EmbedBuilder.create_success_embed(
                title=f"🎲 {dice_emojis[roll - 1]} Rolled {roll}!",
                description=f"🎯 BULLSEYE! You won **{winnings:,} aura**!",
            )
            await self.modify_aura(
                ctx.author.id, winnings, ctx.guild.id, "dice_jackpot"
            )
        elif abs(roll - target) == 1:
            winnings = bet // 2  # Half bet back for close
            embed = EmbedBuilder.create_warning_embed(
                title=f"🎲 {dice_emojis[roll - 1]} Rolled {roll}!",
                description=f"😅 Close! You get **{winnings:,} aura** back",
            )
            await self.modify_aura(
                ctx.author.id, winnings - bet, ctx.guild.id, "dice_close"
            )
        else:
            embed = EmbedBuilder.create_error_embed(
                title=f"🎲 {dice_emojis[roll - 1]} Rolled {roll}!",
                description=f"💸 You lost **{bet:,} aura**",
            )
            await self.modify_aura(ctx.author.id, -bet, ctx.guild.id, "dice_loss")

        await message.edit(embed=embed)

    @aura.command(name="daily", description="Claim your daily aura bonus")
    async def aura_daily(self, ctx):
        """Claim daily aura bonus"""
        aura_data = await self.get_user_aura_data(ctx.author.id, ctx.guild.id)

        now = datetime.now()
        last_daily = aura_data.get("daily_last")

        if last_daily:
            last_daily_dt = datetime.fromisoformat(last_daily)
            if now - last_daily_dt < timedelta(hours=20):  # 20 hour cooldown
                remaining = timedelta(hours=20) - (now - last_daily_dt)
                hours = remaining.total_seconds() // 3600
                minutes = (remaining.total_seconds() % 3600) // 60
                hours_int = int(hours)
                minutes_int = int(minutes)
                await ctx.send(
                    f"⏰ Daily already claimed! Try again in {hours_int}h {minutes_int}m"
                )
                return

        # Calculate daily reward
        base_reward = random.randint(50, 150)
        streak_bonus = random.randint(0, 50)
        total_reward = base_reward + streak_bonus

        # Random bonus events
        bonus_events = [
            (0.05, 500, "🌟 COSMIC ALIGNMENT! Bonus aura rain!"),
            (0.1, 200, "⚡ Lightning struck your aura!"),
            (0.15, 100, "🎪 The cosmic carnival visited you!"),
        ]

        for chance, bonus, _ in bonus_events:
            if random.random() < chance:
                total_reward += bonus
                break

        await self.modify_aura(
            ctx.author.id, total_reward, ctx.guild.id, "daily_reward"
        )

        # Update daily timestamp
        aura_data["daily_last"] = now.isoformat()
        await self.update_user_aura_data(ctx.author.id, aura_data, ctx.guild.id)

        daily_msg = random.choice(DAILY_MESSAGES)
        embed = EmbedBuilder.create_success_embed(
            title="🌅 Daily Aura Claimed!",
            description=f"{daily_msg}\n\n💰 **+{total_reward:,} aura**",
        )
        await ctx.send(embed=embed)

    @aura.command(name="donate", description="Give aura to another user")
    async def aura_donate(self, ctx, target: discord.Member, amount: int):
        """Donate aura to another user"""
        if target.bot:
            await ctx.send("❌ You cannot donate to bots!")
            return

        if target == ctx.author:
            await ctx.send("❌ You cannot donate to yourself!")
            return

        if amount < 10:
            await ctx.send("❌ Minimum donation is 10 aura!")
            return

        donor_data = await self.get_user_aura_data(ctx.author.id, ctx.guild.id)

        if donor_data["amount"] < amount:
            await ctx.send("❌ You don't have enough aura!")
            return

        # Transfer aura
        await self.modify_aura(ctx.author.id, -amount, ctx.guild.id, "donation_sent")
        await self.modify_aura(target.id, amount, ctx.guild.id, "donation_received")

        embed = EmbedBuilder.create_success_embed(
            title="💝 Aura Donation",
            description=(
                f"{ctx.author.mention} donated **{amount:,} aura** to "
                f"{target.mention}!\n\n"
                f"✨ *The universe smiles upon your generosity*"
            ),
        )
        await ctx.send(embed=embed)

    @aura.command(name="drain", description="Attempt to steal aura from someone")
    @commands.cooldown(1, 300, commands.BucketType.user)  # 5 minute cooldown
    async def aura_drain(self, ctx, target: discord.Member):
        """Risky command to steal aura from another user"""
        if target.bot:
            await ctx.send("❌ You cannot drain bots!")
            return

        if target == ctx.author:
            await ctx.send("❌ You cannot drain yourself!")
            return

        drainer_data = await self.get_user_aura_data(ctx.author.id, ctx.guild.id)
        target_data = await self.get_user_aura_data(target.id, ctx.guild.id)

        # Check if target has shield
        now = datetime.now().timestamp()
        has_shield = (
            target_data.get("shield_expires") and now < target_data["shield_expires"]
        )

        # Success rate based on aura difference
        aura_diff = drainer_data["amount"] - target_data["amount"]
        base_success = 0.3  # 30% base success rate

        if aura_diff > 0:
            success_rate = min(0.7, base_success + (aura_diff / 10000) * 0.2)
        else:
            success_rate = max(0.1, base_success + (aura_diff / 10000) * 0.2)

        # Reduce success rate if target has shield
        if has_shield:
            success_rate *= 0.3

        embed = discord.Embed(
            title="🌪️ Aura Drain Attempt", color=discord.Color.purple()
        )
        embed.description = "Channeling dark energy..."
        message = await ctx.send(embed=embed)

        await asyncio.sleep(3)

        if random.random() < success_rate:
            # Success
            max_drain = min(target_data["amount"] // 4, 500)  # Max 25% or 500
            drain_amount = random.randint(max_drain // 3, max_drain)

            if has_shield:
                drain_amount //= 2  # Shield reduces damage

            await self.modify_aura(
                target.id, -drain_amount, ctx.guild.id, "drained_by_user"
            )
            await self.modify_aura(
                ctx.author.id, drain_amount, ctx.guild.id, "successful_drain"
            )

            embed = EmbedBuilder.create_success_embed(
                title="🌪️ Drain Successful!",
                description=(
                    f"You drained **{drain_amount:,} aura** from "
                    f"{target.display_name}!"
                    + (" 🛡️ (Reduced by shield)" if has_shield else "")
                ),
            )
        else:
            # Failure - backfire
            backfire = random.randint(100, 300)
            await self.modify_aura(
                ctx.author.id, -backfire, ctx.guild.id, "drain_backfire"
            )

            embed = EmbedBuilder.create_error_embed(
                title="💥 Drain Backfired!",
                description=(
                    f"Your drain attempt failed and you lost **{backfire:,} aura**!"
                ),
            )

        await message.edit(embed=embed)

    @aura.command(
        name="leaderboard",
        aliases=["lb", "top"],
        description="View the aura leaderboard",
    )
    async def aura_leaderboard(self, ctx):
        """Display the aura leaderboard"""
        db = get_db(self.bot)

        # Get all users with data in this guild
        if isinstance(db, SQLiteManager):
            # SQLite query
            all_users = await db.fetch(
                "SELECT user_id, data FROM user_data WHERE guild_id = ?",
                ctx.guild.id,
            )
        else:
            # PostgreSQL query
            all_users = await db.fetch(
                "SELECT user_id, data FROM user_data WHERE guild_id = $1 AND data ? 'aura'",
                ctx.guild.id,
            )

        if not all_users:
            await ctx.send("❌ No aura data found for this server!")
            return

        # Sort by aura amount
        leaderboard_data = []
        for user_row in all_users:
            user_id = user_row["user_id"]

            # Handle different data formats
            if isinstance(db, SQLiteManager):
                # SQLite stores data as JSON string
                try:
                    import json

                    data = (
                        json.loads(user_row["data"])
                        if isinstance(user_row["data"], str)
                        else user_row["data"]
                    )
                    if "aura" not in data:
                        continue
                    aura_amount = data["aura"]["amount"]
                except (json.JSONDecodeError, KeyError, TypeError):
                    continue
            else:
                # PostgreSQL stores data as JSONB
                if "aura" not in user_row["data"]:
                    continue
                aura_amount = user_row["data"]["aura"]["amount"]

            user = ctx.guild.get_member(user_id)
            if user:  # Only include users still in the guild
                title = self.get_aura_title(aura_amount)
                leaderboard_data.append(
                    {"user": user, "aura": aura_amount, "title": title}
                )

        leaderboard_data.sort(key=lambda x: x["aura"], reverse=True)

        if not leaderboard_data:
            await ctx.send("❌ No users found with aura data!")
            return

        # Create leaderboard embed
        leaderboard_entries = []
        for entry in leaderboard_data[:20]:  # Top 20
            # Format value to include both aura and title
            formatted_value = f"{entry['aura']:,} ✨ ({entry['title']})"
            leaderboard_entries.append(
                {"name": entry["user"].display_name, "value": formatted_value}
            )

        embeds = LeaderboardBuilder.create_leaderboard(
            title="🏆 Aura Leaderboard",
            entries=leaderboard_entries,
            page_size=10,
            key_field="name",
            value_field="value",
            color=discord.Color.gold(),
        )

        await send_paginated_embed(ctx, embeds)

    @aura.command(name="titles", description="View available aura titles")
    async def aura_titles(self, ctx):
        """Display all available aura titles and requirements"""
        embed = discord.Embed(
            title="👑 Aura Titles",
            description="Achieve these aura amounts to unlock titles!",
            color=discord.Color.purple(),
        )

        # Group titles by positive/negative
        positive_titles = [(k, v) for k, v in AURA_TITLES.items() if k >= 0]
        negative_titles = [(k, v) for k, v in AURA_TITLES.items() if k < 0]

        # Sort by requirement
        positive_titles.sort(key=lambda x: x[0], reverse=True)
        negative_titles.sort(key=lambda x: x[0])

        # Add positive titles
        positive_text = ""
        for req, title in positive_titles:
            positive_text += f"**{req:,} ✨** - {title}\n"

        embed.add_field(name="✨ Ascension Titles", value=positive_text, inline=True)

        # Add negative titles
        negative_text = ""
        for req, title in negative_titles:
            negative_text += f"**{req:,} ✨** - {title}\n"

        embed.add_field(name="💀 Descent Titles", value=negative_text, inline=True)

        await ctx.send(embed=embed)

    @aura.command(name="shop", description="Browse the aura shop")
    async def aura_shop(self, ctx, item: str = None):
        """Browse or buy items from the aura shop"""
        if item is None:
            # Display shop
            embed = discord.Embed(
                title="🏪 Aura Shop",
                description="Purchase powerful items with your aura!",
                color=discord.Color.blue(),
            )

            for item_id, item_data in AURA_SHOP.items():
                embed.add_field(
                    name=f"{item_data['name']} - {item_data['cost']:,} ✨",
                    value=item_data["description"],
                    inline=False,
                )

            embed.set_footer(text="Use `/aura shop <item>` to purchase!")
            await ctx.send(embed=embed)
        else:
            # Purchase item
            item_id = item.lower()
            if item_id not in AURA_SHOP:
                await ctx.send(
                    "❌ Item not found! Use `/aura shop` to see available items."
                )
                return

            item_data = AURA_SHOP[item_id]
            aura_data = await self.get_user_aura_data(ctx.author.id, ctx.guild.id)

            if aura_data["amount"] < item_data["cost"]:
                cost = item_data["cost"]
                name = item_data["name"]
                await ctx.send(f"❌ You need {cost:,} aura to buy {name}!")
                return

            # Purchase item
            await self.modify_aura(
                ctx.author.id,
                -item_data["cost"],
                ctx.guild.id,
                f"shop_purchase_{item_id}",
            )

            # Apply item effects
            now = datetime.now().timestamp()

            if item_id == "shield":
                aura_data["shield_expires"] = now + item_data["duration"]
            elif item_id == "multiplier":
                aura_data["multiplier_expires"] = now + item_data["duration"]
            elif item_id in ["bomb"]:
                if "items" not in aura_data:
                    aura_data["items"] = []
                aura_data["items"].append(item_id)

            await self.update_user_aura_data(ctx.author.id, aura_data, ctx.guild.id)

            name = item_data["name"]
            cost = item_data["cost"]
            embed = EmbedBuilder.create_success_embed(
                title="🛒 Purchase Successful!",
                description=f"You bought {name} for {cost:,} aura!",
            )
            await ctx.send(embed=embed)

    # Personal commands
    @commands.hybrid_command(name="erika", description="Give tribute to Erika")
    async def erika_command(self, ctx):
        """Special command for Erika (user ID: 277200034469117955)"""
        erika_id = 277200034469117955

        # Give +1 aura to user, -0.1 to Erika
        await self.modify_aura(ctx.author.id, 1, ctx.guild.id, "erika_tribute_received")
        await self.modify_aura(erika_id, -0.1, ctx.guild.id, "erika_tribute_given")

        embed = EmbedBuilder.create_success_embed(
            title="🌸 Erika's Blessing",
            description=(
                f"{ctx.author.mention} receives **+1 aura** from Erika's grace!\n\n"
                "*Erika sacrifices a tiny bit of her cosmic energy for you...*"
            ),
        )
        await ctx.send(embed=embed)

    # Hidden command (not in help)
    @commands.command(name="opticcat", hidden=True)
    async def optic_cat_command(self, ctx):
        """Secret OpticCat command"""
        # +10,000,000 aura to user, -10,000,000 to bot owner
        bot_owner_id = self.bot.owner_id or 123456789  # Replace with actual owner ID

        await self.modify_aura(
            ctx.author.id, 10000000, ctx.guild.id, "opticcat_blessing"
        )
        await self.modify_aura(
            bot_owner_id, -10000000, ctx.guild.id, "opticcat_sacrifice"
        )

        embed = discord.Embed(
            title="🐱‍👤 OpticCat Appears!",
            description=(
                "**MEGA AURA TRANSFER!**\n\n"
                f"{ctx.author.mention} gains **+10,000,000 aura**!\n"
                "*OpticCat has blessed you with ultimate power...*"
            ),
            color=discord.Color.from_rgb(255, 215, 0),
        )

        # Try to send the placeholder image
        try:
            file = discord.File("assets/opticcat.png", filename="opticcat.png")
            embed.set_image(url="attachment://opticcat.png")
            await ctx.send(embed=embed, file=file)
        except FileNotFoundError:
            embed.set_footer(text="OpticCat image not found - placeholder needed!")
            await ctx.send(embed=embed)


async def setup(bot):
    """Load the Aura cog"""
    os.makedirs("assets", exist_ok=True)
    await bot.add_cog(Aura(bot))
