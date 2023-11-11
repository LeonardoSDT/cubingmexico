from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse

from cubingmexico_web.models import StateTeam

class StaticViewSitemap(Sitemap):
    def items(self):
        return [
            'cubingmexico_web:index',
            'cubingmexico_web:about',
            'cubingmexico_web:development',
            'cubingmexico_web:donations',
            'cubingmexico_web:documents',
            'cubingmexico_web:logo',
            'cubingmexico_web:faq',
            'cubingmexico_web:competitions',
            'cubingmexico_web:records',
            'cubingmexico_web:state_teams',
            ]
    
    def location(self, item):
        return reverse(item)
    
class StateTeamSitemap(Sitemap):
    def items(self):
        return StateTeam.objects.all()