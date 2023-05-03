from django import template

register = template.Library()

@register.filter()
def divide_by_100(value):
    return float(value) / 100
