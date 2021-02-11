from dataclasses import dataclass

from discord.embeds import Embed
from numpy import int


@dataclass(frozen=True)
class NightmareData:
    sp: int
    duration: int
    name: str
    description: str
    card_id: str
    skill_name: str
    lead_time: int
    color: int

    @property
    def embed(self):
        embed = Embed(title=self.name, color=int(self.color))
        embed.add_field(name=self.skill_name, value=self.description.replace(r"\n", "\n"))
        embed.add_field(name="Costs {}SP".format(self.sp),
                        value="Duration: {} seconds.\nLead time: {} seconds.".format(self.duration, self.lead_time))
        embed.set_image(url="https://sinoalice.game-db.tw/images/card/CardS{}.png".format(str(self.card_id).rjust(4, '0')))
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
