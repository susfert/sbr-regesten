"""
This module contains utility classes and functions for the Sbr
Regesten webapp.
"""

import re

from datetime import date
from regesten_webapp import DAY_DEFAULT, MONTH_DEFAULT, RegestTitleType

class RegestTitleAnalyzer(object):
    @staticmethod
    def contains_simple_additions(string):
        return re.match(
            '\d{4}(-\d{2}){0,2}' \
                ' [\(\[]?und ' \
                '\d{4}(-\d{2}){0,2}', string)

    @staticmethod
    def contains_elliptical_additions(string):
        return re.match(
            '\d{4}(-\d{2}){0,2}' \
                ' [\(\[]?und ' \
                '\d{2}(-\d{2})?', string)

    @staticmethod
    def contains_simple_alternatives(string):
        return re.match(
            '\d{4}(-\d{2}){0,2}' \
                '( ?/ ?| [\(\[]| [\(\[]?bzw\.? | [\(\[]?oder )' \
                '\d{4}(-\d{2}){0,2}', string)

    @staticmethod
    def contains_elliptical_alternatives(string):
        return re.match(
            '\d{4}(-\d{2}){0,2}' \
                '( ?/ ?| [\(\[]| [\(\[]?bzw\.? | [\(\[]?oder )' \
                '\d{2}(-\d{2})?', string)

    @staticmethod
    def is_simple_range(string):
        '''
        Checks whether or not string represents a "simple" date range.

        Simple date ranges are non-elliptical, i.e. they include year,
        month, and day information for both start and end date.
        '''
        return re.match('(\d{4}-\d{2}-\d{2}|\d{4}-\d{2}|\d{4})' \
                            '( \(.{2,}\))?' \
                            ' ?- ?' \
                            '(\d{4}-\d{2}-\d{2}|\d{4}-\d{2}|\d{4})', string)

    @staticmethod
    def is_elliptical_range(string):
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
        return re.match('^\d{4}-\d{2}(-\d{2})?' \
                            '( \(\D{2,}\))? bis \d{2}(-\d{2})?', string)


