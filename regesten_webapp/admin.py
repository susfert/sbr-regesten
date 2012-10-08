from regesten_webapp.models import *
from django.contrib import admin
from django.contrib.sites.models import Site

admin.site.unregister(Site)

admin.site.register(Regest)
admin.site.register(RegestTitle)
admin.site.register(RegestLocation)
admin.site.register(RegestType)
admin.site.register(OriginalDateInfo)
admin.site.register(SealInfo)
admin.site.register(ArchiveInfo)
admin.site.register(PrintInfo)
admin.site.register(TranslationInfo)
admin.site.register(OriginalInfo)
admin.site.register(RegestDate)
admin.site.register(StartDate)
admin.site.register(EndDate)
admin.site.register(Content)
admin.site.register(RegestContent)
admin.site.register(Footnote)
admin.site.register(Quote)
admin.site.register(Concept)
admin.site.register(SpecificConcept)
admin.site.register(Landmark)
admin.site.register(Location)
admin.site.register(Person)
admin.site.register(PersonGroup)
admin.site.register(Family)
admin.site.register(IndexEntry)
admin.site.register(Region)
admin.site.register(Country)

