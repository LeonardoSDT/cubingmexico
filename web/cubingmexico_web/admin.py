from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register your models here.
class UserAdmin(UserAdmin):
   # The fields to be used in displaying the User model.
   # These override the definitions on the base UserAdmin
   # that reference specific fields on auth.User.
   list_display = ('id', 'username',  'email', 'is_superuser', 'is_staff', 'first_name', 'last_name', 'date_joined',  'last_login')
admin.site.register(User, UserAdmin)