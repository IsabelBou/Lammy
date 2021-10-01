# Lammy

Bot for Discord servers, designed for the automated management and coordination of SINoALICE's colosseum through pre-configured messages.

To check the list of available commands, use `!help`. To check what an individual command does, write `!help <command>`.

[Add me to your server!](https://discord.com/api/oauth2/authorize?client_id=798683554145894401&permissions=378226048064&scope=bot)

## Initial Setup

1. Give a role with admin permissions to Lammy; she'll need to create roles, ping them, react to messages and be able to write in channels where maybe you don't want other people to do so.
2. Set an administrator group with `!setadmin <AdminRole>`, which will be able to use certain priviledged commands.
3. Set the guild group with `!setmember <GuildRole>`. This is to prevent non-members to check your guild's relevant information, such as nightmare rotation or assignment list.
4. Create a new channel and post `!ask <nightmare>` with as many nightmares as you'd like to take into account. It will auto-react with S, L and checkmark emojis that members should also react to, indicating unevolved, evolved and equipped nightmare, respectively.
5. Write down what nightmare is assigned to what user with `!assign <user> <nightmare>`. This list will be used in the next described command.
6. Set up the initial order of nightmare summoning with `!order <nm1> <nm2> <...>`. Can add nightmares at the start of the list by writing `!order <nm0>`.
7. Set the colosseum start time (UTC) with `!time <UTCtime>`.
8. Assign `@Vanguard` and `@Rearguard` roles to corresponding members so they can be pinged with each colosseum's demon weapons at the appointed time.
9. Run the bot's colosseum aid by typing `!start`.

## Regular actions

- Write down that day's demons with `!sd <FirstDemon> <SecondDemon>`. Check out each demon's indexes by typing `!demonlist`.
- Check that day's demons after tehey have been set with `!getdemons` to check all demon weapons, or use `!demonsvanguard` and `!demonsrearguard` if only interested in vanguad/rearguard weapons.
- Update the assignment list whenever a new member gets an interesting nightmare with `!assign <user> <nightmare>` or change the assignments if necessary.
- Alter the order, if necessary, with any of the `!order` commands, which will reference the assignment list.

## Colosseum actions

- If nightmare summoning can't be done one after the other and time has been lost between summonings, use `!delay <seconds>` to set a delay to all the shotcalls (except the demons' reminder).
- If you want to switch positions in the nightmare summoning (for example, to dounter the enemy's nightmare), use `!order <nightmare1> <nightmare2>`.
- Use `!push` if you want a nightmare to be summoned as soon as possible. Will postpone the remaining nighmares in the order.
