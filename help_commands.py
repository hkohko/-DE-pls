async def helpcommand(entry):
    apos = f"'"
    entry = entry.lower()
    list_help = ['timer', 'sell', 'buy', 'q', 'weapon', 'frame', 'mod', 'wiki', 'progenitor']

    if entry == 'list':
        return (f"{str(list_help).replace('[', '').replace(']', '').replace(apos, '')}\n```For command help, type ,help [command] (e.g. ,help timer)```")
    elif entry == 'timer':
        return (f"```Usage: ,timer\nShows current world timers```")
    elif entry == 'sell':
        return (f"```Usage: ,sell [item name]\n(e.g ',sell tiberon p set')\n\nShows currently online/in-game players who sells [item name]```")
    elif entry == 'buy':
        return (f"```Usage: ,buy [item name] \n(e.g ',buy tiberon p set')\n\nShows currently online/in-game players who are buying [item name]```")
    elif entry == 'q':
        return (f"```Usage: ,q [item name]\n(e.g ',q galvanized')\n\nReturns all market items containing '[item name]' in their name```")
    elif entry == 'weapon':
        return (f"```Usage: ,weapon [weapon name]\n(e.g. ,weapon tiberon prime)\n\nShows weapon stat and wiki```")
    elif entry == 'mod':
        return (f"```Usage: ,mod [mod name]\n(e.g. ,mod Tek Enhance)\n\nReturns mod and its drop location if available```")
    elif entry == 'frame':
        return (f"```Usage: ,frame [frame name]\n(e.g. ,frame Excalibur)\n\nReturns Warframe basic stats and wiki```")
    elif entry == 'wiki':
        return (f"```Usage: ,wiki [item]\n(e.g. ,wiki Excalibur)\n\nReturns a wiki link of said item```")
    elif entry == 'progenitor':
        return (f"```Usage: ,progenitor [element]\n(e.g. ,progenitor heat)\n\nReturns progenitor warframes with element [element]```")
    elif entry not in list_help:
        return ('No such command')