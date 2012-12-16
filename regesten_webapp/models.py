""" This module defines the data model of the Sbr Regesten webapp. """

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy

from regesten_webapp import AUTHORS, COUNTRIES, OFFSET_TYPES, REGION_TYPES
from regesten_webapp import RegestTitleType
from regesten_webapp.utils import RegestTitleAnalyzer, RegestTitleParser

class Regest(models.Model):
    """
    The Regest model represents a single regest.
    """

    title = models.CharField(_('title'), max_length=70)
    location = models.CharField(_('location'), max_length=70, blank=True)
    regest_type = models.CharField(_('type'), max_length=70, blank=True)
    content = models.TextField(_('content'))

    issuer = models.ForeignKey(
        'Person', related_name='regests_issued', verbose_name=_('issuer'),
        null=True)
    mentions = models.ManyToManyField(
        'Concept', related_name='mentioned_in', verbose_name=_('mentions'),
        null=True, blank=True)

    original_date = models.TextField(_('original date'), blank=True)
    seal = models.TextField(_('seal'))
    print_info = models.TextField(_('print info'))
    translation = models.TextField(_('translation'), blank=True)
    original = models.TextField()
    author = models.CharField(_('author'), max_length=3, choices=AUTHORS)

    quotes = generic.GenericRelation('Quote')

    xml_repr = models.TextField(_('XML representation'))

    def save(self, *args, **kwargs):
        super(Regest, self).save(*args, **kwargs)
        self._generate_dates()

    def _generate_dates(self):
        """
        """
        if RegestTitleAnalyzer.contains_simple_additions(self.title):
            dates = RegestTitleParser.extract_dates(
                self.title, RegestTitleType.SIMPLE_ADDITIONS)
        elif RegestTitleAnalyzer.contains_elliptical_additions(self.title):
            dates = RegestTitleParser.extract_dates(
                self.title, RegestTitleType.ELLIPTICAL_ADDITIONS)
        elif RegestTitleAnalyzer.contains_simple_alternatives(self.title):
            dates = RegestTitleParser.extract_dates(
                self.title, RegestTitleType.SIMPLE_ALTERNATIVES)
        elif RegestTitleAnalyzer.contains_elliptical_alternatives(self.title):
            dates = RegestTitleParser.extract_dates(
                self.title, RegestTitleType.ELLIPTICAL_ALTERNATIVES)
        elif RegestTitleAnalyzer.is_simple_range(self.title):
            dates = RegestTitleParser.extract_dates(
                self.title, RegestTitleType.SIMPLE_RANGE)
        elif RegestTitleAnalyzer.is_elliptical_range(self.title):
            dates = RegestTitleParser.extract_dates(
                self.title, RegestTitleType.ELLIPTICAL_RANGE)
        else:
            dates = RegestTitleParser.extract_dates(
                self.title, RegestTitleType.REGULAR)
        self.__delete_existing_dates()
        for start, end, start_offset, end_offset, alt_date in dates:
            RegestDate.objects.create(
                regest=self, start=start, end=end, start_offset=start_offset,
                end_offset=end_offset, alt_date=alt_date)

    def __delete_existing_dates(self):
        # Delete existing dates for current regest to make sure we're
        # not keeping old ones when updating regests in the admin
        # interface
        for regest_date in self.regestdate_set.all():
            regest_date.delete()

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
        return u'{0}'.format(self.info)

    class Meta:
        verbose_name = ugettext_lazy('archive')
        verbose_name_plural = ugettext_lazy('archives')


class RegestDate(models.Model):
    """
    The RegestDate model represents the date of a single regest.

    TODO: Add examples
    """

    regest = models.ForeignKey('Regest')
    start = models.DateField(_('from'))
    start_offset = models.CharField(
        _('start offset'), max_length=20, choices=OFFSET_TYPES)
    end = models.DateField(_('to'))
    end_offset = models.CharField(
        _('end offset'), max_length=20, choices=OFFSET_TYPES)
    alt_date = models.BooleanField(_('alternative date'))

    @property
    def exact(self):
        return not self.start_offset and not self.end_offset

    def __unicode__(self):
        return ugettext_lazy('Starts on') + u' {0}, '.format(self.start) + \
               (ugettext_lazy('ends on') + u' {0}'.format(self.end))

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
        return u'Meta information for regest {0}\n\n' \
               'Tags: {1}\n\n' \
               'Comments: {2}\n'.format(
            self.regest.id, self.tags, self.comments)

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

    related_entries = models.ManyToManyField(
        'self', verbose_name=_('related entries'), null=True, blank=True)
    xml_repr = models.TextField(_('XML representation'))

    def __unicode__(self):
        return ugettext_lazy('Index entry') + ' {0}'.format(self.id)


class Concept(models.Model):
    """
    The Concept model groups attributes common to all types of
    concepts listed in the index of the Sbr Regesten.
    """

    name = models.CharField(_('name'), max_length=70)
    description = models.TextField(_('description'), blank=True)
    additional_names = models.TextField(
        _('additional names'), blank=True)
    related_concepts = models.ManyToManyField(
        'self', verbose_name=_('related concepts'), null=True, blank=True)

    quotes = generic.GenericRelation('Quote')

    def __unicode__(self):
        return ugettext_lazy('Concept') + u' {0}: {1}'.format(
            self.id, self.name)

    class Meta:
        verbose_name = ugettext_lazy('Concept')
        verbose_name_plural = ugettext_lazy('Concepts')


class Landmark(IndexEntry, Concept):
    """
    The landmark model represents a single landmark listed or
    mentioned in the index of the Sbr Regesten.
    """

    landmark_type = models.CharField(
        _('landmark type'), max_length=30)

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
        _('location type'), max_length=30)
    abandoned_village = models.NullBooleanField(_('abandoned village'))
    av_ref = models.CharField(
        _('abandoned village reference'), max_length=100, blank=True)
    reference_point = models.CharField(
        _('reference point'), max_length=100, blank=True)
    district = models.CharField(_('district'), max_length=70, blank=True)
    region = models.ForeignKey(
        'Region', verbose_name=_('region'), null=True, blank=True)
    country = models.CharField(
        _('country'), max_length=20, choices=COUNTRIES, blank=True)

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
        _('forename'), max_length=70)
    surname = models.CharField(
        _('surname'), max_length=70)
    genname = models.CharField(
        _('generational name'), max_length=30, blank=True)
    maidenname = models.CharField(
        _('maiden name'), max_length=70, blank=True)
    rolename = models.CharField(
        _('role name'), max_length=70, blank=True)
    profession = models.CharField(
        _('profession'), max_length=30, blank=True)
    resident_of = models.ForeignKey(
        'Location', verbose_name=_('resident of'), null=True, blank=True)

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
