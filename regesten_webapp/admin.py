from django.contrib import admin
from django.contrib.contenttypes.generic import GenericStackedInline
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _

from regesten_webapp.models import Archive, Concept, Family
from regesten_webapp.models import Footnote, Landmark, Location
from regesten_webapp.models import MetaInfo, Person, PersonGroup
from regesten_webapp.models import Quote, Regest, RegestDate
from regesten_webapp.models import Region


class RegestDateInline(admin.StackedInline):
    model = RegestDate

class ArchiveInline(admin.StackedInline):
    model = Archive
    extra = 2

class FootnoteInline(admin.StackedInline):
    model = Footnote
    extra = 2

class QuoteInline(GenericStackedInline):
    model = Quote
    extra = 2

class MetaInfoInline(admin.StackedInline):
    model = MetaInfo

class RegestAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (('title', 'location', 'regest_type'),)
            }
         ),
        (_('Content'), {
            'fields': ('issuer', 'content', 'mentions')
            },
         ),
        (_('Additional information'), {
            'fields': (
                'original_date', 'seal', 'print_info',
                'translation', 'original', 'author')
            })
        )

    inlines = [
        RegestDateInline,
        ArchiveInline,
        FootnoteInline,
        QuoteInline,
        MetaInfoInline,
        ]

class ConceptAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'description')
            }
         ),
        (_('Additional information'), {
            'fields': (
                'additional_names', 'related_concepts')
            }
         ),
        )

    inlines = [
        QuoteInline,
        ]

class LandmarkAdmin(ConceptAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'landmark_type')
            }
         ),
        (_('Additional information'), {
            'fields': (
                'additional_names', 'related_concepts')
            }
         ),
        (_('Index entry'), {
            'fields': ('related_entries', 'xml_repr')
            }
         ),
        )

class LocationAdmin(ConceptAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'location_type', 'abandoned_village')
            }
         ),
        (_('Details'), {
            'fields': (
                'reference_point', 'district', 'region', 'country', 'av_ref')
            }
         ),
        (_('Additional information'), {
            'fields': (
                'additional_names', 'related_concepts')
            }
         ),
        (_('Index entry'), {
            'fields': ('related_entries', 'xml_repr')
            }
         ),
        )

class PersonAdmin(ConceptAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'description')
            }
         ),
        (_('Details'), {
            'fields': (
                'forename', 'surname', 'genname', 'maidenname', 'rolename',
                'profession', 'resident_of')
            }
         ),
        (_('Additional information'), {
            'fields': (
                'additional_names', 'related_concepts')
            }
         ),
        (_('Index entry'), {
            'fields': ('related_entries', 'xml_repr')
            }
         ),
        )

class PersonGroupAdmin(ConceptAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'members')
            }
         ),
        (_('Additional information'), {
            'fields': (
                'additional_names', 'related_concepts')
            }
         ),
        (_('Index entry'), {
            'fields': ('related_entries', 'xml_repr')
            }
         ),
        )

class FamilyAdmin(ConceptAdmin):
    fieldsets = (
        (None, {
            'fields': (('name', 'location'), 'members')
            }
         ),
        (_('Additional information'), {
            'fields': (
                'additional_names', 'related_concepts')
            }
         ),
        (_('Index entry'), {
            'fields': ('related_entries', 'xml_repr')
            }
         ),
        )


admin.site.unregister(Site)

admin.site.register(Regest, RegestAdmin)
admin.site.register(Concept, ConceptAdmin)
admin.site.register(Landmark, LandmarkAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(PersonGroup, PersonGroupAdmin)
admin.site.register(Family, FamilyAdmin)
admin.site.register(Region)
