import nest_asyncio

nest_asyncio.apply()
import asyncio
import datetime
import os
import random

import discord
import psutil
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix="$", intents=intents)
start_time = datetime.datetime.now()


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    send_daily_embed.start()


@tasks.loop(hours=24)
async def send_daily_embed():
    current_time = datetime.datetime.now()
    current_date = current_time.strftime("%d.%m.")
    funk_int = random.randint(100, 1000)
    gps_int = random.randint(100, 1000)

    funk_channel_id = int(os.environ.get("FUNK_CHANNEL_ID"))
    gps_channel_id = int(os.environ.get("GPS_CHANNEL_ID"))

    funk_channel = client.get_channel(funk_channel_id)
    gps_channel = client.get_channel(gps_channel_id)

    if funk_channel:
        funk_text = f"{current_date} - **{funk_int}** Mhz"
        funk_embed = discord.Embed(title="Funk", description=funk_text, color=0xFFC0CB)
        await funk_channel.send(embed=funk_embed)

    if gps_channel:
        gps_text = f"{current_date} - **{gps_int}** Mhz"
        gps_embed = discord.Embed(title="GPS", description=gps_text, color=0xFFC0CB)
        await gps_channel.send(embed=gps_embed)


@commands.cooldown(1, 5, commands.BucketType.user)  # 1 use per 5 seconds per user
@client.command()
async def hello(ctx):
    await ctx.send("Hello!")


@hello.error
async def hello_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        cooldown = error.retry_after
        await ctx.send(
            f"This command is on cooldown. Please try again in {cooldown:.2f} seconds."
        )


async def get_resource_usage():
    # Get resource usage
    cpu_percent, ram_usage, net_io_counters = await asyncio.gather(
        psutil.cpu_percent(),
        psutil.virtual_memory().percent,
        psutil.net_io_counters()
    )
    return cpu_percent, ram_usage, net_io_counters

def format_size(size):
    # Format the size in bytes to a human-readable format
    power = 2 ** 10
    n = 0
    size_labels = ["B", "KB", "MB", "GB", "TB", "PB"]
    while size > power:
        size /= power
        n += 1
    return f"{round(size, 2)} {size_labels[n]}"


@client.event
async def on_keyboard_interrupt():
    print("Keyboard interrupt detected")
    await client.close()


@client.command()
async def send_embeds(ctx):
    if send_daily_embed.is_running():
        await ctx.send("The daily embeds task is already running.")
    else:
        send_daily_embed.start()
        await ctx.send("The daily embeds task has been started.")


async def start_bot():
    try:
        await client.start(os.environ.get("BOT_TOKEN"))
    except discord.errors.LoginFailure:
        print("Invalid token")
    except KeyboardInterrupt:
        print("Keyboard interrupt detected")
        await client.close()


# Run the bot
loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(start_bot())
except KeyboardInterrupt:
    print("Keyboard interrupt detected")
finally:
    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()
