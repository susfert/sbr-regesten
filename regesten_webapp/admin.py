from django.contrib import admin
from django.contrib.sites.models import Site

from regesten_webapp.models import Archive, Concept, Family
from regesten_webapp.models import Footnote, Landmark, Location
from regesten_webapp.models import Person, PersonGroup, Regest
from regesten_webapp.models import RegestDate, Region


class RegestDateInline(admin.StackedInline):
    model = RegestDate

class ArchiveInline(admin.StackedInline):
    model = Archive

class FootnoteInline(admin.StackedInline):
    model = Footnote

class RegestAdmin(admin.ModelAdmin):
    inlines = [
        RegestDateInline,
        ArchiveInline,
        FootnoteInline,
        ]


admin.site.unregister(Site)

admin.site.register(Regest, RegestAdmin)
admin.site.register(Concept)
admin.site.register(Landmark)
admin.site.register(Location)
admin.site.register(Person)
admin.site.register(PersonGroup)
admin.site.register(Family)
admin.site.register(Region)
