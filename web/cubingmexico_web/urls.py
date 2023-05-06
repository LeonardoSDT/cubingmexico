from django.urls import path

from .views import *

app_name = 'cubingmexico_web'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('person/<str:wca_id>/', MyResultsView.as_view(), name='my_results'),
    path('rankings/<str:event_type>/single/', NationalRankingsView.as_view(), name='national_rankings_single', kwargs={'ranking_type': 'single'}),
    path('rankings/<str:event_type>/average/', NationalRankingsView.as_view(), name='national_rankings_average', kwargs={'ranking_type': 'average'}),
    path('national_records/', NationalRecordsView.as_view(), name='national_records'),
    path('rankings/<str:state>/<str:event_type>/single/', StateRankingsView.as_view(), name='state_rankings_single', kwargs={'ranking_type': 'single'}),
    path('rankings/<str:state>/<str:event_type>/average/', StateRankingsView.as_view(), name='state_rankings_average', kwargs={'ranking_type': 'average'}),
    path('teams/', StateTeamsView.as_view(), name='state_teams'),
    path('team/<int:pk>/', IndividualStateTeamView.as_view(), name='team'),
    path('team/<int:pk>/edit/', EditStateTeamView.as_view(), name='edit_team'),
    path('cubingmexico_wca/callback/', WCACallbackView.as_view(), name='wca_callback'),
]