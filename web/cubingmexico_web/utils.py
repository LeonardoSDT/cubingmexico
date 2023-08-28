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

def get_rankings(event_type='333', ranking_type='single', state=None):
    filter_key = 'best' if ranking_type == 'single' else 'average'

    result_filter = Result.objects.filter(event=event_type, **{f"{filter_key}__gt": 0})
    if state:
        persons = StateRanksSingle.objects.filter(state=state)
        person_ids = persons.values_list('rankssingle__person_id', flat=True)
        unique_person_ids = list(set(person_ids))
        result_filter = result_filter.filter(person_id__in=unique_person_ids)
    else:
        result_filter = result_filter.filter(country_id='Mexico')
    result_ids = result_filter.exclude(event_id__in=['333ft', 'magic', 'mmagic']).order_by("person_id", filter_key).distinct("person_id").values_list("id")
    results = Result.objects.filter(pk__in=result_ids).select_related("event", "person", "competition").order_by(filter_key)
    return results

def get_records(state=None, wca_id=None, is_average=False):
    if is_average:
        field = "average"
    else:
        field = "best"

    filter_kwargs = {f"{field}__gt": 0}
    exclude_event_ids = ['333ft', 'magic', 'mmagic']
    order_by_fields = ["event_id", field]

    if state:
        persons = StateRanksSingle.objects.filter(state=state)
        person_ids = persons.values_list('rankssingle__person_id', flat=True)
        unique_person_ids = list(set(person_ids))
        filter_kwargs["person_id__in"] = unique_person_ids

    if wca_id:
        filter_kwargs["person_id"] = wca_id
        result_ids = (
            Result.objects.filter(**filter_kwargs)
            .exclude(event_id__in=exclude_event_ids)
            .order_by("event_id", field)
            .distinct("event_id")
            .values_list("id")
        )
    else:
        filter_kwargs["country_id"] = 'Mexico'
        result_ids = (
            Result.objects.filter(**filter_kwargs)
            .exclude(event_id__in=exclude_event_ids)
            .order_by(*order_by_fields)
            .distinct("event_id")
            .values_list("id", flat=True)
        )

    results = (
        Result.objects.filter(pk__in=result_ids)
        .select_related("event", "person", "competition")
        .order_by(*order_by_fields)
    )

    ordered_results = results.order_by('event__rank')

    return ordered_results

def get_wcaprofile(wca_id=''):
    return WCAProfile.objects.filter(wca_id=wca_id).first()
