import json
import logging
import math
from pathlib import Path

import numpy as np
import pandas as pd
from django.conf import settings
from django.db import transaction

from cubingmexico_wca.models import (
    Championship,
    Competition,
    Continent,
    Country,
    Event,
    Format,
    Person,
    RanksAverage,
    RanksSingle,
    Result,
    RoundType,
)

from cubingmexico_web.models import (
    State,
    PersonStateTeam,
    CubingmexicoProfile,
    StateRanksAverage,
    StateRanksSingle,
)

from collections import defaultdict

log = logging.getLogger(__name__)

PH_ID = "Mexico"
DUMP_DIR = settings.BASE_DIR.joinpath("data/extracted/")


@transaction.atomic
def import_continents():
    log.info("  importing continents")
    print("  importing continents")
    df = pd.read_csv(DUMP_DIR.joinpath("WCA_export_Continents.tsv"), sep="\t")
    df = df.replace({np.nan: None})

    for row in df.itertuples():
        Continent.objects.update_or_create(
            id=row.id,
            defaults={
                "name": row.name,
                "record_name": row.recordName,
                "latitude": row.latitude,
                "longitude": row.longitude,
                "zoom": row.zoom,
            },
        )


@transaction.atomic
def import_countries():
    log.info("  importing countries")
    print("  importing countries")
    df = pd.read_csv(DUMP_DIR.joinpath("WCA_export_Countries.tsv"), sep="\t")
    df = df.replace({np.nan: None})

    for row in df.itertuples():
        Country.objects.update_or_create(
            id=row.id,
            defaults={
                "name": row.name,
                "continent_id": row.continentId,
                "iso2": row.iso2,
            },
        )


@transaction.atomic
def import_events():
    log.info("  importing events")
    print("  importing events")
    df = pd.read_csv(DUMP_DIR.joinpath("WCA_export_Events.tsv"), sep="\t")
    df = df.replace({np.nan: None})

    for row in df.itertuples():
        Event.objects.update_or_create(
            id=row.id,
            defaults={
                "name": row.name,
                "rank": row.rank,
                "format": row.format,
                "cell_name": row.cellName,
            },
        )


@transaction.atomic
def import_formats():
    log.info("  importing formats")
    print("  importing formats")
    df = pd.read_csv(DUMP_DIR.joinpath("WCA_export_Formats.tsv"), sep="\t")
    df = df.replace({np.nan: None})

    for row in df.itertuples():
        Format.objects.update_or_create(
            id=row.id,
            defaults={
                "name": row.name,
                "sort_by": row.sort_by,
                "sort_by_second": row.sort_by_second,
                "expected_solve_count": row.expected_solve_count,
                "trim_fastest_n": row.trim_fastest_n,
                "trim_slowest_n": row.trim_slowest_n,
            },
        )


@transaction.atomic
def import_round_types():
    log.info("  importing round types")
    print("  importing round types")
    df = pd.read_csv(DUMP_DIR.joinpath("WCA_export_RoundTypes.tsv"), sep="\t")
    df = df.replace({np.nan: None})

    for row in df.itertuples():
        RoundType.objects.update_or_create(
            id=row.id,
            defaults={
                "rank": row.rank,
                "name": row.name,
                "cell_name": row.cellName,
                "final": row.final,
            },
        )


