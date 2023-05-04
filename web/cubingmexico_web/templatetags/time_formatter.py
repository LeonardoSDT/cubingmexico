from django import template

register = template.Library()

@register.filter()
def time_formatter(value):
    value = value/100
    if value >= 60:
        minutes = int(value // 60)
        seconds = value % 60
        time = f"{minutes}:{'0' if seconds < 10 else ''}{seconds:.2f}"
    else:
        time = f"{value:.2f}"

    return time
    
