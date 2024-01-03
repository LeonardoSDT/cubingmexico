from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse

from cubingmexico_web.models import StateTeam, State
from cubingmexico_wca.models import Person, Event

class StaticViewSitemap(Sitemap):
    def items(self):
        return [
            'cubingmexico_web:index',
            'cubingmexico_web:about',
            # 'cubingmexico_web:development',
            'cubingmexico_web:donations',
            # 'cubingmexico_web:documents',
            'cubingmexico_web:logo',
            'cubingmexico_web:faq',
            'cubingmexico_web:competitions',
            'cubingmexico_web:state_teams',
            'cubingmexico_web:persons',
            ]
    
    def location(self, item):
        return reverse(item)
    
class StateTeamSitemap(Sitemap):
    def items(self):
        return StateTeam.objects.all()
    
class RecordsViewGenderSitemap(Sitemap):
    def items(self):
        return ['a', 'm', 'f']

    def location(self, item):
        return reverse('cubingmexico_web:records', args=[item])
    
class RecordsViewGenderStateSitemap(Sitemap):
    def items(self):
        genders = ['a', 'm', 'f']
        states = State.objects.all()
        return [(gender, state) for gender in genders for state in states]

    def location(self, item):
        gender, state = item
        return reverse('cubingmexico_web:records', args=[gender, state.three_letter_code])
    
class CompetitionsStateSitemap(Sitemap):
    def items(self):
        return State.objects.all()

    def location(self, item):
        return reverse('cubingmexico_web:competitions', args=[item.three_letter_code])
    
class PersonsStateSitemap(Sitemap):
    def items(self):
        return State.objects.all()

    def location(self, item):
        return reverse('cubingmexico_web:persons', args=[item.three_letter_code])
    
class RankingsViewGenderSitemap(Sitemap):
    def items(self):
        genders = ['a', 'm', 'f']
        events = Event.objects.exclude(id__in=['333ft', 'magic', 'mmagic', '333mbo'])
        ranking_types = ['average', 'single']
        return [(gender, event, ranking_type) for gender in genders for ranking_type in ranking_types for event in events]

    def location(self, item):
        gender, event, ranking_type = item
        return reverse('cubingmexico_web:rankings', args=[gender, event.id, ranking_type])

class RankingsViewGenderStateSitemap(Sitemap):
    def items(self):
        genders = ['a', 'm', 'f']
        events = Event.objects.exclude(id__in=['333ft', 'magic', 'mmagic', '333mbo'])
        ranking_types = ['average', 'single']
        states = State.objects.all()
        return [(gender, event, ranking_type, state) for gender in genders for ranking_type in ranking_types for event in events for state in states]

    def location(self, item):
        gender, event, ranking_type, state = item
        return reverse('cubingmexico_web:rankings', args=[gender, event.id, ranking_type, state.three_letter_code])
    
class SORViewGenderSitemap(Sitemap):
    def items(self):
        return ['average', 'single']

    def location(self, item):
        return reverse('cubingmexico_web:sor', args=[item])

class SORViewGenderStateSitemap(Sitemap):
    def items(self):
        ranking_types = ['average', 'single']
        states = State.objects.all()
        return [(ranking_type, state) for ranking_type in ranking_types for state in states]

    def location(self, item):
        ranking_type, state = item
        return reverse('cubingmexico_web:sor', args=[ranking_type, state.three_letter_code])
    
class KinchViewGenderSitemap(Sitemap):
    def items(self):
        return State.objects.all()

    def location(self, item):
        return reverse('cubingmexico_web:kinch', args=[item.three_letter_code])