# Lammy

Bot for Discord servers, designed for the automated management and coordination of SINoALICE's colosseum through pre-configured messages.

## Initial Setup

1. Give a role with admin permissions to Lammy; she'll need to create roles, ping them, react to messages and be able to write in channels where maybe you don't want other people to do so.
2. Set an administrator group with `!setadmin <AdminRole>`, which will be able to use certain priviledged commands.
3. Set the guild group with `!setmember <GuildRole>`. This is to prevent non-members to check your guild's relevant information, such as nightmare rotation or assignment list.
4. Create a new channel and post `!ask <nightmare>` with as many nightmares as you'd like to take into account. It will auto-react with S, L and checkmark emojis that members should also react to, indicating unevolved, evolved and equipped nightmare, respectively.
5. Write down what nightmare is assigned to what user with `!assign <user> <nightmare>`. This list will be used in the next described command.
6. Set up the initial order of nightmare summoning with `!order <nm1> <nm2> <...>`. Can add nightmares at the start of the list by writing `!order <nm0>`.
7. Set the colosseum start time (UTC) with `!time <UTCtime>`.

To check the list of available commands, use `!help`. To check what an individual command does, write `!help <command>`