@transaction.atomic
def import_competitions():
    df = pd.read_csv(DUMP_DIR.joinpath("WCA_export_Competitions.tsv"), sep="\t")
    df = df.replace({np.nan: None})
    total_chunks = math.ceil(len(df) / 1000)

    for index, group in df.groupby(np.arange(len(df)) // 1000):
        log.info(f"  importing competitions chunk {index + 1}/{total_chunks}")
        print(f"  importing competitions chunk {index + 1}/{total_chunks}")
        with transaction.atomic():
            for row in group.itertuples():
                Competition.objects.update_or_create(
                    id=row.id,
                    defaults={
                        "name": row.name,
                        "city_name": row.cityName,
                        "country_id": row.countryId,
                        "information": row.information,
                        "year": row.year,
                        "month": row.month,
                        "day": row.day,
                        "end_month": row.endMonth,
                        "end_day": row.endDay,
                        "event_specs": row.eventSpecs,
                        "wca_delegate": row.wcaDelegate,
                        "organizer": row.organiser,
                        "venue": row.venue,
                        "venue_address": row.venueAddress,
                        "venue_details": row.venueDetails,
                        "external_website": row.external_website,
                        "cell_name": row.cellName,
                        "latitude": row.latitude,
                        "longitude": row.longitude,
                    },
                )


def get_persons_df():
    df = pd.read_csv(DUMP_DIR.joinpath("WCA_export_Persons.tsv"), sep="\t")
    ph_df = df[df["countryId"] == PH_ID]
    ph_df = ph_df.replace({np.nan: None})
    return ph_df


@transaction.atomic
def import_persons():
    log.info("  importing persons")
    print("  importing persons")
    df = get_persons_df()

    for row in df.itertuples():
        Person.objects.update_or_create(
            id=row.id,
            defaults={
                "subid": row.subid,
                "name": row.name,
                "country_id": row.countryId,
                "gender": row.gender,
            },
        )


@transaction.atomic
def import_ranks_average():
    log.info("  importing ranks average")
    print("  importing ranks average")
    persons_df = get_persons_df()

    df = pd.read_csv(DUMP_DIR.joinpath("WCA_export_RanksAverage.tsv"), sep="\t", dtype={1:str})
    ph_df = df[df["personId"].isin(persons_df["id"])]
    ph_df = ph_df.replace({np.nan: None})

    StateRanksAverage.objects.all().delete()
    RanksAverage.objects.all().delete()

    for row in ph_df.itertuples():
        RanksAverage.objects.create(
            person_id=row.personId,
            event_id=row.eventId,
            best=row.best,
            world_rank=row.worldRank,
            continent_rank=row.continentRank,
            country_rank=row.countryRank,
        )


@transaction.atomic
def import_ranks_single():
    log.info("  importing ranks single")
    print("  importing ranks single")
    persons_df = get_persons_df()

    df = pd.read_csv(DUMP_DIR.joinpath("WCA_export_RanksSingle.tsv"), sep="\t", dtype={1:str})
    ph_df = df[df["personId"].isin(persons_df["id"])]
    ph_df = ph_df.replace({np.nan: None})

    StateRanksSingle.objects.all().delete()
    RanksSingle.objects.all().delete()

    for row in ph_df.itertuples():
        RanksSingle.objects.create(
            person_id=row.personId,
            event_id=row.eventId,
            best=row.best,
            world_rank=row.worldRank,
            continent_rank=row.continentRank,
            country_rank=row.countryRank,
        )


@transaction.atomic
def import_results():
    df = pd.read_csv(DUMP_DIR.joinpath("WCA_export_Results.tsv"), sep="\t")
    ph_df = df[df["personCountryId"] == PH_ID]
    ph_df = ph_df.replace({np.nan: None})
    total_chunks = math.ceil(len(ph_df) / 1000)

    Result.objects.all().delete()

    for index, group in ph_df.groupby(np.arange(len(ph_df)) // 1000):
        log.info(f"  importing results chunk {index + 1}/{total_chunks}")
        print(f"  importing results chunk {index + 1}/{total_chunks}")
        with transaction.atomic():
            for row in group.itertuples():
                Result.objects.create(
                    competition_id=row.competitionId,
                    event_id=row.eventId,
                    round_type_id=row.roundTypeId,
                    pos=row.pos,
                    best=row.best,
                    average=row.average,
                    person_name=row.personName,
                    person_id=row.personId,
                    country_id=row.personCountryId,
                    format_id=row.formatId,
                    value1=row.value1,
                    value2=row.value2,
                    value3=row.value3,
                    value4=row.value4,
                    value5=row.value5,
                    regional_single_record=row.regionalSingleRecord,
                    regional_average_record=row.regionalAverageRecord,
                )


@transaction.atomic
def import_championships():
    log.info("  importing championships")
    print("  importing championships")
    df = pd.read_csv(DUMP_DIR.joinpath("WCA_export_championships.tsv"), sep="\t")
    df = df.replace({np.nan: None})

    for row in df.itertuples():
        Championship.objects.update_or_create(
            id=row.id,
            defaults={
                "competition_id": row.competition_id,
                "championship_type": row.championship_type,
            },
        )


@transaction.atomic
def determine_state_ranks():
    log.info("  determining state ranks")
    print("  determining state ranks")

    people_by_state = defaultdict(list)
    wcaids_by_state = defaultdict(list)

    personstateteam = PersonStateTeam.objects.all()
    for person in personstateteam:
        state_code = person.state_team.state.three_letter_code
        people_by_state[state_code].append(person)

    cubingmexicoprofile = CubingmexicoProfile.objects.all()
    for profile in cubingmexicoprofile:
        if not profile.person_state_team and profile.state:
            state_code = profile.state.three_letter_code
            people_by_state[state_code].append(profile)

    for state_code, people in people_by_state.items():
        for p in people:
            if isinstance(p, PersonStateTeam):
                wcaids_by_state[state_code].append(p.person.id)
            elif isinstance(p, CubingmexicoProfile):
                wcaids_by_state[state_code].append(p.user.wcaprofile.wca_id)

    mexican_states = State.objects.values_list('three_letter_code', flat=True)
    for state in mexican_states:
        if state in wcaids_by_state:
            ids = wcaids_by_state[state]
            rank_single = RanksSingle.objects.filter(person_id__in=ids).exclude(event_id__in=['333ft', 'magic', 'mmagic']).order_by('event_id', 'country_rank')
            rank_average = RanksAverage.objects.filter(person_id__in=ids).exclude(event_id__in=['333ft', 'magic', 'mmagic']).order_by('event_id', 'country_rank')

            event_state_ranks_single = {}
            event_state_ranks_average = {}

            print(f'Determining rankings for {state}')
            for rs in rank_single:
                event_id = rs.event_id

                current_state_rank = event_state_ranks_single.get(event_id, 0) + 1

                event_state_ranks_single[event_id] = current_state_rank

                StateRanksSingle.objects.create(rankssingle=rs, state=state, state_rank=current_state_rank)

            for ra in rank_average:
                event_id = ra.event_id

                current_state_rank = event_state_ranks_average.get(event_id, 0) + 1

                event_state_ranks_average[event_id] = current_state_rank

                StateRanksAverage.objects.create(ranksaverage=ra, state=state, state_rank=current_state_rank)

        else:
            print(f'No IDs found for {state}')

    
    

def start_import():
    import_continents()
    import_countries()
    import_events()
    import_formats()
    import_round_types()
    import_competitions()
    import_persons()
    import_ranks_average()
    import_ranks_single()
    import_results()
    import_championships()
    determine_state_ranks()
    log.info("Data import successful!")
    print("Data import successful!")


def run():
    log.info("Starting import...")
    print("Starting import...")
    previous_metadata = DUMP_DIR.joinpath("previous_metadata.json")

    if previous_metadata.is_file():
        with open(DUMP_DIR.joinpath("metadata.json")) as metadata_file:
            metadata = json.load(metadata_file)
        with open(previous_metadata) as previous_metadata_file:
            previous_metadata = json.load(previous_metadata_file)
        if metadata["export_date"] == previous_metadata["export_date"]:
            log.info("Data is up-to-date.")
            print("Data is up-to-date.")
            return

    start_import()