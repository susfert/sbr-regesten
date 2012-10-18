""" This module defines the data model of the Sbr Regesten webapp. """

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy

from regesten_webapp import AUTHORS, COUNTRIES, REGION_TYPES

class Regest(models.Model):
    """
    The Regest model represents a single regest.
    """

    title = models.CharField(_('title'), max_length=70)
    location = models.CharField(_('location'), max_length=70, null=True)
    regest_type = models.CharField(_('type'), max_length=70, null=True)
    content = models.TextField(_('content'))

    issuer = models.OneToOneField(
        'Person', verbose_name=_('issuer'), null=True)
    mentions = models.ManyToManyField(
        'Concept', verbose_name=_('mentions'), null=True)

    original_date = models.TextField(_('original date'), null=True)
    seal = models.TextField(_('seal'))
    print_info = models.TextField(_('print info'))
    translation = models.TextField(_('translation'), null=True)
    original = models.TextField()

    quotes = generic.GenericRelation('Quote')

    author = models.CharField(_('author'), max_length=3, choices=AUTHORS)

    xml_repr = models.TextField(_('XML representation'))

    def __unicode__(self):
        return u'Regest {0}: {1}'.format(self.id, self.title)

    class Meta:
        verbose_name = 'Regest'
        verbose_name_plural = 'Regesten'


class Archive(models.Model):
    """
    The Archive model represents information about a specific archive
    associated with one or more regests.

    TODO: Add examples
    """

    regest = models.ForeignKey('Regest')
    info = models.TextField()

    def __unicode__(self):
        return u'{0}'.format(self.content)

    class Meta:
        verbose_name = ugettext_lazy('archive')
        verbose_name_plural = ugettext_lazy('archives')


class RegestDate(models.Model):
    """
    The RegestDate model represents the date of a single regest.

    TODO: Add examples
    """

    OFFSET_TYPES = (
        ('vor', 'vor'),
        ('nach', 'nach'),
        ('um', 'um'),
        ('ca.', 'ca.'),
        ('kurz nach', 'kurz nach'),)

    regest = models.OneToOneField('Regest')
    start = models.DateField(_('from'))
    start_offset = models.CharField(
        _('start offset'), max_length=20, choices=OFFSET_TYPES, null=True)
    end = models.DateField(_('to'))
    end_offset = models.CharField(
        _('end offset'), max_length=20, choices=OFFSET_TYPES, null=True)
    alt_date = models.DateField(_('alternative date'), null=True)

    @property
    def exact(self):
        return not self.start_offset and not self.end_offset

    def __unicode__(self):
        return u'\nStarts on {0}\nEnds on {1}\n\n---> ({2})'.format(
            self.start, self.end, 'exact' if self.exact else 'not exact')

    class Meta:
        verbose_name = ugettext_lazy('regest date')
        verbose_name_plural = ugettext_lazy('regest dates')


class Footnote(models.Model):
    """
    The footnote model represents footnotes referenced e.g. in the
    content of a regest.
    """

    regest = models.ForeignKey('Regest')
    content = models.TextField(_('content'))

    def __unicode__(self):
        return u'Footnote {0}:\n{1}'.format(self.id, self.content)

    class Meta:
        verbose_name = ugettext_lazy('Footnote')
        verbose_name_plural = ugettext_lazy('Footnotes')


class MetaInfo(models.Model):
    """
    The MetaInfo model holds meta information about regests.
    """

    regest = models.OneToOneField('Regest')
    comments = models.TextField(_('comments'))
    tags = models.TextField(_('tags'))

    def __unicode__(self):
        return u''

    class Meta:
        verbose_name = ugettext_lazy('meta information')
        verbose_name_plural = ugettext_lazy('meta information')


class Quote(models.Model):
    """
    The Quote model represents quotes embedded e.g. in the content of
    a regest.
    """

    content = models.TextField(_('content'))
    __limit = models.Q(app_label='regesten_webapp', model='regest') | \
              models.Q(app_label='regesten_webapp', model='concept')
    content_type = models.ForeignKey(ContentType, limit_choices_to=__limit)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return u'{0}'.format(self.content)

    class Meta:
        verbose_name = ugettext_lazy('quote')
        verbose_name_plural = ugettext_lazy('quotes')


class IndexEntry(models.Model):
    """
    The IndexEntry model represents a single entry in the index of the
    Sbr Regesten.
    """

    related_entries = models.OneToOneField(
        'self', verbose_name=_('related entries'), null=True)
    xml_repr = models.TextField(_('XML representation'))

    def __unicode__(self):
        return u'IndexEntry {0}\n\n{1}'.format(self.id, self.defines)


