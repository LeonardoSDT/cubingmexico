from django.conf import settings

from cubingmexico_wca.models import Result
from .models import WCAProfile, StateRanksSingle, StateRanksAverage

def wca_authorize_uri():
    authorize_uri = settings.WCA_OAUTH_URI + 'authorize/'
    authorize_uri += '?client_id=' + settings.WCA_CLIENT_ID
    authorize_uri += '&redirect_uri=' + settings.WCA_CALLBACK
    authorize_uri += '&response_type=code&scope='
    return authorize_uri

def wca_access_token_uri(code):
    access_token_uri = settings.WCA_OAUTH_URI + 'token/'
    access_token_uri += '?client_id=' + settings.WCA_CLIENT_ID
    access_token_uri += '&client_secret=' + settings.WCA_CLIENT_SECRET
    access_token_uri += '&redirect_uri=' + settings.WCA_CALLBACK
    access_token_uri += '&code=' + code
    access_token_uri += '&grant_type=authorization_code'
    return access_token_uri

"""
    event_type can be:
    - 222 (2x2x2 Cube)
    - 333 (Rubik's Cube)
    - 333bf (3x3x3 Blindfolded)
    - 333fm (3x3x3 Fewest Moves)
    - 333ft (3x3x3 With Feet)
    - 333mbf (3x3x3 Multi-Blind)
    - 333mbo (Rubik's Cube: Multi blind old style)
    - 333oh (3x3x3 One-Handed)
    - 444 (4x4x4 Cube)
    - 444bf (4x4x4 Blindfolded)
    - 555 (5x5x5 Cube)
    - 555bf (5x5x5 Blindfolded)
    - 666 (6x6x6 Cube)
    - 777 (7x7x7 Cube)
    - clock (Rubik's Clock)
    - magic (Rubik's Magic)
    - minx (Megaminx)
    - mmagic (Master Magic)
    - pyram (Pyraminx)
    - skewb (Skewb)
    - sq1 (Square-1)
    """

DEFAULT_COUNTRY = 'Mexico'
EXCLUDED_EVENTS = ['333ft', 'magic', 'mmagic']

def get_rankings(event_type='333', ranking_type='single', state=None, gender='a'):
    filter_key = 'best' if ranking_type == 'single' else 'average'
    base_query = Result.objects.filter(event=event_type, **{f"{filter_key}__gt": 0})

    if state:
        person_ids = StateRanksSingle.objects.filter(state=state).values_list('rankssingle__person_id', flat=True)
        unique_person_ids = list(set(person_ids))
        filtered_query = base_query.filter(person_id__in=unique_person_ids)
    else:
        filtered_query = base_query.filter(country_id=DEFAULT_COUNTRY)

    if gender != 'a':
        filtered_query = filtered_query.filter(person__gender=gender)

    result_ids = (filtered_query.exclude(event_id__in=EXCLUDED_EVENTS)
                                  .order_by("person_id", filter_key)
                                  .distinct("person_id")
                                  .values_list("id"))

    results = (Result.objects.filter(pk__in=result_ids)
                             .select_related("event", "person", "competition")
                             .order_by(filter_key))

    return results

def get_records(state=None, wca_id=None, is_average=False, gender='a'):
    field = "average" if is_average else "best"
    order_by_fields = ["event_id", field]

    filter_kwargs = {
        f"{field}__gt": 0,
        "person_id__in": get_unique_person_ids(state) if state else None,
        "person_id": wca_id if wca_id else None,
        "country_id": DEFAULT_COUNTRY if not wca_id else None
    }

    filter_kwargs = {k: v for k, v in filter_kwargs.items() if v is not None}

    if gender != 'a':
        result_ids = (
            Result.objects.filter(**filter_kwargs, person__gender=gender)
            .exclude(event_id__in=EXCLUDED_EVENTS)
            .order_by(*order_by_fields)
            .distinct("event_id")
            .values_list("id", flat=True)
        )
    else:
        result_ids = (
            Result.objects.filter(**filter_kwargs)
            .exclude(event_id__in=EXCLUDED_EVENTS)
            .order_by(*order_by_fields)
            .distinct("event_id")
            .values_list("id", flat=True)
        )

    results = (
        Result.objects.filter(pk__in=result_ids)
        .select_related("event", "person", "competition")
        .order_by(*order_by_fields)
    )

    return results.order_by('event__rank')

def get_unique_person_ids(state):
    persons = StateRanksSingle.objects.filter(state=state)
    person_ids = persons.values_list('rankssingle__person_id', flat=True)
    return list(set(person_ids))

def get_wcaprofile(wca_id=''):
    return WCAProfile.objects.filter(wca_id=wca_id).first()
