"""
This module contains utility classes and functions for the Sbr
Regesten webapp.
"""

import re

from datetime import date
from regesten_webapp import DAY_DEFAULT, MONTH_DEFAULT
from regesten_webapp import EllipsisType, RegestTitleType


class RegestTitleAnalyzer(object):
    """
    The RegestTitleAnalyzer class groups functionalities for analyzing
    regest titles in various ways.
    """
    @staticmethod
    def contains_simple_additions(string):
        """
        Check if string contains 'simple additions'.

        Simple additions are of the form

            yyyy(-mm-dd) und yyyy(-mm-dd)

        Examples:
        - 1524 und 1525
        - 1419-05 und 1419-06
        - 1421-10-05 und 1422-10-04
        """
        return re.match(
            '\d{4}(-\d{2}){0,2}' \
                ' [\(\[]?und ' \
                '\d{4}(-\d{2}){0,2}', string)

    @staticmethod
    def contains_elliptical_additions(string):
        """
        Check if string contains 'elliptical additions'.

        Elliptical additions omit year or year and month information
        and are of the form

            yyyy-mm(-dd) und (mm-)dd

        Examples:
        - 1270-04 und 05
        - 1440-11-12 und 17
        - 1270-04-27 und 05-28
        """
        return re.match(
            '\d{4}(-\d{2}){0,2}' \
                ' [\(\[]?und ' \
                '\d{2}(-\d{2})?', string)

    @staticmethod
    def contains_simple_alternatives(string):
        """
        Check if string contains 'simple alternatives'.

        Examples for simple alternatives include:
        - 1524/1525
        - 1524 / 1525
        - 1419-05/1419-06
        - 1419-05 / 1419-06
        - 1421-10-05/1422-10-04
        - 1421-10-05 / 1422-10-04
        - 1502 (1503)
        - 1502-11 (1503-02)
        - 1502-11-22 (1503-02-07)
        - 1520 [bzw. 1519]
        - 1520-02 [bzw. 1519-03]
        - 1520-02-18 [bzw. 1519-03-06]
        - 1520 bzw. 1519
        - 1520-02 bzw. 1519-03
        - 1520-02-18 bzw. 1519-03-06
        """
        return re.match(
            '\d{4}(-\d{2}){0,2}' \
                '( ?/ ?| [\(\[]| [\(\[]?bzw\.? | [\(\[]?oder )' \
                '\d{4}(-\d{2}){0,2}', string)

    @staticmethod
    def contains_elliptical_alternatives(string):
        """
        Check if string contains 'elliptical alternatives'.

        Examples for elliptical alternatives include:
        - 1270-04/05
        - 1270-04 / 05
        - 1440-11-12/17
        - 1440-11-12 / 17
        - 1270-04-27/05-28
        - 1270-04-27 / 05-28
        - 1466 [04/05]
        - 1466 [04 / 05]
        - 1466-04 [28/29]
        - 1466-04 [28 / 29]
        - 1466 [04-28/05-01]
        - 1466 [04-28 / 05-01]
        - 1506-05 bzw. 11
        - 1506-05-12 bzw. 10
        - 1506-05-12 bzw. 11-10
        - 1343-04 oder 05
        - 1343-04-12 oder 19
        - 1343-04-12 oder 05-19
        """
        return re.match(
            '\d{4}(-\d{2}){0,2}' \
                '( ?/ ?| [\(\[]| [\(\[]?bzw\.? | [\(\[]?oder )' \
                '\d{2}(-\d{2})?[\)\]]?([^\.].+|)$', string)

    @staticmethod
    def is_simple_range(string):
        """
        Check whether or not string represents a 'simple' date range.

        Simple date ranges are non-elliptical, i.e. they include year,
        month, and day information for both start and end date.
        """
        return re.match('(\d{4}-\d{2}-\d{2}|\d{4}-\d{2}|\d{4})' \
                            '( \(.{2,}\))?' \
                            ' ?- ?' \
                            '(\d{4}-\d{2}-\d{2}|\d{4}-\d{2}|\d{4})', string)

    @staticmethod
    def is_elliptical_range(string):
        """
        Check whether or not string represents an 'elliptical' date
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
        """
        return re.match('^\d{4}-\d{2}(-\d{2})?' \
                            '( \(\D{2,}\))? bis \d{2}(-\d{2})?', string)

    @staticmethod
    def determine_ellipsis_type(elliptical_title, separator):
        """
        Return type of ellipsis for a given elliptical title.

        Elliptical regest titles differ in the amount and type of
        information they omit. This needs to be taken into
        consideration when generating RegestDate objects based on the
        title of a given regest. There are three different
        types of ellipses in total, each of which is represented by a
        dedicated constant (defined in __init__.py):

        1270-04 / 05       month different, no day
        1440-11-12 / 17    day different
        1270-04-27 / 05-28 month *and* day different

        | Title                        | Type of Ellipsis          |
        |------------------------------+---------------------------|
        | 1270-04 <separator> 05       | month different, no day   |
        | 1440-11-12 <separator> 17    | day different             |
        | 1270-04-27 <separator> 05-28 | month *and* day different |
        |------------------------------+---------------------------|

        N.B.: This method should be called *after* removing any
        non-standard formatting from the elliptical title in question.
        """
        if re.match(
            '\d{4}-\d{2} ?' + separator + ' ?\d{2}([^\d-].*|)$',
            elliptical_title):
            return EllipsisType.MONTH_DIFFERENT_NO_DAY
        elif re.match(
            '\d{4}-\d{2}-\d{2} ?' + separator + ' ?\d{2}([^\d-].*|)$',
            elliptical_title):
            return EllipsisType.DAY_DIFFERENT
        elif re.match(
            '\d{4}-\d{2}-\d{2} ?' + separator + ' ?\d{2}-\d{2}',
            elliptical_title):
            return EllipsisType.MONTH_AND_DAY_DIFFERENT