class Concept(models.Model):
    """
    The Concept model groups attributes common to all types of
    concepts listed in the index of the Sbr Regesten.
    """

    name = models.TextField(_('name'))
    additional_names = models.TextField(
        _('additional names'), null=True)
    related_concepts = models.ManyToManyField(
        'self', verbose_name=_('related concepts'), null=True)

    quotes = generic.GenericRelation('Quote')

    def __unicode__(self):
        return u'Concept {0}: {1}'.format(self.id, self.name)

    class Meta:
        verbose_name = ugettext_lazy('Concept')
        verbose_name_plural = ugettext_lazy('Concepts')


class Landmark(IndexEntry, Concept):
    """
    The landmark model represents a single landmark listed or
    mentioned in the index of the Sbr Regesten.
    """

    landmark_type = models.CharField(
        _('landmark type'), max_length=30, null=True)

    def __unicode__(self):
        landmark =  u'Landmark {0}: {1}'.format(self.id, self.name)
        if self.landmark_type:
            landmark += u' [{0}]'.format(self.landmark_type)
        return landmark

    class Meta:
        verbose_name = ugettext_lazy('Landmark')
        verbose_name_plural = ugettext_lazy('Landmarks')


class Location(IndexEntry, Concept):
    """
    The Location model represents a single location listed or
    mentioned in the index of the Sbr Regesten.
    """

    location_type = models.CharField(
        _('location type'), max_length=30, null=True)
    abandoned_village = models.NullBooleanField(_('abandoned village'))
    av_ref = models.CharField(
        _('abandoned village reference'), max_length=100, null=True)
    reference_point = models.CharField(
        _('reference point'), max_length=100, null=True)
    district = models.CharField(_('district'), max_length=70, null=True)
    region = models.ForeignKey(
        'Region', verbose_name=_('region'), null=True)
    country = models.CharField(
        _('country'), max_length=20, choices=COUNTRIES, null=True)

    def __unicode__(self):
        location = u'Location {0}: {1}'.format(self.id, self.name)
        if self.location_type:
            location += u' [{0}]'.format(self.location_type)
        return location

    class Meta:
        verbose_name = ugettext_lazy('Location')
        verbose_name_plural = ugettext_lazy('Locations')


class Person(IndexEntry, Concept):
    """
    The Person model represents a single individual listed or
    mentioned in the index of the Sbr Regesten.
    """

    forename = models.CharField(
        _('forename'), max_length=70, null=True)
    surname = models.CharField(
        _('surname'), max_length=70, null=True)
    genname = models.CharField(
        _('generational name'), max_length=30, null=True)
    maidenname = models.CharField(
        _('maiden name'), max_length=70, null=True)
    rolename = models.CharField(
        _('role name'), max_length=70, null=True)
    info = models.TextField(null=True)
    profession = models.CharField(
        _('profession'), max_length=30, null=True)
    resident_of = models.ForeignKey(
        'Location', verbose_name=_('resident of'), null=True)

    def __unicode__(self):
        return u'Person {0}: {1}'.format(self.id, self.name)

    class Meta:
        verbose_name = ugettext_lazy('Person')
        verbose_name_plural = ugettext_lazy('Persons')


class PersonGroup(IndexEntry, Concept):
    """
    The PersonGroup model represents a single group of people related
    e.g. by their profession.
    """

    members = models.ManyToManyField('Person', verbose_name=_('members'))

    def __unicode__(self):
        return u'PersonGroup {0}: {1}'.format(self.id, self.name)

    class Meta:
        verbose_name = ugettext_lazy('Person group')
        verbose_name_plural = ugettext_lazy('Person groups')


class Family(PersonGroup):
    """
    The family model represents a single family.
    """

    location = models.ForeignKey(
        'Location', verbose_name=_('location'), null=True)

    def __unicode__(self):
        return u'Family {0}: {1}'.format(self.id, self.name)

    class Meta:
        """
        Specifies metadata and options for the Family model.
        """

        verbose_name = ugettext_lazy('Family')
        verbose_name_plural = ugettext_lazy('Families')


class Region(models.Model):
    """
    The Region model represents regions mentioned in the (index of
    the) Sbr Regesten.
    """

    name = models.CharField(_('name'), max_length=70)
    region_type = models.CharField(
        _('region type'), max_length=30, choices=REGION_TYPES)

    def __unicode__(self):
        return u'{0}: ({1})'.format(self.name, self.region_type)

    class Meta:
        verbose_name = ugettext_lazy('Region')
        verbose_name_plural = ugettext_lazy('Regions')
