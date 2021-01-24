from discord import Embed
from discord.ext.commands import DefaultHelpCommand

from config.config import BOT_PREFIX


class CustomHelpCommand(DefaultHelpCommand):
    async def send_bot_help(self, mapping):
        destination = self.get_destination()
        embed = Embed(title="**Lammy's Instructions**",
                      description="Use `{}help [command]` for more info on a command.\nThe ones in italics are usable by *`admins only`*".format(BOT_PREFIX), color=0x75ebdb)
        embed.add_field(name="Initial Setup", value="*`setadmin`*, *`setmembers`*, *`time`*", inline=False)
        embed.add_field(name="Colosseum demon settings",
                        value="`demonlist`, *`setdemons`*, `demons`, `demonsrearguard`, `demonsvanguard`", inline=False)
        embed.add_field(name="Nightmare Assignments", value="`assignment`, `nightmares`, `info`", inline=False)
        embed.add_field(name="Colosseum actions", value="*`start`*, *`delay`*, *`push`*, *`replace`*, *`stop`*", inline=False)
        await destination.send(embed=embed)