class RegestDateExtractor(object):
    """
    The RegestDateExtractor class groups functionalities for
    extracting dates from regest titles.
    """
    @classmethod
    def extract_dates(cls, title, title_type):
        """
        Based on its type, extract all dates from a given regest
        title.

        This method serves as an entry point for extracting dates from
        regest titles. It controls the extraction process from start
        to finish and operates as follows:

        (1) Extract offset(s)
        (2) Remove non-standard formatting
            This is done to ease further processing and includes
            offset(s).
        (3) Extract start date
        (4) Extract end date
        (5) Initialize dates list with main date
        (6) Extract any additional dates
        """
        if title_type == RegestTitleType.SIMPLE_RANGE or \
                title_type == RegestTitleType.ELLIPTICAL_RANGE:
            start_offset, end_offset = cls.extract_offsets(title, title_type)
            start_offset, end_offset = cls.determine_final_offsets(
                start_offset, end_offset, title_type)
        else:
            offset = cls.extract_offsets(title, title_type)
            start_offset, end_offset = offset, offset
        title = cls.remove_non_standard_formatting(title, title_type)
        start = cls.extract_start(title, title_type)
        end = cls.extract_end(title, title_type, start)
        dates = [(start, end, start_offset, end_offset, False)]
        if title_type == RegestTitleType.SIMPLE_ALTERNATIVES or \
                title_type == RegestTitleType.SIMPLE_ADDITIONS:
            dates = cls.extract_simple_additions(
                title, title_type, offset, start, dates)
        elif title_type == RegestTitleType.ELLIPTICAL_ALTERNATIVES or \
                title_type == RegestTitleType.ELLIPTICAL_ADDITIONS:
            dates = cls.extract_elliptical_additions(
                title, title_type, offset, start, dates)
        return dates

    @classmethod
    def extract_offsets(cls, title, title_type):
        """
        Based on its type, extract offset(s) from a given regest
        title.
        """
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
        """
        Determine the final values for start_offset and end_offset of
        a given regest title, taking into account the type of the
        title.

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
        """
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
        """
        Based on its type, remove all non-standard formatting from a
        given regest title (including offsets).

        Non-standard formatting includes locations, duplicates, and
        miscellaneous information, as well as offsets and non-standard
        separators for additional dates (the standard separator being
        '/' for alternatives and 'und' for additions). The order in
        which the formatting is removed matters; the method operates
        as follows:

        Irrespective of the type of the regest title, the following
        steps are performed first:

        (1) Replace 'bzw.', '(bzw.', '[bzw.', 'oder', '(oder', '[oder'
            with '/'
        (2) Remove duplicates, offsets, and misc
        (3) Remove ')' and ']'
        (4) Remove locations

        Then, depending on the type of the regest title, do one of the
        following:
        - Replace '(' and '[' with '/ ' (simple alternatives)
        - Replace ' (' and ' [' with '-' (elliptical alternatives)
        - Remove '(' and '[' (simple and elliptical additions)
        """
        title = re.sub('[\(\[]?(bzw\.?|oder)', '/', title)
        title = re.sub(' \((\D+|\d{2}\..+)\)', '', title)
        title = re.sub('[\)\]]', '', title)
        title = re.sub(' \D+$', '', title)
        if title_type == RegestTitleType.SIMPLE_ALTERNATIVES:
            title = re.sub('[\(\[]', '/ ', title)
        elif title_type == RegestTitleType.ELLIPTICAL_ALTERNATIVES:
            title = re.sub(' [\(\[]', '-', title)
        elif title_type == RegestTitleType.SIMPLE_ADDITIONS or \
                title_type == RegestTitleType.ELLIPTICAL_ADDITIONS:
            title = re.sub('[\(\[]', '', title)
        return title

    @classmethod
    def extract_start(cls, title, title_type):
        """
        Based on its type, extract start date from a given regest title.
        """
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
        """
        Based on its type, extract end date from a given regest title.
        """
        if title_type == RegestTitleType.SIMPLE_RANGE:
            end = re.search(
                ' ?- ?(?P<end>\d{4}-\d{2}-\d{2}|\d{4}-\d{2}|\d{4})',
                title).group('end')
            end = cls.extract_date(end)
        elif title_type == RegestTitleType.ELLIPTICAL_RANGE:
            end = re.search(
                ' bis (?P<end>\d{2}-\d{2}|\d{2})', title).group('end')
            ellipsis_type = RegestTitleAnalyzer.determine_ellipsis_type(
                title, separator='bis')
            if ellipsis_type == EllipsisType.MONTH_DIFFERENT_NO_DAY:
                end = date(start.year, int(end), DAY_DEFAULT)
            elif ellipsis_type == EllipsisType.DAY_DIFFERENT:
                end = date(start.year, start.month, int(end))
            elif ellipsis_type == EllipsisType.MONTH_AND_DAY_DIFFERENT:
                end_month, end_day = re.split('-', end)
                end = date(start.year, int(end_month), int(end_day))
        else:
            end = start
        return end

    @classmethod
    def extract_simple_additions(
        cls, title, title_type, offset, start, dates):
        """
        Extract any additional dates (alternatives or additions) from
        a given regest title which is non-elliptical.
        """
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
        cls, title, title_type, offset, start, dates):
        """
        Extract any additional dates (alternatives or additions) from
        a given regest title which is elliptical.
        """
        alt_date = title_type == RegestTitleType.ELLIPTICAL_ALTERNATIVES
        separator = '/' if alt_date else 'und'
        add_dates = re.search(
            '(?P<add_dates>' \
                '( ?' + separator + ' ?\d{2}-\d{2})+|' \
                '( ?' + separator + ' ?\d{2})+)', title).group('add_dates')
        ellipsis_type = RegestTitleAnalyzer.determine_ellipsis_type(
            title, separator)
        if ellipsis_type == EllipsisType.MONTH_DIFFERENT_NO_DAY:
            for add_date in re.findall(
                ' ?' + separator + ' ?(\d{2})', add_dates):
                start = date(start.year, int(add_date), DAY_DEFAULT)
                dates.append((start, start, offset, offset, alt_date))
        elif ellipsis_type == EllipsisType.DAY_DIFFERENT:
            for add_date in re.findall(
                ' ?' + separator + ' ?(\d{2})', add_dates):
                start = date(start.year, start.month, int(add_date))
                dates.append((start, start, offset, offset, alt_date))
        elif ellipsis_type == EllipsisType.MONTH_AND_DAY_DIFFERENT:
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
        """
        Extract year, month, and day from string and use the values to
        return a datetime.date object.

        The string parameter is of the form

            yyyy(-mm-dd)

        If string includes year, month, and day information, the
        extracted values can be used as they are to create the
        datetime.date object. If string is missing day information,
        day defaults to the value of the DAY_DEFAULT constant; if it
        is missing month *and* day information, month and day default
        to MONTH_DEFAULT and DAY_DEFAULT, respectively. The
        MONTH_DEFAULT and DAY_DEFAULT constants are defined in
        __init__.py.
        """
        year, month, day = re.search(
            '(?P<year>\d{4})-?(?P<month>\d{2})?-?(?P<day>\d{2})?',
            string).group('year', 'month', 'day')
        if year and month and day:
            return date(int(year), int(month), int(day))
        elif year and month and not day:
            return date(int(year), int(month), DAY_DEFAULT)
        elif year and not month and not day:
            return date(int(year), MONTH_DEFAULT, DAY_DEFAULT)
