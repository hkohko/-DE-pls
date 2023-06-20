import aiohttp
import aiofiles
import asyncio
import discord
import json
from bs4 import BeautifulSoup
import api_get.leven_search as leven
import api_get.progenitor_wf as progenitor
import query.query_frames as query_frames

escape = '\n'


class WF_init:
    async def init_db(self):
        URL = f'https://api.warframestat.us/items/'
        URL_mod = f'https://api.warframestat.us/mods/'
        URL_frames = f'https://api.warframestat.us/warframes/'
        URL_wep = f'https://api.warframestat.us/weapons/'

        r = get_db(URL)
        r_mod = get_db(URL_mod)
        r_frames = get_db(URL_frames)
        r_wep = get_db(URL_wep)

        r, r_mod, r_frames, r_wep = await asyncio.gather(r, r_mod, r_frames, r_wep)

        self.wf_item = r
        self.wf_mod = r_mod
        self.wf_frames = r_frames
        self.wf_wep = r_wep
        self._names = [self.wf_item[i]['name'] for i, _ in enumerate(self.wf_item)]

    async def del_db(self):
        del self.wf_item, self.wf_mod, self.wf_frames, self.wf_wep, self._names


class Lookup:
    async def weapons_db(self):
        self.weapondb = {}
        for i, _ in enumerate(wf_init.wf_wep):
            name = wf_init.wf_wep[i]["name"]
            self.weapondb[name] = i

    async def frames_db(self):
        self.framedb = {}
        for i, _ in enumerate(wf_init.wf_frames):
            name = wf_init.wf_frames[i]["name"]
            self.framedb[name] = i

    async def mod_db(self):
        self.moddb = {}
        for i, _ in enumerate(wf_init.wf_mod):
            name = wf_init.wf_mod[i]["name"]
            self.moddb[name] = i
    

class ProgenitorCommand:
    def __init__(self):
        element_img_dict = {
            'Toxin': r'https://static.wikia.nocookie.net/warframe/images/f/f1/ToxinModBundleIcon.png/revision/latest?cb=20191103222538'
            , 'Cold': r'https://static.wikia.nocookie.net/warframe/images/c/c9/ColdModBundleIcon.png/revision/latest?cb=20191103222451'
            , 'Heat': r'https://static.wikia.nocookie.net/warframe/images/4/4a/HeatModBundleIcon.png/revision/latest?cb=20191103222525'
            , 'Electricity': r'https://static.wikia.nocookie.net/warframe/images/8/86/ElectricModBundleIcon.png/revision/latest?cb=20191103222514'
            , 'Magnetic': r'https://static.wikia.nocookie.net/warframe/images/e/ea/EssentialMagneticGlyph.png/revision/latest?cb=20191015193508'
            , 'Radiation': r'https://static.wikia.nocookie.net/warframe/images/6/6a/EssentialRadiationGlyph.png/revision/latest?cb=20191015193509'
            , 'Impact': r'https://static.wikia.nocookie.net/warframe/images/c/cc/EssentialImpactGlyph.png/revision/latest?cb=20210326161740'
        }
        self.element_img = element_img_dict

    async def storeinfo(self):
        async with aiofiles.open('wiki/progenitor.json') as file:
            self.info = json.loads(await file.read())

    async def qpg(self, entry):
        entry = entry.strip()
        elementlist = list(progenitor.q_progenitor.set_values)
        entry = await leven.fsearch(entry, elementlist)
        progenitor_list = []
        for i in self.info.items():
            if i[1] == entry:
                progenitor_list.append(i[0])
        embed = discord.Embed(
        colour=discord.Colour.dark_purple(),
        title=f"Progenitors: {entry}",
        url=r'https://warframe.fandom.com/wiki/Kuva_Lich/Progenitor'
        )
        embed.add_field(name='', value=f"{escape.join(progenitor_list)}")
        embed.set_thumbnail(url=self.element_img[entry])
        return embed
    

