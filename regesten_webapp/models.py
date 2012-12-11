""" This module defines the data model of the Sbr Regesten webapp. """

import re
from datetime import date

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy

from regesten_webapp import AUTHORS, COUNTRIES, OFFSET_TYPES, REGION_TYPES
from regesten_webapp import DAY_DEFAULT, MONTH_DEFAULT, RegestTitleType

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
        # - Duplicates
        # 1273 (a)
        # 1273 (b)
        # 1273 (c)
        # 1270-07-21 (a)
        # 1270-07-21 (b)
        # 1270-07-21 (c)
        # 1377-03-08 (d)
        # 1377-03-08 (e)
        # 1377-03-08 (f)
        # 1424-06-09 (a) und (b)
        #
        # Duplicates + Location
        # 1442 (a) Saarbruecken
        # 1354-04-01 (a) Toul
        # 1354-04-01 (b) Tull
        #
        # - Duplicates + Offset
        # 1200 (um) (a)
        # 1200 (um) (b)
        # 1472 (a) (ca.)
        # 1472 (b) (ca.)
        # 1450 (a) (ca. Mitte 15. Jh.)
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
        # - Range + Offset + Duplicates
        # 1460-1466 (a) ca.
        # 1460-1466 (b) ca.
        #
        # - Alternatives
        # 1270-04-27/04-28
        # 1466 [04-28 / 05-01]
        # 1421-10-05 / 1422-10-04
        # 1440-11-12/17
        # 1343-04-12 oder 19
        #
        # - Alternatives + Location
        # 1502-11-22 (1503-02-07)259 Saarbruecken
        # 1506-05-12 bzw. 11-10 bzw. 12-01 Saarbruecken
        # 1520-02-18 [bzw. 1519-03-06] Saarbruecken
        #
        # - Alternatives + Offset
        # 1524/1525 (ca.)
        #
        # - Alternatives + Duplicates + Location
        # 1504/1505 (a) Saarbruecken
        # 1504/1505 (b) Saarbruecken
        # 1504/1505 (c) Saarbruecken

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
        if self.__contains_simple_additions(self.title):
            dates = self.__extract_dates(
                RegestTitleType.SIMPLE_ADDITIONS)
        elif self.__contains_elliptical_additions(self.title):
            dates = self.__extract_dates(
                RegestTitleType.ELLIPTICAL_ADDITIONS)
        elif self.__contains_simple_alternatives(self.title):
            dates = self.__extract_dates(
                RegestTitleType.SIMPLE_ALTERNATIVES)
        elif self.__contains_elliptical_alternatives(self.title):
            dates = self.__extract_dates(
                RegestTitleType.ELLIPTICAL_ALTERNATIVES)
        elif self.__is_simple_range(self.title):
            dates = self.__extract_dates(
                RegestTitleType.SIMPLE_RANGE)
        elif self.__is_elliptical_range(self.title):
            dates = self.__extract_dates(
                RegestTitleType.ELLIPTICAL_RANGE)
        else:
            dates = self.__extract_dates(
                RegestTitleType.REGULAR)
        self.__delete_existing_dates()
        for start, end, start_offset, end_offset, alt_date in dates:
            RegestDate.objects.create(
                regest=self, start=start, end=end, start_offset=start_offset,
                end_offset=end_offset, alt_date=alt_date)

    def __contains_simple_additions(self, string):
        return re.match(
            '\d{4}(-\d{2}){0,2}' \
                ' [\(\[]?und ' \
                '\d{4}(-\d{2}){0,2}', string)

    def __contains_elliptical_additions(self, string):
        return re.match(
            '\d{4}(-\d{2}){0,2}' \
                ' [\(\[]?und ' \
                '\d{2}(-\d{2})?', string)

    def __contains_simple_alternatives(self, string):
        return re.match(
            '\d{4}(-\d{2}){0,2}' \
                '( ?/ ?| [\(\[]| [\(\[]?bzw\.? | [\(\[]?oder )' \
                '\d{4}(-\d{2}){0,2}', string)

    def __contains_elliptical_alternatives(self, string):
        return re.match(
            '\d{4}(-\d{2}){0,2}' \
                '( ?/ ?| [\(\[]| [\(\[]?bzw\.? | [\(\[]?oder )' \
                '\d{2}(-\d{2})?', string)

    def __is_simple_range(self, string):
        '''
        Checks whether or not string represents a "simple" date range.

        Simple date ranges are non-elliptical, i.e. they include year,
        month, and day information for both start and end date.
        '''
        return re.match('(\d{4}-\d{2}-\d{2}|\d{4}-\d{2}|\d{4})' \
                            '( \(.{2,}\))?' \
                            ' ?- ?' \
                            '(\d{4}-\d{2}-\d{2}|\d{4}-\d{2}|\d{4})', string)

    def __is_elliptical_range(self, string):
        '''
        Checks whether or not string starts with an "elliptical" date
        range.

        Elliptical date ranges are used to denote time spans that are
        shorter than one year. Depending on the level of precision
        (month or day), they omit year or year and month information
        in the end date. In the Sbr Regesten, they always use 'bis'
        instead of '-' to separate start and end date of the range.

        Examples:
        - 1419-05 bis 06 (denotes a time span of one month ranging
          from May to June of 1419)
        - 1419-05-10 bis 20 (denotes a time span of ten days ranging
          from May 10th to May 20th, 1419).
        '''
        return re.match('^\d{4}-\d{2}(-\d{2})? bis \d{2}(\D.*|)$', string)

    def __extract_dates(self, title_type):
        if title_type == RegestTitleType.REGULAR:
            start, offset = re.search(
                '(?P<start>\d{4}-\d{2}-\d{2}|\d{4}-\d{2}|\d{4})' \
                    ' ?(\([a-z]\)|[\w\. ]+)? ?' \
                    '\(?(?P<offset>' \
                    'ca\.|nach|kurz nach|post|um|vor)?\)?',
                self.title).group('start', 'offset')
            start = self.__extract_date(start)
            start_offset, end_offset = self.__determine_offsets(
                offset, offset, title_type)
            return [(start, start, start_offset, end_offset, False)]
        elif title_type == RegestTitleType.SIMPLE_RANGE:
            start, start_offset, end, end_offset = re.search(
                '(?P<start>\d{4}-\d{2}-\d{2}|\d{4}-\d{2}|\d{4})' \
                    ' ?\(?(?P<start_offset>' \
                    'ca\.|nach|kurz nach|post|um|vor)?\)?' \
                    ' ?- ?' \
                    '(?P<end>\d{4}-\d{2}-\d{2}|\d{4}-\d{2}|\d{4})' \
                    ' ?(\([a-z]\)|[\w\. ]+)? ?' \
                    '\(?(?P<end_offset>' \
                    'ca\.|nach|kurz nach|post|um|vor|zwischen)?\)?',
                self.title).group(
                'start', 'start_offset', 'end', 'end_offset')
            start = self.__extract_date(start)
            end = self.__extract_date(end)
            start_offset, end_offset = self.__determine_offsets(
                start_offset=start_offset, end_offset=end_offset,
                title_type=title_type)
            return [(start, end, start_offset, end_offset, False)]
        elif title_type == RegestTitleType.ELLIPTICAL_RANGE:
            start, end, offset = re.search(
                '(?P<start>\d{4}-\d{2}|\d{4}-\d{2}-\d{2})' \
                    ' bis (?P<end>\d{2})' \
                    ' ?(\([a-z]\))? ?' \
                    '\(?(?P<offset>' \
                    'ca\.|nach|kurz nach|post|um|vor|zwischen)?\)?',
                self.title).group('start', 'end', 'offset')
            start = self.__extract_date(start)
            if re.match('^\d{4}-\d{2} bis \d{2}', self.title):
                end = date(start.year, int(end), DAY_DEFAULT)
            elif re.match('^\d{4}-\d{2}-\d{2} bis \d{2}', self.title):
                end = date(start.year, start.month, int(end))
            start_offset, end_offset = self.__determine_offsets(
                start_offset=offset, end_offset=offset, title_type=title_type)
            return [(start, end, start_offset, end_offset, False)]
        elif title_type == RegestTitleType.SIMPLE_ALTERNATIVES:
            offset = self.__extract_offset()
            title = self.__remove_non_standard_formatting(title_type)
            main_date, alt_dates = re.search(
                '(?P<main_date>\d{4}|\d{4}-\d{2}|\d{4}-\d{2}-\d{2})' \
                    '(?P<alt_dates>' \
                    '( ?/ ?\d{4}-\d{2}-\d{2})+|' \
                    '( ?/ ?\d{4}-\d{2})+|' \
                    '( ?/ ?\d{4})+)',
                title).group('main_date', 'alt_dates')
            start = self.__extract_date(main_date)
            dates = [(start, start, offset, offset, False)]
            for alt_date in re.findall(
                ' ?/ ?(\d{4}-\d{2}-\d{2}|\d{4}-\d{2}|\d{4})', alt_dates):
                start = self.__extract_date(alt_date)
                dates.append((start, start, offset, offset, True))
            return dates
        elif title_type == RegestTitleType.ELLIPTICAL_ALTERNATIVES:
            offset = self.__extract_offset()
            title = self.__remove_non_standard_formatting(title_type)
            main_date, alt_dates = re.search(
                '(?P<main_date>\d{4}-\d{2}-\d{2}|\d{4}-\d{2}|\d{4})' \
                    '(?P<alt_dates>' \
                    '( ?/ ?\d{2}-\d{2})+|' \
                    '( ?/ ?\d{2})+)',
                title).group('main_date', 'alt_dates')
            start = self.__extract_date(main_date)
            dates = [(start, start, offset, offset, False)]
            # month different, no day:
            if re.match('\d{4}-\d{2} ?/ ?\d{2}([^\d-].*|)$', title):
                for alt_date in re.findall(' ?/ ?(\d{2})', alt_dates):
                    start = date(start.year, int(alt_date), DAY_DEFAULT)
                    dates.append((start, start, offset, offset, True))
            # day different:
            elif re.match('\d{4}-\d{2}-\d{2} ?/ ?\d{2}([^\d-].*|)$', title):
                for alt_date in re.findall(' ?/ ?(\d{2})', alt_dates):
                    start = date(start.year, start.month, int(alt_date))
                    dates.append((start, start, offset, offset, True))
            # month *and* day different:
            elif re.match('\d{4}-\d{2}-\d{2} ?/ ?\d{2}-\d{2}', title):
                for alt_date in re.findall(' ?/ ?(\d{2}-\d{2})', alt_dates):
                    alt_month, alt_day = re.search(
                        '(?P<alt_month>\d{2})-(?P<alt_day>\d{2})',
                        alt_date).group('alt_month', 'alt_day')
                    start = date(start.year, int(alt_month), int(alt_day))
                    dates.append((start, start, offset, offset, True))
            return dates
        elif title_type == RegestTitleType.SIMPLE_ADDITIONS:
            offset = self.__extract_offset()
            title = self.__remove_non_standard_formatting(title_type)
            main_date, alt_dates = re.search(
                '(?P<main_date>\d{4}|\d{4}-\d{2}|\d{4}-\d{2}-\d{2})' \
                    '(?P<alt_dates>' \
                    '( ?und ?\d{4}-\d{2}-\d{2})+|' \
                    '( ?und ?\d{4}-\d{2})+|' \
                    '( ?und ?\d{4})+)',
                title).group('main_date', 'alt_dates')
            start = self.__extract_date(main_date)
            dates = [(start, start, offset, offset, False)]
            for alt_date in re.findall(
                ' ?und ?(\d{4}-\d{2}-\d{2}|\d{4}-\d{2}|\d{4})', alt_dates):
                start = self.__extract_date(alt_date)
                dates.append((start, start, offset, offset, False))
            return dates
        elif title_type == RegestTitleType.ELLIPTICAL_ADDITIONS:
            offset = self.__extract_offset()
            title = self.__remove_non_standard_formatting(title_type)
            main_date, alt_dates = re.search(
                '(?P<main_date>\d{4}-\d{2}-\d{2}|\d{4}-\d{2}|\d{4})' \
                    '(?P<alt_dates>' \
                    '( ?und ?\d{2}-\d{2})+|' \
                    '( ?und ?\d{2})+)',
                title).group('main_date', 'alt_dates')
            start = self.__extract_date(main_date)
            dates = [(start, start, offset, offset, False)]
            # month different, no day:
            if re.match('\d{4}-\d{2} ?und ?\d{2}([^\d-].*|)$', title):
                for alt_date in re.findall(' ?und ?(\d{2})', alt_dates):
                    start = date(start.year, int(alt_date), DAY_DEFAULT)
                    dates.append((start, start, offset, offset, False))
            # day different:
            elif re.match('\d{4}-\d{2}-\d{2} ?und ?\d{2}([^\d-].*|)$', title):
                for alt_date in re.findall(' ?und ?(\d{2})', alt_dates):
                    start = date(start.year, start.month, int(alt_date))
                    dates.append((start, start, offset, offset, False))
            # month *and* day different:
            elif re.match('\d{4}-\d{2}-\d{2} ?und ?\d{2}-\d{2}', title):
                for alt_date in re.findall(' ?und ?(\d{2}-\d{2})', alt_dates):
                    alt_month, alt_day = re.search(
                        '(?P<alt_month>\d{2})-(?P<alt_day>\d{2})',
                        alt_date).group('alt_month', 'alt_day')
                    start = date(start.year, int(alt_month), int(alt_day))
                    dates.append((start, start, offset, offset, False))
            return dates

    def __extract_offset(self):
        match = re.search(
            '(?P<offset>ca\.|nach|kurz nach|post|um|vor)', self.title)
        return match.group('offset') if match else ''

    def __remove_non_standard_formatting(self, title_type):
        # - Replace 'bzw.' and '(bzw.' and '[bzw.' and 'oder' and
        #   '(oder' and '[oder' with '/' (dot optional after 'bzw')
        # - Remove duplicates and offsets
        # - Remove ')' and ']'
        title = re.sub('[\(\[]?(bzw\.?|oder)', '/', self.title)
        title = re.sub('\(\D+\)', '', title)
        title = re.sub('[\)\]]', '', title)
        if title_type == RegestTitleType.SIMPLE_ALTERNATIVES:
            # - Replace '(' and '[' with '/ '
            title = re.sub('[\(\[]', '/ ', title)
        elif title_type == RegestTitleType.ELLIPTICAL_ALTERNATIVES:
            # - Replace ' (' and ' [' with '-'
            title = re.sub(' [\(\[]', '-', title)
        elif title_type == RegestTitleType.SIMPLE_ADDITIONS or \
                title_type == RegestTitleType.ELLIPTICAL_ADDITIONS:
            # - Remove '(' and '['
            title = re.sub('[\(\[]', '', title)
        return title

    def __delete_existing_dates(self):
        # Delete existing dates for current regest to make sure we're
        # not keeping old ones when updating regests in the admin
        # interface
        for regest_date in self.regestdate_set.all():
            regest_date.delete()

    def __extract_date(self, string):
        year, month, day = re.search(
            '(?P<year>\d{4})-?(?P<month>\d{2})?-?(?P<day>\d{2})?',
            string).group('year', 'month', 'day')
        if year and month and day:
            return date(int(year), int(month), int(day))
        elif year and month and not day:
            return date(int(year), int(month), DAY_DEFAULT)
        elif year and not month and not day:
            return date(int(year), MONTH_DEFAULT, DAY_DEFAULT)

    def __determine_offsets(self, start_offset, end_offset, title_type):
        '''
        To determine the final values for start_offset and end_offset
        the following combinations of values need to be considered:

        - start_offset and end_offset
          If a given regest title contains both a start_offset and an
          end_offset, we don't have to do anything; both values
          returned by the regex search will be different from the
          empty string ('') or None so we can simply use these values
          as is.

        - start_offset and not end_offset
          If we do not get a match for end_offset in a regest title,
          the regex search returns None for this variable. In this
          case, we minimally need to set end_offset to the empty
          string (''). If we are dealing with a non-range, we want to
          set end_offset to start_offset.

        - not start_offset and end_offset
          This is the most complex case. If we do not get a match for
          start_offset and end_offset is one of {nach, kurz nach,
          post, um, vor}, we want to set start_offset to the same
          value as end_offset. If end_offset == 'zwischen', this means
          that the events covered by the regest took place over a
          period of time that *excludes* the start and end dates given
          in the title. In this case, start_offset needs to be set to
          'nach', and end_offset needs to be set to 'vor'.

        - not start_offset and not end_offset
          If a regest title contains no offsets at all, the regex
          search returns None for the start_offset and end_offset
          variables. In this case, we need to manually set the values
          of both of these variables to the empty string ('').
        '''
        start_offset = start_offset or ''
        end_offset = end_offset or ''
        if start_offset and not end_offset and \
                title_type == RegestTitleType.REGULAR:
            end_offset = start_offset
        elif not start_offset and end_offset:
            if end_offset == 'zwischen':
                start_offset = 'nach'
                end_offset = 'vor'
            else:
                start_offset = end_offset
        return start_offset, end_offset


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
