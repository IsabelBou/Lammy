from collections import namedtuple
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from discord import Embed
from pandas import Series


def dict_to_named_tuple(dict: dict):
    A = namedtuple("a", dict)
    return A(**dict)


@dataclass(frozen=True)
class NightmareSkill:
    name: str
    sp: int
    duration:  str
    lead_time: int
    description: str


@dataclass(frozen=True)
class NightmareData:
    name: str
    card_id: str
    colo_skill: NightmareSkill
    story_skill: NightmareSkill
    color: int
    resource_name: str
    _short_name: str = field(default=str())

    @classmethod
    def from_series(cls, series: Series):
        as_dict = series.to_dict()
        as_dict["private_short_name"] = as_dict["_short_name"]
        del as_dict["_short_name"]
        series = dict_to_named_tuple(as_dict)
        colo_skill = NightmareSkill(name=series.skill_name, sp=series.sp, duration=series.duration,
                                    lead_time=series.lead_time, description=series.skill_description)
        story_skill = NightmareSkill(name=series.story_skill_name, sp=series.story_skill_sp, duration=series.story_skill_duration,
                                     lead_time=series.story_skill_lead_time, description=series.story_skill_description)
        return cls(name=series.name, card_id=series.card_id, resource_name=series.resource_name, color=series.color,
                   _short_name=series.private_short_name, colo_skill=colo_skill, story_skill=story_skill)

    @property
    def short_name(self):
        return self._short_name.split(",")[0].strip()

    @property
    def embed(self):
        embed = Embed(title=self.name, color=int(self.color))
        embed.add_field(name=self.colo_skill.name, value=self.colo_skill.description.replace(r"\n", "\n"))
        embed.add_field(name=f"Costs {self.colo_skill.sp}SP",
                        value=f"Duration: {self.colo_skill.duration} seconds.\nLead time: {self.colo_skill.lead_time} seconds.")
        embed.set_image(url=f"https://sinoalice.game-db.tw/images/card/CardS{str(self.resource_name).rjust(4, '0')}.png")
        return embed


@dataclass
class User:
    name: str
    mention: str

    def __bool__(self):
        return self.name != self.mention

    def __hash__(self) -> int:
        return hash(self.name)


@dataclass(unsafe_hash=True)
class AssignmentData:
    nm: NightmareData
    user: User
