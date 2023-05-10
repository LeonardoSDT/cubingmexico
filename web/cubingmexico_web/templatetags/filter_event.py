from django import template

register = template.Library()

@register.filter
def filter_event(value, arg):
    return [item for item in value if item.event_id == arg.id]
