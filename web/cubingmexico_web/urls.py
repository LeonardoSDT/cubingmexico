from django.urls import path

from .views import *

app_name = 'cubingmexico_web'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('person/<str:wca_id>/', MyResultsView.as_view(), name='my_results'),
    path('rankings/<str:event_type>/<str:ranking_type>/', RankingsView.as_view(), name='rankings'),
    path('rankings/<str:event_type>/<str:ranking_type>/<str:state>/', RankingsView.as_view(), name='rankings'),
    path('records/', RecordsView.as_view(), name='records'),
    path('records/<str:state>/', RecordsView.as_view(), name='records'),
    path('teams/', StateTeamsView.as_view(), name='state_teams'),
    path('team/<int:pk>/', IndividualStateTeamView.as_view(), name='team'),
    path('team/<int:pk>/edit/', EditStateTeamView.as_view(), name='edit_team'),
    path('team/<int:pk>/add_member/', AddStateTeamMemberView.as_view(), name='add_member'),
    path('cubingmexico_wca/callback/', WCACallbackView.as_view(), name='wca_callback'),
]