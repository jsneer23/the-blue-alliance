from typing import List, TypedDict

from backend.common.models.alliance import EventAlliance
from backend.common.models.keys import TeamKey


class DistrictRecap(TypedDict):
    year: int
    num_teams: int
    num_events: int

    dcmp_winning_alliances: List[EventAlliance]
    dcmp_finalist_alliances: List[EventAlliance]
    dcmp_impact_winners: List[TeamKey]
