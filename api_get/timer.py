import aiohttp
import asyncio
import discord


async def get_cycle_status(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response_json = await response.json()
    return response_json


async def timer():
    URL_cambion = "https://api.warframestat.us/pc/cambionCycle"
    URL_cetus = "https://api.warframestat.us/pc/cetusCycle"
    URL_vallis = "https://api.warframestat.us/pc/vallisCycle/"
    cambion = get_cycle_status(URL_cambion)
    cetus = get_cycle_status(URL_cetus)
    vallis = get_cycle_status(URL_vallis)

    cambion, cetus, vallis = await asyncio.gather(cambion, cetus, vallis)

    _cetus_keys = [
        "id",
        "activation",
        "isDay",
        "expiry",
        "state",
        "timeLeft",
        "isCetus",
        "shortString",
    ]
    _vallis_keys = ["id", "isWarm", "expiry", "timeLeft"]
    _cambion_keys = ["id", "expiry", "activation", "active", "timeLeft"]
    # CETUS
    for _ in _cetus_keys:
        cetus_timeLeft = cetus["timeLeft"]
        cetus_state = (cetus["state"]).title()
    # CAMBION DRIFT
    for _ in _cambion_keys:
        cambion_active = cambion["active"]
        cambion_timeLeft = cambion["timeLeft"]
    # VALLIS
    for _ in _vallis_keys:
        vallis_state = vallis["isWarm"]
        vallis_timeLeft = vallis["timeLeft"]
    embed = discord.Embed(
        colour=discord.Colour.dark_purple(),
    )
    if vallis_state == False:
        embed.add_field(
            name="Plains of Eidolon",
            value=f"*{cetus_state}*\nExpires in {cetus_timeLeft}",
            inline=False,
        )

        embed.add_field(
            name="Orb Vallis",
            value=f"*Cold*\nExpires in {vallis_timeLeft}",
            inline=False,
        )

        embed.add_field(
            name="Cambion Drift",
            value=f"*{(cambion_active).title()}*\nExpires in: {cambion_timeLeft}",
            inline=False,
        )
        return embed

    else:
        embed.add_field(
            name="Plains of Eidolon",
            value=f"*{cetus_state}*\nExpires in {cetus_timeLeft}",
            inline=False,
        )

        embed.add_field(
            name="Orb Vallis",
            value=f"*Warm*\nExpires in {vallis_timeLeft}",
            inline=False,
        )

        embed.add_field(
            name="Cambion Drift",
            value=f"*{(cambion_active).title()}*\nExpires in: {cambion_timeLeft}",
            inline=False,
        )
        return embed
