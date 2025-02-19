from typing import Dict, List
from backend.common.consts.award_type import AwardType
from backend.common.models.award import Award
from backend.common.models.district import District
from backend.common.models.district_recap import DistrictRecap
from backend.common.models.keys import DistrictKey, Year
from backend.common.queries.award_query import EventAwardsQuery
from backend.common.queries.district_query import DistrictQuery
from backend.common.queries.event_query import (
    DistrictChampsInYearQuery,
    DistrictEventsQuery,
)
from backend.common.queries.team_query import DistrictTeamsQuery


class DistrictRecapHelper:
    @staticmethod
    def make_recaps(districts: List[District]) -> List[DistrictRecap]:
        dcmp_futures = []
        for district in districts:
            dcmp_futures.append(
                DistrictChampsInYearQuery(year=district.year).fetch_async()
            )

        dcmps = []
        for district, future in zip(districts, dcmp_futures):
            dcmp_list = future.get_result()

            dcmp_list = [
                d
                for d in dcmp_list
                if d.district_key.string_id() == district.key.string_id()
            ]
            dcmps.append(dcmp_list)

        finalist_alliances = []
        winning_alliances = []
        for dcmp_list in dcmps:
            dcmp_finalists = []
            dcmp_winners = []

            for dcmp in dcmp_list:
                for alliance in dcmp.alliance_selections:
                    if alliance["status"]["status"] == "won":
                        dcmp_winners.append(alliance)
                    elif (
                        alliance["status"]["status"] == "eliminated"
                        and alliance["status"]["level"] == "f"
                    ):
                        dcmp_finalists.append(alliance)

            finalist_alliances.append(dcmp_finalists)
            winning_alliances.append(dcmp_winners)

        event_futures = []
        for district in districts:
            event_futures.append(
                DistrictEventsQuery(district_key=district.key.string_id()).fetch_async()
            )
        num_events = []
        for future in event_futures:
            num_events.append(len(future.get_result()))

        team_futures = []
        for district in districts:
            team_futures.append(
                DistrictTeamsQuery(district_key=district.key.string_id()).fetch_async()
            )
        num_teams = []
        for future in team_futures:
            num_teams.append(len(future.get_result()))

        award_futures: Dict[Year, List[Award]] = {d.year: [] for d in districts}
        for dcmp_list in dcmps:
            for dcmp in dcmp_list:
                award_futures[dcmp.year].append(
                    EventAwardsQuery(event_key=dcmp.key.string_id()).fetch_async()
                )

        impact_winners: Dict[Year, List[str]] = {d.year: [] for d in districts}
        for year, future_list in award_futures.items():
            for future in future_list:
                awards = future.get_result()
                for award in awards:
                    if award.award_type_enum == AwardType.CHAIRMANS:
                        for team in award.team_list:
                            impact_winners[year].append(team.string_id())

        return [
            DistrictRecap(
                year=district.year,
                num_teams=team_count,
                num_events=event_count,
                dcmp_impact_winners=impact_winners_year,
                dcmp_winning_alliances=winning_alliance,
                dcmp_finalist_alliances=finalist_alliance,
            )
            for district, winning_alliance, finalist_alliance, event_count, team_count, impact_winners_year in zip(
                districts,
                winning_alliances,
                finalist_alliances,
                num_events,
                num_teams,
                impact_winners.values(),
            )
        ]