class RegestTitleParser(object):
    @classmethod
    def extract_dates(cls, title, title_type):
        # Offset(s)
        if title_type == RegestTitleType.SIMPLE_RANGE or \
                title_type == RegestTitleType.ELLIPTICAL_RANGE:
            start_offset, end_offset = cls.extract_offsets(title, title_type)
            start_offset, end_offset = cls.determine_final_offsets(
                start_offset, end_offset, title_type)
        else:
            offset = cls.extract_offsets(title, title_type)
            start_offset, end_offset = offset, offset
        title = cls.remove_non_standard_formatting(title, title_type)
        # Start date
        start = cls.extract_start(title, title_type)
        # End date
        end = cls.extract_end(title, title_type, start)
        dates = [(start, end, start_offset, end_offset, False)]
        # Extract alternatives/additions
        if title_type == RegestTitleType.SIMPLE_ALTERNATIVES or \
                title_type == RegestTitleType.SIMPLE_ADDITIONS:
            dates = cls.extract_simple_additions(
                title, title_type, start, offset, dates)
        elif title_type == RegestTitleType.ELLIPTICAL_ALTERNATIVES or \
                title_type == RegestTitleType.ELLIPTICAL_ADDITIONS:
            dates = cls.extract_elliptical_additions(
                title, title_type, start, offset, dates)
        return dates

    @classmethod
    def extract_offsets(cls, title, title_type):
        if title_type == RegestTitleType.SIMPLE_RANGE:
            match = re.search(
                '\(?(?P<start_offset>ca\.|nach|kurz nach|post|um|vor)?\)?' \
                    ' ?- ?' \
                    '(\d{4}-\d{2}-\d{2}|\d{4}-\d{2}|\d{4})' \
                    ' ?(\([a-z]\)|[\w\. ]+)? ?' \
                    '\(?(?P<end_offset>' \
                    'ca\.|nach|kurz nach|post|um|vor|zwischen)?\)?',
                title)
            return match.group('start_offset') or '', \
                match.group('end_offset') or ''
        elif title_type == RegestTitleType.ELLIPTICAL_RANGE:
            match = re.search(
                '\(?(?P<start_offset>ca\.|nach|kurz nach|post|um|vor)?\)?' \
                    ' bis ' \
                    '(\d{2}-\d{2}|\d{2})' \
                    ' ?(\([a-z]\)|[\w\. ]+)? ?' \
                    '\(?(?P<end_offset>' \
                    'ca\.|nach|kurz nach|post|um|vor|zwischen)?\)?',
                title)
            return match.group('start_offset') or '', \
                match.group('end_offset') or ''
        else:
            match = re.search(
                '(?P<offset>ca\.|nach|kurz nach|post|um|vor)', title)
            return match.group('offset') if match else ''

    @classmethod
    def determine_final_offsets(cls, start_offset, end_offset, title_type):
        '''
        To determine the final values for start_offset and end_offset
        the following combinations of values need to be considered:

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
        '''
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

    @classmethod
    def remove_non_standard_formatting(cls, title, title_type):
        # - Replace 'bzw.' and '(bzw.' and '[bzw.' and 'oder' and
        #   '(oder' and '[oder' with '/' (dot optional after 'bzw')
        # - Remove duplicates and offsets
        # - Remove ')' and ']'
        # - Remove locations
        title = re.sub('[\(\[]?(bzw\.?|oder)', '/', title)
        title = re.sub(' \(\D+\)', '', title)
        title = re.sub('[\)\]]', '', title)
        title = re.sub(' \D+$', '', title)
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

    @classmethod
    def extract_start(cls, title, title_type):
        if title_type == RegestTitleType.ELLIPTICAL_RANGE:
            start = re.search(
                '(?P<start>\d{4}-\d{2}-\d{2}|\d{4}-\d{2})', title).group(
                'start')
        elif title_type == RegestTitleType.SIMPLE_RANGE:
            start = re.search(
                '(?P<start>\d{4}-\d{2}-\d{2}|\d{4}-\d{2}|\d{4}) ?- ?',
                title).group('start')
        else:
            start = re.search(
                '(?P<start>\d{4}-\d{2}-\d{2}|\d{4}-\d{2}|\d{4})',
                title).group('start')
        return cls.extract_date(start)

    @classmethod
    def extract_end(cls, title, title_type, start):
        if title_type == RegestTitleType.SIMPLE_RANGE:
            end = re.search(
                ' ?- ?(?P<end>\d{4}-\d{2}-\d{2}|\d{4}-\d{2}|\d{4})',
                title).group('end')
            end = cls.extract_date(end)
        elif title_type == RegestTitleType.ELLIPTICAL_RANGE:
            end = re.search(
                ' bis (?P<end>\d{2}-\d{2}|\d{2})', title).group('end')
            # month *and* day different
            if re.match(
                '^\d{4}-\d{2}-\d{2} bis \d{2}-\d{2}', title):
                end_month, end_day = re.split('-', end)
                end = date(start.year, int(end_month), int(end_day))
            # day different
            elif re.match(
                '^\d{4}-\d{2}-\d{2} bis \d{2}', title):
                end = date(start.year, start.month, int(end))
            # month different, no day
            elif re.match('^\d{4}-\d{2} bis \d{2}', title):
                end = date(start.year, int(end), DAY_DEFAULT)
        else:
            end = start
        return end

    @classmethod
    def extract_simple_additions(
        cls, title, title_type, start, offset, dates):
        alt_date = title_type == RegestTitleType.SIMPLE_ALTERNATIVES
        separator = '/' if alt_date else 'und'
        add_dates = re.search(
            '(?P<add_dates>' \
                '( ?' + separator + ' ?\d{4}-\d{2}-\d{2})+|' \
                '( ?' + separator + ' ?\d{4}-\d{2})+|' \
                '( ?' + separator + ' ?\d{4})+)', title).group('add_dates')
        for add_date in re.findall(
            ' ?' + separator + ' ?(\d{4}-\d{2}-\d{2}|\d{4}-\d{2}|\d{4})',
            add_dates):
            start = cls.extract_date(add_date)
            dates.append((start, start, offset, offset, alt_date))
        return dates

    @classmethod
    def extract_elliptical_additions(
        cls, title, title_type, start, offset, dates):
        alt_date = title_type == RegestTitleType.ELLIPTICAL_ALTERNATIVES
        separator = '/' if alt_date else 'und'
        add_dates = re.search(
            '(?P<add_dates>' \
                '( ?' + separator + ' ?\d{2}-\d{2})+|' \
                '( ?' + separator + ' ?\d{2})+)', title).group('add_dates')
        # month different, no day:
        if re.match(
            '\d{4}-\d{2} ?' + separator + ' ?\d{2}([^\d-].*|)$', title):
            for add_date in re.findall(
                ' ?' + separator + ' ?(\d{2})', add_dates):
                start = date(start.year, int(add_date), DAY_DEFAULT)
                dates.append((start, start, offset, offset, alt_date))
        # day different:
        elif re.match(
            '\d{4}-\d{2}-\d{2} ?' + separator + ' ?\d{2}([^\d-].*|)$',
            title):
            for add_date in re.findall(
                ' ?' + separator + ' ?(\d{2})', add_dates):
                start = date(start.year, start.month, int(add_date))
                dates.append((start, start, offset, offset, alt_date))
        # month *and* day different:
        elif re.match(
            '\d{4}-\d{2}-\d{2} ?' + separator + ' ?\d{2}-\d{2}', title):
            for add_date in re.findall(
                ' ?' + separator + ' ?(\d{2}-\d{2})', add_dates):
                add_month, add_day = re.search(
                    '(?P<add_month>\d{2})-(?P<add_day>\d{2})',
                    add_date).group('add_month', 'add_day')
                start = date(start.year, int(add_month), int(add_day))
                dates.append((start, start, offset, offset, alt_date))
        return dates

    @classmethod
    def extract_date(cls, string):
        year, month, day = re.search(
            '(?P<year>\d{4})-?(?P<month>\d{2})?-?(?P<day>\d{2})?',
            string).group('year', 'month', 'day')
        if year and month and day:
            return date(int(year), int(month), int(day))
        elif year and month and not day:
            return date(int(year), int(month), DAY_DEFAULT)
        elif year and not month and not day:
            return date(int(year), MONTH_DEFAULT, DAY_DEFAULT)
