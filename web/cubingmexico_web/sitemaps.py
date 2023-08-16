from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import StateTeam

class StateTeamSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return StateTeam.objects.all()

    def location(self, obj):
        return reverse('cubingmexico_web:team', args=[obj.team_code])

sitemaps = {
    'state_teams': StateTeamSitemap,
}
