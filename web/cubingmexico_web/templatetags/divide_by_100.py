from django import template

register = template.Library()

@register.filter()
def divide_by_100(value):
    return value/100
    
