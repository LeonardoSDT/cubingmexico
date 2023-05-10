from django import template

register = template.Library()

@register.filter()
def missing_rank_formatter(value):
    return value+1
    
