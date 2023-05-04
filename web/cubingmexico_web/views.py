import requests

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.views import LogoutView
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from .models import User, WCAProfile, CubingmexicoProfile
from .forms import CubingmexicoProfileForm
from .utils import wca_authorize_uri, wca_access_token_uri, get_single_rankings, get_average_rankings

# Create your views here.

#########################################################################################################################

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
    
class NationalRankings333SingleView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/333/single.html'
    page = 'cubingmexico_web:national_rankings_333_single'

    def get_context_data(self, **kwargs):
        context = super(NationalRankings333SingleView, self).get_context_data(**kwargs)
        context['single_333'] = get_single_rankings(event_type='333')
        context['selected_event'] = '333'
        return context
    
class NationalRankings333AverageView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/333/average.html'
    page = 'cubingmexico_web:national_rankings_333_average'

    def get_context_data(self, **kwargs):
        context = super(NationalRankings333AverageView, self).get_context_data(**kwargs)
        context['average_333'] = get_average_rankings(event_type='333')
        context['selected_event'] = '333'
        return context

class NationalRankings222SingleView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/222/single.html'
    page = 'cubingmexico_web:national_rankings_222_single'

    def get_context_data(self, **kwargs):
        context = super(NationalRankings222SingleView, self).get_context_data(**kwargs)
        context['single_222'] = get_single_rankings(event_type='222')
        context['selected_event'] = '222'
        return context
    
class NationalRankings222AverageView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/222/average.html'
    page = 'cubingmexico_web:national_rankings_222_average'

    def get_context_data(self, **kwargs):
        context = super(NationalRankings222AverageView, self).get_context_data(**kwargs)
        context['average_222'] = get_average_rankings(event_type='222')
        context['selected_event'] = '222'
        return context

class NationalRankings444SingleView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/444/single.html'
    page = 'cubingmexico_web:national_rankings_444_single'

    def get_context_data(self, **kwargs):
        context = super(NationalRankings444SingleView, self).get_context_data(**kwargs)
        context['single_444'] = get_single_rankings(event_type='444')
        context['selected_event'] = '444'
        return context
    
class NationalRankings444AverageView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/444/average.html'
    page = 'cubingmexico_web:national_rankings_444_average'

    def get_context_data(self, **kwargs):
        context = super(NationalRankings444AverageView, self).get_context_data(**kwargs)
        context['average_444'] = get_average_rankings(event_type='444')
        context['selected_event'] = '444'
        return context

class NationalRankings555SingleView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/555/single.html'
    page = 'cubingmexico_web:national_rankings_555_single'

    def get_context_data(self, **kwargs):
        context = super(NationalRankings555SingleView, self).get_context_data(**kwargs)
        context['single_555'] = get_single_rankings(event_type='555')
        context['selected_event'] = '555'
        return context
    
class NationalRankings555AverageView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/555/average.html'
    page = 'cubingmexico_web:national_rankings_555_average'

    def get_context_data(self, **kwargs):
        context = super(NationalRankings555AverageView, self).get_context_data(**kwargs)
        context['average_555'] = get_average_rankings(event_type='555')
        context['selected_event'] = '555'
        return context
    
class NationalRankings666SingleView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/666/single.html'
    page = 'cubingmexico_web:national_rankings_666_single'

    def get_context_data(self, **kwargs):
        context = super(NationalRankings666SingleView, self).get_context_data(**kwargs)
        context['single_666'] = get_single_rankings(event_type='666')
        context['selected_event'] = '666'
        return context
    
class NationalRankings666AverageView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/666/average.html'
    page = 'cubingmexico_web:national_rankings_666_average'

    def get_context_data(self, **kwargs):
        context = super(NationalRankings666AverageView, self).get_context_data(**kwargs)
        context['average_666'] = get_average_rankings(event_type='666')
        context['selected_event'] = '666'
        return context

class NationalRankings777SingleView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/777/single.html'
    page = 'cubingmexico_web:national_rankings_777_single'

    def get_context_data(self, **kwargs):
        context = super(NationalRankings777SingleView, self).get_context_data(**kwargs)
        context['single_777'] = get_single_rankings(event_type='777')
        context['selected_event'] = '777'
        return context
    
class NationalRankings777AverageView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/777/average.html'
    page = 'cubingmexico_web:national_rankings_777_average'

    def get_context_data(self, **kwargs):
        context = super(NationalRankings777AverageView, self).get_context_data(**kwargs)
        context['average_777'] = get_average_rankings(event_type='777')
        context['selected_event'] = '777'
        return context


