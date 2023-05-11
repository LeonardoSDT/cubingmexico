import requests

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.views import LogoutView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import Http404
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.crypto import get_random_string
from django.views.generic import TemplateView, DetailView
from django.views.generic.base import RedirectView
from django.views.generic.edit import UpdateView, CreateView

from django.core.files.storage import default_storage

from django.db.models import Max, F

from itertools import groupby

from .models import User, WCAProfile, CubingmexicoProfile, PersonStateTeam
from cubingmexico_wca.models import Event, RanksSingle, RanksAverage
from .forms import *
from .utils import *

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

class ProfileView(AuthenticateMixin, ContentMixin, TemplateView):
    template_name = 'pages/profile.html'
    page = 'cubingmexico_web:profile'

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
                rank_single = RanksSingle.objects.filter(event_id=event_type, person_id__in=person_ids).order_by('country_rank')
                context['rankings'] = zip(results, rank_single)
            else:
                rank_average = RanksAverage.objects.filter(event_id=event_type, person_id__in=person_ids).order_by('country_rank')
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

    def get_context_data(self, **kwargs):
        state = self.kwargs.get('state')
        ranking_type = self.kwargs.get('ranking_type')
        context = super().get_context_data(**kwargs)

        if state:
            persons = PersonStateTeam.objects.filter(state_team__state__three_letter_code=state)
            person_ids = persons.values_list('person_id', flat=True)
            if ranking_type == 'single':
                sors = RanksSingle.objects.filter(person_id__in=person_ids)
            else:
                sors = RanksAverage.objects.filter(person_id__in=person_ids)

            context['selected_state'] = state
        else:
            if ranking_type == 'single':
                sors = RanksSingle.objects.filter(person__country_id='Mexico')
            else:
                sors = RanksAverage.objects.filter(person__country_id='Mexico')

            context['selected_state'] = None

        sors = sors.exclude(event_id__in=['333ft', 'magic', 'mmagic', '333mbo']).select_related("event", "person").order_by('person_id', 'event__rank').values('person_id', 'event_id', 'country_rank')
        
        if ranking_type == 'single':
            worst_country_ranks = RanksSingle.objects.values('event')
        else:
            worst_country_ranks = RanksAverage.objects.values('event')

        wcrs = worst_country_ranks.exclude(event_id__in=['333ft', 'magic', 'mmagic', '333mbo']).annotate(country_rank=Max('country_rank')).order_by('event__rank').annotate(country_rank=F('country_rank') + 1)

        sors_dicts = list(sors)

        wcrs = list(wcrs)

        for item in wcrs:
            item['event_id'] = item.pop('event')

        event_country_rank = {w['event_id']: w['country_rank'] for w in wcrs}

        combined_dicts = sors_dicts

        unique_person_ids = set(sors_dict['person_id'] for sors_dict in sors_dicts)
        for person_id in unique_person_ids:
            for event_id, country_rank in event_country_rank.items():
                if not any(d['person_id'] == person_id and d['event_id'] == event_id for d in combined_dicts):
                    combined_dicts.append({
                        'person_id': person_id,
                        'event_id': event_id,
                        'country_rank': country_rank
                    })

        def group_dictionaries_by_key(dictionaries, key):
            grouped_dicts = sorted(dictionaries, key=lambda x: x[key])
            grouped_dictionaries = []
            
            for _, group in groupby(grouped_dicts, key=lambda x: x[key]):
                grouped_dictionaries.append(list(group))
            
            return grouped_dictionaries

        grouped_dicts = group_dictionaries_by_key(combined_dicts, 'person_id')

        overalls = []
        totals = {}

        for entry in combined_dicts:
            person_id = entry['person_id']
            country_rank = entry['country_rank']
            
            if person_id in totals:
                totals[person_id] += country_rank
            else:
                totals[person_id] = country_rank

        for person_id, total in totals.items():
            overalls.append({'person_id': person_id, 'total': total})

        overalls = sorted(overalls, key=lambda x: x['total'])

        context['ranks'] = zip(grouped_dicts, overalls)
        context['selected_ranking'] = ranking_type
        context['states'] = State.objects.all()
        context['events'] = Event.objects.exclude(id__in=['333ft', 'magic', 'mmagic', '333mbo']).order_by('rank')

        return context

class StateTeamsView(ContentMixin, TemplateView):
    template_name = 'pages/teams/teams.html'
    page = 'cubingmexico_web:state_teams'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['state_teams'] = StateTeam.objects.all()
        return context
    
class IndividualStateTeamView(ContentMixin, DetailView):
    model = StateTeam
    template_name = 'pages/teams/team.html'

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