class Frame_Progen:
    async def initialize(self):
        await query_frames.init_query_frames()
        await progenitor.progenitor_wf_start()
        self.progenlist = progenitor.framepy.getprogenitor

    async def update(self):
        self.progenlist.clear()
        print('Cleared self.progenlist')
        await progenitor.progenitor_wf_start(True)
        self.progenlist = progenitor.framepy.getprogenitor


wf_init = WF_init()    
lookup = Lookup()
fprogen = Frame_Progen()
progenitor_cmd = ProgenitorCommand()


async def initialize():
    await wf_init.init_db()


async def clear_db():
    await wf_init.del_db()


asyncio.run(fprogen.initialize())
asyncio.run(progenitor_cmd.storeinfo())


async def get_db(URL):
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as response:
            response_json = await response.json()
    return response_json


async def wiki_image(img):
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
    await lookup.mod_db()

    display = []

    entry_mod = await leven.fsearch(var, wf_init._names)
    num = lookup.moddb[entry_mod]
    embed = discord.Embed(
        colour=discord.Colour.dark_purple(),
        title=f"{entry_mod}",
        url=f"{wf_init.wf_mod[num]['wikiaUrl']}"
    )

    try:
        embed.set_thumbnail(url=f"{wf_init.wf_mod[num]['wikiaThumbnail']}")
    except KeyError:
        embed.set_thumbnail(url=f"{await wiki_image(entry_mod)}")

    enum = []

    try:
        if wf_init.wf_mod[num]['name'] == entry_mod:
            if wf_init.wf_mod[num].get('drops') == None:
                embed.add_field(name="Showing the first 10 locations:", value=f"```Drop table data unavailable```")
                return embed
            else:
                display.append('```')
                for y, x in enumerate(wf_init.wf_mod[num]['drops']):
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
    await lookup.weapons_db()
    entry = await leven.fsearch(var, wf_init._names)
    num = lookup.weapondb[entry]
    embed = discord.Embed(
    colour=discord.Colour.dark_purple(),
    title=f"{entry}",
    url=f"{wf_init.wf_wep[num]['wikiaUrl']}",
    )

    try:
        embed.set_thumbnail(url=f"{wf_init.wf_wep[num]['wikiaThumbnail']}")
    except KeyError:
        embed.set_thumbnail(url=f"{await wiki_image(entry)}")

    display = []
    dmg = []
    try:
        if wf_init.wf_wep[num]['name'] == entry:
            for j in wf_init.wf_wep[num]['attacks']:
                embed.add_field(name=f"{j['name']}", value=f"Crit. Chance\n{j['crit_chance']}%\nCrit. Damage\n{j['crit_mult']}x\nStat. Chance\n{j['status_chance']}%")

                dmg_dict = j['damage']
                for key in dmg_dict:
                    display.append(f'{key} - {dmg_dict[key]}')
                    dmg.append(dmg_dict[key])

                total_dmg = int(sum(dmg))

                embed.add_field(name=f"Damage: {total_dmg}", value=f"{escape.join(display)}")
                embed.add_field(name="", value=f"")

                display.clear()
                dmg.clear()

    except KeyError:
        embed.add_field(name="Value not found", value="")
        return  embed
    return embed


async def frame(var):
    await lookup.frames_db()

    entry = await leven.fsearch(var, wf_init._names)
    num = lookup.framedb[entry]

    embed = discord.Embed(
    colour=discord.Colour.dark_purple(),
    title=f"{entry}",
    url=f"{wf_init.wf_frames[num]['wikiaUrl']}",
    )

    try:
        embed.set_thumbnail(url=f"{wf_init.wf_frames[num]['wikiaThumbnail']}")
    except KeyError:
        embed.set_thumbnail(url=f"{await wiki_image(entry)}")


    embed.add_field(name=f"Stats at Rank 30:", value=f"Armor - {wf_init.wf_frames[num]['armor']}\nShield - {wf_init.wf_frames[num]['shield']*3}\nHealth - {wf_init.wf_frames[num]['health']*3}\nEnergy - {int(wf_init.wf_frames[num]['power']*1.5)}")
    embed.add_field(name="Progenitor: ", value=fprogen.progenlist[entry], inline=False)
    return embed