class NationalRankings333bfSingleView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/333bf/single.html'
    page = 'cubingmexico_web:national_rankings_333bf_single'

    def get_context_data(self, **kwargs):
        context = super(NationalRankings333bfSingleView, self).get_context_data(**kwargs)
        context['single_333bf'] = get_single_rankings(event_type='333bf')
        context['selected_event'] = '3bf'
        return context
    
class NationalRankings333bfAverageView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/333bf/average.html'
    page = 'cubingmexico_web:national_rankings_333bf_average'

    def get_context_data(self, **kwargs):
        context = super(NationalRankings333bfAverageView, self).get_context_data(**kwargs)
        context['average_333bf'] = get_average_rankings(event_type='333bf')
        context['selected_event'] = '3bf'
        return context

class NationalRankings333fmSingleView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/333fm/single.html'
    page = 'cubingmexico_web:national_rankings_333fm_single'

    def get_context_data(self, **kwargs):
        context = super(NationalRankings333fmSingleView, self).get_context_data(**kwargs)
        context['single_333fm'] = get_single_rankings(event_type='333fm')
        context['selected_event'] = '3fm'
        return context
    
class NationalRankings333fmAverageView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/333fm/average.html'
    page = 'cubingmexico_web:national_rankings_333fm_average'

    def get_context_data(self, **kwargs):
        context = super(NationalRankings333fmAverageView, self).get_context_data(**kwargs)
        context['average_333fm'] = get_average_rankings(event_type='333fm')
        context['selected_event'] = '3fm'
        return context

class NationalRankings333ohSingleView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/333oh/single.html'
    page = 'cubingmexico_web:national_rankings_333oh_single'

    def get_context_data(self, **kwargs):
        context = super(NationalRankings333ohSingleView, self).get_context_data(**kwargs)
        context['single_333oh'] = get_single_rankings(event_type='333oh')
        context['selected_event'] = '3oh'
        return context
    
class NationalRankings333ohAverageView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/333oh/average.html'
    page = 'cubingmexico_web:national_rankings_333oh_average'

    def get_context_data(self, **kwargs):
        context = super(NationalRankings333ohAverageView, self).get_context_data(**kwargs)
        context['average_333oh'] = get_average_rankings(event_type='333oh')
        context['selected_event'] = '3oh'
        return context

class NationalRankingsclockSingleView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/clock/single.html'
    page = 'cubingmexico_web:national_rankings_clock_single'

    def get_context_data(self, **kwargs):
        context = super(NationalRankingsclockSingleView, self).get_context_data(**kwargs)
        context['single_clock'] = get_single_rankings(event_type='clock')
        context['selected_event'] = 'clock'
        return context
    
class NationalRankingsclockAverageView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/clock/average.html'
    page = 'cubingmexico_web:national_rankings_clock_average'

    def get_context_data(self, **kwargs):
        context = super(NationalRankingsclockAverageView, self).get_context_data(**kwargs)
        context['average_clock'] = get_average_rankings(event_type='clock')
        context['selected_event'] = 'clock'
        return context

class NationalRankingsminxSingleView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/minx/single.html'
    page = 'cubingmexico_web:national_rankings_minx_single'

    def get_context_data(self, **kwargs):
        context = super(NationalRankingsminxSingleView, self).get_context_data(**kwargs)
        context['single_minx'] = get_single_rankings(event_type='minx')
        context['selected_event'] = 'minx'
        return context
    
class NationalRankingsminxAverageView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/minx/average.html'
    page = 'cubingmexico_web:national_rankings_minx_average'

    def get_context_data(self, **kwargs):
        context = super(NationalRankingsminxAverageView, self).get_context_data(**kwargs)
        context['average_minx'] = get_average_rankings(event_type='minx')
        context['selected_event'] = 'minx'
        return context

class NationalRankingspyramSingleView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/pyram/single.html'
    page = 'cubingmexico_web:national_rankings_pyram_single'

    def get_context_data(self, **kwargs):
        context = super(NationalRankingspyramSingleView, self).get_context_data(**kwargs)
        context['single_pyram'] = get_single_rankings(event_type='pyram')
        context['selected_event'] = 'pyram'
        return context
    
class NationalRankingspyramAverageView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/pyram/average.html'
    page = 'cubingmexico_web:national_rankings_pyram_average'

    def get_context_data(self, **kwargs):
        context = super(NationalRankingspyramAverageView, self).get_context_data(**kwargs)
        context['average_pyram'] = get_average_rankings(event_type='pyram')
        context['selected_event'] = 'pyram'
        return context

