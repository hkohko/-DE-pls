from bs4 import BeautifulSoup
import aiohttp
import asyncio
import json

class ProgenitorScrape:
    async def get_url(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as wiki:
                assert wiki.status == 200
                page =  await wiki.text()
        return page
    
    async def check_sections(self):
        try:
            return self.sidebar.find_all('section')
        except AttributeError:
            return None
        
    async def get_progenitor(self):
        span_texts = []
        try:
            for section in self.sections: #typeerror
                divs = section.find_all('div')
                for div in divs:
                    spans = div.find('span', {'style': True})
                    if spans == None:
                        pass
                    else:
                        span_texts.append(spans.text)
                        break

            if len(span_texts) == 2:
                return span_texts[-1]
            else:
                return span_texts[0]
            
        except IndexError:
            return "ProgenitorScrape.get_progenitor() unavailable"

    async def get_elements(self, name): #input
        self.name = name
        URL = rf'https://warframe.fandom.com/wiki/{name}'

        self.page = await self.get_url(URL)

        soup = BeautifulSoup(self.page, 'lxml')

        self.sidebar = soup.find('aside'
                            , {'class':
                            'portable-infobox pi-background pi-border-color pi-theme-wikia pi-layout-default'}
                            )
        
        if self.sidebar == None:
            return 'ProgenitorScrape().sidebar unavailable'

        self.sections = await self.check_sections()
        if self.sections == None:
            return 'ProgenitorScrape().sections unavailable'
        else:
            return await self.get_progenitor() #output
        
class QueryProgenitor:

    async def read(self):
        with open(r'wiki/frame_names.json', 'r') as framelist:
            self.frames = framelist.read()

    async def write_progenitors(self):
        frames = json.loads(self.frames)
        frame_progenitor = {}
        frame_progenitor_all = {}
        for keys, _ in frames.items():
            progenitor = await scrape.get_elements(keys.strip().replace(" ", "_"))
            frame_progenitor_all[keys] = progenitor
            if 'Prime' not in keys:
                frame_progenitor[keys] = progenitor
                print(frame_progenitor)
        with open('wiki\progenitor.json', 'w') as file:
            file.write(json.dumps(frame_progenitor))
        with open('wiki\progenitor_all.json', 'w') as file:
            file.write(json.dumps(frame_progenitor_all))

    async def cleaning(self):
        valuelist = []
        with open('wiki\progenitor.json', 'r', errors='ignore') as file:
            progenitor = json.loads(file.read())
        for _, values in progenitor.items():
            valuelist.append(values)
        self.set_values = set(valuelist)
        print(self.set_values)

q_progenitor = QueryProgenitor()

scrape = ProgenitorScrape()

async def initialize():
    await q_progenitor.read()

async def save_progenitors():
    return await q_progenitor.write_progenitors()

async def getprogenitor(name):
    return await scrape.get_elements(name)

async def progenitor_wf_start():
    with asyncio.Runner() as runner:
        runner.run(initialize())
        runner.run(save_progenitors())
# asyncio.run(initialize())
# asyncio.run(save_progenitors())
# asyncio.run(q_progenitor.cleaning())
