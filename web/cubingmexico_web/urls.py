from django.urls import path

from .views import (
    IndexView, ProfileView, WCACallbackView, UserLogoutView,
)

app_name = 'cubingmexico_web'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('cubingmexico_wca/callback/', WCACallbackView.as_view(), name='wca_callback'),
]