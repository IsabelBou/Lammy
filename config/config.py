from enum import Enum
from typing import Dict, List

from discord import Intents

from config.dataclasses import AssignmentData, NightmareData, User

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


# nightmare order: Order based on the positions of nightmares in assignments matrix
# 0: mensaje perder ganar 1: asdjhakd
initial_order = list()


class Emojis(Enum):
    L = "🇱"
    S = "🇸"
    V = "☑️"

