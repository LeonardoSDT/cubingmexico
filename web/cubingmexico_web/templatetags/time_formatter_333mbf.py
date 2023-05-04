from django import template

register = template.Library()

@register.filter()
def time_formatter_333mbf(value):

    value_str = str(value)
    DD = value_str[:2]
    TTTTT = value_str[2:7]
    MM = value_str[7:]

    difference = 99 - int(DD)
    missed = MM
    solved = difference + int(missed)
    attempted = solved + int(missed)

    TTTTT = int(TTTTT)
    minutes = int(TTTTT // 60)
    seconds = TTTTT % 60
    time = f"{solved}/{attempted} {minutes}:{'0' if seconds < 10 else ''}{seconds}"

    return time
    
