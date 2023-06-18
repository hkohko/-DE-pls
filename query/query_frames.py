import aiohttp
import json

escape = '\n'


async def get_db(URL):
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as response:
            response_json = await response.json()
    return response_json


class WF_init:
    async def init_db(self):
        URL_frames = f'https://api.warframestat.us/warframes/'
        self.wf_frames = await get_db(URL_frames)

    async def del_db(self):
        del self.wf_frames

class Lookup:
    async def frames_db(self):
        self.framedb = {}
        for i, _ in enumerate(wf_init.wf_frames):
            name = wf_init.wf_frames[i]["name"]
            self.framedb[name] = i

wf_init = WF_init()    
lookup = Lookup()


async def initialize():
    await wf_init.init_db()


async def clear_db():
    await wf_init.del_db()

async def write_frames():
    notprime_frames = {}
    await lookup.frames_db()
    frame_list = lookup.framedb
    for keys, values in frame_list.items():
        notprime_frames[keys] = values
    with open(r'wiki/frame_names.json', 'w') as notprimes:
        notprimes.write(json.dumps(notprime_frames))

async def init_query_frames():
    await initialize()
    await write_frames()