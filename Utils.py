import datetime as date
import os
import xml.etree.ElementTree as ET
from time import sleep

from discord.member import Member
from numpy.testing._private.utils import measure

from config import NightmareData, User
from NightmareScrapper import nightmare_scrapper


def user_is_permitted(author, roles):
    """
    Returns whether or not the given user (Should be of type member! (Context.author))
    belongs to the given role
    """
    return isinstance(author, Member) and (
        any(((role in author.roles) or (role.mention == author.mention)) for role in roles)
    )


def get_user_from_username(username: str, ctx, strict=True):
    lowered = username.lower()
    for member in ctx.guild.members:
        if (
            strict and (
                member.name.lower() == lowered or (member.nick and member.nick.lower() == lowered))
        ) or (
                not strict and (
                    lowered in member.name.lower() or (member.nick and lowered in member.nick.lower())
                )):
            return User(name=member.name, mention=member.mention)
    return User(name=username, mention=username)


def get_nm_mention(roles, nm: NightmareData):
    """
    Function that gets a nightmare and returns a string representing its role (the "mention").
    If a role doesn't exist for this nightmare in the guild, returns the nightmare's name.
    """
    for role in roles:
        if str(role).lower() == nm.name.lower():
            return role.mention
    return nm.name


def get_nm_data_from_message(message):
    df = nightmare_scrapper.find_nm(message)
    if df.empty or len(df) > 1:
        return None
    return NightmareData(**df.iloc[0].to_dict())


def lookup_nms(message):
    df = nightmare_scrapper.nm_lookup(message)
    return [NightmareData(**item.to_dict()) for item in df.iloc]


def get_nm_assignment_from_message(message, assignments, index_from_order_arr=False, current_order_list=None):
    """
    :param message: A string/int which represents the name of a nightmare/member in the assignments list
    :param index_from_order_arr: If given message is an int representing an index, specify if that index is of order list or assignments list
    :param current_order_list: if index_from_order_arr is true (message could be an index representing order list), then uses that order list
    """
    try:
        message = int(message)
        if index_from_order_arr:
            return assignments[current_order_list[message]]
        return assignments[message]
    except ValueError:
        message = str(message).lower()
        for assignment in assignments:
            if message in assignment.nm.name.lower() or message in assignment.user.name.lower():
                return assignment
    except IndexError:
        pass


def readToken():
    with open('token.txt', 'r') as f:
        return f.readline().strip("\n")


def getString(id, node, dynamicParam):
    xml = ET.parse('strings.xml')
    root = xml.getroot()
    messages = root[0]
    if dynamicParam == None:
        for message in messages.findall(node):
            if message.attrib.get('id') == id:
                return(message.text)
    else:
        for message in messages.findall(node):
            if message.attrib.get('id') == id:
                dynamicText = message.text
                dynamicText = dynamicText.replace('{PARAM}', dynamicParam)
                return(dynamicText)


def get2String(id, node, dynamicParam1, dynamicParam2):
    xml = ET.parse('strings.xml')
    root = xml.getroot()
    messages = root[0]
    if dynamicParam1 == None:
        if dynamicParam2 == None:
            for message in messages.findall(node):
                if message.attrib.get('id') == id:
                    return(message.text)
    else:
        for message in messages.findall(node):
            if message.attrib.get('id') == id:
                dynamicText = message.text
                dynamicText = dynamicText.replace('{PARAM1}', dynamicParam1)
                dynamicText = dynamicText.replace('{PARAM2}', dynamicParam2)

                return(dynamicText)


def fullClear():
    os.system('clear')


def clear():
    print()
    print()
    print()


def getRole(guild_roles, assignment_role):
    guild_roles = guild_roles or list()
    for role in guild_roles:
        if str(assignment_role).lower() in (str(role.mention).lower(), str(role.id).lower(), str(role.name).lower()):
            return role
    return User(str(assignment_role), str(assignment_role))


def getDiff(start_time, stop_time):
    date1 = date.date(1, 1, 1)
    datetime1 = date.datetime.combine(date1, start_time)
    datetime2 = date.datetime.combine(date1, stop_time)
    result = datetime2 - datetime1
    return result


def log(message, hasToPrint):
    if hasToPrint:
        print(f'{message}')
    log = str(date.datetime.now()) + ' | ' + message


def err(message, hasToPrint):
    if hasToPrint:
        print("\033[91m{}\033[0m".format(message))

    err = str(date.datetime.now()) + ' | ' + message
    with open("Lammy_log", "a") as f:
        f.writelines("'ERROR: {}'".format(err))
