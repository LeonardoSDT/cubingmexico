from django.conf import settings

from cubingmexico_wca.models import Result

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

def get_single_rankings(event_type='333'):
    """
    Returns the single rankings:
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

    result_ids = (
        Result.objects.filter(country_id='Mexico', event=event_type, best__gt=0)
        .order_by("person_id", "best")
        .distinct("person_id")
        .values_list("id")
    )
    results = (
        Result.objects.filter(pk__in=result_ids)
        .select_related("event", "person", "competition")
        .order_by("best")
    )
    
    return results

def get_average_rankings(event_type='333'):
    """
    Returns the average rankings:
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

    result_ids = (
        Result.objects.filter(country_id='Mexico', event=event_type, average__gt=0)
        .order_by("person_id", "average")
        .distinct("person_id")
        .values_list("id")
    )
    results = (
        Result.objects.filter(pk__in=result_ids)
        .select_related("event", "person", "competition")
        .order_by("average")
    )
    
    return results
