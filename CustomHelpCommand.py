from discord import Embed
from discord.ext.commands import DefaultHelpCommand
from discord.ext.commands.core import Command

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

#assignments

    async def send_command_help(self, command: Command):
        destination = self.get_destination()
        embed = Embed(title="**Assignments**",
                      description="Command names: `{}assignment`, `{}assignmentlist`, `{}a`, `{}as` and `{}ass` ".format(BOT_PREFIX), color=0x75ebdb)
        embed.add_field(name="!Assignment", value="Displays the current assignment list", inline=False)
        embed.add_field(name="!Assignment `<nightmare>` `<user>`",
                        value="Assigns a nightmare to the user, which will be later referenced during shotcalling with the `!order` command.
						\nIf the user is already in the assignment list with a different nightmare, it will be updated with the new one
						\nLikewise, if the command specifies a different user for an already assigned nightmare, its summoner will be updated.
						\n*Note: You can also use the command by swapping the parameters; there's no need to do it in a soecific order!*", inline=False)
        await destination.send(embed=embed)

#Set demons

    async def send_command_help(self, command: Command):
        destination = self.get_destination()
        embed = Embed(title="**Set Demons**",
                      description="Command names: `{}setdemons`, `{}sd`".format(BOT_PREFIX), color=0x75ebdb)
        embed.add_field(name="!setdemons `<Demon1>` `<Demon2>`", value="*Admin-exclusive command.* Sets the incoming colosseum's demons. The demons shall be indicated in order with their associated index, which can be checked with `!demonlist`", inline=False)
		await destination.send(embed=embed)
		
#Demonlist

    async def send_command_help(self, command: Command):
        destination = self.get_destination()
        embed = Embed(title="**Demon list**",
                      description="Command names: `{}demonlist`, `{dl}`".format(BOT_PREFIX), color=0x75ebdb)
        embed.add_field(name="!demonlist", value="Displays the six demon options with their index, which should be referenced when setting the demons with `!setdemon`", inline=False)
		await destination.send(embed=embed)
		
#Get Demons

    async def send_command_help(self, command: Command):
        destination = self.get_destination()
        embed = Embed(title="**Get Demons**",
                      description="Command names: `{}getdemons`, `{}gd`, `{}d`".format(BOT_PREFIX), color=0x75ebdb)
        embed.add_field(name="!getdemons", value="If the demons have been set with ´!setdemons´, it will display those and their order.
						\n*Note: If interested only in rearguard or vanguard weapons, commands `!demonsrearguard` and `!demonsvanguard` can be used instead, respectively*", inline=False)
		await destination.send(embed=embed)
		
#Rearguard Demons

    async def send_command_help(self, command: Command):
        destination = self.get_destination()
        embed = Embed(title="**Rearguard Demons**",
                      description="Command names: `{}demonsrearguard`, `{}dr`".format(BOT_PREFIX), color=0x75ebdb)
        embed.add_field(name="!demonsrearguard", value="If the demons have been set with ´!setdemons´, it will display only the rearguard's weapons for both demons", inline=False)
		await destination.send(embed=embed)
		
#Vanguard Demons

    async def send_command_help(self, command: Command):
        destination = self.get_destination()
        embed = Embed(title="**Vanguard Demons**",
                      description="Command names: `{}demonsvanguard`, `{}dv`".format(BOT_PREFIX), color=0x75ebdb)
        embed.add_field(name="!demonsvanguard", value="If the demons have been set with ´!setdemons´, it will display only the vanguard's weapons for both demons", inline=False)
		await destination.send(embed=embed)
		
#Info

    async def send_command_help(self, command: Command):
        destination = self.get_destination()
        embed = Embed(title="**Nightmare information**",
                      description="Command names: `{}info`, `{}in`, `{}i`".format(BOT_PREFIX), color=0x75ebdb)
        embed.add_field(name="!info `<nightmare>`", value="Will display the inputted nightmare's relevant information. Doesn't require the full nightmare name; a reduced, unique string of characters for said nightmare is enough.
						\n*Note: Lammy is a smol clam, so if your reduced string is not unique to one nightmare and is, in fact, part of more than one nightmare's full name, Lammy will be confused and won't retrieve the information!*", inline=False)
		await destination.send(embed=embed)
	
#setadmin

    async def send_command_help(self, command: Command):
        destination = self.get_destination()
        embed = Embed(title="**Set admin**",
                      description="Command names: `{}setadmin`, `{}sa`".format(BOT_PREFIX), color=0x75ebdb)
        embed.add_field(name="!setadmin `<role>`", value="*Admin-exclusive command.* Sets a role as an administrator for Lammy. Only Lammy admins can use admin-exclusive commands, such as modifying `!assigments`, `!order` or `!setdemons`", inline=False)
		await destination.send(embed=embed)

#setmember

    async def send_command_help(self, command: Command):
        destination = self.get_destination()
        embed = Embed(title="**Set member**",
                      description="Command names: `{}setadmin`, `{}sa`".format(BOT_PREFIX), color=0x75ebdb)
        embed.add_field(name="!setmember `<role>`", value="*Admin-exclusive command.* Sets a role as guild member. This allows users with the inputted role to check commands such as `!assigments` or `!order`, in case a discord server has members that aren't from the guild and shouldn't be able to view that information.", inline=False)
		await destination.send(embed=embed)
		
#Nightmare order

    async def send_command_help(self, command: Command):
        destination = self.get_destination()
        embed = Embed(title="**Nightmare Order**",
                      description="Command names: `{}nightmares`, `{}order`, `{}nmorder`, `{}nm`, `{}o`".format(BOT_PREFIX), color=0x75ebdb)
        embed.add_field(name="!order", value="Displays the current nightmare summoning order, showing their place in the rotation, the nightmare's name, preparation time and lead time", inline=False)
		embed.add_field(name="!order `<Nightmare1>` `<Nightmare2>` `[...]`", value="*Admin-exclusive command.* Adds the inputted nightmares to the order, if they weren't already part of it
						\n*Note: the inputted nightmares must have an assigned summoner first, which can be set with the command ´!assignment <nightmare> <user>´. Otherwise, Lammy wouldn't know who to ping when their summoning time comes!*", inline=False)
						\n*Note 2: If used during colosseum with two nightmares as parameters, it will swap their positions in the rotation.*
		await destination.send(embed=embed)
		
#Start

    async def send_command_help(self, command: Command):
        destination = self.get_destination()
        embed = Embed(title="**Start**",
                      description="Command name: `{}start`".format(BOT_PREFIX), color=0x75ebdb)
        embed.add_field(name="!start", value="*Admin-exclusive command.* Starts the countdown until colosseum starts. Should be sent after the demons are set with `!setdemons`, and requires `!time` to be specified previously, too", inline=False)
		await destination.send(embed=embed)

#Time

    async def send_command_help(self, command: Command):
        destination = self.get_destination()
        embed = Embed(title="**Time**",
                      description="Command names: `{}time`, `{}t`".format(BOT_PREFIX), color=0x75ebdb)
        embed.add_field(name="!time `<UTCtime>`", value="*Admin-exclusive command.* Sets the time at which colosseum starts, specified in UTC timezone", inline=False)
		await destination.send(embed=embed)
		
#afk

    async def send_command_help(self, command: Command):
        destination = self.get_destination()
        embed = Embed(title="**AFK**",
                      description="Command names: `{}afk`".format(BOT_PREFIX), color=0x75ebdb)
        embed.add_field(name="!afk", value="Sets the sender as afk for the current colosseum match. If the sender was assigned a nightmare, members equipping said nightmare will be pinged instead", inline=False)
        embed.add_field(name="!afk `<user>`", value="Sets the inputted user as afk for the current colosseum match. If the user was assigned a nightmare, members equipping said nightmare will be pinged instead", inline=False)
		await destination.send(embed=embed)
		
#push

    async def send_command_help(self, command: Command):
        destination = self.get_destination()
        embed = Embed(title="**Push a nightmare**",
                      description="Command names: `{}push`, `{}p`".format(BOT_PREFIX), color=0x75ebdb)
        embed.add_field(name="!push `<Nightmare>`", value="During colo, sets the inputted nightmare as next to be summoned and pushes it into the current order, postponing the rest of the nightmares to be summoned", inline=False)
		await destination.send(embed=embed)

#delay

    async def send_command_help(self, command: Command):
        destination = self.get_destination()
        embed = Embed(title="**Delay the summoning**",
                      description="Command names: `{}delay`, `{}d`".format(BOT_PREFIX), color=0x75ebdb)
        embed.add_field(name="!delay `<seconds>`", value="Sets a delay, in seconds, to have into account when shotcalling for the nightmare summonings", inline=False)
		await destination.send(embed=embed)
		
######WIP
		
#Ask

    async def send_command_help(self, command: Command):
        destination = self.get_destination()
        embed = Embed(title="**Ask for nightmares**",
                      description="Command names: `{}ask`".format(BOT_PREFIX), color=0x75ebdb)
        embed.add_field(name="!ask `<nightmare>`", value="Sends a message with the nightmare information and three emojis for members to react to: *emojis here*. Each member should select either *S or L* to indicate said nightmare's availability and evolution level, as well as *check* to indicate the nightmare is being equipped, in case it needs to be summoned and the assigned summoner is afk for colosseum.", inline=False)
		await destination.send(embed=embed)
		
#check

    async def send_command_help(self, command: Command):
        destination = self.get_destination()
        embed = Embed(title="**Check nightmare availability in the guild**",
                      description="Command names: `{}check`".format(BOT_PREFIX), color=0x75ebdb)
        embed.add_field(name="!check `<nightmare>`", value="Checks the members' reacts to the message generated with `!ask` to return who has it, its evolution level, and who is equipping it in their colosseum grid, in case it needs to be summoned and the assigned summoner is afk for colosseum.", inline=False)
		await destination.send(embed=embed)
		
#Infomore

    async def send_command_help(self, command: Command):
        destination = self.get_destination()
        embed = Embed(title="**Nightmare information (more)**",
                      description="Command names: `{}infomore`, `{}inmo`".format(BOT_PREFIX), color=0x75ebdb)
        embed.add_field(name="!infomore `<nightmare>`", value="Will display the inputted nightmare's relevant information, as well as who in the guild owns it, its evolution level and who is equipping it at the moment. Doesn't require the full nightmare name; a reduced, unique string of characters for said nightmare is enough.
						\n*Note: Lammy is a smol clam, so if your reduced string is not unique to one nightmare and is, in fact, part of more than one nightmare's full name, Lammy will be confused and won't retrieve the information!*", inline=False)
		await destination.send(embed=embed)
		        
#dumb
        
    async def send_command_help(self, command: Command):
        destination = self.get_destination()
        print(command.usage, command.help, command.brief)
        await destination.send("You asked for {} help but I'm stupid rn so no command for you".format(command.name))
