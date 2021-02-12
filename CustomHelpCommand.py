from discord import Embed
from discord.ext.commands import DefaultHelpCommand
from discord.ext.commands.core import Command

from config.config import BOT_PREFIX
from config.CustomHelpConfig import EMBED_MAPPING


class CustomHelpCommand(DefaultHelpCommand):
    async def send_bot_help(self, mapping):
        destination = self.get_destination()
        embed = Embed(title="**Lammy's Instructions**",
                      description="Use `{}help [command]` for more info on a command.\nThe ones in italics are usable by *`admins only`*".format(BOT_PREFIX), color=0x75ebdb)
        embed.add_field(name="Initial Setup", value="*`setadmin`*, *`setmembers`*, *`time`*", inline=False)
        embed.add_field(name="Colosseum demon settings",
                        value="`demonlist`, *`setdemons`*, `getdemons`, `demonsrearguard`, `demonsvanguard`", inline=False)
        embed.add_field(name="Nightmare Assignments", value="`assignment`, `nightmares`, `info`, `check`, *`ask`*", inline=False)
        embed.add_field(name="Colosseum actions", value="*`start`*, *`delay`*, *`push`*, *`replace`*, *`stop`*", inline=False)
        await destination.send(embed=embed)

    async def send_command_help(self, command: Command):
        destination = self.get_destination()
        command_name = command.name
        if command_name not in EMBED_MAPPING:
            return await super().send_command_help(command)
        embed_data = EMBED_MAPPING[command_name]
        embed = Embed(title=embed_data["title"], description=embed_data["description"], color=embed_data["color"])
        for field in embed_data["fields"]:
            embed.add_field(name=field["name"], value=field["value"], inline=False)
        await destination.send(embed=embed)
