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
    inlines = [
        QuoteInline,
        ]


admin.site.unregister(Site)

admin.site.register(Regest, RegestAdmin)
admin.site.register(Concept, ConceptAdmin)
admin.site.register(Landmark, ConceptAdmin)
admin.site.register(Location, ConceptAdmin)
admin.site.register(Person, ConceptAdmin)
admin.site.register(PersonGroup, ConceptAdmin)
admin.site.register(Family, ConceptAdmin)
admin.site.register(Region)
