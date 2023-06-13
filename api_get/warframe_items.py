import aiohttp
import json
import aiofiles
import discord
from Levenshtein import ratio

URL = 'https://api.warframestat.us/items/'
folder = 'wiki'


async def get_data():
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as items:
            async with aiofiles.open(f'{folder}/items.json', 'w', encoding='ascii', errors='ignore') as f:
                r = await items.text()
                await f.write(r)


async def write_data():
    async with aiofiles.open(f'{folder}/items.json', 'r') as f:
        r = await f.read()

    r = json.loads(r)

    dict_items = {}
    list_items = []

    async with aiofiles.open(f'{folder}/item_name.json', 'w', errors='ignore') as names:
        for i in range(len(r)):
            dict_items[f'{r[i]["name"]}'] = i
        names_json = json.dumps(dict_items)
        await names.write(names_json)

    async with aiofiles.open(f'{folder}/fsearch_item.json', 'w', errors='ignore') as fsearch:
        for i in range(len(r)):
            list_items.append(r[i]['name'])
        fsearch_json = json.dumps(list_items)
        await fsearch.write(fsearch_json)


async def fsearch(var):
    async with aiofiles.open(f'{folder}/fsearch_item.json', 'r', errors='ignore') as f:
        r = await f.read()

    choices = json.loads(r)
    cutoff = 0.55
    candidates = {}

    for i in choices:
        score = ratio(var, i)
        if score > cutoff:
            candidates[i] = score

    try:
        return max(candidates, key=candidates.get)
    except ValueError:
        pass


async def wiki(var):

    entry = await fsearch(str(var).title())
 
    async with aiofiles.open(f'{folder}/item_name.json', 'r', errors='ignore') as names:
        item_keys = json.loads(await names.read())
        async with aiofiles.open(f'{folder}/items.json', 'r') as f:
            keys = json.loads(await f.read())
            try:
                url_api = keys[item_keys[entry]]['wikiaUrl']
                embed = discord.Embed(
                colour=discord.Colour.dark_purple(),
                title=f"{entry}",
                url=url_api
                )
                
                return embed
            
            except KeyError:
                embed = discord.Embed(
                colour=discord.Colour.dark_purple(),
                title=f"{entry}",
                url=f"https://warframe.fandom.com/wiki/{entry.replace(' ', '_')}"
                )

                return embed