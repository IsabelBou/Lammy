from datetime import date, datetime, time, timedelta, timezone
from enum import Enum
from typing import Dict, List, Tuple

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


class Emojis(Enum):
    L = "🇱"
    S = "🇸"
    V = "☑️"
    ZERO = "0️⃣"
    TEN = "🔟"
    THREE = "3️⃣"


EMOJIS_TO_WORD_MAPPING = {
    Emojis.L: "Evolved",
    Emojis.S: "Unevolved",
    Emojis.V: "Equiped"
}

CONQUEST_TIMESLOTS: Tuple[time] = time(8, 30, tzinfo=timezone.utc), time(11, 30, tzinfo=timezone.utc), time(15, 30, tzinfo=timezone.utc), time(
    17, 30, tzinfo=timezone.utc), time(19, 30, tzinfo=timezone.utc), time(21, 30, tzinfo=timezone.utc), time(23, 30, tzinfo=timezone.utc), time(1, 30, tzinfo=timezone.utc), time(3, 30, tzinfo=timezone.utc)


def get_next_conquest(delta: timedelta = timedelta()) -> datetime:
    now = datetime.now(tz=timezone.utc)
    next_conquest_time = min(tuple(
        datetime.combine(date.min, ts, tzinfo=timezone.utc) for ts in CONQUEST_TIMESLOTS
        if datetime.combine(date.min, ts, tzinfo=timezone.utc) > datetime.combine(date.min, now.time(), tzinfo=timezone.utc)
    ) or (datetime.combine(date.min, ts, tzinfo=timezone.utc) for ts in CONQUEST_TIMESLOTS)).time()
    destination = datetime.combine(now.date(), next_conquest_time, tzinfo=timezone.utc) + delta
    return destination
