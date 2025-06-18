# 🌟 Aura System Documentation

The Aura System is a comprehensive gaming and social feature for your Discord bot that allows users to gain, lose, and compete with "aura" - a mystical power measurement.

## 📋 Commands Overview

### 🔍 Basic Commands

- **`!aura`** or **`!aura check [@user]`** - Check your aura or someone else's aura
  - Shows current aura amount, title, active effects, and statistics
  - Beautiful color-coded embeds based on aura level

### 🎰 Gambling Commands

- **`!aura slots [bet]`** - Play the aura slot machine (default bet: 50)

  - Uses EVAL characters: 🔥⚡💎🌟👑🎯🚀💀🌙☄️
  - Triple matches have huge multipliers (Diamond 💎 = 50x!)
  - 30-second cooldown

- **`!aura flip [bet] [heads/tails]`** - Coin flip gambling (default bet: 25)

  - Choose heads or tails, win double your bet
  - 15-second cooldown

- **`!aura roll [bet] [target]`** - Dice roll gambling (default bet: 30, target: 6)
  - Match the target number for 5x multiplier
  - Close numbers give partial refund
  - 20-second cooldown

### 💰 Economy Commands

- **`!aura daily`** - Claim daily aura bonus (50-150 base + bonuses)

  - 20-hour cooldown
  - Random cosmic events for bonus aura
  - Fun flavor messages

- **`!aura donate [@user] [amount]`** - Give aura to another user

  - Minimum donation: 10 aura
  - Shows generosity in beautiful embed

- **`!aura drain [@user]`** - Attempt to steal aura (RISKY!)
  - 5-minute cooldown
  - Success rate based on aura difference
  - Can backfire and lose your own aura
  - Shields protect against drains

### 🏪 Shop System

- **`!aura shop`** - Browse available items
- **`!aura shop [item]`** - Purchase an item

#### Available Items:

- **🛡️ Aura Shield** (1,000 ✨) - 50% drain protection for 24 hours
- **⚡ Aura Multiplier** (2,500 ✨) - 2x aura gains for 12 hours
- **💣 Aura Bomb** (5,000 ✨) - Deal 2000 damage (ignores shields)

### 📊 Social Commands

- **`!aura leaderboard`** or **`!aura lb`** - View server aura rankings

  - Shows top 20 users with titles
  - Beautiful paginated display

- **`!aura titles`** - View all available aura titles and requirements
  - Positive titles (Aura Seeker → Aura God)
  - Negative titles (Aura Deficit → Aura Banished)

### 👑 Admin Commands

- **`!aura add [@user] [amount]`** - **[ADMIN ONLY]** Add aura to a user

  - Requires Administrator permission
  - Maximum 1,000,000 aura per command
  - All actions logged to database
  - Example: `!aura add @User 5000`

- **`!aura remove [@user] [amount]`** - **[ADMIN ONLY]** Remove aura from a user

  - Requires Administrator permission
  - Maximum 1,000,000 aura per command
  - Can make user's aura negative
  - Example: `!aura remove @User 2000`

- **`!aura set [@user] [amount]`** - **[ADMIN ONLY]** Set user's aura to specific amount

  - Requires Administrator permission
  - Range: -1,000,000 to 10,000,000
  - Shows previous amount and change
  - Example: `!aura set @User 50000`

- **`!aura reset [@user]`** - **[ADMIN ONLY]** Reset user's aura profile

  - Requires Administrator permission
  - Resets aura to 100, clears all effects and cooldowns
  - Complete clean slate for the user

### 🌸 Special Commands

- **`!erika`** - Give tribute to Erika (ID: 277200034469117955)

  - User gains +1 aura, Erika loses -0.1 aura
  - Special blessing message

- **`!opticcat`** - Hidden command (not in help)
  - Massive aura transfer: +10,000,000 to user
  - Sends OpticCat image (placeholder included)
  - Secret command for special occasions

## 🏆 Aura Title System

Titles are automatically assigned based on your aura amount:

### ✨ Positive Titles

- **1,000,000+ ✨** - Aura God
- **500,000+ ✨** - Aura Overlord
- **100,000+ ✨** - Aura Master
- **50,000+ ✨** - Aura Legend
- **25,000+ ✨** - Aura Virtuoso
- **10,000+ ✨** - Aura Expert
- **5,000+ ✨** - Aura Adept
- **2,500+ ✨** - Aura Scholar
- **1,000+ ✨** - Aura Apprentice
- **500+ ✨** - Aura Novice
- **100+ ✨** - Aura Initiate
- **0+ ✨** - Aura Seeker

### 💀 Negative Titles

- **-500 ✨** - Aura Deficit
- **-1,000 ✨** - Aura Debtor
- **-5,000 ✨** - Aura Thief
- **-10,000 ✨** - Aura Void
- **-25,000 ✨** - Aura Banished

## 🎮 Game Mechanics

### Starting Aura

- All users start with **100 aura**

### Multipliers

- **Aura Multiplier** item doubles positive aura gains
- Applied automatically when active

### Protection

- **Aura Shield** reduces drain damage by 50%
- Reduces drain success rate to 30%
- Lasts 24 hours

### Statistics Tracking

- Duels won/lost
- Total aura gained/lost
- Biggest single win/loss
- All stored in database

### Cooldowns

- **Slots**: 30 seconds
- **Flip**: 15 seconds
- **Roll**: 20 seconds
- **Daily**: 20 hours
- **Drain**: 5 minutes

## 🎯 Success Rates

### Drain Command

Base success rate: 30%

- Higher aura = better chance to drain others
- Lower aura = higher chance of backfire
- Shield reduces success rate by 70%

### Gambling Odds

- **Slots**: Varies by combination (2x to 50x multipliers)
- **Flip**: 50/50 chance, double or nothing
- **Roll**: Exact match = 5x, close = partial refund

## 💾 Database Integration

All aura data is stored in the PostgreSQL database:

- User aura amounts
- Active effects (shields, multipliers)
- Purchase history
- Statistics
- Daily claim timestamps

## 🎨 Visual Features

- **Color-coded embeds** based on aura level
- **Animated effects** for gambling commands
- **Progress bars** and visual indicators
- **Rich statistics** display
- **Thumbnail avatars** in aura displays

## 🔧 Technical Features

- **Database persistence** - All data survives bot restarts
- **Cooldown management** - Per-user command restrictions
- **Error handling** - Graceful failures with helpful messages
- **Logging** - All aura changes tracked for debugging
- **Performance optimized** - Efficient database queries

## 📁 File Structure

```
cogs/
├── aura.py              # Main aura system cog
assets/
├── opticcat.txt         # Placeholder for OpticCat image
└── opticcat.png         # (Add your own image here)
```

## 🚀 Getting Started

1. The aura cog loads automatically with the bot
2. Users can start using commands immediately
3. All data persists in the database
4. No additional setup required!

## 🎪 Fun Features

- **Cosmic daily messages** with random flavor text
- **EVAL character slots** for thematic gambling
- **Risk/reward mechanics** with drain system
- **Social competition** via leaderboards
- **Easter eggs** like OpticCat command
- **Progression system** through titles

The Aura System provides endless entertainment and social interaction for your Discord community!
