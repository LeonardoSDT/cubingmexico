from django.contrib import admin
from .models import StateTeam, CubingmexicoProfile, PersonStateTeam, WCAProfile, User

# Register your models here.

admin.site.register(User)
admin.site.register(WCAProfile)
admin.site.register(StateTeam)
admin.site.register(PersonStateTeam)
admin.site.register(CubingmexicoProfile)