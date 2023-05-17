import aiohttp
import asyncio
import discord
from fuzzywuzzy import process
from bs4 import BeautifulSoup
import api_get.comp_pol as comp_pol
# import comp_pol
escape = f'\n'

def del_db():
  global wf_item, wf_mod, wf_frames, wf_wep, _names
  del wf_item, wf_mod, wf_frames, wf_wep, _names

async def get_db(URL):
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as response:
            response_json = await response.json()
    return response_json

async def init_db():
    global wf_item, wf_mod, wf_frames, wf_wep, _names
    URL = f'https://api.warframestat.us/items/'
    URL_mod = f'https://api.warframestat.us/mods/'
    URL_frames = f'https://api.warframestat.us/warframes/'
    URL_wep = f'https://api.warframestat.us/weapons/'

    r = get_db(URL)
    r_mod = get_db(URL_mod)
    r_frames = get_db(URL_frames)
    r_wep = get_db(URL_wep)

    r, r_mod, r_frames, r_wep = await asyncio.gather(r, r_mod, r_frames, r_wep)

    wf_item = r
    wf_mod = r_mod
    wf_frames = r_frames
    wf_wep = r_wep
    _names = [wf_item[i]['name'] for i, j in enumerate(wf_item)]

async def weapons_db():
    global weapondb
    weapondb = {}
    for i, _ in enumerate(wf_wep):
        name = wf_wep[i]["name"]
        weapondb[name] = i

async def frames_db():
    global framedb
    framedb = {}
    for i, _ in enumerate(wf_frames):
        name = wf_frames[i]["name"]
        framedb[name] = i

async def mod_db():
    global moddb
    moddb = {}
    for i, _ in enumerate(wf_mod):
        name = wf_mod[i]["name"]
        moddb[name] = i

async def fsearch(entry):
    a = process.extractOne(entry, _names)
    return a[0]

async def wfmod(img):
    webpage = f'https://warframe.fandom.com/wiki/{img}'.replace(" ", "_")
    async def get_image():
        async with aiohttp.ClientSession() as session:
            async with session.get(webpage) as page:
                return await page.text()
            
    source = await get_image()

    soup = BeautifulSoup(source, 'lxml')

    sidebar = soup.find(
        'aside',
        class_=
        'portable-infobox pi-background pi-border-color pi-theme-wikia pi-layout-default'
    )
    img = sidebar.find('a', class_='image image-thumbnail').get('href')
    return (img)

async def mod(var):
    await mod_db()
    display = []
    entry_mod = await fsearch(var)
    num = moddb[entry_mod]
    embed = discord.Embed(
        colour=discord.Colour.dark_purple(),
        title=f"{entry_mod}",
        url=f"{wf_mod[num]['wikiaUrl']}"
    )
    try:
        embed.set_thumbnail(url=f"{wf_mod[num]['wikiaThumbnail']}")
    except KeyError:
        embed.set_thumbnail(url=f"{await wfmod(entry_mod)}")


    enum = []

    try:
        if wf_mod[num]['name'] == entry_mod:
            if wf_mod[num].get('drops') == None:
                embed.add_field(name="Showing the first 10 locations:", value=f"```Drop table data unavailable```")
                return embed
            else:
                display.append('```')
                for y, x in enumerate(wf_mod[num]['drops']):
                    display.append(f"- {x['location']}")
                    enum.append(y)
                    if len(enum) == 10:
                        break
                display.append(f'```')
    except KeyError:
        pass

    embed.add_field(name="Showing the first 10 locations:", value=f"{escape.join(display)}")
    return embed

async def weapon(var):
    await weapons_db()
    entry = await fsearch(var)
    num = weapondb[entry]
    embed = discord.Embed(
    colour=discord.Colour.dark_purple(),
    title=f"{entry}",
    url=f"{wf_wep[num]['wikiaUrl']}",
)
    embed.set_thumbnail(url=f"{wf_wep[num]['wikiaThumbnail']}")
    display = []
    dmg = []
    try:
        if wf_wep[num]['name'] == entry:

            for j in wf_wep[num]['attacks']:

                embed.add_field(name=f"{j['name']}", value=f"Crit. Chance\n{j['crit_chance']}%\nCrit. Damage\n{j['crit_mult']}x\nStat. Chance\n{j['status_chance']}%")

                dmg_dict = j['damage']
                for key in dmg_dict:
                    display.append(f'{key} - {dmg_dict[key]}')
                    dmg.append(dmg_dict[key])

                total_dmg = int(sum(dmg))

                embed.add_field(name=f"Damage", value=f"{escape.join(display)}")
                embed.add_field(name="Total Damage", value=f"{total_dmg}")

                display.clear()
                dmg_dict.clear()
                dmg.clear()

    except KeyError:
        embed.add_field(name="Value not found", value="")
        return  embed
    return embed

async def frame(var):

    await frames_db()

    entry = await fsearch(var)
    num = framedb[entry]

    embed = discord.Embed(
    colour=discord.Colour.dark_purple(),
    title=f"{entry}",
    url=f"{wf_frames[num]['wikiaUrl']}",
)
    embed.set_thumbnail(url=f"{wf_frames[num]['wikiaThumbnail']}")
    
    try:

        embed.add_field(name=f"Stats at Rank 30:", value=f"Armor - {wf_frames[num]['armor']}\nShield - {wf_frames[num]['shield']*3}\nHealth - {wf_frames[num]['health']*3}\nEnergy - {int(wf_frames[num]['power']*1.5)}")

    except KeyError:
        
        embed.add_field(name=f"Stats at Rank 30:", value=f"Armor - {wf_frames[num]['armor']}\nShield - {wf_frames[num]['shield']*3}\nHealth - {wf_frames[num]['health']*3}\nEnergy - {int(wf_frames[num]['power']*1.5)}")

    return embed