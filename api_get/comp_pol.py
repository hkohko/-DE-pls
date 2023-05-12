# import asyncio
pol_symbol = {
    "madurai" : "https://i.imgur.com/cnFPEL7.png",
    "vazarin" : "https://i.imgur.com/YB0SltQ.png",
    "naramon" : "https://i.imgur.com/cPIHGLQ.png",
    "zenurik" : "https://i.imgur.com/InII3qf.png",
    "unairu" : "https://i.imgur.com/h0myT7U.png",
    "penjaga" : "https://i.imgur.com/B7sBpNp.png",
    "umbra" : "https://i.imgur.com/nDnziga.png",
    "aura" : "https://i.imgur.com/kDyUTbz.png",
}
async def polarity(pol):
    pol = str(pol).lower()
    return pol_symbol[f"{pol}"]

# print(asyncio.run(polarity('madurai')))