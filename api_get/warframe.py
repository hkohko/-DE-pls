import aiohttp
import asyncio
import discord
from fuzzywuzzy import process
from bs4 import BeautifulSoup
import thumb.comp_pol as comp_pol

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
    for i, j in enumerate(wf_wep):
        name = wf_wep[i]["name"]
        weapondb[name] = i


async def frames_db():
    global framedb
    framedb = {}
    for i, j in enumerate(wf_frames):
        name = wf_frames[i]["name"]
        framedb[name] = i


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
    global thumb, entry_mod
    display = []
    thumb = []
    entry_mod = await fsearch(var)

    embed = discord.Embed(
        colour=discord.Colour.dark_purple(),
        title=f"{entry_mod}"
    )

    try:
        for i, j in enumerate(wf_mod):
            if wf_mod[i]['name'] == entry_mod:
                if wf_mod[i].get('drops') == None:
                    continue
                else:
                    display.append('```')
                    display.append(wf_mod[i]['name'])
                    display.append('Drop Locations:')
                    for x in wf_mod[i]['drops']:
                        display.append(x['location'])
                    display.append(f'```')
                    break
    except KeyError:
        pass
    send_display = f'{escape.join(display)}'
    return (send_display)

async def mod_thumb():
    image = await wfmod(entry_mod)
    return (image)

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
            # display.append(wf_wep[num]['name'])
            # display.append(wf_wep[num]['wikiaUrl'])
            for j in wf_wep[num]['attacks']:
                # display.append('```')
                # display.append(j['name'])
                embed.add_field(name=f"{j['name']}", value=f"Crit. Chance\n{j['crit_chance']}%\nCrit. Damage\n{j['crit_mult']}x\nStat. Chance\n{j['status_chance']}%")

                # display.append(f"Crit. Chance: {j['crit_chance']}%")
                # embed.add_field(name="Crit. Chance", value=f"{j['crit_chance']}%")

                # display.append(f"Crit. Damage: {j['crit_mult']}x")
                # embed.add_field(name="Crit. Damage", value=f"{j['crit_mult']}x")

                # display.append(f"Stat. Chance: {j['status_chance']}%")
                # embed.add_field(name="Stat. Chance", value=f"{j['status_chance']}%")
                dmg_dict = j['damage']
                for key in dmg_dict:
                    display.append(f'{key} - {dmg_dict[key]}')
                    dmg.append(dmg_dict[key])
                    # embed.add_field(name=f"{dmg_dict[key]}", value=f"{key} - {dmg_dict[key]}")
                total_dmg = int(sum(dmg))
                # display.append(f"Total Damage: {int(sum(dmg))}")
                embed.add_field(name=f"Damage", value=f"{escape.join(display)}")
                embed.add_field(name="Total Damage", value=f"{total_dmg}")
                display.clear()
                dmg_dict.clear()
                dmg.clear()
                # display.append('```')
    except KeyError:
        return 'Value not found'
    return embed
    # return (escape.join(display))


async def frame(var):
    escape = f'\n'
    await frames_db()
    display = []
    polarity = {}
    apos = r"'"
    entry = await fsearch(var)
    num = framedb[entry]

    embed = discord.Embed(
    colour=discord.Colour.dark_purple(),
    title=f"{entry}",
    url=f"{wf_wep[num]['wikiaUrl']}",
)
    

    try:
        # display.append(f"{wf_frames[num]['name']}")
        # display.append(wf_frames[num]['wikiaUrl'])
        # display.append('```')

        # display.append(
        #     f"Aura: {str(wf_frames[num]['aura']).replace('madurai', 'V').replace('vazarin', 'D').replace('naramon', 'dash').replace('zenurik', 'scratch')}"
        # )

        pol_list = [i for i in wf_frames[num]['polarities']]
        polarity['polarity'] = pol_list
        print(polarity)
        # embed.add_field(name="Aura", value=f"{comp_pol.polarity(wf_frames[num]['aura'])}")
        
        # polarity_str = str(polarity['polarity']).replace('[', '').replace(
        #     ']', '').replace(apos, '')
        # pol_str_conv = polarity_str.replace('madurai', 'V').replace(
        #     'vazarin', 'D').replace('naramon',
        #                             'dash').replace('zenurik', 'scratch')
        display.append(f"Polarity: {pol_str_conv}")
        display.append('Stats at Rank 30:')
        display.append(f"Armor - {wf_frames[num]['armor']}")
        display.append(f"Shield - {wf_frames[num]['shield']*3}")
        display.append(f"Health - {wf_frames[num]['health']*3}")
        display.append(f"Energy - {int(wf_frames[num]['power']*1.5)}")
        display.append('```')
    except KeyError:
        try:
            display.append('Aura: None')
            pol_list = [i for i in wf_frames[num]['polarities']]
            polarity['polarity'] = pol_list
            polarity_str = str(polarity['polarity']).replace('[', '').replace(
                ']', '').replace(apos, '')
            pol_str_conv = polarity_str.replace('madurai', 'V').replace(
                'vazarin', 'D').replace('naramon',
                                        'dash').replace('zenurik', 'scratch')
            display.append(f"Polarity: {pol_str_conv}")
            display.append('Stats at Rank 30:')
            display.append(f"Armor - {wf_frames[num]['armor']}")
            display.append(f"Shield - {wf_frames[num]['shield']*3}")
            display.append(f"Health - {wf_frames[num]['health']*3}")
            display.append(f"Energy - {int(wf_frames[num]['power']*1.5)}")
            display.append('```')
        except KeyError:
            try:
                display.append('Stats at Rank 30:')
                display.append(f"Armor - {wf_frames[num]['armor']}")
                display.append(f"Shield - {wf_frames[num]['shield']*3}")
                display.append(f"Health - {wf_frames[num]['health']*3}")
                display.append(f"Energy - {int(wf_frames[num]['power']*1.5)}")
                display.append('```')
            except KeyError:
                pass
    # return (escape.join(display))



asyncio.run(init_db())
# asyncio.run(mod('ravage'))
# asyncio.run(mod('ravage'))
# asyncio.run(mod_thumb())
# asyncio.run(weapon('tiberon prime'))
# asyncio.run(frame('excalibur'))
asyncio.run(frame('excalibur'))