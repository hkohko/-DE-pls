import pendulum
import api_get.leven_search as leven
import discord
import asyncio


class Timezone:
    def __init__(self):
        self.embed = discord.Embed(
            title="Timezones", color=discord.Colour.dark_purple()
        )

    async def whattime(self, entry, day, month, year, hour, minute, second):
        if entry is None and day is None and month is None and year is None:
            self.embed.add_field(
                name="",
                value=f"```{', '.join([i for i in pendulum.timezones if '/' not in i and i.isupper()])}```",
            )
            return self.embed
        else:
            try:
                list_timezone = [i.lower() for i in pendulum.timezones]
                entry = await leven.fsearch(entry.lower(), list_timezone)
                in_other = pendulum.datetime(
                    int(year),
                    int(month),
                    int(day),
                    int(hour),
                    int(minute),
                    int(second),
                    tz=entry,
                )
            except TypeError:
                entry = await leven.fsearch(entry.lower(), list_timezone)
                self.embed.add_field(
                    name="",
                    value=f"```{entry.upper()} : {str(pendulum.now(entry)).split('T')[1]} / {str(pendulum.now(entry)).split('T')[0]}```",
                )
                return self.embed
            tz = pendulum.timezone("Asia/Jakarta")
            in_local = tz.convert(in_other)
            self.embed.add_field(
                name="",
                value=f"```{entry.upper()} | WIB: {str(in_local).split('T')[1]} / {str(in_local).split('T')[0]}```",
            )
            return self.embed
