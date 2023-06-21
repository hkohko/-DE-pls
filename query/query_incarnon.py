from bs4 import BeautifulSoup
import aiohttp
import discord
from collections import defaultdict

escape = "\n"


class IncarnonGenesis:
    def __init__(self) -> None:
        URL = r"https://warframe.fandom.com/wiki/Incrnon"
        self.url = URL
        self.embed = discord.Embed(
            title="Incarnon Genesis",
            url=URL,
            colour=discord.Color.dark_purple(),
        )

    async def get_page(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as page:
                try:
                    status = page.status
                    assert status == 200
                    self.read = await page.text()
                except AssertionError:
                    await self.incarnon_cmd(False, "AssertionError", status)
                    await self.get_genesis(False)

    async def get_genesis(self, check=True):
        if check:
            await self.get_page()

            genesis_week = defaultdict(list)
            try:
                soup = BeautifulSoup(self.read, "lxml")
                divs = soup.find("div", {"class": "main-container"})
                mains = divs.find("main", {"class": "page__main"})
                divs2 = mains.find("div", {"id": "content"})
                divs3 = divs2.find("div", {"class": "mw-parser-output"})
                tables = divs3.find("table")
                trs = tables.find_all("tr")
                for tr in trs:
                    lis = tr.find_all("li")
                    tds = tr.find("td")
                    for li in lis:
                        spans = li.find_all("span", {"data-param": True})
                        for span in spans:
                            genesis = span["data-param"]
                            if "genesis" in genesis.lower():
                                genesis_week[tds.text.strip()] += [
                                    genesis.replace("Incarnon Genesis", "")
                                ]

                return dict(genesis_week)
            except AttributeError:
                await self.incarnon_cmd(False, "AttributeError")

    async def incarnon_cmd(self, check=True, source=None, status=""):
        print(check)
        print(source)
        print(status)
        if check and source == None:
            get_genesis = await self.get_genesis()# return code has to be from here
            for keys, value in get_genesis.items():
                self.embed.add_field(name=f"{keys}", value=f"{escape.join(value)}")
            return self.embed
        elif source == "AssertionError":
            self.embed.add_field(name=source, value=status)
            return self.embed
        else:
            self.embed.add_field(name=source, value="bs4 failed to scrape")
            return self.embed


incarnon = IncarnonGenesis()
