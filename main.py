import os
from typing import Optional
import discord
import asyncio
from dotenv import load_dotenv
from discord.ext import commands
import api_get.market as market
import api_get.warframe as warframe
import api_get.timer as world_time
import help_commands

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print('bot is running')
    await bot.change_presence(activity=discord.Game(name=",wfhelp list"))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Field cannot be empty, type `,wfhelp [command]` for usage')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.startswith(',DE'):
        await message.channel.send('pls')
    await bot.process_commands(message)

@bot.command()
async def wfhelp(ctx, *, entry):
    result = asyncio.create_task(help_commands.helpcommand(entry))
    await ctx.send(await result)
    
@bot.command()
async def db(ctx):
    market.del_db()
    warframe.del_db()
    await ctx.send('Cleared db')
    await market.init_db()
    await warframe.init_db()
    await ctx.send('Finished updating')

@bot.command()
async def timer(ctx):
    result = asyncio.create_task(world_time.timer())
    await ctx.send(embed = await result)

@bot.command()
async def q(ctx, *, entry):
    result = asyncio.create_task(market.query(entry))
    await ctx.send(embed = await result)

@bot.command()
async def sell(ctx, *, entry):
    view = market.market_sell(entry)
    await ctx.send(view=view)

@bot.command()
async def buy(ctx, *, entry):
    view = market.market_buy(entry)
    await ctx.send(view=view)

@bot.command()
async def mod(ctx, *, var):
    result_mod = asyncio.create_task(warframe.mod(var))
    await ctx.send(embed = await result_mod)

@bot.command()
async def weapon(ctx, *, var):
    result = asyncio.create_task(warframe.weapon(var))
    await ctx.send(embed = await result)

@bot.command()
async def frame(ctx, *, var):
    result = asyncio.create_task(warframe.frame(var))
    await ctx.send(embed = await result)

asyncio.run(warframe.init_db())
asyncio.run(market.init_db())
load_dotenv()
bot.run(os.getenv("BOT_TOKEN"))
