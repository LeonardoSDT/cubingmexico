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

from django.db.models import Max, F, Value, Q

from itertools import groupby

import copy

from .models import User, WCAProfile, CubingmexicoProfile, PersonStateTeam
from cubingmexico_wca.models import Event, RanksSingle, RanksAverage, Competition
from .forms import *
from .utils import *
from datetime import date

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
    
class CompetitionsView(ContentMixin, TemplateView):
    template_name = 'pages/competitions.html'
    page = 'cubingmexico_web:competitions'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect(reverse_lazy('cubingmexico_web:logout'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        today = date.today()
        
        upcoming_competitions = Competition.objects.filter(
            Q(country__name='Mexico') & Q(year__gte=today.year) & (
                Q(month__gt=today.month) | (Q(month=today.month) & Q(day__gte=today.day))
            )
        ).annotate(
            competition_state=F('competitionstate__state__name')
        ).order_by('year', 'month', 'day')[:10]

        past_competitions = Competition.objects.filter(
            Q(country__name='Mexico') & (
                Q(year__lt=today.year) | (Q(year=today.year) & Q(month__lt=today.month)) |
                (Q(year=today.year) & Q(month=today.month) & Q(day__lt=today.day))
            )
        ).annotate(
            competition_state=F('competitionstate__state__name')
        ).order_by('-year', '-month', '-day')
        
        context['upcoming_competitions'] = upcoming_competitions
        context['past_competitions'] = past_competitions
        
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
        my_rank_single = RanksSingle.objects.filter(person_id=wca_id).order_by('event__rank')
        context['my_single_results'] = zip(my_single_results, my_rank_single)

        my_average_results = get_records(wca_id=wca_id, is_average=True)
        my_rank_average = RanksAverage.objects.filter(person_id=wca_id).order_by('event__rank')
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
            persons = PersonStateTeam.objects.filter(state_team__state__three_letter_code=state)
            person_ids = persons.values_list('person_id', flat=True)
            if self.ranking_type == 'single':
                rank_single = RanksSingle.objects.filter(event_id=event_type, person_id__in=person_ids).order_by('best')
                context['rankings'] = zip(results, rank_single)
            else:
                rank_average = RanksAverage.objects.filter(event_id=event_type, person_id__in=person_ids).order_by('best')
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
        # Extract 'state' and 'ranking_type' from URL keyword arguments
        state = self.kwargs.get('state')
        ranking_type = self.kwargs.get('ranking_type')
        context = super().get_context_data(**kwargs)

        excluded_event_ids = ['333ft', 'magic', 'mmagic', '333mbo']

        if state:
            # Fetch data for a specific state
            persons = PersonStateTeam.objects.filter(state_team__state__three_letter_code=state)
            person_ids = persons.values_list('person_id', flat=True)
            if ranking_type == 'single':
                sors = RanksSingle.objects.filter(person_id__in=person_ids)
            else:
                sors = RanksAverage.objects.filter(person_id__in=person_ids)

            context['selected_state'] = state
        else:
            # Fetch data for the entire country
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

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect(reverse_lazy('cubingmexico_web:logout'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # Extract 'state' and 'ranking_type' from URL keyword arguments
        state = self.kwargs.get('state')
        context = super().get_context_data(**kwargs)

        excluded_event_ids = ['333ft', 'magic', 'mmagic', '333mbo']

        event_ids = ["333", "222", "444", "555", "666", "777", "333bf", "333fm", "333oh", "clock", "minx", "pyram", "skewb", "sq1", "444bf", "555bf", "333mbf"]

        personal_single_records = {}
        personal_average_records = {}

        if state:
            # Fetch data for a specific state
            persons = PersonStateTeam.objects.filter(state_team__state__three_letter_code=state)
            person_ids = persons.values_list('person_id', flat=True)

            single_records = get_records(state=state, is_average=False)
            average_records = get_records(state=state, is_average=True)
            
            for person in person_ids:
                psr = get_records(state=state, wca_id=person, is_average=False)
                par = get_records(state=state, wca_id=person, is_average=True)

                psr = list(psr.select_related("event", "person").order_by("person_id", "event__rank").values("person__name", "event_id", "best"))
                par = list(par.select_related("event", "person").order_by("person_id", "event__rank").values("person__name", "event_id", "average"))

                for event_id in event_ids:
                    # Check if a record exists for this event and person
                    if not any(record['event_id'] == event_id for record in psr):
                        # If no record exists, add a default record with best = 0
                        psr.append({
                            "event_id": event_id,
                            "best": 0
                        })
                    
                    if not any(record['event_id'] == event_id for record in par):
                        # If no record exists, add a default record with best = 0
                        par.append({
                            "event_id": event_id,
                            "average": 0
                        })

                personal_single_records[person] = psr
                personal_average_records[person] = par

            context['selected_state'] = state
        # else:
        #     # Fetch data for the entire country
        #     persons = Person.objects.all()
        #     person_ids = persons.values_list('id', flat=True)

        #     single_records = get_records(is_average=False)
        #     average_records = get_records(is_average=True)

        #     for person in person_ids:
        #         psr = get_records(wca_id=person, is_average=False)
        #         par = get_records(wca_id=person, is_average=True)

        #         psr = list(psr.select_related("event", "person").order_by("person_id", "event__rank").values("person__name", "event_id", "best"))
        #         par = list(par.select_related("event", "person").order_by("person_id", "event__rank").values("person__name", "event_id", "average"))

        #         for event_id in event_ids:
        #             # Check if a record exists for this event and person
        #             if not any(record['event_id'] == event_id for record in psr):
        #                 # If no record exists, add a default record with best = 0
        #                 psr.append({
        #                     "event_id": event_id,
        #                     "best": 0
        #                 })
                    
        #             if not any(record['event_id'] == event_id for record in par):
        #                 # If no record exists, add a default record with best = 0
        #                 par.append({
        #                     "event_id": event_id,
        #                     "average": 0
        #                 })

        #         personal_single_records[person] = psr
        #         personal_average_records[person] = par
                
        #     context['selected_state'] = None

        # Filter and order data, select related fields
        single_records = list(single_records.select_related("event").order_by("event__rank").values("event_id", "best"))
        average_records = list(average_records.select_related("event").order_by("event__rank").values("event_id", "average"))

        full_single_records = {}
        full_average_records = {}

        # Create a dictionary to map event IDs to their averages
        full_single_records = {record['event_id']: record['best'] for record in single_records}
        full_average_records = {record['event_id']: record['average'] for record in average_records}

        # Create the final list with ordered event averages
        full_single_records = [
            {'event_id': event_id, 'best': full_single_records.get(event_id, 0)}
            for event_id in event_ids
        ]
        full_average_records = [
            {'event_id': event_id, 'average': full_average_records.get(event_id, 0)}
            for event_id in event_ids
        ]

        # Sort records within personal_single_records and personal_average_records by event_id_order
        for person in personal_single_records:
            personal_single_records[person].sort(key=lambda x: event_ids.index(x['event_id']))

        for person in personal_average_records:
            personal_average_records[person].sort(key=lambda x: event_ids.index(x['event_id']))

        # Create a dictionary to store the calculated kinch ranks for each person
        single_kinch_ranks = {}
        average_kinch_ranks = {}

        # Iterate through each person's single records
        for person_id, person_records in personal_single_records.items():
            # person_name = person_records[0]['person__name']
            
            # Initialize a list to store the calculated kinch ranks for the person's events
            person_kinch_ranks = []
            
            # Iterate through each event's records for the person
            for record in person_records:
                event_id = record['event_id']
                personal_single = record['best']
                
                # Find the corresponding single from full_single_records
                corresponding_single = next(item['best'] for item in full_single_records if item['event_id'] == event_id)
                
                # Calculate the kinch rank and append to the person_kinch_ranks list
                if personal_single != 0:  # Avoid division by zero
                    kinch_rank = (corresponding_single / personal_single) * 100
                else:
                    kinch_rank = 0  # Set kinch rank to 0 if personal single is 0
                person_kinch_ranks.append({'event_id': event_id, 'kinch_rank': kinch_rank})
            
            # Calculate the overall kinch rank for the person
            overall_kinch_rank = sum(event_kinch_rank['kinch_rank'] for event_kinch_rank in person_kinch_ranks) / len(person_kinch_ranks)
            
            # Add the person's kinch ranks and overall kinch rank to the dictionary
            single_kinch_ranks[person_id] = {'event_kinch_ranks': person_kinch_ranks, 'overall_kinch_rank': overall_kinch_rank}

        # Iterate through each person's average records
        for person_id, person_records in personal_average_records.items():
            # person_name = person_records[0]['person__name']
            
            # Initialize a list to store the calculated kinch ranks for the person's events
            person_kinch_ranks = []
            
            # Iterate through each event's records for the person
            for record in person_records:
                event_id = record['event_id']
                personal_average = record['average']
                
                # Find the corresponding average from full_average_records
                corresponding_average = next(item['average'] for item in full_average_records if item['event_id'] == event_id)
                
                # Calculate the kinch rank and append to the person_kinch_ranks list
                if personal_average != 0:  # Avoid division by zero
                    kinch_rank = (corresponding_average / personal_average) * 100
                else:
                    kinch_rank = 0  # Set kinch rank to 0 if personal average is 0
                person_kinch_ranks.append({'event_id': event_id, 'kinch_rank': kinch_rank})
            
            # Calculate the overall kinch rank for the person
            overall_kinch_rank = sum(event_kinch_rank['kinch_rank'] for event_kinch_rank in person_kinch_ranks) / len(person_kinch_ranks)
            
            # Add the person's kinch ranks and overall kinch rank to the dictionary
            average_kinch_ranks[person_id] = {'event_kinch_ranks': person_kinch_ranks, 'overall_kinch_rank': overall_kinch_rank}

        single_sorted_kinch_ranks = dict(sorted(single_kinch_ranks.items(), key=lambda item: item[1]['overall_kinch_rank'], reverse=True))
        average_sorted_kinch_ranks = dict(sorted(average_kinch_ranks.items(), key=lambda item: item[1]['overall_kinch_rank'], reverse=True))

        # Initialize the new dictionary
        final_kinch_ranks = {}

        # Define the list of events for each category
        average_events = ["333", "222", "444", "555", "666", "777", "333oh", "clock", "minx", "pyram", "skewb", "sq1"]
        single_events = ["444bf", "555bf", "333mbf"]
        max_events = ["333bf", "333fm"]

        # Iterate through each person's records in average_sorted_kinch_ranks
        for person_name, person_data in average_sorted_kinch_ranks.items():
            new_event_kinch_ranks = []

            # Iterate through each event in average_events
            for event in average_events:
                event_data = next((item for item in person_data['event_kinch_ranks'] if item['event_id'] == event), None)
                if event_data:
                    new_event_kinch_ranks.append(event_data)

            # Add the corresponding single event data from single_sorted_kinch_ranks
            for event in single_events:
                single_event_data = next((item for item in single_sorted_kinch_ranks[person_name]['event_kinch_ranks'] if item['event_id'] == event), None)
                if single_event_data:
                    new_event_kinch_ranks.append(single_event_data)

            # Choose the maximum value for the max_events from both single and average data
            for event in max_events:
                average_event_data = next((item for item in person_data['event_kinch_ranks'] if item['event_id'] == event), None)
                single_event_data = next((item for item in single_sorted_kinch_ranks[person_name]['event_kinch_ranks'] if item['event_id'] == event), None)
                
                if average_event_data and single_event_data:
                    max_kinch_rank = max(average_event_data['kinch_rank'], single_event_data['kinch_rank'])
                    new_event_kinch_ranks.append({'event_id': event, 'kinch_rank': max_kinch_rank})


            # Calculate the overall kinch rank for the person
            overall_kinch_rank = sum(event_kinch_rank['kinch_rank'] for event_kinch_rank in new_event_kinch_ranks) / len(new_event_kinch_ranks)

            # Add the person's kinch ranks and overall kinch rank to the final dictionary
            final_kinch_ranks[person_name] = {'event_kinch_ranks': new_event_kinch_ranks, 'overall_kinch_rank': overall_kinch_rank}

            print(final_kinch_ranks)

        # Iterate through each person's records in average_sorted_kinch_ranks
        for person_name, person_data in final_kinch_ranks.items():
            new_event_kinch_ranks = []

            # Reorder events according to the desired order
            for event in event_ids:
                event_data = next((item for item in person_data['event_kinch_ranks'] if item['event_id'] == event), None)
                if event_data:
                    new_event_kinch_ranks.append(event_data)

            # Calculate the overall kinch rank for the person
            overall_kinch_rank = sum(event_kinch_rank['kinch_rank'] for event_kinch_rank in new_event_kinch_ranks) / len(new_event_kinch_ranks)

            # Add the person's kinch ranks and overall kinch rank to the final dictionary
            final_kinch_ranks[person_name] = {'event_kinch_ranks': new_event_kinch_ranks, 'overall_kinch_rank': overall_kinch_rank}

        # Sort the final_kinch_ranks dictionary by overall_kinch_rank
        final_sorted_kinch_ranks = dict(sorted(final_kinch_ranks.items(), key=lambda item: item[1]['overall_kinch_rank'], reverse=True))

        context['single_sorted_kinch_ranks'] = single_sorted_kinch_ranks
        context['average_sorted_kinch_ranks'] = average_sorted_kinch_ranks

        context['final_sorted_kinch_ranks'] = final_sorted_kinch_ranks

        # Populate the context dictionary with processed data
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
        context['state_teams'] = StateTeam.objects.all()
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

        # Login the user
        login(self.request, wca_profile.user)

        return reverse(redirect_uri)
