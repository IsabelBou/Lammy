from typing import List

from discord import Intents

from config.dataclasses import AssignmentData, NightmareData

# The next var defines whether or not the messages have to be printed on the bash.
# In production it must to be set to False
has_to_print = True

BOT_PREFIX = "!"
CASE_INSENSITIVE = True

DISCORD_INTENT = Intents.all()

GUILD_NAME = "Kyobo"
GUILD_ROLE_NAME = GUILD_NAME
VANGUARD_ROLE_NAME = "Vanguard"
REARGUARD_ROLE_NAME = "Rearguard"


# represents: Nightmare (mentioned with role), Assigned person, Total duration
assignments: List[AssignmentData] = []
# nightmare order: Order based on the positions of nightmares in assignments matrix
# 0: mensaje perder ganar 1: asdjhakd
initial_order = []
