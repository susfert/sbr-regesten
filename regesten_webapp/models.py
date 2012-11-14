""" This module defines the data model of the Sbr Regesten webapp. """

import re
from datetime import date

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy

from regesten_webapp import AUTHORS, COUNTRIES, OFFSET_TYPES, REGION_TYPES
from regesten_webapp import DAY_DEFAULT, MONTH_DEFAULT

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
        self._generate_date()

    def _generate_date(self):
        """
        # Examples:
        # - Simple
        # 1009
        # 1235-04
        # 1190-12-20
        #
        # - Location
        # 0977-05-11 Diedenhofen
        # 1285-03-08 St. Arnual
        # 1398-01-18 Frankfurt am Main
        #
        # - ?
        # 0857 (?)
        # 0601-0609 (?)
        # 1426-12-29 (?)
        # 1507-12-27 (?) Saarbruecken
        #
        # - Offset
        # 1350 (ca.)
        # 1267 (um)
        # 1147-06-22 (um)
        # 1253 (vor)
        # 1313-08 (vor)
        # 1236-06-05 (vor)
        # 1434 (nach)
        # 1377-03-08 (nach)
        # 1503-04-22 (post)
        #
        # - Offset + Location
        # 1509 (ca.) Saarbruecken
        # 1065-08-28 Saarbruecken (nach)
        # 1507-12-29 (nach) Saarbruecken
        # 1477-03-29 (kurz nach) Saarbruecken
        # 1504 (um) Saarbruecken
        #
        # - Alternatives
        # 1273 (a)
        # 1273 (b)
        # 1273 (c)
        # 1270-07-21 (a)
        # 1270-07-21 (b)
        # 1270-07-21 (c)
        # 1377-03-08 (d)
        # 1377-03-08 (e)
        # 1377-03-08 (f)
        # 1270-04-27/04-28
        # 1466 [04-28 / 05-01]
        # 1421-10-05 / 1422-10-04
        # 1440-11-12/17
        # 1343-04-12 oder 19
        # 1424-06-09 (a) und (b)
        # 1502-11-22 (1503-02-07)259 Saarbruecken
        # 1506-05-12 bzw. 11-10 bzw. 12-01 Saarbruecken
        # 1520-02-18 [bzw. 1519-03-06] Saarbruecken
        #
        # Alternatives + Location
        # 1442 (a) Saarbruecken
        # 1354-04-01 (a) Toul
        # 1354-04-01 (b) Tull
        # 1504/1505 (a) Saarbruecken
        # 1504/1505 (b) Saarbruecken
        # 1504/1505 (c) Saarbruecken
        #
        # - Alternatives + Offset
        # 1200 (um) (a)
        # 1200 (um) (b)
        # 1472 (a) (ca.)
        # 1472 (b) (ca.)
        # 1450 (a) (ca. Mitte 15. Jh.)
        # 1524/1525 (ca.)
        #
        # - Range
        # 1419-05 bis 06 (Mai bis Juli)
        # 1492-1545 (ohne Datum)
        #
        # - Range + Offset
        # 0935-1000 (ca.)
        # 1518-1520 (ca.)
        # 1431 - 1459 (zwischen)
        # 1482-07-16 (nach) - 1499-01-08 (vor)
        #
        # - Range + Offset + Alternatives
        # 1460-1466 (a) ca.
        # 1460-1466 (b) ca.

        # - MISC
        # 1337-12-
        # 1400 (15. Jh., Anfang)
        # 1419-10-09 (und oefter)
        # 1461-04-28 und 06-15 Saarbruecken
        # 1500 (a) (15. Jh., Ende) Saarbruecken
        # 1500 (b) (15. Jh., Ende) Saarbruecken
        # 1500 (c) (15. Jh., Ende)
        # 1500 (e) (16. Jh., Anfang)
        """
        year, month, day, offset = re.search(
            '(?P<year>\d{4})-?(?P<month>\d{2})?-?(?P<day>\d{2})?' \
                ' ?(\([a-z]\)|\w+)? ?' \
                '\(?(?P<offset>ca\.|nach|kurz nach|um|vor)?\)?',
            self.title).group('year', 'month', 'day', 'offset')
        if year and month and day:
            start = date(int(year), int(month), int(day))
        elif year and month and not day:
            start = date(int(year), int(month), DAY_DEFAULT)
        elif year and not month and not day:
            start = date(int(year), MONTH_DEFAULT, DAY_DEFAULT)
        end = start
        if RegestDate.objects.filter(regest=self).exists():
            regest_date = RegestDate.objects.get(regest=self)
            regest_date.start, regest_date.end = start, end
            regest_date.save()
        else:
            regest_date = RegestDate.objects.create(
                regest=self, start=start, end=end)
        if offset:
            regest_date.start_offset = offset
            regest_date.save()

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

    regest = models.OneToOneField('Regest')
    start = models.DateField(_('from'))
    start_offset = models.CharField(
        _('start offset'), max_length=20, choices=OFFSET_TYPES, blank=True)
    end = models.DateField(_('to'))
    end_offset = models.CharField(
        _('end offset'), max_length=20, choices=OFFSET_TYPES, blank=True)
    alt_date = models.DateField(_('alternative date'), null=True, blank=True)

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
