from dataclasses import dataclass

from numpy import int


@dataclass
class NightmareData:
    sp: int
    duration: int
    name: str
    description: str
    card_id: str
    skill_name: str
    lead_time: int
    color: int


@dataclass
class User:
    name: str
    mention: str

    def __bool__(self):
        return self.name != self.mention

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, o: 'User') -> bool:
        return self.name == o.name and self.mention == o.mention


@dataclass
class AssignmentData:
    nm: NightmareData
    user: User
