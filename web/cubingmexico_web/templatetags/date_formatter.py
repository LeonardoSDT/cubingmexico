from django import template
from django.utils.translation import gettext as _

register = template.Library()

@register.filter(name='format_competition_date_spanish')
def format_competition_date_spanish(competition):
    # Define Spanish month names
    spanish_month_names = [
        _("enero"), _("febrero"), _("marzo"), _("abril"), _("mayo"),
        _("junio"), _("julio"), _("agosto"), _("septiembre"), _("octubre"),
        _("noviembre"), _("diciembre")
    ]
    
    start_day = competition.day
    start_month = competition.month
    end_day = competition.end_day
    end_month = competition.end_month
    
    if end_day and end_month and (start_day != end_day or start_month != end_month):
        if start_month == end_month:
            formatted_date = f"{start_day} al {end_day} de {spanish_month_names[start_month - 1]} de {competition.year}"
        else:
            formatted_date = f"{start_day} de {spanish_month_names[start_month - 1]} al {end_day} de {spanish_month_names[end_month - 1]} de {competition.year}"
    else:
        formatted_date = f"{start_day} de {spanish_month_names[start_month - 1]} de {competition.year}"
    
    return formatted_date
