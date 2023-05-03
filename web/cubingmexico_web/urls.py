from django.urls import path

from .views import (
    IndexView, ProfileView, NationalRankingsView, StateRankingsView, StateRecordsView, StateTeamsView, UNRsView, WCACallbackView, UserLogoutView,
)

app_name = 'cubingmexico_web'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('national_rankings/', NationalRankingsView.as_view(), name='national_rankings'),
    path('state_rankings/', StateRankingsView.as_view(), name='state_rankings'),
    path('state_records/', StateRecordsView.as_view(), name='state_records'),
    path('state_teams/', StateTeamsView.as_view(), name='state_teams'),
    path('unrs/', UNRsView.as_view(), name='unrs'),
    path('cubingmexico_wca/callback/', WCACallbackView.as_view(), name='wca_callback'),
]