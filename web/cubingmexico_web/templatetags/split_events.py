from django import template

register = template.Library()

EVENT_ORDER = {
    "333": 0,
    "222": 1,
    "444": 2,
    "555": 3,
    "666": 4,
    "777": 5,
    "333bf": 6,
    "333fm": 7,
    "333oh": 8,
    "clock": 9,
    "minx": 10,
    "pyram": 11,
    "skewb": 12,
    "sq1": 13,
    "444bf": 14,
    "555bf": 15,
    "333mbf": 16,
    "333ft": 17,
    "magic": 18,
    "mmagic": 19,
}

@register.filter
def split_string_and_sort(value):
    event_specs = value.split()
    sorted_event_specs = sorted(event_specs, key=lambda spec: EVENT_ORDER.get(spec, float('inf')))
    return sorted_event_specs
