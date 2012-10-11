from django.contrib import admin
from django.contrib.sites.models import Site

from regesten_webapp.models import Archive, Concept, Country
from regesten_webapp.models import Family, Footnote, IndexEntry
from regesten_webapp.models import Landmark, Location, Person
from regesten_webapp.models import PersonGroup, Regest, RegestDate
from regesten_webapp.models import Region


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

class RegionInline(admin.StackedInline):
    model = Region

class CountryInline(admin.StackedInline):
    model = Country

class LocationAdmin(admin.ModelAdmin):
    inlines = [
        RegionInline,
        CountryInline,
        ]


admin.site.unregister(Site)

admin.site.register(Regest, RegestAdmin)
admin.site.register(Concept)
admin.site.register(Landmark)
admin.site.register(Location)
admin.site.register(Person)
admin.site.register(PersonGroup)
admin.site.register(Family)
admin.site.register(IndexEntry)
admin.site.register(Region)
admin.site.register(Country)
