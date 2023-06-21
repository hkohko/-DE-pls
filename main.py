import os
import discord
import asyncio
from dotenv import load_dotenv
from discord.ext import commands
import api_get.market as market
import api_get.warframe as warframe
import api_get.timer as world_time
import help_commands
import api_get.warframe_items as wf_items
import query.query_incarnon as query_incarnon

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=",", intents=intents, help_command=None)


@bot.event
async def on_ready():
    print("bot is running")
    await bot.change_presence(activity=discord.Game(name=",help"))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Field cannot be empty, type `,help`")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.startswith(",DE"):
        await message.channel.send("pls")
    await bot.process_commands(message)


@bot.command()
@commands.is_owner()
async def db(ctx):
    await market.clear_db()
    await warframe.clear_db()
    await ctx.send("Cleared market&warframe db")
    await asyncio.gather(
        market.initialize(), warframe.initialize(), wf_items.get_data()
    )
    await wf_items.write_data()
    await warframe.fprogen.update()
    await ctx.send("Finished updating")


@bot.command()
async def help(ctx, *, entry="list"):
    result = asyncio.create_task(help_commands.helpcommand(entry))
    await ctx.send(await result)


@bot.command()
async def timer(ctx):
    result = asyncio.create_task(world_time.timer())
    await ctx.send(embed=await result)


@bot.command()
async def q(ctx, *, entry):
    result = asyncio.create_task(market.query(entry))
    await ctx.send(embed=await result)


@bot.command()
async def sell(ctx, *, entry):
    view = market.market_sell(entry)
    await view.send(ctx)


@bot.command()
async def buy(ctx, *, entry):
    view = market.market_buy(entry)
    await view.send(ctx)


@bot.command()
async def mod(ctx, *, var):
    result_mod = asyncio.create_task(warframe.mod(var))
    await ctx.send(embed=await result_mod)


@bot.command()
async def weapon(ctx, *, var):
    result = asyncio.create_task(warframe.weapon(var))
    await ctx.send(embed=await result)


@bot.command()
async def frame(ctx, *, var):
    result = asyncio.create_task(warframe.frame(var))
    await ctx.send(embed=await result)


@bot.command()
async def wiki(ctx, *, entry):
    result = await asyncio.create_task(wf_items.wiki(entry))
    await ctx.send(embed=result)


@bot.command()
async def progenitor(ctx, *, entry):
    result = await asyncio.create_task(warframe.progenitor_cmd.qpg(entry))
    await ctx.send(embed=result)


@bot.command()
async def incarnon(ctx):
    result = await asyncio.create_task(query_incarnon.incarnon.incarnon_cmd())
    await ctx.send(embed=result)


async def execute():
    await warframe.initialize()
    await market.initialize()
    await wf_items.get_data()
    await wf_items.write_data()
    await wf_items.initialize()


asyncio.run(execute())
load_dotenv()
bot.run(os.getenv("BOT_TOKEN"))
