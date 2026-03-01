import discord
from discord.ext import commands
import asyncio
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Bot setup
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Owner ID - get from environment variable or set directly
OWNER_ID = int(os.getenv('OWNER_ID', '1193907780793409610'))  # Replace with your ID

def is_owner():
    async def predicate(ctx):
        return ctx.author.id == OWNER_ID
    return commands.check(predicate)

@bot.event
async def on_ready():
    print(f'✅ {bot.user} has connected to Discord!')
    print(f'📊 Bot is in {len(bot.guilds)} servers')
    
    # Set bot status
    await bot.change_presence(activity=discord.Game(name="!help | Mass DM Bot"))

@bot.command(name='massdm')
@is_owner()
async def mass_dm(ctx, guild_id: int, *, message: str):
    """DMs all members of a specific server"""
    
    guild = bot.get_guild(guild_id)
    if not guild:
        await ctx.send("❌ Could not find a server with that ID!")
        return
    
    # Filter out bots
    members = [m for m in guild.members if not m.bot]
    member_count = len(members)
    
    # Confirmation
    confirm_msg = await ctx.send(
        f"⚠️ **Warning**\n"
        f"This will DM **{member_count}** members in **{guild.name}**.\n"
        f"Type `CONFIRM` within 30 seconds to proceed."
    )
    
    def check(m):
        return m.author == ctx.author and m.content == "CONFIRM"
    
    try:
        await bot.wait_for('message', timeout=30.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send("❌ Mass DM cancelled (timeout).")
        return
    
    status_msg = await ctx.send(f"📨 Starting mass DM to {member_count} members...")
    
    success_count = 0
    failed_count = 0
    failed_users = []
    
    for member in members:
        try:
            await member.send(message)
            success_count += 1
            
            if success_count % 10 == 0:
                await status_msg.edit(content=f"📨 Progress: {success_count}/{member_count} DMs sent...")
            
            await asyncio.sleep(1)  # Rate limiting delay
            
        except discord.Forbidden:
            failed_count += 1
            failed_users.append(f"{member.name}#{member.discriminator}")
        except Exception as e:
            failed_count += 1
            failed_users.append(f"{member.name}#{member.discriminator}")
    
    report = (
        f"✅ **Mass DM Complete!**\n"
        f"📊 **Statistics:**\n"
        f"• Successfully sent: {success_count}\n"
        f"• Failed: {failed_count}\n"
    )
    
    await status_msg.edit(content=report)

@bot.command(name='servers')
@is_owner()
async def list_servers(ctx):
    """Lists all servers the bot is in"""
    embed = discord.Embed(title="Bot's Servers", color=discord.Color.blue())
    
    for guild in bot.guilds:
        member_count = len([m for m in guild.members if not m.bot])
        embed.add_field(
            name=guild.name,
            value=f"ID: {guild.id}\nMembers: {member_count}",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command(name='ping')
async def ping(ctx):
    """Check bot latency"""
    await ctx.send(f'Pong! 🏓 Latency: {round(bot.latency * 1000)}ms')

# Error handling
@mass_dm.error
async def mass_dm_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("❌ This command can only be used by the bot owner!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Usage: `!massdm [guild_id] [message]`")
    else:
        await ctx.send(f"❌ An error occurred: {str(error)}")

# Run the bot
if __name__ == "__main__":
    token = os.getenv('MTQ3NzUyMzE1ODI5MzgwNzEyNQ.G-Ygl7.T2zDRI5Foez1Ns3jUFVynqS9WghNGENZnL_88I')
    if not token:
        print("❌ Error: BOT_TOKEN not found in environment variables!")
        exit(1)
    
    bot.run(token)