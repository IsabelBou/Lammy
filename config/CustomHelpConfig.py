
from config.config import BOT_PREFIX

EMBED_MAPPING = dict(
    assignment=dict(
        title="**Assignments**",
        description="Command names: `{0}assignment`, `{0}assignmentlist`, `{0}a`, `{0}as` and `{0}ass` ".format(BOT_PREFIX),
        color=0x75ebdb,
        fields=[
            dict(
                name="{0}Assignment".format(BOT_PREFIX),
                value="Displays the current assignment list"
            ),
            dict(
                name="{0}Assignment `<nightmare>` `<user>`".format(BOT_PREFIX),
                value="""Assigns a nightmare to the user, 
		which will be later referenced during shotcalling with the `{0}order` command.
                        If the user is already in the assignment list with a different nightmare, it will be updated with the new one.
                        Likewise, if the command specifies a different user for an already assigned nightmare, its summoner will be updated.
                        *Note: You can also use the command by swapping the parameters, there's no need to do it in a specific order!*""".format(BOT_PREFIX)
            ),
            dict(
                name="{0}Assignment -r `<Nightmare/user>`".format(BOT_PREFIX),
                value="*Admin-exclusive command.* Removes the inputted nightmare or user from the assignment list, if they were part of it."
	    )
        ]
    ),
    setdemons=dict(
        title="**Set Demons**",
        description="Command names: `{0}setdemons`, `{0}sd`".format(BOT_PREFIX),
        color=0x75ebdb,
        fields=[
            dict(
                name="{0}setdemons `<Demon1>` `<Demon2>`".format(BOT_PREFIX),
                value="*Admin-exclusive command.* Sets the incoming colosseum's demons. The demons shall be indicated in order with their associated index, which can be checked with `{0}demonlist`".format(
                    BOT_PREFIX)
            )
        ]
    ),
    demonlist=dict(
        title="**Demon list**",
        description="Command names: `{0}demonlist`, `{0}`".format(BOT_PREFIX),
        color=0x75ebdb,
        fields=[
            dict(
                name="{0}demonlist".format(BOT_PREFIX),
                value="Displays the six demon options with their index, which should be referenced when setting the demons with `{0}setdemon`".format(
                    BOT_PREFIX)
            )
        ]
    ),
    getdemons=dict(
        title="**Get Demons**",
        description="Command names: `{0}getdemons`, `{0}gd`, `{0}d`".format(BOT_PREFIX),
        color=0x75ebdb,
        fields=[
            dict(
                name="{0}getdemons".format(BOT_PREFIX),
                value="""If the demons have been set with ´{0}setdemons´, it will display those and their order.
                        *Note: If interested only in rearguard or vanguard weapons, commands `{0}demonsrearguard` and `{0}demonsvanguard` can be used instead, respectively *""".format(BOT_PREFIX)
            )
        ]
    ),
    demonsrearguard=dict(
        title="**Rearguard Demons**",
        description="Command names: `{0}demonsrearguard`, `{0}dr`".format(BOT_PREFIX),
        color=0x75ebdb,
        fields=[
            dict(
                name="{0}demonsrearguard".format(BOT_PREFIX),
                value="If the demons have been set with ´{0}setdemons´, it will display only the rearguard's weapons for both demons".format(
                    BOT_PREFIX)
            )
        ]
    ),
    demonsvanguard=dict(
        title="**Vanguard Demons**",
        description="Command names: `{0}demonsvanguard`, `{0}dv`".format(BOT_PREFIX),
        color=0x75ebdb,
        fields=[
            dict(
                name="{0}demonsvanguard".format(BOT_PREFIX),
                value="If the demons have been set with ´{0}setdemons´, it will display only the vanguard's weapons for both demons".format(
                    BOT_PREFIX)
            )
        ]
    ),
    info=dict(
        title="**Nightmare information**",
        description="Command names: `{0}info`, `{0}in`, `{0}i`".format(BOT_PREFIX),
        color=0x75ebdb,
        fields=[
            dict(name="{0}info `<nightmare>`".format(BOT_PREFIX),
                 value="""Will display the inputted nightmare's relevant information. Doesn't require the full nightmare name a reduced, unique string of characters for said nightmare is enough.
                	*Note: Lammy is a smol clam, so if your reduced string is not unique to one nightmare and is, in fact, part of more than one nightmare's full name, Lammy will be confused and won't retrieve the information!*"""
                 )
        ]
    ),
    setadmin=dict(
        title="**Set admin**",
        description="Command names: `{0}setadmin`, `{0}sa`".format(BOT_PREFIX),
        color=0x75ebdb,
        fields=[
            dict(
                name="{0}setadmin `<role/user>`".format(BOT_PREFIX),
                value="*Admin-exclusive command.* Sets a role/user as an administrator for Lammy. Only Lammy admins can use admin-exclusive commands, such as modifying `{0}assigments`, `{0}order` or `{0}setdemons`".format(
                    BOT_PREFIX)            
	    ),		
            dict(
                name="{0}setadmin -r `<role/user>`".format(BOT_PREFIX),
                value="*Admin-exclusive command.* Removes admin capabilities from a role/user, if they had them in the first place."
            )
        ]
    ),
    setmembers=dict(
        title="**Set member**",
        description="Command names: `{0}setadmin`, `{0}sa`".format(BOT_PREFIX),
        color=0x75ebdb,
        fields=[
            dict(
                name="{0}setmember `<role>`".format(BOT_PREFIX),
                value="*Admin-exclusive command.* Sets a role as guild member. This allows users with the inputted role to check commands such as `{0}assigments` or `{0}order`, in case a discord server has members that aren't from the guild and shouldn't be able to view that information.".format(
                    BOT_PREFIX)
            )
        ]
    ),
    order=dict(
        title="**Nightmare Order**",
        description="Command names: `{0}nightmares`, `{0}order`, `{0}nmorder`, `{0}nm`, `{0}o`".format(BOT_PREFIX),
        color=0x75ebdb,
        fields=[
            dict(
                name="{0}order".format(BOT_PREFIX),
                value="Displays the current nightmare summoning order, showing their place in the rotation, the nightmare's name, preparation time and lead time"
            ),
            dict(
                name="{0}order `<Nightmare1>` `<Nightmare2>` `[...]`".format(BOT_PREFIX),
                value="""*Admin-exclusive command.* Adds the inputted nightmares to the order, if they weren't already part of it
                        *Note: the inputted nightmares must have an assigned summoner first, which can be set with the command ´{0}assignment <nightmare> <user>´. Otherwise, Lammy wouldn't know who to ping when their summoning time comes!*
						*Note 2: If used during colosseum with two nightmares as parameters, it will swap their positions in the rotation.*""".format(BOT_PREFIX)
            ),
            dict(
                name="{0}order -r `<Nightmare/user>`".format(BOT_PREFIX),
                value="*Admin-exclusive command.* Removes the inputted nightmare or user from the order list, if they were part of it."
            )
        ]
    ),
    start=dict(
        title="**Start**",
        description="Command name: `{0}start`".format(BOT_PREFIX),
        color=0x75ebdb,
        fields=[
            dict(
                name="{0}start".format(BOT_PREFIX),
                value="*Admin-exclusive command.* Starts the countdown until colosseum starts. Should be sent after the demons are set with `{0}setdemons`, and requires `{0}time` to be specified previously, too".format(
                    BOT_PREFIX)
            )
        ]
    ),
    time=dict(
        title="**Time**",
        description="Command names: `{0}time`, `{0}t`".format(BOT_PREFIX), color=0x75ebdb,
        fields=[
            dict(
                name="{0}time `<UTCtime>`".format(BOT_PREFIX),
                value="*Admin-exclusive command.* Sets the time at which colosseum starts, specified in UTC timezone"
            )
        ]
    ),
    afk=dict(
        title="**AFK**",
        description="Command names: `{0}afk`".format(BOT_PREFIX),
        color=0x75ebdb,
        fields=[
            dict(
                name="{0}afk".format(BOT_PREFIX),
                value="Sets the sender as afk for the current colosseum match. If the sender was assigned a nightmare, members equipping said nightmare will be pinged instead"
            ),
            dict(
                name="{0}afk `<user>`".format(BOT_PREFIX),
                value="Sets the inputted user as afk for the current colosseum match. If the user was assigned a nightmare, members equipping said nightmare will be pinged instead"
            ),		
            dict(
                name="{0}afk -r `<user>`".format(BOT_PREFIX),
                value="If the user was set as afk, said user will be removed from the afk list and will be pinged for their assigned nightmare summoning."
            )
        ]
    ),
    push=dict(
        title="**Push a nightmare**",
        description="Command names: `{0}push`, `{0}p`".format(BOT_PREFIX),
        color=0x75ebdb,
        fields=[
            dict(
                name="{0}push `<Nightmare>`".format(BOT_PREFIX),
                value="During colo, sets the inputted nightmare as next to be summoned and pushes it into the current order, postponing the rest of the nightmares to be summoned"
            )
        ]
    ),
    replace=dict(
        title="**Replace a nightmare**",
        description="Command names: `{0}replace`, `{0}replacenightmare`, `{0}r`, `{0}rn`".format(BOT_PREFIX),
        color=0x75ebdb,
        fields=[
            dict(
                name="{0}replace `<Nightmare>`".format(BOT_PREFIX),
                value="During colo, sets the inputted nightmare, which was already included in the list, as next to be summoned and pushes it into the current order, postponing the rest of the nightmares to be summoned until getting to the inputted nightmare's original psition"
            )
        ]
    ),
    delay=dict(
        title="**Delay the summoning**",
        description="Command names: `{0}delay`, `{0}d`".format(BOT_PREFIX),
        color=0x75ebdb,
        fields=[
            dict(
                name="{0}delay `<seconds>`".format(BOT_PREFIX),
                value="Sets a delay, in seconds, to have into account when shotcalling for the nightmare summonings"
            )
        ]
    ),
    ask=dict(
        title="**Ask for nightmares**",
        description="Command names: `{0}ask`".format(BOT_PREFIX),
        color=0x75ebdb,
        fields=[
       		dict(
                name="{0}ask".format(BOT_PREFIX),
                value="Checks that channel's `{0}ask <nightmare>` messages to count the current amount of reacts in every polled nightmare."
            ),
		dict(
                name="{0}ask `<nightmare>`".format(BOT_PREFIX),
                value="Sends a message with the nightmare information and three emojis for members to react to: *emojis here*. Each member should select either :regional_indicator_s: or :regional_indicator_l: to indicate said nightmare's availability and evolution level, as well as :ballot_box_with_check: to indicate the nightmare is being equipped, in case it needs to be summoned and the assigned summoner is afk for colosseum."
            )
        ]
    ),    
    lookup=dict(
        title="**Look for nightmares**",
        description="Command names: `{0}lookup`, `{0}l`".format(BOT_PREFIX),
        color=0x75ebdb,
        fields=[
            dict(
                name="{0}lookup `<description>`".format(BOT_PREFIX),
                value="Looks for nightmares whose description matches with the string inputted."
            )
        ]
    ),
    update=dict(
        title="**Update**",
        description="Command names: `{0}Update`".format(BOT_PREFIX),
        color=0x75ebdb,
        fields=[
       		dict(
                name="{0}ask".format(BOT_PREFIX),
                value="Instantly checks the datamine source to update the supplied nightmare information."
            )
        ]
    ),
    check=dict(
        title="**Check nightmare availability in the guild**",
        description="Command names: `{0}check`".format(BOT_PREFIX),
        color=0x75ebdb,
        fields=[
            dict(
                name="{0}check `<nightmare>`".format(BOT_PREFIX),
                value="Checks the members' reacts to the message generated with `{0}ask` to return who has it, its evolution level, and who is equipping it in their colosseum grid, in case it needs to be summoned and the assigned summoner is afk for colosseum.".format(
                    BOT_PREFIX)
            )
        ]
    )
)
