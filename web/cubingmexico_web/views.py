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

from .models import User, WCAProfile, CubingmexicoProfile, PersonStateTeam
from cubingmexico_wca.models import Event
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

class CanEditStateTeamView(PermissionRequiredMixin):
    permission_required = 'cubingmexico_web.edit_stateteam'

    def has_permission(self):
        if self.request.user.is_authenticated:
            try:
                profile = self.request.user.cubingmexicoprofile
                return profile.is_state_team_leader
            except CubingmexicoProfile.DoesNotExist:
                return False
        return False

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
        context['my_single_results'] = get_my_results(wca_id=wca_id, is_average=False)
        context['my_average_results'] = get_my_results(wca_id=wca_id, is_average=True)
        context['wca_profile'] = get_wcaprofile(wca_id=wca_id)
        return context

class RankingsView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/rankings.html'

    def dispatch(self, request, *args, **kwargs):
        self.ranking_type = kwargs.pop('ranking_type', 'single')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        event_type = self.kwargs.get('event_type', '333')
        state = self.kwargs.get('state')
        context = super().get_context_data(**kwargs)
        
        if state:
            context['rankings'] = get_rankings(state=state, event_type=event_type, ranking_type=self.ranking_type)
            context['selected_state'] = state
        else:
            context['rankings'] = get_rankings(event_type=event_type, ranking_type=self.ranking_type)
            context['selected_state'] = None
        
        context['selected_event'] = event_type
        context['selected_ranking'] = self.ranking_type
        context['states'] = State.objects.all()
        context['events'] = Event.objects.exclude(id__in=['333ft', 'magic', 'mmagic', '333mbo']).order_by('rank')
        
        return context
    
class NationalRecordsView(ContentMixin, TemplateView):
    page = 'cubingmexico_web:national_records'

    template_name = 'pages/records/national.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['single_records'] = get_records(is_average=False)
        context['average_records'] = get_records(is_average=True)
        context['events'] = Event.objects.all()
        return context
    
class StateRecordsView(ContentMixin, TemplateView):
    page = 'cubingmexico_web:state_records'

    template_name = 'pages/records/state.html'

    def get_context_data(self, **kwargs):
        state = self.kwargs.get('state', 'CMX')
        context = super().get_context_data(**kwargs)
        context['single_records'] = get_state_records(state=state, is_average=False)
        context['average_records'] = get_state_records(state=state, is_average=True)
        context['selected_state'] = state
        context['states'] = State.objects.all()
        context['events'] = Event.objects.all()
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        wca_ids = WCAProfile.objects.filter(user__cubingmexicoprofile__person_state_team__state_team__id=self.object.pk).values_list('wca_id', flat=True)

        context['team_members'] = PersonStateTeam.objects.filter(state_team_id=self.object.pk).exclude(person__id__in=wca_ids)
        context['auth_team_members'] = User.objects.filter(cubingmexicoprofile__person_state_team__state_team__id=self.object.pk)
        
        return context
    
class EditStateTeamView(ContentMixin, CanEditStateTeamView, UpdateView):
    model = StateTeam
    template_name = 'pages/teams/edit_team.html'
    form_class = StateTeamForm

    def get_success_url(self):
        return reverse_lazy('cubingmexico_web:team', kwargs={'pk': self.object.pk})

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return self.render_to_response(self.get_context_data(form=form))
    
    def get_queryset(self):
        qs = super().get_queryset()
        profile = self.request.user.cubingmexicoprofile
        if profile and profile.person_state_team.state_team:
            qs = qs.filter(pk=profile.person_state_team.state_team.pk)
        else:
            qs = qs.none()
        return qs

class AddStateTeamMemberView(ContentMixin, CanEditStateTeamView, CreateView):
    template_name = 'pages/teams/add_member.html'
    form_class = PersonStateTeamForm

    def get_success_url(self):
        return reverse('cubingmexico_web:team', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['state_team'] = get_object_or_404(StateTeam, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        # Get the StateTeam object based on the URL parameter pk
        state_team = get_object_or_404(StateTeam, pk=self.kwargs['pk'])
        
        # Set the 'state_team' field of the PersonStateTeam instance
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
