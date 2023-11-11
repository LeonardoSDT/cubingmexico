import requests

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.views import LogoutView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import Http404
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.crypto import get_random_string
from django.views.generic import TemplateView, DetailView, DeleteView
from django.views.generic.base import RedirectView
from django.views.generic.edit import UpdateView, CreateView

from django.core.files.storage import default_storage

from django.db.models import Max, F, Value, Q, Count

from itertools import groupby

import copy, json

from .models import User, WCAProfile, CubingmexicoProfile, PersonStateTeam, StateRanksSingle, StateRanksAverage, Donor, Sponsor
from cubingmexico_wca.models import Event, RanksSingle, RanksAverage, Competition
from .forms import *
from .utils import *
from datetime import date, datetime

# Create your views here.

class AuthenticateMixin:
    """
    Ensures that users are authenticated.
    We redirect guests to the login page if they aren't logged in.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('cubingmexico_web:index')
        return super(AuthenticateMixin, self).dispatch(request, *args, **kwargs)

class ContentMixin:
    """
    Sets WCA related data into the view's context.
    """
    page = ''

    def get_context_data(self, **kwargs):
        context = super(ContentMixin, self).get_context_data(**kwargs)

        context['last_competition'] = Competition.objects.filter(country='Mexico', result__isnull=False).order_by('result__id').last()

        now = datetime.now()

        past_competition = Competition.objects.filter(
            Q(country__name='Mexico') & (
                Q(year__lt=now.year) | (Q(year=now.year) & Q(month__lt=now.month)) |
                (Q(year=now.year) & Q(month=now.month) & Q(day__lt=now.day))
            )
        ).exclude(
            Q(country__name='Mexico') &
            Q(year=now.year) & Q(month=now.month) & Q(day__lte=now.day) &
            Q(year=now.year) & Q(end_month__gte=now.month) & Q(end_day__gte=now.day)
        ).exclude(id__in=['PerryOpen2013', 'ChapingoOpen2020'])
        
        past_competition_2 = Competition.objects.filter(country='Mexico', result__isnull=False).distinct()

        missing_competitions = past_competition.exclude(
            Q(id__in=past_competition_2.values('id'))
        ).union(
            past_competition_2.exclude(
                Q(id__in=past_competition.values('id'))
            )
        )

        context['missing_competitions'] = missing_competitions

        context['wca_login_uri'] = wca_authorize_uri()
        context['page'] = self.page

        return context
    
class UserLogoutView(LogoutView):
    next_page = 'cubingmexico_web:index'

class IndexView(ContentMixin, TemplateView):
    template_name = 'pages/index.html'
    page = 'cubingmexico_web:index'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect(reverse_lazy('cubingmexico_web:logout'))
        return super().dispatch(request, *args, **kwargs)
    
class AboutView(ContentMixin, TemplateView):
    template_name = 'pages/about/about.html'
    page = 'cubingmexico_web:about'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect(reverse_lazy('cubingmexico_web:logout'))
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        number_person = Person.objects.filter(result__competition__country='Mexico').distinct().count()

        number_competitions  = Competition.objects.filter(country='Mexico', result__isnull=False).distinct().count()

        context['number_competitions'] = number_competitions
        context['number_person'] = number_person

        return context
        
class FAQView(ContentMixin, TemplateView):
    template_name = 'pages/about/faq.html'
    page = 'cubingmexico_web:faq'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect(reverse_lazy('cubingmexico_web:logout'))
        return super().dispatch(request, *args, **kwargs)
    
class DevelopmentView(ContentMixin, TemplateView):
    template_name = 'pages/about/development.html'
    page = 'cubingmexico_web:development'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect(reverse_lazy('cubingmexico_web:logout'))
        return super().dispatch(request, *args, **kwargs)
    
class LogoView(ContentMixin, TemplateView):
    template_name = 'pages/about/logo.html'
    page = 'cubingmexico_web:logo'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect(reverse_lazy('cubingmexico_web:logout'))
        return super().dispatch(request, *args, **kwargs)
    
class DocumentsView(ContentMixin, TemplateView):
    template_name = 'pages/about/documents.html'
    page = 'cubingmexico_web:documents'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect(reverse_lazy('cubingmexico_web:logout'))
        return super().dispatch(request, *args, **kwargs)

class DonationsView(ContentMixin, TemplateView):
    template_name = 'pages/about/donations.html'
    page = 'cubingmexico_web:donations'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect(reverse_lazy('cubingmexico_web:logout'))
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        donors = Donor.objects.filter(is_active=True).order_by('-amount')
        sponsors = Sponsor.objects.filter(is_active=True).order_by('-amount')

        context['donors'] = donors
        context['sponsors'] = sponsors

        return context
    
class DonationCompletedView(ContentMixin, TemplateView):
    template_name = 'pages/about/donations/completed.html'
    page = 'cubingmexico_web:donation_completed'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect(reverse_lazy('cubingmexico_web:logout'))
        return super().dispatch(request, *args, **kwargs)
    
class DonationCancelView(ContentMixin, TemplateView):
    template_name = 'pages/about/donations/cancel.html'
    page = 'cubingmexico_web:donation_cancel'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect(reverse_lazy('cubingmexico_web:logout'))
        return super().dispatch(request, *args, **kwargs)
    
class CompetitionsView(ContentMixin, TemplateView):
    template_name = 'pages/competitions.html'
    page = 'cubingmexico_web:competitions'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect(reverse_lazy('cubingmexico_web:logout'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        state = self.kwargs.get('state')
        context = super().get_context_data(**kwargs)

        context['selected_state'] = state
        context['states'] = State.objects.all()
        
        now = datetime.now()  # Get the current date and time
        
        # Filter upcoming competitions excluding current competitions
        upcoming_competitions = Competition.objects.filter(
            Q(country__name='Mexico') & Q(year__gte=now.year) & (
                Q(month__gt=now.month) | (Q(month=now.month) & Q(day__gte=now.day))
            ) & ~Q(year=now.year, month=now.month, day=now.day)
        ).annotate(
            competition_state=F('competitionstate__state__name')
        ).order_by('year', 'month', 'day')

        # Filter competitions that are in Mexico and have already ended
        past_competitions = Competition.objects.filter(
            Q(country__name='Mexico') & (
                Q(year__lt=now.year) | (Q(year=now.year) & Q(month__lt=now.month)) |
                (Q(year=now.year) & Q(month=now.month) & Q(day__lt=now.day))
            )
        ).annotate(
            competition_state=F('competitionstate__state__name')
        )

        # Exclude competitions that match the current date criteria
        past_competitions = past_competitions.exclude(
            Q(country__name='Mexico') &
            Q(year=now.year) & Q(month=now.month) & Q(day__lte=now.day) &
            Q(year=now.year) & Q(end_month__gte=now.month) & Q(end_day__gte=now.day)
        ).order_by('-year', '-month', '-day')

        # Filter competitions that are being celebrated right now
        current_competitions = Competition.objects.filter(
            Q(country__name='Mexico') &
            Q(year=now.year) & Q(month=now.month) & Q(day__lte=now.day) &
            Q(year=now.year) & Q(end_month__gte=now.month) & Q(end_day__gte=now.day)
        ).annotate(
            competition_state=F('competitionstate__state__name')
        )

        if state:
            upcoming_competitions = upcoming_competitions.filter(competitionstate__state__three_letter_code=state)
            past_competitions = past_competitions.filter(competitionstate__state__three_letter_code=state)
            current_competitions = current_competitions.filter(competitionstate__state__three_letter_code=state)

        context['uc_count'] = upcoming_competitions.count()
        context['pc_count'] = past_competitions.count()
        context['cc_count'] = current_competitions.count()

        context['total_count'] = context['uc_count'] + context['pc_count'] + context['cc_count']

        context['upcoming_competitions'] = upcoming_competitions[:10]
        context['past_competitions'] = past_competitions
        context['current_competitions'] = current_competitions
        
        context['upcoming_competitions_list_json'] = json.dumps(list(upcoming_competitions.values('name', 'latitude', 'longitude', 'competitionstate__state__name')))
        context['past_competitions_list_json'] = json.dumps(list(past_competitions.values('name', 'latitude', 'longitude', 'competitionstate__state__name')))
        context['current_competitions_list_json'] = json.dumps(list(current_competitions.values('name', 'latitude', 'longitude', 'competitionstate__state__name')))
        
        return context

class ProfileView(AuthenticateMixin, ContentMixin, TemplateView):
    template_name = 'pages/profile.html'
    page = 'cubingmexico_web:profile'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect(reverse_lazy('cubingmexico_web:logout'))
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = CubingmexicoProfileForm(request.POST, instance=request.user.cubingmexicoprofile)
        if form.is_valid():
            form.save()
        return redirect('cubingmexico_web:profile')

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        context['form'] = CubingmexicoProfileForm(instance=self.request.user.cubingmexicoprofile)
        return context
    
class MyResultsView(ContentMixin, TemplateView):
    template_name = 'pages/my_results.html'
    page = 'cubingmexico_web:my_results'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect(reverse_lazy('cubingmexico_web:logout'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MyResultsView, self).get_context_data(**kwargs)
        wca_id = self.kwargs['wca_id']
        my_single_results = get_records(wca_id=wca_id, is_average=False)
        my_rank_single = StateRanksSingle.objects.filter(rankssingle__person_id=wca_id).order_by('rankssingle__event__rank')
        context['my_single_results'] = zip(my_single_results, my_rank_single)

        my_average_results = get_records(wca_id=wca_id, is_average=True)
        my_rank_average = StateRanksAverage.objects.filter(ranksaverage__person_id=wca_id).order_by('ranksaverage__event__rank')
        context['my_average_results'] = zip(my_average_results, my_rank_average)

        context['wca_profile'] = get_wcaprofile(wca_id=wca_id)

        return context

class RankingsView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/rankings.html'

    def dispatch(self, request, *args, **kwargs):
        event_type = kwargs.get('event_type')
        ranking_type = kwargs.get('ranking_type')

        if request.user.is_superuser:
            return redirect(reverse_lazy('cubingmexico_web:logout'))
        
        if event_type == '333mbf' and ranking_type == 'average':
            return redirect('cubingmexico_web:rankings', event_type='333mbf', ranking_type='single')
        
        self.ranking_type = kwargs.pop('ranking_type', 'single')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        event_type = self.kwargs.get('event_type', '333')
        state = self.kwargs.get('state')
        context = super().get_context_data(**kwargs)
        
        if state:
            results = get_rankings(state=state, event_type=event_type, ranking_type=self.ranking_type)
            persons = StateRanksSingle.objects.filter(state=state)
            person_ids = persons.values_list('rankssingle__person_id', flat=True)
            unique_person_ids = list(set(person_ids))
            if self.ranking_type == 'single':
                rank_single = RanksSingle.objects.filter(event_id=event_type, person_id__in=unique_person_ids).order_by('best')
                context['rankings'] = zip(results, rank_single)
            else:
                rank_average = RanksAverage.objects.filter(event_id=event_type, person_id__in=unique_person_ids).order_by('best')
                context['rankings'] = zip(results, rank_average)

            context['selected_state'] = state
        else:
            context['rankings'] = get_rankings(event_type=event_type, ranking_type=self.ranking_type)
            context['selected_state'] = None
        
        context['selected_event'] = event_type
        context['selected_ranking'] = self.ranking_type
        context['states'] = State.objects.all()
        context['events'] = Event.objects.exclude(id__in=['333ft', 'magic', 'mmagic', '333mbo']).order_by('rank')
        
        return context
    
class RecordsView(ContentMixin, TemplateView):
    page = 'cubingmexico_web:records'

    template_name = 'pages/records/records.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect(reverse_lazy('cubingmexico_web:logout'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        state = self.kwargs.get('state')
        context = super().get_context_data(**kwargs)
        context['selected_state'] = state
        context['states'] = State.objects.all()
        context['events'] = Event.objects.exclude(id__in=['333ft', 'magic', 'mmagic', '333mbo'])

        if state:
            context['single_records'] = get_records(state=state, is_average=False)
            context['average_records'] = get_records(state=state, is_average=True)
        else:
            context['single_records'] = get_records(is_average=False)
            context['average_records'] = get_records(is_average=True)

        return context

class SORView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/sor.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect(reverse_lazy('cubingmexico_web:logout'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        state = self.kwargs.get('state')
        ranking_type = self.kwargs.get('ranking_type')
        context = super().get_context_data(**kwargs)

        excluded_event_ids = ['333ft', 'magic', 'mmagic', '333mbo']

        if state:
            persons = StateRanksSingle.objects.filter(state=state)
            person_ids = persons.values_list('rankssingle__person_id', flat=True)
            unique_person_ids = list(set(person_ids))
            if ranking_type == 'single':
                sors = RanksSingle.objects.filter(person_id__in=unique_person_ids)
            else:
                sors = RanksAverage.objects.filter(person_id__in=unique_person_ids)

            context['selected_state'] = state
        else:
            if ranking_type == 'single':
                sors = RanksSingle.objects.filter(person__country_id='Mexico')
            else:
                sors = RanksAverage.objects.filter(person__country_id='Mexico')

            context['selected_state'] = None

        # Filter and order data, select related fields
        sors = sors.exclude(event_id__in=excluded_event_ids).select_related("event", "person").order_by('person_id', 'event__rank').values('person__name', 'person_id', 'event_id', 'country_rank')
        
        if ranking_type == 'single':
            worst_country_ranks = RanksSingle.objects.values('event')
        else:
            worst_country_ranks = RanksAverage.objects.values('event')

        wcrs = worst_country_ranks.exclude(event_id__in=excluded_event_ids).annotate(country_rank=Max('country_rank')).order_by('event__rank').annotate(country_rank=F('country_rank') + 1).annotate(has_rank=Value(False))

        wcrs = list(wcrs)

        # Sort data and group by person
        sors = sorted(sors, key=lambda x: (x['person_id'], x['person__name']))

        grouped_sors = groupby(sors, key=lambda x: (x['person_id'], x['person__name']))

        grouped_results = {}

        # Process data and group by person for ranks association
        for (person_id, person__name), group in grouped_sors:
            group_list = list(group)
            
            group_list = [{k: v for k, v in item.items() if k not in ('person_id', 'person__name')} for item in group_list]
            
            grouped_results[(person_id, person__name)] = group_list

        sor_results = {}

        # Associate worst country ranks with actual ranks
        for (person_id, person__name), group in grouped_results.items():
            wcrs_copy = copy.deepcopy(wcrs)
            new_list = []
            for wcr in wcrs_copy:
                for grp in group:
                    if wcr['event'] == grp['event_id']:
                        if grp['country_rank'] == 0:
                            wcr['has_rank'] = False
                        else:
                            wcr['country_rank'] = grp['country_rank']
                            wcr['has_rank'] = True
                        break
                new_list.append(wcr)

            sor_results[(person_id, person__name)] = new_list

        sor_overall_results = {}

        # Calculate overall ranks for each person
        for (person_id, person__name), group in sor_results.items():
            overall = 0
            for item in group:
                overall += item['country_rank']

            sor_overall_results[(person_id, person__name, overall)] = group

        # Populate the context dictionary with processed data
        context['sor_overall_results'] = sorted(sor_overall_results.items(), key=lambda x: x[0][2])
        context['selected_ranking'] = ranking_type
        context['states'] = State.objects.all()
        context['events'] = Event.objects.exclude(id__in=excluded_event_ids).order_by('rank')

        return context
    
class KinchView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/kinch.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect(reverse_lazy('cubingmexico_web:logout'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        state = self.kwargs.get('state')
        context = super().get_context_data(**kwargs)

        excluded_event_ids = ['333ft', 'magic', 'mmagic', '333mbo']

        if state:
            persons = StateRanksSingle.objects.filter(state=state)
            person_ids = persons.values_list('rankssingle__person_id', flat=True)
            unique_person_ids = list(set(person_ids))

            for person in unique_person_ids:
                personal_single_records = get_records(wca_id=person, is_average=False)
                personal_average_records = get_records(wca_id=person, is_average=False)

            state_single_records = get_records(state=state, is_average=False)
            state_average_records = get_records(state=state, is_average=True)

            context['selected_state'] = state
        else:
            persons = Person.objects.all()
            person_ids = persons.values_list('id', flat=True)

            for person in person_ids:
                personal_single_records = get_records(wca_id=person, is_average=False)
                personal_average_records = get_records(wca_id=person, is_average=False)
            
            national_single_records = get_records(is_average=False)
            national_average_records = get_records(is_average=True)

            context['selected_state'] = None

        context['states'] = State.objects.all()
        context['events'] = Event.objects.exclude(id__in=excluded_event_ids).order_by('rank')

        return context

class StateTeamsView(ContentMixin, TemplateView):
    template_name = 'pages/teams/teams.html'
    page = 'cubingmexico_web:state_teams'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect(reverse_lazy('cubingmexico_web:logout'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        state_teams = StateTeam.objects.annotate(person_count=Count('personstateteam'))
        state_teams = state_teams.order_by('-person_count')

        context['state_teams'] = state_teams
        return context
    
class IndividualStateTeamView(ContentMixin, DetailView):
    model = StateTeam
    template_name = 'pages/teams/team.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect(reverse_lazy('cubingmexico_web:logout'))
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        team_code = self.kwargs['team_code']
        state = State.objects.get(three_letter_code=team_code)
        state_team = StateTeam.objects.get(state=state)

        return state_team

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        wca_ids = WCAProfile.objects.filter(user__cubingmexicoprofile__person_state_team__state_team__id=self.object.pk).values_list('wca_id', flat=True)
        context['team_members'] = PersonStateTeam.objects.filter(state_team_id=self.object.pk).exclude(person__id__in=wca_ids)
        context['auth_team_members'] = User.objects.filter(cubingmexicoprofile__person_state_team__state_team__id=self.object.pk)

        return context
    
class EditStateTeamView(ContentMixin, UpdateView):
    model = StateTeam
    form_class = StateTeamForm
    template_name = 'pages/teams/edit_team.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect(reverse_lazy('cubingmexico_web:logout'))

        if not request.user.is_authenticated or not (
            request.user.cubingmexicoprofile.is_state_team_leader and 
            request.user.cubingmexicoprofile.person_state_team.state_team_id == self.get_object().pk
        ):
            return redirect(reverse_lazy('cubingmexico_web:state_teams'))

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('cubingmexico_web:team', args=[self.kwargs['team_code']])

    def get_object(self, queryset=None):
        state = State.objects.get(three_letter_code=self.kwargs['team_code'])
        obj, created = StateTeam.objects.get_or_create(state=state)
        return obj

class AddStateTeamMemberView(ContentMixin, CreateView):
    model = PersonStateTeam
    fields = ['person']
    template_name = 'pages/teams/add_member.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect(reverse_lazy('cubingmexico_web:logout'))
        
        state_team = get_object_or_404(StateTeam, state__three_letter_code=self.kwargs['team_code'])
        if not request.user.is_authenticated or not (
            request.user.cubingmexicoprofile.is_state_team_leader and 
            request.user.cubingmexicoprofile.person_state_team.state_team_id == state_team.pk
        ):
            return redirect(reverse_lazy('cubingmexico_web:state_teams'))

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        state = get_object_or_404(State, three_letter_code=self.kwargs['team_code'])
        return reverse('cubingmexico_web:team', args=[state.three_letter_code])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        state = get_object_or_404(State, three_letter_code=self.kwargs['team_code'])
        context['state'] = state
        return context

    def form_valid(self, form):
        state_team = get_object_or_404(StateTeam, state__three_letter_code=self.kwargs['team_code'])
        person_state_team = form.save(commit=False)
        person_state_team.state_team = state_team
        person_state_team.save()

        person_id = person_state_team.person.id

        try:
            wca_profile = WCAProfile.objects.get(wca_id=person_id)
            user_id = wca_profile.user
            cubingmexico_profile = CubingmexicoProfile.objects.get(user=user_id)
            cubingmexico_profile.person_state_team = person_state_team
            cubingmexico_profile.save()
        except WCAProfile.DoesNotExist:
            pass
        
        return super().form_valid(form)
    
class RemoveStateTeamMemberView(DeleteView):
    model = PersonStateTeam
    template_name = 'pages/teams/remove_member.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect(reverse_lazy('cubingmexico_web:logout'))

        state_team = get_object_or_404(StateTeam, state__three_letter_code=self.kwargs['team_code'])

        if not request.user.is_authenticated:
            return redirect(reverse_lazy('cubingmexico_web:state_teams'))

        # Check if the user is a state team leader and belongs to the same state_team
        user_profile = request.user.cubingmexicoprofile
        if not (user_profile.is_state_team_leader and user_profile.person_state_team.state_team_id == state_team.pk):
            return redirect(reverse_lazy('cubingmexico_web:state_teams'))

        # Restrict the queryset to the current state_team
        self.queryset = PersonStateTeam.objects.filter(state_team=state_team)

        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        state = get_object_or_404(State, three_letter_code=self.kwargs['team_code'])
        return reverse('cubingmexico_web:team', args=[state.three_letter_code])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        state = get_object_or_404(State, three_letter_code=self.kwargs['team_code'])
        context['state'] = state
        return context

class WCACallbackView(RedirectView):
    """
    Validates WCA user, creates a Cubingmexico user and a WCA profile
    if the user is new. Otherwise, we just do authentication.
    """

    def get_redirect_url(self, *args, **kwargs):
        data = self.request.GET
        code = data.get('code')
        redirect_uri = 'cubingmexico_web:index'
        print('WCA Callback: {}'.format(data))

        # Get access token
        access_token_uri = wca_access_token_uri(code)
        response = requests.post(access_token_uri)
        access_token = response.json().get('access_token')

        # Get WCA Profile
        response = requests.get(settings.WCA_API_URI + 'me', headers={
            'Authorization': 'Bearer {}'.format(access_token),
        })
        profile = response.json()
        profile_data = profile.get('me')
        if not profile_data:
            raise Http404
        print('WCA Profile: {}'.format(profile))

        # Check if WCAProfile is already saved, create if not.
        wca_profile = WCAProfile.objects.filter(wca_pk=profile_data['id']).first()
        if not wca_profile:
            # Create user
            user = User.objects.create_user(
                username=str(profile_data['id']),  # Default username is wca_pk
                password=get_random_string(64),  # Generate random password
            )
            # Create WCA profile
            wca_profile = WCAProfile.objects.create(
                user=user,
                wca_pk=profile_data['id'],
                wca_id=profile_data['wca_id'],
                name=profile_data['name'],
                gender=profile_data['gender'],
                country_iso2=profile_data['country_iso2'],
                delegate_status=profile_data['delegate_status'],
                avatar_url=profile_data['avatar']['url'],
                avatar_thumb_url=profile_data['avatar']['thumb_url'],
                is_default_avatar=profile_data['avatar']['is_default'],
                wca_created_at=profile_data['created_at'],
                wca_updated_at=profile_data['updated_at'],
            )
            # Create Cubingmexico profile
            try:
                person_state_team = PersonStateTeam.objects.get(person=wca_profile.wca_id)
                person_state = person_state_team.state_team.state
            except PersonStateTeam.DoesNotExist:
                person_state_team = None
                person_state = None

            CubingmexicoProfile.objects.create(
                user=user,
                state=person_state,
                person_state_team=person_state_team,
            )
            # Redirect new users to their profile page
            redirect_uri = 'cubingmexico_web:profile'

        else:
            wca_profile.name = profile_data['name']
            wca_profile.gender = profile_data['gender']
            wca_profile.avatar_url = profile_data['avatar']['url']
            wca_profile.avatar_thumb_url = profile_data['avatar']['thumb_url']
            wca_profile.is_default_avatar = profile_data['avatar']['is_default']
            wca_profile.save()

        # Login the user
        login(self.request, wca_profile.user)

        return reverse(redirect_uri)
