from config.config import BOT_PREFIX


class Helps:
    assignment = "Displays/manages nightmare assignments for colo!\nAdd/modify nightmare assignment using:\n\t`{}assignment {{nm}} {{user}}`\nWhere \"nm\" is the nightmare to assign and \"user\" is the user assigned to that nightmare".format(BOT_PREFIX)
    setdemons = ""
    demonsrearguard = ""
    demonsvanguard = ""
    nightmares = "Manage/Show current order of colosseum nightmares. Nightmares can be named as their name or by their position in the current nightmare order."
    delay = ""
    push = ""
    summon = ""
    list_demons = ""
    stop = ""
    time = "Command for handling time setting of colo"
    start = ""
    setmembers = ""
    setadmin = ""
    info = ""
    afk = ""


class Usages:
    assignment = "[nm, user]"
    setdemons = ""
    demonsrearguard = ""
    demonsvanguard = ""
    nightmares = "[nightmare1, nightmare2]"
    delay = ""
    push = ""
    summon = ""
    list_demons = ""
    stop = ""
    time = "[hour in utc]"
    start = ""
    setmembers = ""
    setadmin = ""
    info = ""
    afk = "[username/\"me\"/\"self\"]"


class Briefs:
    assignment = "shows coloseum nightmare assignments"
    setdemons = "sets today's demon"
    demonsrearguard = "gets today's demons for rearguards"
    demonsvanguard = "gets today's demons for vanguards"
    nightmares = "manage/Show current order of colosseum nightmares."
    delay = "sets the current delay of nightmare summon"
    push = "sets the next nightmare as given nightmare and pushes it into the current nm order"
    summon = "sets next nightmare as given nightmare"
    list_demons = "lists all possible demon configuration"
    stop = "stops pinging for colo"
    time = "handles colo time"
    start = "waits for colo, then pings for updates in colo!"
    setmembers = ""
    setadmin = ""
    info = ""
    afk = ""
