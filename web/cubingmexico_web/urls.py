from django.urls import path

from .views import *

app_name = 'cubingmexico_web'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('person/<str:wca_id>/', MyResultsView.as_view(), name='my_results'),
    path('rankings/single/<str:event_type>/', NationalRankingsSingleView.as_view(), name='national_rankings_single'),
    path('rankings/average/<str:event_type>/', NationalRankingsAverageView.as_view(), name='national_rankings_average'),
    # path('state_rankings/', StateRankingsView.as_view(), name='state_rankings'),
    # path('state_records/', StateRecordsView.as_view(), name='state_records'),
    path('state_teams/', StateTeamsView.as_view(), name='state_teams'),
    path('team/<int:pk>/', IndividualStateTeamView.as_view(), name='team'),
    path('team/<int:pk>/edit/', EditStateTeamView.as_view(), name='edit_team'),
    # path('unrs/', UNRsView.as_view(), name='unrs'),
    path('cubingmexico_wca/callback/', WCACallbackView.as_view(), name='wca_callback'),
]