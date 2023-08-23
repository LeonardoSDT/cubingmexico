from django.contrib import admin
from .models import StateTeam, CubingmexicoProfile, PersonStateTeam, WCAProfile, User, CompetitionState, Competition

# Register your models here.

admin.site.register(User)
admin.site.register(WCAProfile)
admin.site.register(StateTeam)
admin.site.register(PersonStateTeam)
admin.site.register(CubingmexicoProfile)

class CompetitionStateAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "competition":
            kwargs["queryset"] = Competition.objects.filter(country_id="Mexico")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(CompetitionState, CompetitionStateAdmin)