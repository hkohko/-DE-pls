import json
import asyncio
import aiohttp
from fuzzywuzzy import process
from collections import OrderedDict
import api_get.leven_search as leven
import discord

escape = f"\n"

header_def = {"Platform": "pc"}
header_xbox = {"Platform": "xbox"}
header_ps = {"Platform": "ps4"}
header_switch = {"Platform": "switch"}


class market_sell(discord.ui.View):
    def __init__(self, entry):
        super().__init__()
        self.value = None
        self.entry = entry

    async def send(self, ctx):
        result = asyncio.create_task(sell(self.entry, header_def))
        self.message = await ctx.send(embed=await result, view=self)

    @discord.ui.button(label="PC", style=discord.ButtonStyle.green)
    async def pc(self, interaction: discord.Interaction, button: discord.ui.Button):
        result = asyncio.create_task(sell(self.entry, header_def))
        await interaction.response.edit_message(embed=await result)

    @discord.ui.button(label="XBOX", style=discord.ButtonStyle.green)
    async def xbox(self, interaction: discord.Interaction, button: discord.ui.Button):
        result = asyncio.create_task(sell(self.entry, header_xbox))
        await interaction.response.edit_message(embed=await result)

    @discord.ui.button(label="Playstation", style=discord.ButtonStyle.green)
    async def ps(self, interaction: discord.Interaction, button: discord.ui.Button):
        result = asyncio.create_task(sell(self.entry, header_ps))
        await interaction.response.edit_message(embed=await result)

    @discord.ui.button(label="Switch", style=discord.ButtonStyle.green)
    async def switch(self, interaction: discord.Interaction, button: discord.ui.Button):
        result = asyncio.create_task(sell(self.entry, header_switch))
        await interaction.response.edit_message(embed=await result)


class market_buy(discord.ui.View):
    def __init__(self, entry):
        super().__init__()
        self.value = None
        self.entry = entry

    async def send(self, ctx):
        result = asyncio.create_task(buy(self.entry, header_def))
        self.message = await ctx.send(embed=await result, view=self)

    @discord.ui.button(label="PC", style=discord.ButtonStyle.green)
    async def pc(self, interaction: discord.Interaction, button: discord.ui.Button):
        result = asyncio.create_task(buy(self.entry, header_def))
        await interaction.response.edit_message(embed=await result)

    @discord.ui.button(label="XBOX", style=discord.ButtonStyle.green)
    async def xbox(self, interaction: discord.Interaction, button: discord.ui.Button):
        result = asyncio.create_task(buy(self.entry, header_xbox))
        await interaction.response.edit_message(embed=await result)

    @discord.ui.button(label="Playstation", style=discord.ButtonStyle.green)
    async def ps(self, interaction: discord.Interaction, button: discord.ui.Button):
        result = asyncio.create_task(buy(self.entry, header_ps))
        await interaction.response.edit_message(embed=await result)

    @discord.ui.button(label="Switch", style=discord.ButtonStyle.green)
    async def switch(self, interaction: discord.Interaction, button: discord.ui.Button):
        result = asyncio.create_task(buy(self.entry, header_switch))
        await interaction.response.edit_message(embed=await result)


class DB:
    async def init_db(self):
        URL_market = r"https://api.warframe.market/v1/items"
        async with aiohttp.ClientSession() as session:
            async with session.get(URL_market) as market:
                self.r_market = await market.text()

    async def del_db(self):
        del self.r_market


db = DB()


async def initialize():
    await db.init_db()


async def clear_db():
    await db.del_db()


async def query(entry):
    read = json.loads(db.r_market)
    payload = read["payload"]
    _items = payload["items"]

    list_of_query = []
    query_list = []

    embed = discord.Embed(colour=discord.Colour.dark_purple(), title="Query")

    for i in _items:
        list_of_query.append(i["item_name"])

    output_query = process.extract(f"{entry}", list_of_query, limit=100)

    for i in output_query:
        if i[1] >= 80:
            query_list.append(f"{i[0]}")
    if len(query_list) == 0:
        embed.add_field(name=f"{entry}", value="No matching queries")
        return embed
    else:
        embed.add_field(name=f"{entry}", value=f"{escape.join(sorted(query_list))}")
        return embed


