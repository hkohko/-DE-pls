import json
import aiohttp
from fuzzywuzzy import process
from collections import OrderedDict
import discord
escape = f'\n'

def del_db():
    global r_market
    del r_market

async def init_db():
    global r_market
    URL_market = r'https://api.warframe.market/v1/items'
    async with aiohttp.ClientSession() as session:
        async with session.get(URL_market) as market:
            r_market = await market.text()

async def query(entry):
    read = json.loads(r_market)
    payload = read['payload']
    _items = payload['items']

    list_of_query = []
    query_list = []

    embed = discord.Embed(
        colour=discord.Colour.dark_purple(),
        title="Query"
    )

    for i in _items:
        list_of_query.append(i['item_name'])

    output_query = process.extract(f'{entry}', list_of_query, limit=100)

    for i in output_query:
        if i[1] >= 80:
            query_list.append(f'{i[0]}')
    if len(query_list) == 0:
        embed.add_field(name=f"{entry}", value="No matching queries")
        return embed
    else:
        embed.add_field(name=f"{entry}", value=f"{escape.join(sorted(query_list))}")
        return embed

async def sell(entry):
    entry = entry.replace(' ', '').lower()
    read = json.loads(r_market)
    payload = read['payload']
    _items = payload['items']

    top = 5

    list_of_items = []

    for i in _items:
        list_of_items.append(i['url_name'])

    output = process.extractOne(f'{entry}', list_of_items)
    orders = f'https://api.warframe.market/v1/items/{output[0]}/orders'

    embed = discord.Embed(
    colour=discord.Colour.dark_purple(),
    title=f"Sell Orders: {str(output[0]).replace('_', ' ').title()}",
    url=f"https://warframe.market/items/{output[0]}"
)

    async def sell_order():
        async with aiohttp.ClientSession() as session:
            async with session.get(orders) as get_seller:
                read = await get_seller.text()
                return read
            
    r_orders = await (sell_order())
    read_orders = json.loads(r_orders)

    payload_orders = read_orders['payload']
    orders_market = payload_orders['orders']
    avglist = []
    enum = []
    display = []
    seller_dict = {}
    try:
        for i, j in enumerate(orders_market):
            seller = orders_market[i]['user']
            if j['order_type'] == 'sell':
                avglist.append(int(j["platinum"]))
        average = sum(avglist) / len(avglist)

        for i, j in enumerate(orders_market):
            seller = orders_market[i]['user']
            if j['order_type'] == 'sell' and int(j['platinum']) <= (average):
                if seller['status'] == 'ingame' or seller['status'] == 'online':
                    seller_dict[seller['ingame_name']] = [str(j['platinum']),  seller['status'], j['order_type']] #collect all buyers
    except ZeroDivisionError:
        embed.add_field(name="", value="```No price equal or below average```")
        return embed
    
    sorted_sellerdict = OrderedDict(sorted(seller_dict.items(), key=lambda t:int(t[1][0]), reverse=False)) #1 = refer to the list, 0 = first value in that list
    list_seller = list(sorted_sellerdict.items()) #IMPORTAAAAAAANT for enabling indexing
    for j, i in enumerate(list_seller):
        display.append(f'{i[0]} ({i[1][1]}): is {i[1][2]}ing for {i[1][0]}\n')
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

async def buy(entry):
    entry = entry.replace(' ', '').lower()
    read = json.loads(r_market)
    payload = read['payload']
    _items = payload['items']

    top = 5

    list_of_items = []

    for i in _items:
        list_of_items.append(i['url_name'])

    output = process.extractOne(f'{entry}', list_of_items)

    orders = f'https://api.warframe.market/v1/items/{output[0]}/orders'

    embed = discord.Embed(
    colour=discord.Colour.dark_purple(),
    title=f"Buy Orders: {str(output[0]).replace('_', ' ').title()}",
    url=f"https://warframe.market/items/{output[0]}"
)
    async def buy_order():
        async with aiohttp.ClientSession() as session:
            async with session.get(orders) as get_buyer:
                read = await get_buyer.text()
                return read
            
    r_orders = await buy_order()
    read_orders = json.loads(r_orders)

    payload_orders = read_orders['payload']
    orders_market = payload_orders['orders']
    avglist = []
    buyer_dict = {}
    enum = []
    display = []
    try:
        for i, j in enumerate(orders_market):
            seller = orders_market[i]['user']
            if j['order_type'] == 'buy':
                avglist.append(int(j["platinum"]))
        average = sum(avglist) / len(avglist)

        for i, j in enumerate(orders_market):
            seller = orders_market[i]['user']
            if j['order_type'] == 'buy' and int(j['platinum']) > (average):
                if seller['status'] == 'ingame' or seller['status'] == 'online':
                    buyer_dict[seller['ingame_name']] = [str(j['platinum']),  seller['status'], j['order_type']] #collect all buyers
    except ZeroDivisionError:
        embed.add_field(name="", value="```No price equal or above average```")
        return embed
    sorted_buyerdict = OrderedDict(sorted(buyer_dict.items(), key=lambda t:int(t[1][0]), reverse=True)) #1 = refer to the list, 0 = first value in that list
    list_buyer = list(sorted_buyerdict.items()) #IMPORTANT for enabling indexing
    for j, i in enumerate(list_buyer):
        display.append(f'{i[0]} ({i[1][1]}): is {i[1][2]}ing for {i[1][0]}\n')
        enum.append(j)
        if len(enum) == top:
            break
    if len(list_buyer) == 0:
        embed.add_field(name="", value="No price equal or below average")
        embed.set_footer(text=f"Average Price: {average} (warframe.market)")
        return embed
    else:
        embed.add_field(name="Showing Top 5 Results", value=f"```{''.join(display)}```")
        embed.set_footer(text=f"Average Price: {average} (warframe.market)")
        return embed