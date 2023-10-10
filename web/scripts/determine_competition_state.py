import logging
import geopandas as gpd
from shapely.geometry import Point

from django.db import transaction

log = logging.getLogger(__name__)

from cubingmexico_wca.models import (
    Competition,
)

from cubingmexico_web.models import (
    CompetitionState,
)

shapefile_path = "shp/mexican_states.shp"
mexican_states = gpd.read_file(shapefile_path)

def find_state(latitude, longitude):
    point = Point(longitude/1000000, latitude/1000000)
    for idx, state in mexican_states.iterrows():
        if state.geometry.contains(point):
            return idx + 1
    return "Unknown"

@transaction.atomic
def determine_competition_state():
    log.info("  determining")
    print("  determining")

    competitions = Competition.objects.filter(country='Mexico')
    for c in competitions:
        id = c.id
        name = c.name
        latitude = c.latitude
        longitude = c.longitude
        state = find_state(latitude, longitude)
        existing_competition_state = CompetitionState.objects.filter(competition=id).first()

        if not existing_competition_state:
            CompetitionState.objects.create(competition_id=id, state_id=state)
            print(f"{name} is in {state}.")

    

def run():
    determine_competition_state()