async def sell(entry, header):
    entry = entry.replace(" ", "").lower()
    read = json.loads(db.r_market)
    payload = read["payload"]
    _items = payload["items"]

    header_chk = header["Platform"]
    header_url = f"{header_chk}."
    if header_chk == "pc":
        header_url = ""

    top = 5

    list_of_items = []

    for i in _items:
        list_of_items.append(i["url_name"])
    output = await leven.fsearch(entry, list_of_items)
    orders = f"https://api.warframe.market/v1/items/{output}/orders"

    embed = discord.Embed(
        colour=discord.Colour.dark_purple(),
        title=f"({header_chk.upper()}) Sell Orders: {str(output).replace('_', ' ').title()}",
        url=f"https://{header_url}warframe.market/items/{output}",
    )

    async def sell_order():
        async with aiohttp.ClientSession(headers=header) as session:
            async with session.get(orders) as get_seller:
                read = await get_seller.text()
                return read

    r_orders = await sell_order()
    read_orders = json.loads(r_orders)

    payload_orders = read_orders["payload"]
    orders_market = payload_orders["orders"]
    avglist = []
    enum = []
    display = []
    seller_dict = {}

    try:
        for i, j in enumerate(orders_market):
            seller = orders_market[i]["user"]
            if j["order_type"] == "sell":
                avglist.append(int(j["platinum"]))
        average = sum(avglist) / len(avglist)
    except ZeroDivisionError:
        embed.add_field(name="", value="```No price equal or below average```")
        return embed

    for i, j in enumerate(orders_market):
        seller = orders_market[i]["user"]
        if j["order_type"] == "sell" and int(j["platinum"]) <= (average):
            if seller["status"] == "ingame" or seller["status"] == "online":
                seller_dict[seller["ingame_name"]] = [
                    str(j["platinum"]),
                    seller["status"],
                    j["order_type"],
                ]

    sorted_sellerdict = OrderedDict(
        sorted(seller_dict.items(), key=lambda t: int(t[1][0]), reverse=False)
    )
    list_seller = list(sorted_sellerdict.items())
    for j, i in enumerate(list_seller):
        display.append(f"{i[0]} ({i[1][1]}): is {i[1][2]}ing for {i[1][0]}\n")
        enum.append(j)
        if len(enum) == top:
            break
    if len(list_seller) == 0:
        embed.add_field(name="", value="No price equal or below average")
        embed.set_footer(text=f"Average Price: {average} (warframe.market)")
        return embed
    else:
        embed.add_field(name="Showing Top 5 Results", value=f"```{''.join(display)}```")
        embed.set_footer(text=f"Average Price: {average} (warframe.market)")
        return embed


async def buy(entry, header):
    entry = entry.replace(" ", "").lower()
    read = json.loads(db.r_market)
    payload = read["payload"]
    _items = payload["items"]

    header_chk = header["Platform"]
    header_url = f"{header_chk}."
    if header_chk == "pc":
        header_url = ""

    top = 5

    list_of_items = []

    for i in _items:
        list_of_items.append(i["url_name"])

    output = await leven.fsearch(entry, list_of_items)
    orders = f"https://api.warframe.market/v1/items/{output}/orders"

    embed = discord.Embed(
        colour=discord.Colour.dark_purple(),
        title=f"({header_chk.upper()}) Buy Orders: {str(output).replace('_', ' ').title()}",
        url=f"https://{header_url}warframe.market/items/{output}",
    )

    async def buy_order():
        async with aiohttp.ClientSession(headers=header) as session:
            async with session.get(orders) as get_buyer:
                read = await get_buyer.text()
                return read

    r_orders = await buy_order()
    read_orders = json.loads(r_orders)

    payload_orders = read_orders["payload"]
    orders_market = payload_orders["orders"]
    avglist = []
    buyer_dict = {}
    enum = []
    display = []
    try:
        for i, j in enumerate(orders_market):
            seller = orders_market[i]["user"]
            if j["order_type"] == "buy":
                avglist.append(int(j["platinum"]))
        average = sum(avglist) / len(avglist)
    except ZeroDivisionError:
        embed.add_field(name="", value="```No price equal or above average```")
        return embed
    for i, j in enumerate(orders_market):
        seller = orders_market[i]["user"]
        if j["order_type"] == "buy" and int(j["platinum"]) > (average):
            if seller["status"] == "ingame" or seller["status"] == "online":
                buyer_dict[seller["ingame_name"]] = [
                    str(j["platinum"]),
                    seller["status"],
                    j["order_type"],
                ]

    sorted_buyerdict = OrderedDict(
        sorted(buyer_dict.items(), key=lambda t: int(t[1][0]), reverse=True)
    )
    list_buyer = list(sorted_buyerdict.items())
    for j, i in enumerate(list_buyer):
        display.append(f"{i[0]} ({i[1][1]}): is {i[1][2]}ing for {i[1][0]}\n")
        enum.append(j)
        if len(enum) == top:
            break
    if len(list_buyer) == 0:
        embed.add_field(name="", value="No price equal or above average")
        embed.set_footer(text=f"Average Price: {average} (warframe.market)")
        return embed
    else:
        embed.add_field(name="Showing Top 5 Results", value=f"```{''.join(display)}```")
        embed.set_footer(text=f"Average Price: {average} (warframe.market)")
        return embed