class NationalRankingsskewbSingleView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/skewb/single.html'
    page = 'cubingmexico_web:national_rankings_skewb_single'

    def get_context_data(self, **kwargs):
        context = super(NationalRankingsskewbSingleView, self).get_context_data(**kwargs)
        context['single_skewb'] = get_single_rankings(event_type='skewb')
        context['selected_event'] = 'skewb'
        return context
    
class NationalRankingsskewbAverageView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/skewb/average.html'
    page = 'cubingmexico_web:national_rankings_skewb_average'

    def get_context_data(self, **kwargs):
        context = super(NationalRankingsskewbAverageView, self).get_context_data(**kwargs)
        context['average_skewb'] = get_average_rankings(event_type='skewb')
        context['selected_event'] = 'skewb'
        return context

class NationalRankingssq1SingleView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/sq1/single.html'
    page = 'cubingmexico_web:national_rankings_sq1_single'

    def get_context_data(self, **kwargs):
        context = super(NationalRankingssq1SingleView, self).get_context_data(**kwargs)
        context['single_sq1'] = get_single_rankings(event_type='sq1')
        context['selected_event'] = 'sq1'
        return context
    
class NationalRankingssq1AverageView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/sq1/average.html'
    page = 'cubingmexico_web:national_rankings_sq1_average'

    def get_context_data(self, **kwargs):
        context = super(NationalRankingssq1AverageView, self).get_context_data(**kwargs)
        context['average_sq1'] = get_average_rankings(event_type='sq1')
        context['selected_event'] = 'sq1'
        return context

class NationalRankings444bfSingleView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/444bf/single.html'
    page = 'cubingmexico_web:national_rankings_444bf_single'

    def get_context_data(self, **kwargs):
        context = super(NationalRankings444bfSingleView, self).get_context_data(**kwargs)
        context['single_444bf'] = get_single_rankings(event_type='444bf')
        context['selected_event'] = '4bf'
        return context
    
class NationalRankings444bfAverageView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/444bf/average.html'
    page = 'cubingmexico_web:national_rankings_444bf_average'

    def get_context_data(self, **kwargs):
        context = super(NationalRankings444bfAverageView, self).get_context_data(**kwargs)
        context['average_444bf'] = get_average_rankings(event_type='444bf')
        context['selected_event'] = '4bf'
        return context

class NationalRankings555bfSingleView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/555bf/single.html'
    page = 'cubingmexico_web:national_rankings_555bf_single'

    def get_context_data(self, **kwargs):
        context = super(NationalRankings555bfSingleView, self).get_context_data(**kwargs)
        context['single_555bf'] = get_single_rankings(event_type='555bf')
        context['selected_event'] = '5bf'
        return context
    
class NationalRankings555bfAverageView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/555bf/average.html'
    page = 'cubingmexico_web:national_rankings_555bf_average'

    def get_context_data(self, **kwargs):
        context = super(NationalRankings555bfAverageView, self).get_context_data(**kwargs)
        context['average_555bf'] = get_average_rankings(event_type='555bf')
        context['selected_event'] = '5bf'
        return context

class NationalRankings333mbfView(ContentMixin, TemplateView):
    template_name = 'pages/rankings/333mbf/333mbf.html'
    page = 'cubingmexico_web:national_rankings_333mbf'

    def get_context_data(self, **kwargs):
        context = super(NationalRankings333mbfView, self).get_context_data(**kwargs)
        context['single_333mbf'] = get_single_rankings(event_type='333mbf')
        context['selected_event'] = '3mbf'
        return context
    
class StateRankingsView(ContentMixin, TemplateView):
    template_name = 'pages/state/rankings.html'
    page = 'cubingmexico_web:state_rankings'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['segment'] = 'state_rankings'
        return context
    
class StateRecordsView(ContentMixin, TemplateView):
    template_name = 'pages/state/records.html'
    page = 'cubingmexico_web:state_records'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['segment'] = 'state_records'
        return context

class StateTeamsView(ContentMixin, TemplateView):
    template_name = 'pages/state/teams.html'
    page = 'cubingmexico_web:state_teams'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['segment'] = 'state_teams'
        return context
    
class UNRsView(ContentMixin, TemplateView):
    template_name = 'pages/national/unrs.html'
    page = 'cubingmexico_web:unrs'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['segment'] = 'unrs'
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
            CubingmexicoProfile.objects.create(
                user=user,
            )
            # Redirect new users to their profile page
            redirect_uri = 'cubingmexico_web:profile'

        # Login the user
        login(self.request, wca_profile.user)

        return reverse(redirect_uri)
    