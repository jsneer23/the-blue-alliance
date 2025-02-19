from typing import Dict, List
from google.appengine.ext import ndb

from backend.common.consts.event_type import EventType
from backend.common.helpers.district_recap_helper import DistrictRecapHelper
from backend.common.models.district import District
from backend.common.models.district_team import DistrictTeam
from backend.common.models.event import Event
from backend.common.models.event_details import EventDetails
from backend.common.models.keys import TeamNumber
from backend.common.models.team import Team
from backend.tests.json_data_importer import JsonDataImporter


def _make_winning_alliance(teams: List[TeamNumber]) -> Dict:
    return {
        "declines": [],
        "picks": [f"frc{team}" for team in teams],
        "status": {
            "current_level_record": {"losses": 0, "ties": 0, "wins": 0},
            "level": "f",
            "record": {"losses": 0, "ties": 0, "wins": 0},
            "status": "won",
        },
    }


def _make_finalist_alliance(teams: List[TeamNumber]) -> Dict:
    return {
        "declines": [],
        "picks": [f"frc{team}" for team in teams],
        "status": {
            "current_level_record": {"losses": 0, "ties": 0, "wins": 0},
            "level": "f",
            "record": {"losses": 0, "ties": 0, "wins": 0},
            "status": "eliminated",
        },
    }


def _make_nonfinalist_alliance(teams: List[TeamNumber]) -> Dict:
    return {
        "declines": [],
        "picks": [f"frc{team}" for team in teams],
        "status": {
            "current_level_record": {"losses": 0, "ties": 0, "wins": 0},
            "level": "sf",
            "record": {"losses": 0, "ties": 0, "wins": 0},
            "status": "eliminated",
        },
    }


def _create_fake_district_1():
    district = District(id="2024ne", year=2024, abbreviation="ne")
    district.put()
    e1 = Event(
        id="2024necmp",
        year=2024,
        event_short="necmp",
        event_type_enum=EventType.DISTRICT_CMP,
        district_key=ndb.Key(District, "2024ne"),
    )
    e1.put()

    e2 = Event(
        id="2024nede",
        year=2024,
        event_short="nede",
        event_type_enum=EventType.DISTRICT,
        district_key=ndb.Key(District, "2024ne"),
    )
    e2.put()

    for t in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
        Team(
            id=f"frc{t}",
            team_number=t,
        ).put()
        DistrictTeam(
            team=ndb.Key(Team, f"frc{t}"),
            district_key=ndb.Key(District, "2024ne"),
            year=2024,
        ).put()

    detail = EventDetails.get_or_insert("2024necmp")
    detail.alliance_selections = [
        _make_finalist_alliance([1, 2, 3]),
        _make_winning_alliance([4, 5, 6]),
        _make_nonfinalist_alliance([7, 8, 9]),
    ]
    detail.put()

    return district


def _create_fake_district_2():
    district = District(id="2023ne", year=2023, abbreviation="ne")
    district.put()

    for t in range(11, 30):
        Team(
            id=f"frc{t}",
            team_number=t,
        ).put()
        DistrictTeam(
            team=ndb.Key(Team, f"frc{t}"),
            district_key=ndb.Key(District, "2023ne"),
            year=2023,
        ).put()

    e1 = Event(
        id="2023necmp",
        year=2023,
        event_short="necmp",
        event_type_enum=EventType.DISTRICT_CMP,
        district_key=ndb.Key(District, "2023ne"),
    )
    e1.put()
    e1_detail = EventDetails.get_or_insert("2023necmp")
    e1_detail.alliance_selections = [
        _make_winning_alliance([11, 12, 13]),
        _make_finalist_alliance([24, 25, 26]),
    ]
    e1_detail.put()

    e2 = Event(
        id="2023necmp1",
        year=2023,
        event_short="necmp1",
        event_type_enum=EventType.DISTRICT_CMP_DIVISION,
        district_key=ndb.Key(District, "2023ne"),
    )
    e2.put()
    e2_detail = EventDetails.get_or_insert("2023necmp1")
    e2_detail.alliance_selections = [
        _make_finalist_alliance([11, 12, 13]),
        _make_winning_alliance([14, 15, 16]),
        _make_nonfinalist_alliance([17, 18, 19]),
    ]
    e2_detail.put()

    e3 = Event(
        id="2023necmp2",
        year=2023,
        event_short="necmp2",
        event_type_enum=EventType.DISTRICT_CMP_DIVISION,
        district_key=ndb.Key(District, "2023ne"),
    )
    e3.put()
    e3_detail = EventDetails.get_or_insert("2023necmp2")
    e3_detail.alliance_selections = [
        _make_finalist_alliance([21, 22, 23]),
        _make_winning_alliance([24, 25, 26]),
        _make_nonfinalist_alliance([27, 28, 29]),
    ]
    e3_detail.put()

    return district


def test_district_recap_helper(ndb_stub) -> None:
    district_1 = _create_fake_district_1()
    district_2 = _create_fake_district_2()

    recaps = DistrictRecapHelper.make_recaps([district_1, district_2])

    assert len(recaps) == 2
    assert recaps[0]["year"] == 2024
    assert recaps[0]["num_teams"] == 10
    assert recaps[0]["num_events"] == 2
    assert recaps[0]["dcmp_winning_alliances"] == [
        {
            "declines": [],
            "picks": ["frc4", "frc5", "frc6"],
            "status": {
                "current_level_record": {"losses": 0, "ties": 0, "wins": 0},
                "level": "f",
                "record": {"losses": 0, "ties": 0, "wins": 0},
                "status": "won",
            },
        },
    ]
    assert recaps[0]["dcmp_finalist_alliances"] == [
        {
            "declines": [],
            "picks": ["frc1", "frc2", "frc3"],
            "status": {
                "current_level_record": {"losses": 0, "ties": 0, "wins": 0},
                "level": "f",
                "record": {"losses": 0, "ties": 0, "wins": 0},
                "status": "eliminated",
            },
        },
    ]

    assert recaps[1]["dcmp_impact_winners"] == []
    assert recaps[1]["year"] == 2023
    assert recaps[1]["num_teams"] == 19
    assert recaps[1]["num_events"] == 3
    assert recaps[1]["dcmp_winning_alliances"] == [
        {
            "declines": [],
            "picks": ["frc11", "frc12", "frc13"],
            "status": {
                "current_level_record": {"losses": 0, "ties": 0, "wins": 0},
                "level": "f",
                "record": {"losses": 0, "ties": 0, "wins": 0},
                "status": "won",
            },
        },
    ]
    assert recaps[1]["dcmp_finalist_alliances"] == [
        {
            "declines": [],
            "picks": ["frc24", "frc25", "frc26"],
            "status": {
                "current_level_record": {"losses": 0, "ties": 0, "wins": 0},
                "level": "f",
                "record": {"losses": 0, "ties": 0, "wins": 0},
                "status": "eliminated",
            },
        },
    ]
    assert recaps[1]["dcmp_impact_winners"] == []
