"""
This module provides tests for non-trivial methods of the model layer.

They can be run via

python manage.py test regesten_webapp
"""

from collections import namedtuple
from datetime import date
from django.test import TestCase
from regesten_webapp.models import Regest


class RegestTest(TestCase):
    class RegestDate(namedtuple('RegestDate',
        ['start', 'end', 'start_offset', 'end_offset', 'alt_date'])):
        __slots__ = ()
        def __str__(self):
            return 'Start: {0}\n' \
                'End: {1}\n' \
                'Start offset: {2}\n' \
                'End offset: {3}\n' \
                'Alt date: {4}'.format(
                self.start, self.end, self.start_offset or '<none>',
                self.end_offset or '<none>', self.alt_date)

    def __create_and_check_dates(self, regest_title, *dates):
        regest = Regest.objects.create(title=regest_title)
        for regest_date in dates:
            try:
                regest.regestdate_set.get(
                    start=regest_date.start,
                    end=regest_date.end,
                    start_offset=regest_date.start_offset,
                    end_offset=regest_date.end_offset,
                    alt_date=regest_date.alt_date)
            except Exception as e:
                self.fail(
                    msg='\n\n=== INFO ===' \
                        '\nRegest title: {0}' \
                        '\n\nMissing date:\n{1}' \
                        '\n\nException: {2}' \
                        '\n============'.format(
                        regest.title, regest_date, e.message))

    def test_regular_dates(self):
        '''
        Tests whether or not *regular dates* are extracted correctly
        from the title of a given regest.

        Regular dates include:
        - 1009 (year only)
        - 1009-10 (year and month)
        - 1009-10-20 (year, month, and day)
        '''
        self.__create_and_check_dates('1009', self.RegestDate(
                date(1009, 01, 01), date(1009, 01, 01), '', '', False))
        self.__create_and_check_dates('1009-10', self.RegestDate(
                date(1009, 10, 01), date(1009, 10, 01), '', '', False))
        self.__create_and_check_dates('1009-10-20', self.RegestDate(
                date(1009, 10, 20), date(1009, 10, 20), '', '', False))

    def test_regular_dates_with_location(self):
        '''
        Tests whether or not regular dates are extracted correctly
        from titles that include a location.

        Examples:
        - 1009 Diedenhofen
        - 1009-10 Frankfurt am Main
        - 1009-10-20 St. Arnual
        '''
        self.__create_and_check_dates('1009 Diedenhofen', self.RegestDate(
                date(1009, 01, 01), date(1009, 01, 01), '', '', False))
        self.__create_and_check_dates(
            '1009-10 Frankfurt am Main', self.RegestDate(
                date(1009, 10, 01), date(1009, 10, 01), '', '', False))
        self.__create_and_check_dates(
            '1009-10-20 St. Arnual', self.RegestDate(
                date(1009, 10, 20), date(1009, 10, 20), '', '', False))

    def test_regular_dates_with_offset(self):
        '''
        Tests whether or not regular dates that include an offset are
        extracted correctly from regest titles.

        Positive examples:
        - 1009 (vor)
        - 1009-10 (nach)
        - 1009-10-20 (ca.)

        Negative examples:
        - 1009 (?)
        - 1009-10 (?)
        - 1009-10-20 (?)

        For a complete list of possible offsets see the OFFSET_TYPES
        constant in regesten_webapp.__init__.py.
        '''
        self.__create_and_check_dates('1009 (vor)', self.RegestDate(
                date(1009, 01, 01), date(1009, 01, 01), 'vor', 'vor', False))
        self.__create_and_check_dates('1009-10 (nach)', self.RegestDate(
                date(1009, 10, 01), date(1009, 10, 01),
                'nach', 'nach', False))
        self.__create_and_check_dates('1009-10-20 (ca.)', self.RegestDate(
                date(1009, 10, 20), date(1009, 10, 20), 'ca.', 'ca.', False))
        self.__create_and_check_dates('1009 (?)', self.RegestDate(
                date(1009, 01, 01), date(1009, 01, 01), '', '', False))
        self.__create_and_check_dates('1009-10 (?)', self.RegestDate(
                date(1009, 10, 01), date(1009, 10, 01), '', '', False))
        self.__create_and_check_dates('1009-10-20 (?)', self.RegestDate(
                date(1009, 10, 20), date(1009, 10, 20), '', '', False))

    def test_regular_dates_with_offset_and_location(self):
        '''
        Tests whether or not regular dates that include an offset are
        extracted correctly from regest titles which include a
        location.

        Examples:
        - 1009 (vor) Diedenhofen
        - 1009-10 (nach) Frankfurt am Main
        - 1009-10-20 (um) St. Arnual
        - 1009 Diedenhofen (kurz nach)
        - 1009-10 Frankfurt am Main (post)
        - 1009-10-20 St. Arnual (ca.)

        For a complete list of possible offsets see the OFFSET_TYPES
        constant in regesten_webapp.__init__.py.
        '''
        self.__create_and_check_dates(
            '1009 (vor) Diedenhofen', self.RegestDate(
                date(1009, 01, 01), date(1009, 01, 01), 'vor', 'vor', False))
        self.__create_and_check_dates(
            '1009-10 (nach) Frankfurt am Main', self.RegestDate(
                date(1009, 10, 01), date(1009, 10, 01),
                'nach', 'nach', False))
        self.__create_and_check_dates(
            '1009-10-20 (um) St. Arnual', self.RegestDate(
                date(1009, 10, 20), date(1009, 10, 20), 'um', 'um', False))
        self.__create_and_check_dates(
            '1009 Diedenhofen (kurz nach)', self.RegestDate(
                date(1009, 01, 01), date(1009, 01, 01),
                'kurz nach', 'kurz nach', False))
        self.__create_and_check_dates(
            '1009-10 Frankfurt am Main (post)', self.RegestDate(
                date(1009, 10, 01), date(1009, 10, 01),
                'post', 'post', False))
        self.__create_and_check_dates(
            '1009-10-20 St. Arnual (ca.)', self.RegestDate(
                date(1009, 10, 20), date(1009, 10, 20), 'ca.', 'ca.', False))

    def test_regular_dates_with_duplicates(self):
        '''
        Tests whether or not regular dates are extracted correctly
        from regest titles which contain *duplicate markers*.

        A duplicate marker consists of a lowercase letter surrounded
        by parentheses: ([a-z])

        Examples:
        - 1273 (a)
        - 1270-07 (b)
        - 1377-03-05 (c)
        - 1424-06-03 (a) und (b)
        '''
        self.__create_and_check_dates('1273 (a)', self.RegestDate(
                date(1273, 01, 01), date(1273, 01, 01), '', '', False))
        self.__create_and_check_dates('1270-07 (b)', self.RegestDate(
                date(1270, 07, 01), date(1270, 07, 01), '', '', False))
        self.__create_and_check_dates('1377-03-05 (c)', self.RegestDate(
                date(1377, 03, 05), date(1377, 03, 05), '', '', False))
        self.__create_and_check_dates(
            '1424-06-03 (a) und (b)', self.RegestDate(
                date(1424, 06, 03), date(1424, 06, 03), '', '', False))

    def test_regular_dates_with_duplicates_and_location(self):
        '''
        Tests whether or not regular dates are extracted correctly
        from regest titles which contain duplicate markers and
        locations.

        A duplicate marker consists of a lowercase letter surrounded
        by parentheses: ([a-z])

        Examples:
        - 1442 (a) Diedenhofen
        - 1270-07 (b) Frankfurt am Main
        - 1354-04-01 (c) St. Arnual
        - 1424-06-03 (a) und (b) Tull
        '''
        self.__create_and_check_dates('1442 (a) Diedenhofen', self.RegestDate(
                date(1442, 01, 01), date(1442, 01, 01), '', '', False))
        self.__create_and_check_dates(
            '1270-07 (b) Frankfurt am Main', self.RegestDate(
                date(1270, 07, 01), date(1270, 07, 01), '', '', False))
        self.__create_and_check_dates('1354-04-01 (c)', self.RegestDate(
                date(1354, 04, 01), date(1354, 04, 01), '', '', False))
        self.__create_and_check_dates(
            '1424-06-03 (a) und (b)', self.RegestDate(
                date(1424, 06, 03), date(1424, 06, 03), '', '', False))

    def test_regular_dates_with_duplicates_and_offset(self):
        '''
        Tests whether or not regular dates and their offsets are
        extracted correctly from regest titles which contain duplicate
        markers.

        A duplicate marker consists of a lowercase letter surrounded
        by parentheses: ([a-z])

        Examples:
        - 1200 (vor) (a)
        - 1200 (a) (vor)
        - 1200-03 (kurz nach) (b)
        - 1200-03 (b) (kurz nach)
        - 1200-03-12 (ca.) (c)
        - 1200-03-12 (c) (ca.)
        '''
        self.__create_and_check_dates('1200 (vor) (a)', self.RegestDate(
                date(1200, 01, 01), date(1200, 01, 01), 'vor', 'vor', False))
        self.__create_and_check_dates('1200 (a) (vor)', self.RegestDate(
                date(1200, 01, 01), date(1200, 01, 01), 'vor', 'vor', False))
        self.__create_and_check_dates(
            '1200-03 (kurz nach) (b)', self.RegestDate(
                date(1200, 03, 01), date(1200, 03, 01),
                'kurz nach', 'kurz nach', False))
        self.__create_and_check_dates(
            '1200-03 (b) (kurz nach)', self.RegestDate(
                date(1200, 03, 01), date(1200, 03, 01),
                'kurz nach', 'kurz nach', False))
        self.__create_and_check_dates('1200-03-12 (ca.) (c)', self.RegestDate(
                date(1200, 03, 12), date(1200, 03, 12), 'ca.', 'ca.', False))
        self.__create_and_check_dates('1200-03-12 (c) (ca.)', self.RegestDate(
                date(1200, 03, 12), date(1200, 03, 12), 'ca.', 'ca.', False))

    def test_date_ranges(self):
        '''
        Tests whether or not *date ranges* are extracted correctly
        from the title of a given regest.

        Examples:
        - 1024-1030
        - 1024 - 1030
        - 1419-05 - 1419-06
        - 1419-05 bis 06
        - 1482-07-16 - 1499-01-03
        - 1419-05-10 bis 20
        '''
        self.__create_and_check_dates('1024-1030', self.RegestDate(
                date(1024, 01, 01), date(1030, 01, 01), '', '', False))
        self.__create_and_check_dates('1024 - 1030', self.RegestDate(
                date(1024, 01, 01), date(1030, 01, 01), '', '', False))
        self.__create_and_check_dates('1419-05 - 1419-06', self.RegestDate(
                date(1419, 05, 01), date(1419, 06, 01), '', '', False))
        self.__create_and_check_dates('1419-05 bis 06', self.RegestDate(
                date(1419, 05, 01), date(1419, 06, 01), '', '', False))
        self.__create_and_check_dates(
            '1484-07-16 - 1499-01-03', self.RegestDate(
                date(1484, 07, 16), date(1499, 01, 03), '', '', False))
        self.__create_and_check_dates(
            '1419-05-10 bis 20', self.RegestDate(
                date(1419, 05, 10), date(1419, 05, 20), '', '', False))

    def test_date_ranges_with_offset(self):
        '''
        Tests whether or not date ranges and their offsets are
        extracted correctly from the title of a given regest.

        Examples:
        - 0935-1000 (ca.)
        - 1431 - 1459 (zwischen)
        - 1419-05 - 1419-06 (um)
        - 1419-05 (nach) - 1419-06 (vor)
        - 1419-05 bis 06 (kurz nach)
        - 1482-07-16 - 1499-01-08 (ca.)
        - 1482-07-16 (nach) - 1499-01-08 (vor)
        - 1419-05-10 bis 20 (ca.)
        '''
        self.__create_and_check_dates('0935-1000 (ca.)', self.RegestDate(
                date(935, 01, 01), date(1000, 01, 01), 'ca.', 'ca.', False))
        self.__create_and_check_dates(
            '1431 - 1459 (zwischen)', self.RegestDate(
                date(1431, 01, 01), date(1459, 01, 01), 'nach', 'vor', False))
        self.__create_and_check_dates(
            '1419-05 - 1419-06 (um)', self.RegestDate(
                date(1419, 05, 01), date(1419, 06, 01), 'um', 'um', False))
        self.__create_and_check_dates(
            '1419-05 (nach) - 1419-06 (vor)', self.RegestDate(
                date(1419, 05, 01), date(1419, 06, 01), 'nach', 'vor', False))
        self.__create_and_check_dates(
            '1419-05 bis 06 (kurz nach)', self.RegestDate(
                date(1419, 05, 01), date(1419, 06, 01),
                'kurz nach', 'kurz nach', False))
        self.__create_and_check_dates(
            '1484-07-16 - 1499-01-03 (ca.)', self.RegestDate(
                date(1484, 07, 16), date(1499, 01, 03), 'ca.', 'ca.', False))
        self.__create_and_check_dates(
            '1484-07-16 (nach) - 1499-01-03 (vor)', self.RegestDate(
                date(1484, 07, 16), date(1499, 01, 03), 'nach', 'vor', False))
        self.__create_and_check_dates(
            '1419-05-10 bis 20 (ca.)', self.RegestDate(
                date(1419, 05, 10), date(1419, 05, 20), 'ca.', 'ca.', False))

    def test_date_ranges_with_offset_and_duplicates(self):
        '''
        Tests whether or not date ranges and their offsets are
        extracted correctly from regest titles containing duplicates.

        Examples:
        - 1460-1466 (a) ca.
        - 1460-1466 (ca.) (b)
        - 1460-1466 (c) (ca.)
        - 1419-05 - 1419-06 (a) um
        - 1419-05 - 1419-06 (um) (b)
        - 1419-05 - 1419-06 (c) (um)
        - 1419-05 bis 06 (a) kurz nach
        - 1419-05 bis 06 (kurz nach) (b)
        - 1419-05 bis 06 (c) (kurz nach)
        - 1482-07-16 - 1499-01-08 (a) ca.
        - 1482-07-16 - 1499-01-08 (ca.) (b)
        - 1482-07-16 - 1499-01-08 (c) (ca.)
        - 1419-05-10 bis 20 (a) ca.
        - 1419-05-10 bis 20 (ca.) (b)
        - 1419-05-10 bis 20 (c) (ca.)
        - 1482-07-16 (nach) - 1499-01-08 (vor) (a)
        '''
        self.__create_and_check_dates('1460-1466 (a) ca.', self.RegestDate(
                date(1460, 01, 01), date(1466, 01, 01), 'ca.', 'ca.', False))
        self.__create_and_check_dates('1460-1466 (ca.) (b)', self.RegestDate(
                date(1460, 01, 01), date(1466, 01, 01), 'ca.', 'ca.', False))
        self.__create_and_check_dates('1460-1466 (c) (ca.)', self.RegestDate(
                date(1460, 01, 01), date(1466, 01, 01), 'ca.', 'ca.', False))
        self.__create_and_check_dates(
            '1419-05 - 1419-06 (a) um', self.RegestDate(
                date(1419, 05, 01), date(1419, 06, 01), 'um', 'um', False))
        self.__create_and_check_dates(
            '1419-05 - 1419-06 (um) (b)', self.RegestDate(
                date(1419, 05, 01), date(1419, 06, 01), 'um', 'um', False))
        self.__create_and_check_dates(
            '1419-05 - 1419-06 (c) (um)', self.RegestDate(
                date(1419, 05, 01), date(1419, 06, 01), 'um', 'um', False))
        self.__create_and_check_dates(
            '1419-05 bis 06 (a) kurz nach', self.RegestDate(
                date(1419, 05, 01), date(1419, 06, 01),
                'kurz nach', 'kurz nach', False))
        self.__create_and_check_dates(
            '1419-05 bis 06 (kurz nach) (b)', self.RegestDate(
                date(1419, 05, 01), date(1419, 06, 01),
                'kurz nach', 'kurz nach', False))
        self.__create_and_check_dates(
            '1419-05 bis 06 (c) (kurz nach)', self.RegestDate(
                date(1419, 05, 01), date(1419, 06, 01),
                'kurz nach', 'kurz nach', False))
        self.__create_and_check_dates(
            '1484-07-16 - 1499-01-03 (a) ca.', self.RegestDate(
                date(1484, 07, 16), date(1499, 01, 03), 'ca.', 'ca.', False))
        self.__create_and_check_dates(
            '1484-07-16 - 1499-01-03 (ca.) (b)', self.RegestDate(
                date(1484, 07, 16), date(1499, 01, 03), 'ca.', 'ca.', False))
        self.__create_and_check_dates(
            '1484-07-16 - 1499-01-03 (c) (ca.)', self.RegestDate(
                date(1484, 07, 16), date(1499, 01, 03), 'ca.', 'ca.', False))
        self.__create_and_check_dates(
            '1419-05-10 bis 20 (a) ca.', self.RegestDate(
                date(1419, 05, 10), date(1419, 05, 20), 'ca.', 'ca.', False))
        self.__create_and_check_dates(
            '1419-05-10 bis 20 (ca.) (b)', self.RegestDate(
                date(1419, 05, 10), date(1419, 05, 20), 'ca.', 'ca.', False))
        self.__create_and_check_dates(
            '1419-05-10 bis 20 (c) (ca.)', self.RegestDate(
                date(1419, 05, 10), date(1419, 05, 20), 'ca.', 'ca.', False))
        self.__create_and_check_dates(
            '1484-07-16 (nach) - 1499-01-03 (vor) (a)', self.RegestDate(
                date(1484, 07, 16), date(1499, 01, 03), 'nach', 'vor', False))

    def test_simple_alternatives(self):
        '''
        Examples:
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
        - 1520 bzw. 1519 bzw. 1518
        - 1520-02 bzw. 1519-03 bzw. 1518-04
        - 1520-02-18 bzw. 1519-03-06 bzw. 1518-04-23
        '''
        self.__create_and_check_dates(
            '1524/1525', self.RegestDate(
                date(1524, 01, 01), date(1524, 01, 01), '', '', False),
            self.RegestDate(
                date(1525, 01, 01), date(1525, 01, 01), '', '', True))
        self.__create_and_check_dates(
            '1524 / 1525', self.RegestDate(
                date(1524, 01, 01), date(1524, 01, 01), '', '', False),
            self.RegestDate(
                date(1525, 01, 01), date(1525, 01, 01), '', '', True))
        self.__create_and_check_dates(
            '1419-05/1419-06', self.RegestDate(
                date(1419, 05, 01), date(1419, 05, 01), '', '', False),
            self.RegestDate(
                date(1419, 06, 01), date(1419, 06, 01), '', '', True))
        self.__create_and_check_dates(
            '1419-05 / 1419-06', self.RegestDate(
                date(1419, 05, 01), date(1419, 05, 01), '', '', False),
            self.RegestDate(
                date(1419, 06, 01), date(1419, 06, 01), '', '', True))
        self.__create_and_check_dates(
            '1421-10-05/1422-10-04', self.RegestDate(
                date(1421, 10, 05), date(1421, 10, 05), '', '', False),
            self.RegestDate(
                date(1422, 10, 04), date(1422, 10, 04), '', '', True))
        self.__create_and_check_dates(
            '1421-10-05 / 1422-10-04', self.RegestDate(
                date(1421, 10, 05), date(1421, 10, 05), '', '', False),
            self.RegestDate(
                date(1422, 10, 04), date(1422, 10, 04), '', '', True))
        self.__create_and_check_dates(
            '1502 (1503)', self.RegestDate(
                date(1502, 01, 01), date(1502, 01, 01), '', '', False),
            self.RegestDate(
                date(1503, 01, 01), date(1503, 01, 01), '', '', True))
        self.__create_and_check_dates(
            '1502-11 (1503-02)', self.RegestDate(
                date(1502, 11, 01), date(1502, 11, 01), '', '', False),
            self.RegestDate(
                date(1503, 02, 01), date(1503, 02, 01), '', '', True))
        self.__create_and_check_dates(
            '1502-11-22 (1503-02-07)', self.RegestDate(
                date(1502, 11, 22), date(1502, 11, 22), '', '', False),
            self.RegestDate(
                date(1503, 02, 07), date(1503, 02, 07), '', '', True))
        self.__create_and_check_dates(
            '1520 [bzw. 1519]', self.RegestDate(
                date(1520, 01, 01), date(1520, 01, 01), '', '', False),
            self.RegestDate(
                date(1519, 01, 01), date(1519, 01, 01), '', '', True))
        self.__create_and_check_dates(
            '1520-02 [bzw. 1519-03]', self.RegestDate(
                date(1520, 02, 01), date(1520, 02, 01), '', '', False),
            self.RegestDate(
                date(1519, 03, 01), date(1519, 03, 01), '', '', True))
        self.__create_and_check_dates(
            '1520-02-18 [bzw. 1519-03-06]', self.RegestDate(
                date(1520, 02, 18), date(1520, 02, 18), '', '', False),
            self.RegestDate(
                date(1519, 03, 06), date(1519, 03, 06), '', '', True))
        self.__create_and_check_dates(
            '1520 bzw. 1519', self.RegestDate(
                date(1520, 01, 01), date(1520, 01, 01), '', '', False),
            self.RegestDate(
                date(1519, 01, 01), date(1519, 01, 01), '', '', True))
        self.__create_and_check_dates(
            '1520-02 bzw. 1519-03', self.RegestDate(
                date(1520, 02, 01), date(1520, 02, 01), '', '', False),
            self.RegestDate(
                date(1519, 03, 01), date(1519, 03, 01), '', '', True))
        self.__create_and_check_dates(
            '1520-02-18 bzw. 1519-03-06', self.RegestDate(
                date(1520, 02, 18), date(1520, 02, 18), '', '', False),
            self.RegestDate(
                date(1519, 03, 06), date(1519, 03, 06), '', '', True))
        self.__create_and_check_dates(
            '1520 bzw. 1519 bzw. 1518', self.RegestDate(
                date(1520, 01, 01), date(1520, 01, 01), '', '', False),
            self.RegestDate(
                date(1519, 01, 01), date(1519, 01, 01), '', '', True),
            self.RegestDate(
                date(1518, 01, 01), date(1518, 01, 01), '', '', True))
        self.__create_and_check_dates(
            '1520-02 bzw. 1519-03 bzw. 1518-04', self.RegestDate(
                date(1520, 02, 01), date(1520, 02, 01), '', '', False),
            self.RegestDate(
                date(1519, 03, 01), date(1519, 03, 01), '', '', True),
            self.RegestDate(
                date(1518, 04, 01), date(1518, 04, 01), '', '', True))
        self.__create_and_check_dates(
            '1520-02-18 bzw. 1519-03-06 bzw. 1518-04-23', self.RegestDate(
                date(1520, 02, 18), date(1520, 02, 18), '', '', False),
            self.RegestDate(
                date(1519, 03, 06), date(1519, 03, 06), '', '', True),
            self.RegestDate(
                date(1518, 04, 23), date(1518, 04, 23), '', '', True))

    def test_simple_alternatives_with_location(self):
        '''
        Examples:
        - 1524/1525 Diedenhofen
        - 1524 / 1525 Frankfurt am Main
        - 1419-05/1419-06 St. Arnual
        - 1419-05 / 1419-06 Diedenhofen
        - 1421-10-05/1422-10-04 Frankfurt am Main
        - 1421-10-05 / 1422-10-04 St. Arnual
        - 1502 (1503) Diedenhofen
        - 1502-11 (1503-02) Frankfurt am Main
        - 1502-11-22 (1503-02-07) St. Arnual
        - 1520 [bzw. 1519] Diedenhofen
        - 1520-02 [bzw. 1519-03] Frankfurt am Main
        - 1520-02-18 [bzw. 1519-03-06] St. Arnual
        - 1520 bzw. 1519 Diedenhofen
        - 1520-02 bzw. 1519-03 Frankfurt am Main
        - 1520-02-18 bzw. 1519-03-06 St. Arnual
        - 1520 bzw. 1519 bzw. 1518 Diedenhofen
        - 1520-02 bzw. 1519-03 bzw. 1518-04 Frankfurt am Main
        - 1520-02-18 bzw. 1519-03-06 bzw. 1518-04-23 St. Arnual
        '''
        self.__create_and_check_dates(
            '1524/1525 Diedenhofen', self.RegestDate(
                date(1524, 01, 01), date(1524, 01, 01), '', '', False),
            self.RegestDate(
                date(1525, 01, 01), date(1525, 01, 01), '', '', True))
        self.__create_and_check_dates(
            '1524 / 1525 Frankfurt am Main', self.RegestDate(
                date(1524, 01, 01), date(1524, 01, 01), '', '', False),
            self.RegestDate(
                date(1525, 01, 01), date(1525, 01, 01), '', '', True))
        self.__create_and_check_dates(
            '1419-05/1419-06 St. Arnual', self.RegestDate(
                date(1419, 05, 01), date(1419, 05, 01), '', '', False),
            self.RegestDate(
                date(1419, 06, 01), date(1419, 06, 01), '', '', True))
        self.__create_and_check_dates(
            '1419-05 / 1419-06 Diedenhofen', self.RegestDate(
                date(1419, 05, 01), date(1419, 05, 01), '', '', False),
            self.RegestDate(
                date(1419, 06, 01), date(1419, 06, 01), '', '', True))
        self.__create_and_check_dates(
            '1421-10-05/1422-10-04 Frankfurt am Main', self.RegestDate(
                date(1421, 10, 05), date(1421, 10, 05), '', '', False),
            self.RegestDate(
                date(1422, 10, 04), date(1422, 10, 04), '', '', True))
        self.__create_and_check_dates(
            '1421-10-05 / 1422-10-04 St. Arnual', self.RegestDate(
                date(1421, 10, 05), date(1421, 10, 05), '', '', False),
            self.RegestDate(
                date(1422, 10, 04), date(1422, 10, 04), '', '', True))
        self.__create_and_check_dates(
            '1502 (1503) Diedenhofen', self.RegestDate(
                date(1502, 01, 01), date(1502, 01, 01), '', '', False),
            self.RegestDate(
                date(1503, 01, 01), date(1503, 01, 01), '', '', True))
        self.__create_and_check_dates(
            '1502-11 (1503-02) Frankfurt am Main', self.RegestDate(
                date(1502, 11, 01), date(1502, 11, 01), '', '', False),
            self.RegestDate(
                date(1503, 02, 01), date(1503, 02, 01), '', '', True))
        self.__create_and_check_dates(
            '1502-11-22 (1503-02-07) St. Arnual', self.RegestDate(
                date(1502, 11, 22), date(1502, 11, 22), '', '', False),
            self.RegestDate(
                date(1503, 02, 07), date(1503, 02, 07), '', '', True))
        self.__create_and_check_dates(
            '1520 [bzw. 1519] Diedenhofen', self.RegestDate(
                date(1520, 01, 01), date(1520, 01, 01), '', '', False),
            self.RegestDate(
                date(1519, 01, 01), date(1519, 01, 01), '', '', True))
        self.__create_and_check_dates(
            '1520-02 [bzw. 1519-03] Frankfurt am Main', self.RegestDate(
                date(1520, 02, 01), date(1520, 02, 01), '', '', False),
            self.RegestDate(
                date(1519, 03, 01), date(1519, 03, 01), '', '', True))
        self.__create_and_check_dates(
            '1520-02-18 [bzw. 1519-03-06] St. Arnual', self.RegestDate(
                date(1520, 02, 18), date(1520, 02, 18), '', '', False),
            self.RegestDate(
                date(1519, 03, 06), date(1519, 03, 06), '', '', True))
        self.__create_and_check_dates(
            '1520 bzw. 1519 Diedenhofen', self.RegestDate(
                date(1520, 01, 01), date(1520, 01, 01), '', '', False),
            self.RegestDate(
                date(1519, 01, 01), date(1519, 01, 01), '', '', True))
        self.__create_and_check_dates(
            '1520-02 bzw. 1519-03 Frankfurt am Main', self.RegestDate(
                date(1520, 02, 01), date(1520, 02, 01), '', '', False),
            self.RegestDate(
                date(1519, 03, 01), date(1519, 03, 01), '', '', True))
        self.__create_and_check_dates(
            '1520-02-18 bzw. 1519-03-06 St. Arnual', self.RegestDate(
                date(1520, 02, 18), date(1520, 02, 18), '', '', False),
            self.RegestDate(
                date(1519, 03, 06), date(1519, 03, 06), '', '', True))
        self.__create_and_check_dates(
            '1520 bzw. 1519 bzw. 1518 Diedenhofen', self.RegestDate(
                date(1520, 01, 01), date(1520, 01, 01), '', '', False),
            self.RegestDate(
                date(1519, 01, 01), date(1519, 01, 01), '', '', True),
            self.RegestDate(
                date(1518, 01, 01), date(1518, 01, 01), '', '', True))
        self.__create_and_check_dates(
            '1520-02 bzw. 1519-03 bzw. 1518-04 Frankfurt am Main',
            self.RegestDate(
                date(1520, 02, 01), date(1520, 02, 01), '', '', False),
            self.RegestDate(
                date(1519, 03, 01), date(1519, 03, 01), '', '', True),
            self.RegestDate(
                date(1518, 04, 01), date(1518, 04, 01), '', '', True))
        self.__create_and_check_dates(
            '1520-02-18 bzw. 1519-03-06 bzw. 1518-04-23 St. Arnual',
            self.RegestDate(
                date(1520, 02, 18), date(1520, 02, 18), '', '', False),
            self.RegestDate(
                date(1519, 03, 06), date(1519, 03, 06), '', '', True),
            self.RegestDate(
                date(1518, 04, 23), date(1518, 04, 23), '', '', True))

    def test_simple_alternatives_with_duplicates(self):
        '''
        Examples:
        - 1524/1525 (a)
        - 1524 / 1525 (b)
        - 1419-05/1419-06 (c)
        - 1419-05 / 1419-06 (a)
        - 1421-10-05/1422-10-04 (b)
        - 1421-10-05 / 1422-10-04 (c)
        - 1502 (1503) (a)
        - 1502-11 (1503-02) (b)
        - 1502-11-22 (1503-02-07) (c)
        - 1520 [bzw. 1519] (a)
        - 1520-02 [bzw. 1519-03] (b)
        - 1520-02-18 [bzw. 1519-03-06] (c)
        - 1520 bzw. 1519 (a)
        - 1520-02 bzw. 1519-03 (b)
        - 1520-02-18 bzw. 1519-03-06 (c)
        - 1520 bzw. 1519 bzw. 1518 (a)
        - 1520-02 bzw. 1519-03 bzw. 1518-04 (b)
        - 1520-02-18 bzw. 1519-03-06 bzw. 1518-04-23 (c)
        '''
        self.__create_and_check_dates(
            '1524/1525 (a)', self.RegestDate(
                date(1524, 01, 01), date(1524, 01, 01), '', '', False),
            self.RegestDate(
                date(1525, 01, 01), date(1525, 01, 01), '', '', True))
        self.__create_and_check_dates(
            '1524 / 1525 (b)', self.RegestDate(
                date(1524, 01, 01), date(1524, 01, 01), '', '', False),
            self.RegestDate(
                date(1525, 01, 01), date(1525, 01, 01), '', '', True))
        self.__create_and_check_dates(
            '1419-05/1419-06 (c)', self.RegestDate(
                date(1419, 05, 01), date(1419, 05, 01), '', '', False),
            self.RegestDate(
                date(1419, 06, 01), date(1419, 06, 01), '', '', True))
        self.__create_and_check_dates(
            '1419-05 / 1419-06 (a)', self.RegestDate(
                date(1419, 05, 01), date(1419, 05, 01), '', '', False),
            self.RegestDate(
                date(1419, 06, 01), date(1419, 06, 01), '', '', True))
        self.__create_and_check_dates(
            '1421-10-05/1422-10-04 (b)', self.RegestDate(
                date(1421, 10, 05), date(1421, 10, 05), '', '', False),
            self.RegestDate(
                date(1422, 10, 04), date(1422, 10, 04), '', '', True))
        self.__create_and_check_dates(
            '1421-10-05 / 1422-10-04 (c)', self.RegestDate(
                date(1421, 10, 05), date(1421, 10, 05), '', '', False),
            self.RegestDate(
                date(1422, 10, 04), date(1422, 10, 04), '', '', True))
        self.__create_and_check_dates(
            '1502 (1503) (a)', self.RegestDate(
                date(1502, 01, 01), date(1502, 01, 01), '', '', False),
            self.RegestDate(
                date(1503, 01, 01), date(1503, 01, 01), '', '', True))
        self.__create_and_check_dates(
            '1502-11 (1503-02) (b)', self.RegestDate(
                date(1502, 11, 01), date(1502, 11, 01), '', '', False),
            self.RegestDate(
                date(1503, 02, 01), date(1503, 02, 01), '', '', True))
        self.__create_and_check_dates(
            '1502-11-22 (1503-02-07) (c)', self.RegestDate(
                date(1502, 11, 22), date(1502, 11, 22), '', '', False),
            self.RegestDate(
                date(1503, 02, 07), date(1503, 02, 07), '', '', True))
        self.__create_and_check_dates(
            '1520 [bzw. 1519] (a)', self.RegestDate(
                date(1520, 01, 01), date(1520, 01, 01), '', '', False),
            self.RegestDate(
                date(1519, 01, 01), date(1519, 01, 01), '', '', True))
        self.__create_and_check_dates(
            '1520-02 [bzw. 1519-03] (b)', self.RegestDate(
                date(1520, 02, 01), date(1520, 02, 01), '', '', False),
            self.RegestDate(
                date(1519, 03, 01), date(1519, 03, 01), '', '', True))
        self.__create_and_check_dates(
            '1520-02-18 [bzw. 1519-03-06] (c)', self.RegestDate(
                date(1520, 02, 18), date(1520, 02, 18), '', '', False),
            self.RegestDate(
                date(1519, 03, 06), date(1519, 03, 06), '', '', True))
        self.__create_and_check_dates(
            '1520 bzw. 1519 (a)', self.RegestDate(
                date(1520, 01, 01), date(1520, 01, 01), '', '', False),
            self.RegestDate(
                date(1519, 01, 01), date(1519, 01, 01), '', '', True))
        self.__create_and_check_dates(
            '1520-02 bzw. 1519-03 (b)', self.RegestDate(
                date(1520, 02, 01), date(1520, 02, 01), '', '', False),
            self.RegestDate(
                date(1519, 03, 01), date(1519, 03, 01), '', '', True))
        self.__create_and_check_dates(
            '1520-02-18 bzw. 1519-03-06 (c)', self.RegestDate(
                date(1520, 02, 18), date(1520, 02, 18), '', '', False),
            self.RegestDate(
                date(1519, 03, 06), date(1519, 03, 06), '', '', True))
        self.__create_and_check_dates(
            '1520 bzw. 1519 bzw. 1518 (a)', self.RegestDate(
                date(1520, 01, 01), date(1520, 01, 01), '', '', False),
            self.RegestDate(
                date(1519, 01, 01), date(1519, 01, 01), '', '', True),
            self.RegestDate(
                date(1518, 01, 01), date(1518, 01, 01), '', '', True))
        self.__create_and_check_dates(
            '1520-02 bzw. 1519-03 bzw. 1518-04 (b)', self.RegestDate(
                date(1520, 02, 01), date(1520, 02, 01), '', '', False),
            self.RegestDate(
                date(1519, 03, 01), date(1519, 03, 01), '', '', True),
            self.RegestDate(
                date(1518, 04, 01), date(1518, 04, 01), '', '', True))
        self.__create_and_check_dates(
            '1520-02-18 bzw. 1519-03-06 bzw. 1518-04-23 (c)', self.RegestDate(
                date(1520, 02, 18), date(1520, 02, 18), '', '', False),
            self.RegestDate(
                date(1519, 03, 06), date(1519, 03, 06), '', '', True),
            self.RegestDate(
                date(1518, 04, 23), date(1518, 04, 23), '', '', True))

    def test_simple_alternatives_with_duplicates_and_location(self):
        '''
        Examples:
        - 1524/1525 (a) Diedenhofen
        - 1524 / 1525 (b) Frankfurt am Main
        - 1419-05/1419-06 (c) St. Arnual
        - 1419-05 / 1419-06 (a) Diedenhofen
        - 1421-10-05/1422-10-04 (b) Frankfurt am Main
        - 1421-10-05 / 1422-10-04 (c) St. Arnual
        - 1502 (1503) (a) Diedenhofen
        - 1502-11 (1503-02) (b) Frankfurt am Main
        - 1502-11-22 (1503-02-07) (c) St. Arnual
        - 1520 [bzw. 1519] (a) Diedenhofen
        - 1520-02 [bzw. 1519-03] (b) Frankfurt am Main
        - 1520-02-18 [bzw. 1519-03-06] (c) St. Arnual
        - 1520 bzw. 1519 (a) Diedenhofen
        - 1520-02 bzw. 1519-03 (b) Frankfurt am Main
        - 1520-02-18 bzw. 1519-03-06 (c) St. Arnual
        - 1520 bzw. 1519 bzw. 1518 (a) Diedenhofen
        - 1520-02 bzw. 1519-03 bzw. 1518-04 (b) Frankfurt am Main
        - 1520-02-18 bzw. 1519-03-06 bzw. 1518-04-23 (c) St. Arnual
        '''
        self.__create_and_check_dates(
            '1524/1525 (a) Diedenhofen', self.RegestDate(
                date(1524, 01, 01), date(1524, 01, 01), '', '', False),
            self.RegestDate(
                date(1525, 01, 01), date(1525, 01, 01), '', '', True))
        self.__create_and_check_dates(
            '1524 / 1525 (b) Frankfurt am Main', self.RegestDate(
                date(1524, 01, 01), date(1524, 01, 01), '', '', False),
            self.RegestDate(
                date(1525, 01, 01), date(1525, 01, 01), '', '', True))
        self.__create_and_check_dates(
            '1419-05/1419-06 (c) St. Arnual', self.RegestDate(
                date(1419, 05, 01), date(1419, 05, 01), '', '', False),
            self.RegestDate(
                date(1419, 06, 01), date(1419, 06, 01), '', '', True))
        self.__create_and_check_dates(
            '1419-05 / 1419-06 (a) Diedenhofen', self.RegestDate(
                date(1419, 05, 01), date(1419, 05, 01), '', '', False),
            self.RegestDate(
                date(1419, 06, 01), date(1419, 06, 01), '', '', True))
        self.__create_and_check_dates(
            '1421-10-05/1422-10-04 (b) Frankfurt am Main', self.RegestDate(
                date(1421, 10, 05), date(1421, 10, 05), '', '', False),
            self.RegestDate(
                date(1422, 10, 04), date(1422, 10, 04), '', '', True))
        self.__create_and_check_dates(
            '1421-10-05 / 1422-10-04 (c) St. Arnual', self.RegestDate(
                date(1421, 10, 05), date(1421, 10, 05), '', '', False),
            self.RegestDate(
                date(1422, 10, 04), date(1422, 10, 04), '', '', True))
        self.__create_and_check_dates(
            '1502 (1503) (a) Diedenhofen', self.RegestDate(
                date(1502, 01, 01), date(1502, 01, 01), '', '', False),
            self.RegestDate(
                date(1503, 01, 01), date(1503, 01, 01), '', '', True))
        self.__create_and_check_dates(
            '1502-11 (1503-02) (b) Frankfurt am Main', self.RegestDate(
                date(1502, 11, 01), date(1502, 11, 01), '', '', False),
            self.RegestDate(
                date(1503, 02, 01), date(1503, 02, 01), '', '', True))
        self.__create_and_check_dates(
            '1502-11-22 (1503-02-07) (c) St. Arnual', self.RegestDate(
                date(1502, 11, 22), date(1502, 11, 22), '', '', False),
            self.RegestDate(
                date(1503, 02, 07), date(1503, 02, 07), '', '', True))
        self.__create_and_check_dates(
            '1520 [bzw. 1519] (a) Diedenhofen', self.RegestDate(
                date(1520, 01, 01), date(1520, 01, 01), '', '', False),
            self.RegestDate(
                date(1519, 01, 01), date(1519, 01, 01), '', '', True))
        self.__create_and_check_dates(
            '1520-02 [bzw. 1519-03] (b) Frankfurt am Main', self.RegestDate(
                date(1520, 02, 01), date(1520, 02, 01), '', '', False),
            self.RegestDate(
                date(1519, 03, 01), date(1519, 03, 01), '', '', True))
        self.__create_and_check_dates(
            '1520-02-18 [bzw. 1519-03-06] (c) St. Arnual', self.RegestDate(
                date(1520, 02, 18), date(1520, 02, 18), '', '', False),
            self.RegestDate(
                date(1519, 03, 06), date(1519, 03, 06), '', '', True))
        self.__create_and_check_dates(
            '1520 bzw. 1519 (a) Diedenhofen', self.RegestDate(
                date(1520, 01, 01), date(1520, 01, 01), '', '', False),
            self.RegestDate(
                date(1519, 01, 01), date(1519, 01, 01), '', '', True))
        self.__create_and_check_dates(
            '1520-02 bzw. 1519-03 (b) Frankfurt am Main', self.RegestDate(
                date(1520, 02, 01), date(1520, 02, 01), '', '', False),
            self.RegestDate(
                date(1519, 03, 01), date(1519, 03, 01), '', '', True))
        self.__create_and_check_dates(
            '1520-02-18 bzw. 1519-03-06 (c) St. Arnual', self.RegestDate(
                date(1520, 02, 18), date(1520, 02, 18), '', '', False),
            self.RegestDate(
                date(1519, 03, 06), date(1519, 03, 06), '', '', True))
        self.__create_and_check_dates(
            '1520 bzw. 1519 bzw. 1518 (a) Diedenhofen', self.RegestDate(
                date(1520, 01, 01), date(1520, 01, 01), '', '', False),
            self.RegestDate(
                date(1519, 01, 01), date(1519, 01, 01), '', '', True),
            self.RegestDate(
                date(1518, 01, 01), date(1518, 01, 01), '', '', True))
        self.__create_and_check_dates(
            '1520-02 bzw. 1519-03 bzw. 1518-04 (b) Frankfurt am Main',
            self.RegestDate(
                date(1520, 02, 01), date(1520, 02, 01), '', '', False),
            self.RegestDate(
                date(1519, 03, 01), date(1519, 03, 01), '', '', True),
            self.RegestDate(
                date(1518, 04, 01), date(1518, 04, 01), '', '', True))
        self.__create_and_check_dates(
            '1520-02-18 bzw. 1519-03-06 bzw. 1518-04-23 (c) St. Arnual',
            self.RegestDate(
                date(1520, 02, 18), date(1520, 02, 18), '', '', False),
            self.RegestDate(
                date(1519, 03, 06), date(1519, 03, 06), '', '', True),
            self.RegestDate(
                date(1518, 04, 23), date(1518, 04, 23), '', '', True))

    def test_simple_alternatives_with_offset(self):
        '''
        Examples:
        - 1524/1525 (vor)
        - 1524 / 1525 (nach)
        - 1419-05/1419-06 (um)
        - 1419-05 / 1419-06 (ca.)
        - 1421-10-05/1422-10-04 (kurz nach)
        - 1421-10-05 / 1422-10-04 (post)
        - 1502 (1503) (vor)
        - 1502-11 (1503-02) (nach)
        - 1502-11-22 (1503-02-07) (um)
        - 1520 [bzw. 1519] (ca.)
        - 1520-02 [bzw. 1519-03] (kurz nach)
        - 1520-02-18 [bzw. 1519-03-06] (post)
        - 1520 bzw. 1519 (um)
        - 1520-02 bzw. 1519-03 (ca.)
        - 1520-02-18 bzw. 1519-03-06 (kurz nach)
        - 1520 bzw. 1519 bzw. 1518 (um)
        - 1520-02 bzw. 1519-03 bzw. 1518-04 (ca.)
        - 1520-02-18 bzw. 1519-03-06 bzw. 1518-04-23 (kurz nach)
        '''
        self.__create_and_check_dates(
            '1524/1525 (vor)', self.RegestDate(
                date(1524, 01, 01), date(1524, 01, 01), 'vor', 'vor', False),
            self.RegestDate(
                date(1525, 01, 01), date(1525, 01, 01), 'vor', 'vor', True))
        self.__create_and_check_dates(
            '1524 / 1525 (nach)', self.RegestDate(
                date(1524, 01, 01), date(1524, 01, 01),
                'nach', 'nach', False),
            self.RegestDate(
                date(1525, 01, 01), date(1525, 01, 01), 'nach', 'nach', True))
        self.__create_and_check_dates(
            '1419-05/1419-06 (um)', self.RegestDate(
                date(1419, 05, 01), date(1419, 05, 01), 'um', 'um', False),
            self.RegestDate(
                date(1419, 06, 01), date(1419, 06, 01), 'um', 'um', True))
        self.__create_and_check_dates(
            '1419-05 / 1419-06 (ca.)', self.RegestDate(
                date(1419, 05, 01), date(1419, 05, 01), 'ca.', 'ca.', False),
            self.RegestDate(
                date(1419, 06, 01), date(1419, 06, 01), 'ca.', 'ca.', True))
        self.__create_and_check_dates(
            '1421-10-05/1422-10-04 (kurz nach)', self.RegestDate(
                date(1421, 10, 05), date(1421, 10, 05),
                'kurz nach', 'kurz nach', False),
            self.RegestDate(
                date(1422, 10, 04), date(1422, 10, 04),
                'kurz nach', 'kurz nach', True))
        self.__create_and_check_dates(
            '1421-10-05 / 1422-10-04 (post)', self.RegestDate(
                date(1421, 10, 05), date(1421, 10, 05),
                'post', 'post', False),
            self.RegestDate(
                date(1422, 10, 04), date(1422, 10, 04), 'post', 'post', True))
        self.__create_and_check_dates(
            '1502 (1503) (vor)', self.RegestDate(
                date(1502, 01, 01), date(1502, 01, 01), 'vor', 'vor', False),
            self.RegestDate(
                date(1503, 01, 01), date(1503, 01, 01), 'vor', 'vor', True))
        self.__create_and_check_dates(
            '1502-11 (1503-02) (nach)', self.RegestDate(
                date(1502, 11, 01), date(1502, 11, 01),
                'nach', 'nach', False),
            self.RegestDate(
                date(1503, 02, 01), date(1503, 02, 01), 'nach', 'nach', True))
        self.__create_and_check_dates(
            '1502-11-22 (1503-02-07) (um)', self.RegestDate(
                date(1502, 11, 22), date(1502, 11, 22), 'um', 'um', False),
            self.RegestDate(
                date(1503, 02, 07), date(1503, 02, 07), 'um', 'um', True))
        self.__create_and_check_dates(
            '1520 [bzw. 1519] (ca.)', self.RegestDate(
                date(1520, 01, 01), date(1520, 01, 01), 'ca.', 'ca.', False),
            self.RegestDate(
                date(1519, 01, 01), date(1519, 01, 01), 'ca.', 'ca.', True))
        self.__create_and_check_dates(
            '1520-02 [bzw. 1519-03] (kurz nach)', self.RegestDate(
                date(1520, 02, 01), date(1520, 02, 01),
                'kurz nach', 'kurz nach', False),
            self.RegestDate(
                date(1519, 03, 01), date(1519, 03, 01),
                'kurz nach', 'kurz nach', True))
        self.__create_and_check_dates(
            '1520-02-18 [bzw. 1519-03-06] (post)', self.RegestDate(
                date(1520, 02, 18), date(1520, 02, 18),
                'post', 'post', False),
            self.RegestDate(
                date(1519, 03, 06), date(1519, 03, 06), 'post', 'post', True))
        self.__create_and_check_dates(
            '1520 bzw. 1519 (um)', self.RegestDate(
                date(1520, 01, 01), date(1520, 01, 01), 'um', 'um', False),
            self.RegestDate(
                date(1519, 01, 01), date(1519, 01, 01), 'um', 'um', True))
        self.__create_and_check_dates(
            '1520-02 bzw. 1519-03 (ca.)', self.RegestDate(
                date(1520, 02, 01), date(1520, 02, 01), 'ca.', 'ca.', False),
            self.RegestDate(
                date(1519, 03, 01), date(1519, 03, 01), 'ca.', 'ca.', True))
        self.__create_and_check_dates(
            '1520-02-18 bzw. 1519-03-06 (kurz nach)', self.RegestDate(
                date(1520, 02, 18), date(1520, 02, 18),
                'kurz nach', 'kurz nach', False),
            self.RegestDate(
                date(1519, 03, 06), date(1519, 03, 06),
                'kurz nach', 'kurz nach', True))
        self.__create_and_check_dates(
            '1520 bzw. 1519 bzw. 1518 (um)', self.RegestDate(
                date(1520, 01, 01), date(1520, 01, 01), 'um', 'um', False),
            self.RegestDate(
                date(1519, 01, 01), date(1519, 01, 01), 'um', 'um', True),
            self.RegestDate(
                date(1518, 01, 01), date(1518, 01, 01), 'um', 'um', True))
        self.__create_and_check_dates(
            '1520-02 bzw. 1519-03 bzw. 1518-04 (ca.)', self.RegestDate(
                date(1520, 02, 01), date(1520, 02, 01), 'ca.', 'ca.', False),
            self.RegestDate(
                date(1519, 03, 01), date(1519, 03, 01), 'ca.', 'ca.', True),
            self.RegestDate(
                date(1518, 04, 01), date(1518, 04, 01), 'ca.', 'ca.', True))
        self.__create_and_check_dates(
            '1520-02-18 bzw. 1519-03-06 bzw. 1518-04-23 (kurz nach)',
            self.RegestDate(
                date(1520, 02, 18), date(1520, 02, 18),
                'kurz nach', 'kurz nach', False),
            self.RegestDate(
                date(1519, 03, 06), date(1519, 03, 06),
                'kurz nach', 'kurz nach', True),
            self.RegestDate(
                date(1518, 04, 23), date(1518, 04, 23),
                'kurz nach', 'kurz nach', True))

    def test_elliptical_alternatives(self):
        '''
        Examples:
        - 1270-04/05 (month different, no day)
        - 1270-04 / 05 (month different, no day)
        - 1440-11-12/17 (day different)
        - 1440-11-12 / 17 (day different)
        - 1270-04-27/05-28 (month *and* day different)
        - 1270-04-27 / 05-28 (month *and* day different)

        - 1466 [04/05] (month different, no day)
        - 1466 [04 / 05] (month different, no day)
        - 1466-04 [28/29] (day different)
        - 1466-04 [28 / 29] (day different)
        - 1466 [04-28/05-01] (month *and* day different)
        - 1466 [04-28 / 05-01] (month *and* day different)

        - 1506-05 bzw. 11 (month different, no day)
        - 1506-05-12 bzw. 10 (day different)
        - 1506-05-12 bzw. 11-10 (month *and* day different)
        - 1506-05 bzw. 11 bzw. 12 (month different, no day)
        - 1506-05-12 bzw. 10 bzw. 01 (day different)
        - 1506-05-12 bzw. 11-10 bzw. 12-01 (month *and* day different)

        - 1343-04 oder 05 (month different, no day)
        - 1343-04-12 oder 19 (day different)
        - 1343-04-12 oder 05-19 (month *and* day different)
        '''
        self.__create_and_check_dates(
            '1270-04/05', self.RegestDate(
                date(1270, 04, 01), date(1270, 04, 01), '', '', False),
            self.RegestDate(
                date(1270, 05, 01), date(1270, 05, 01), '', '', True))
        self.__create_and_check_dates(
            '1270-04 / 05', self.RegestDate(
                date(1270, 04, 01), date(1270, 04, 01), '', '', False),
            self.RegestDate(
                date(1270, 05, 01), date(1270, 05, 01), '', '', True))
        self.__create_and_check_dates(
            '1440-11-12/17', self.RegestDate(
                date(1440, 11, 12), date(1440, 11, 12), '', '', False),
            self.RegestDate(
                date(1440, 11, 17), date(1440, 11, 17), '', '', True))
        self.__create_and_check_dates(
            '1440-11-12 / 17', self.RegestDate(
                date(1440, 11, 12), date(1440, 11, 12), '', '', False),
            self.RegestDate(
                date(1440, 11, 17), date(1440, 11, 17), '', '', True))
        self.__create_and_check_dates(
            '1270-04-27/05-28', self.RegestDate(
                date(1270, 04, 27), date(1270, 04, 27), '', '', False),
            self.RegestDate(
                date(1270, 05, 28), date(1270, 05, 28), '', '', True))
        self.__create_and_check_dates(
            '1270-04-27 / 05-28', self.RegestDate(
                date(1270, 04, 27), date(1270, 04, 27), '', '', False),
            self.RegestDate(
                date(1270, 05, 28), date(1270, 05, 28), '', '', True))
        self.__create_and_check_dates(
            '1466 [04/05]', self.RegestDate(
                date(1466, 04, 01), date(1466, 04, 01), '', '', False),
            self.RegestDate(
                date(1466, 05, 01), date(1466, 05, 01), '', '', True))
        self.__create_and_check_dates(
            '1466 [04 / 05]', self.RegestDate(
                date(1466, 04, 01), date(1466, 04, 01), '', '', False),
            self.RegestDate(
                date(1466, 05, 01), date(1466, 05, 01), '', '', True))
        self.__create_and_check_dates(
            '1466-04 [28/29]', self.RegestDate(
                date(1466, 04, 28), date(1466, 04, 28), '', '', False),
            self.RegestDate(
                date(1466, 04, 29), date(1466, 04, 29), '', '', True))
        self.__create_and_check_dates(
            '1466-04 [28 / 29]', self.RegestDate(
                date(1466, 04, 28), date(1466, 04, 28), '', '', False),
            self.RegestDate(
                date(1466, 04, 29), date(1466, 04, 29), '', '', True))
        self.__create_and_check_dates(
            '1466 [04-28/05-01]', self.RegestDate(
                date(1466, 04, 28), date(1466, 04, 28), '', '', False),
            self.RegestDate(
                date(1466, 05, 01), date(1466, 05, 01), '', '', True))
        self.__create_and_check_dates(
            '1466 [04-28/05-01]', self.RegestDate(
                date(1466, 04, 28), date(1466, 04, 28), '', '', False),
            self.RegestDate(
                date(1466, 05, 01), date(1466, 05, 01), '', '', True))
        self.__create_and_check_dates(
            '1506-05 bzw. 11', self.RegestDate(
                date(1506, 05, 01), date(1506, 05, 01), '', '', False),
            self.RegestDate(
                date(1506, 11, 01), date(1506, 11, 01), '', '', True))
        self.__create_and_check_dates(
            '1506-05-12 bzw. 10', self.RegestDate(
                date(1506, 05, 12), date(1506, 05, 12), '', '', False),
            self.RegestDate(
                date(1506, 05, 10), date(1506, 05, 10), '', '', True))
        self.__create_and_check_dates(
            '1506-05-12 bzw. 11-10', self.RegestDate(
                date(1506, 05, 12), date(1506, 05, 12), '', '', False),
            self.RegestDate(
                date(1506, 11, 10), date(1506, 11, 10), '', '', True))
        self.__create_and_check_dates(
            '1506-05 bzw. 11 bzw. 12', self.RegestDate(
                date(1506, 05, 01), date(1506, 05, 01), '', '', False),
            self.RegestDate(
                date(1506, 11, 01), date(1506, 11, 01), '', '', True),
            self.RegestDate(
                date(1506, 12, 01), date(1506, 12, 01), '', '', True))
        self.__create_and_check_dates(
            '1506-05-12 bzw. 10 bzw. 01', self.RegestDate(
                date(1506, 05, 12), date(1506, 05, 12), '', '', False),
            self.RegestDate(
                date(1506, 05, 10), date(1506, 05, 10), '', '', True),
            self.RegestDate(
                date(1506, 05, 01), date(1506, 05, 01), '', '', True))
        self.__create_and_check_dates(
            '1506-05-12 bzw. 11-10 bzw. 12-01', self.RegestDate(
                date(1506, 05, 12), date(1506, 05, 12), '', '', False),
            self.RegestDate(
                date(1506, 11, 10), date(1506, 11, 10), '', '', True),
            self.RegestDate(
                date(1506, 12, 01), date(1506, 12, 01), '', '', True))
        self.__create_and_check_dates(
            '1343-04 oder 05', self.RegestDate(
                date(1343, 04, 01), date(1343, 04, 01), '', '', False),
            self.RegestDate(
                date(1343, 05, 01), date(1343, 05, 01), '', '', True))
        self.__create_and_check_dates(
            '1343-04-12 oder 19', self.RegestDate(
                date(1343, 04, 12), date(1343, 04, 12), '', '', False),
            self.RegestDate(
                date(1343, 04, 19), date(1343, 04, 19), '', '', True))
        self.__create_and_check_dates(
            '1343-04-12 oder 05-19', self.RegestDate(
                date(1343, 04, 12), date(1343, 04, 12), '', '', False),
            self.RegestDate(
                date(1343, 05, 19), date(1343, 05, 19), '', '', True))

    def test_elliptical_alternatives_with_location(self):
        '''
        Examples:
        - 1270-04/05 Diedenhofen
        - 1270-04 / 05 Frankfurt am Main
        - 1440-11-12/17 St. Arnual
        - 1440-11-12 / 17 Diedenhofen
        - 1270-04-27/05-28 Frankfurt am Main
        - 1270-04-27 / 05-28 St. Arnual

        - 1466 [04/05] Diedenhofen
        - 1466 [04 / 05] Frankfurt am Main
        - 1466-04 [28/29] St. Arnual
        - 1466-04 [28 / 29] Diedenhofen
        - 1466 [04-28/05-01] Frankfurt am Main
        - 1466 [04-28 / 05-01] St. Arnual

        - 1506-05 bzw. 11 Diedenhofen
        - 1506-05-12 bzw. 10 Frankfurt am Main
        - 1506-05-12 bzw. 11-10 St. Arnual
        - 1506-05 bzw. 11 bzw. 12 Diedenhofen
        - 1506-05-12 bzw. 10 bzw. 01 Frankfurt am Main
        - 1506-05-12 bzw. 11-10 bzw. 12-01 St. Arnual

        - 1343-04 oder 05 Diedenhofen
        - 1343-04-12 oder 19 Frankfurt am Main
        - 1343-04-12 oder 05-19 St. Arnual
        '''
        self.__create_and_check_dates(
            '1270-04/05 Diedenhofen', self.RegestDate(
                date(1270, 04, 01), date(1270, 04, 01), '', '', False),
            self.RegestDate(
                date(1270, 05, 01), date(1270, 05, 01), '', '', True))
        self.__create_and_check_dates(
            '1270-04 / 05 Frankfurt am Main', self.RegestDate(
                date(1270, 04, 01), date(1270, 04, 01), '', '', False),
            self.RegestDate(
                date(1270, 05, 01), date(1270, 05, 01), '', '', True))
        self.__create_and_check_dates(
            '1440-11-12/17 St. Arnual', self.RegestDate(
                date(1440, 11, 12), date(1440, 11, 12), '', '', False),
            self.RegestDate(
                date(1440, 11, 17), date(1440, 11, 17), '', '', True))
        self.__create_and_check_dates(
            '1440-11-12 / 17 Diedenhofen', self.RegestDate(
                date(1440, 11, 12), date(1440, 11, 12), '', '', False),
            self.RegestDate(
                date(1440, 11, 17), date(1440, 11, 17), '', '', True))
        self.__create_and_check_dates(
            '1270-04-27/05-28 Frankfurt am Main', self.RegestDate(
                date(1270, 04, 27), date(1270, 04, 27), '', '', False),
            self.RegestDate(
                date(1270, 05, 28), date(1270, 05, 28), '', '', True))
        self.__create_and_check_dates(
            '1270-04-27 / 05-28 St. Arnual', self.RegestDate(
                date(1270, 04, 27), date(1270, 04, 27), '', '', False),
            self.RegestDate(
                date(1270, 05, 28), date(1270, 05, 28), '', '', True))
        self.__create_and_check_dates(
            '1466 [04/05] Diedenhofen', self.RegestDate(
                date(1466, 04, 01), date(1466, 04, 01), '', '', False),
            self.RegestDate(
                date(1466, 05, 01), date(1466, 05, 01), '', '', True))
        self.__create_and_check_dates(
            '1466 [04 / 05] Frankfurt am Main', self.RegestDate(
                date(1466, 04, 01), date(1466, 04, 01), '', '', False),
            self.RegestDate(
                date(1466, 05, 01), date(1466, 05, 01), '', '', True))
        self.__create_and_check_dates(
            '1466-04 [28/29] St. Arnual', self.RegestDate(
                date(1466, 04, 28), date(1466, 04, 28), '', '', False),
            self.RegestDate(
                date(1466, 04, 29), date(1466, 04, 29), '', '', True))
        self.__create_and_check_dates(
            '1466-04 [28 / 29] Diedenhofen', self.RegestDate(
                date(1466, 04, 28), date(1466, 04, 28), '', '', False),
            self.RegestDate(
                date(1466, 04, 29), date(1466, 04, 29), '', '', True))
        self.__create_and_check_dates(
            '1466 [04-28/05-01] Frankfurt am Main', self.RegestDate(
                date(1466, 04, 28), date(1466, 04, 28), '', '', False),
            self.RegestDate(
                date(1466, 05, 01), date(1466, 05, 01), '', '', True))
        self.__create_and_check_dates(
            '1466 [04-28/05-01] St. Arnual', self.RegestDate(
                date(1466, 04, 28), date(1466, 04, 28), '', '', False),
            self.RegestDate(
                date(1466, 05, 01), date(1466, 05, 01), '', '', True))
        self.__create_and_check_dates(
            '1506-05 bzw. 11 Diedenhofen', self.RegestDate(
                date(1506, 05, 01), date(1506, 05, 01), '', '', False),
            self.RegestDate(
                date(1506, 11, 01), date(1506, 11, 01), '', '', True))
        self.__create_and_check_dates(
            '1506-05-12 bzw. 10 Frankfurt am Main', self.RegestDate(
                date(1506, 05, 12), date(1506, 05, 12), '', '', False),
            self.RegestDate(
                date(1506, 05, 10), date(1506, 05, 10), '', '', True))
        self.__create_and_check_dates(
            '1506-05-12 bzw. 11-10 St. Arnual', self.RegestDate(
                date(1506, 05, 12), date(1506, 05, 12), '', '', False),
            self.RegestDate(
                date(1506, 11, 10), date(1506, 11, 10), '', '', True))
        self.__create_and_check_dates(
            '1506-05 bzw. 11 bzw. 12 Diedenhofen', self.RegestDate(
                date(1506, 05, 01), date(1506, 05, 01), '', '', False),
            self.RegestDate(
                date(1506, 11, 01), date(1506, 11, 01), '', '', True),
            self.RegestDate(
                date(1506, 12, 01), date(1506, 12, 01), '', '', True))
        self.__create_and_check_dates(
            '1506-05-12 bzw. 10 bzw. 01 Frankfurt am Main', self.RegestDate(
                date(1506, 05, 12), date(1506, 05, 12), '', '', False),
            self.RegestDate(
                date(1506, 05, 10), date(1506, 05, 10), '', '', True),
            self.RegestDate(
                date(1506, 05, 01), date(1506, 05, 01), '', '', True))
        self.__create_and_check_dates(
            '1506-05-12 bzw. 11-10 bzw. 12-01 St. Arnual', self.RegestDate(
                date(1506, 05, 12), date(1506, 05, 12), '', '', False),
            self.RegestDate(
                date(1506, 11, 10), date(1506, 11, 10), '', '', True),
            self.RegestDate(
                date(1506, 12, 01), date(1506, 12, 01), '', '', True))
        self.__create_and_check_dates(
            '1343-04 oder 05 Diedenhofen', self.RegestDate(
                date(1343, 04, 01), date(1343, 04, 01), '', '', False),
            self.RegestDate(
                date(1343, 05, 01), date(1343, 05, 01), '', '', True))
        self.__create_and_check_dates(
            '1343-04-12 oder 19 Frankfurt am Main', self.RegestDate(
                date(1343, 04, 12), date(1343, 04, 12), '', '', False),
            self.RegestDate(
                date(1343, 04, 19), date(1343, 04, 19), '', '', True))
        self.__create_and_check_dates(
            '1343-04-12 oder 05-19 St. Arnual', self.RegestDate(
                date(1343, 04, 12), date(1343, 04, 12), '', '', False),
            self.RegestDate(
                date(1343, 05, 19), date(1343, 05, 19), '', '', True))

    def test_elliptical_alternatives_with_duplicates(self):
        '''
        Examples:
        - 1270-04/05 (a)
        - 1270-04 / 05 (b)
        - 1440-11-12/17 (c)
        - 1440-11-12 / 17 (a)
        - 1270-04-27/05-28 (b)
        - 1270-04-27 / 05-28 (c)

        - 1466 [04/05] (a)
        - 1466 [04 / 05] (b)
        - 1466-04 [28/29] (c)
        - 1466-04 [28 / 29] (a)
        - 1466 [04-28/05-01] (b)
        - 1466 [04-28 / 05-01] (c)

        - 1506-05 bzw. 11 (a)
        - 1506-05-12 bzw. 10 (b)
        - 1506-05-12 bzw. 11-10 (c)
        - 1506-05 bzw. 11 bzw. 12 (a)
        - 1506-05-12 bzw. 10 bzw. 01 (b)
        - 1506-05-12 bzw. 11-10 bzw. 12-01 (c)

        - 1343-04 oder 05 (a)
        - 1343-04-12 oder 19 (b)
        - 1343-04-12 oder 05-19 (c)
        '''
        self.__create_and_check_dates(
            '1270-04/05 (a)', self.RegestDate(
                date(1270, 04, 01), date(1270, 04, 01), '', '', False),
            self.RegestDate(
                date(1270, 05, 01), date(1270, 05, 01), '', '', True))
        self.__create_and_check_dates(
            '1270-04 / 05 (b)', self.RegestDate(
                date(1270, 04, 01), date(1270, 04, 01), '', '', False),
            self.RegestDate(
                date(1270, 05, 01), date(1270, 05, 01), '', '', True))
        self.__create_and_check_dates(
            '1440-11-12/17 (c)', self.RegestDate(
                date(1440, 11, 12), date(1440, 11, 12), '', '', False),
            self.RegestDate(
                date(1440, 11, 17), date(1440, 11, 17), '', '', True))
        self.__create_and_check_dates(
            '1440-11-12 / 17 (a)', self.RegestDate(
                date(1440, 11, 12), date(1440, 11, 12), '', '', False),
            self.RegestDate(
                date(1440, 11, 17), date(1440, 11, 17), '', '', True))
        self.__create_and_check_dates(
            '1270-04-27/05-28 (b)', self.RegestDate(
                date(1270, 04, 27), date(1270, 04, 27), '', '', False),
            self.RegestDate(
                date(1270, 05, 28), date(1270, 05, 28), '', '', True))
        self.__create_and_check_dates(
            '1270-04-27 / 05-28 (c)', self.RegestDate(
                date(1270, 04, 27), date(1270, 04, 27), '', '', False),
            self.RegestDate(
                date(1270, 05, 28), date(1270, 05, 28), '', '', True))
        self.__create_and_check_dates(
            '1466 [04/05] (a)', self.RegestDate(
                date(1466, 04, 01), date(1466, 04, 01), '', '', False),
            self.RegestDate(
                date(1466, 05, 01), date(1466, 05, 01), '', '', True))
        self.__create_and_check_dates(
            '1466 [04 / 05] (b)', self.RegestDate(
                date(1466, 04, 01), date(1466, 04, 01), '', '', False),
            self.RegestDate(
                date(1466, 05, 01), date(1466, 05, 01), '', '', True))
        self.__create_and_check_dates(
            '1466-04 [28/29] (c)', self.RegestDate(
                date(1466, 04, 28), date(1466, 04, 28), '', '', False),
            self.RegestDate(
                date(1466, 04, 29), date(1466, 04, 29), '', '', True))
        self.__create_and_check_dates(
            '1466-04 [28 / 29] (a)', self.RegestDate(
                date(1466, 04, 28), date(1466, 04, 28), '', '', False),
            self.RegestDate(
                date(1466, 04, 29), date(1466, 04, 29), '', '', True))
        self.__create_and_check_dates(
            '1466 [04-28/05-01] (b)', self.RegestDate(
                date(1466, 04, 28), date(1466, 04, 28), '', '', False),
            self.RegestDate(
                date(1466, 05, 01), date(1466, 05, 01), '', '', True))
        self.__create_and_check_dates(
            '1466 [04-28/05-01] (c)', self.RegestDate(
                date(1466, 04, 28), date(1466, 04, 28), '', '', False),
            self.RegestDate(
                date(1466, 05, 01), date(1466, 05, 01), '', '', True))
        self.__create_and_check_dates(
            '1506-05 bzw. 11 (a)', self.RegestDate(
                date(1506, 05, 01), date(1506, 05, 01), '', '', False),
            self.RegestDate(
                date(1506, 11, 01), date(1506, 11, 01), '', '', True))
        self.__create_and_check_dates(
            '1506-05-12 bzw. 10 (b)', self.RegestDate(
                date(1506, 05, 12), date(1506, 05, 12), '', '', False),
            self.RegestDate(
                date(1506, 05, 10), date(1506, 05, 10), '', '', True))
        self.__create_and_check_dates(
            '1506-05-12 bzw. 11-10 (c)', self.RegestDate(
                date(1506, 05, 12), date(1506, 05, 12), '', '', False),
            self.RegestDate(
                date(1506, 11, 10), date(1506, 11, 10), '', '', True))
        self.__create_and_check_dates(
            '1506-05 bzw. 11 bzw. 12 (a)', self.RegestDate(
                date(1506, 05, 01), date(1506, 05, 01), '', '', False),
            self.RegestDate(
                date(1506, 11, 01), date(1506, 11, 01), '', '', True),
            self.RegestDate(
                date(1506, 12, 01), date(1506, 12, 01), '', '', True))
        self.__create_and_check_dates(
            '1506-05-12 bzw. 10 bzw. 01 (b)', self.RegestDate(
                date(1506, 05, 12), date(1506, 05, 12), '', '', False),
            self.RegestDate(
                date(1506, 05, 10), date(1506, 05, 10), '', '', True),
            self.RegestDate(
                date(1506, 05, 01), date(1506, 05, 01), '', '', True))
        self.__create_and_check_dates(
            '1506-05-12 bzw. 11-10 bzw. 12-01 (c)', self.RegestDate(
                date(1506, 05, 12), date(1506, 05, 12), '', '', False),
            self.RegestDate(
                date(1506, 11, 10), date(1506, 11, 10), '', '', True),
            self.RegestDate(
                date(1506, 12, 01), date(1506, 12, 01), '', '', True))
        self.__create_and_check_dates(
            '1343-04 oder 05 (a)', self.RegestDate(
                date(1343, 04, 01), date(1343, 04, 01), '', '', False),
            self.RegestDate(
                date(1343, 05, 01), date(1343, 05, 01), '', '', True))
        self.__create_and_check_dates(
            '1343-04-12 oder 19 (b)', self.RegestDate(
                date(1343, 04, 12), date(1343, 04, 12), '', '', False),
            self.RegestDate(
                date(1343, 04, 19), date(1343, 04, 19), '', '', True))
        self.__create_and_check_dates(
            '1343-04-12 oder 05-19 (c)', self.RegestDate(
                date(1343, 04, 12), date(1343, 04, 12), '', '', False),
            self.RegestDate(
                date(1343, 05, 19), date(1343, 05, 19), '', '', True))

    def test_elliptical_alternatives_with_duplicates_and_location(self):
        '''
        Examples:
        - 1270-04/05 (a) Diedenhofen
        - 1270-04 / 05 (b) Frankfurt am Main
        - 1440-11-12/17 (c) St. Arnual
        - 1440-11-12 / 17 (a) Diedenhofen
        - 1270-04-27/05-28 (b) Frankfurt am Main
        - 1270-04-27 / 05-28 (c) St. Arnual

        - 1466 [04/05] (a) Diedenhofen
        - 1466 [04 / 05] (b) Frankfurt am Main
        - 1466-04 [28/29] (c) St. Arnual
        - 1466-04 [28 / 29] (a) Diedenhofen
        - 1466 [04-28/05-01] (b) Frankfurt am Main
        - 1466 [04-28 / 05-01] (c) St. Arnual

        - 1506-05 bzw. 11 (a) Diedenhofen
        - 1506-05-12 bzw. 10 (b) Frankfurt am Main
        - 1506-05-12 bzw. 11-10 (c) St. Arnual
        - 1506-05 bzw. 11 bzw. 12 (a) Diedenhofen
        - 1506-05-12 bzw. 10 bzw. 01 (b) Frankfurt am Main
        - 1506-05-12 bzw. 11-10 bzw. 12-01 (c) St. Arnual

        - 1343-04 oder 05 (a) Diedenhofen
        - 1343-04-12 oder 19 (b) Frankfurt am Main
        - 1343-04-12 oder 05-19 (c) St. Arnual
        '''
        self.__create_and_check_dates(
            '1270-04/05 (a) Diedenhofen', self.RegestDate(
                date(1270, 04, 01), date(1270, 04, 01), '', '', False),
            self.RegestDate(
                date(1270, 05, 01), date(1270, 05, 01), '', '', True))
        self.__create_and_check_dates(
            '1270-04 / 05 (b) Frankfurt am Main', self.RegestDate(
                date(1270, 04, 01), date(1270, 04, 01), '', '', False),
            self.RegestDate(
                date(1270, 05, 01), date(1270, 05, 01), '', '', True))
        self.__create_and_check_dates(
            '1440-11-12/17 (c) St. Arnual', self.RegestDate(
                date(1440, 11, 12), date(1440, 11, 12), '', '', False),
            self.RegestDate(
                date(1440, 11, 17), date(1440, 11, 17), '', '', True))
        self.__create_and_check_dates(
            '1440-11-12 / 17 (a) Diedenhofen', self.RegestDate(
                date(1440, 11, 12), date(1440, 11, 12), '', '', False),
            self.RegestDate(
                date(1440, 11, 17), date(1440, 11, 17), '', '', True))
        self.__create_and_check_dates(
            '1270-04-27/05-28 (b) Frankfurt am Main', self.RegestDate(
                date(1270, 04, 27), date(1270, 04, 27), '', '', False),
            self.RegestDate(
                date(1270, 05, 28), date(1270, 05, 28), '', '', True))
        self.__create_and_check_dates(
            '1270-04-27 / 05-28 (c) St. Arnual', self.RegestDate(
                date(1270, 04, 27), date(1270, 04, 27), '', '', False),
            self.RegestDate(
                date(1270, 05, 28), date(1270, 05, 28), '', '', True))
        self.__create_and_check_dates(
            '1466 [04/05] (a) Diedenhofen', self.RegestDate(
                date(1466, 04, 01), date(1466, 04, 01), '', '', False),
            self.RegestDate(
                date(1466, 05, 01), date(1466, 05, 01), '', '', True))
        self.__create_and_check_dates(
            '1466 [04 / 05] (b) Frankfurt am Main', self.RegestDate(
                date(1466, 04, 01), date(1466, 04, 01), '', '', False),
            self.RegestDate(
                date(1466, 05, 01), date(1466, 05, 01), '', '', True))
        self.__create_and_check_dates(
            '1466-04 [28/29] (c) St. Arnual', self.RegestDate(
                date(1466, 04, 28), date(1466, 04, 28), '', '', False),
            self.RegestDate(
                date(1466, 04, 29), date(1466, 04, 29), '', '', True))
        self.__create_and_check_dates(
            '1466-04 [28 / 29] (a) Diedenhofen', self.RegestDate(
                date(1466, 04, 28), date(1466, 04, 28), '', '', False),
            self.RegestDate(
                date(1466, 04, 29), date(1466, 04, 29), '', '', True))
        self.__create_and_check_dates(
            '1466 [04-28/05-01] (b) Frankfurt am Main', self.RegestDate(
                date(1466, 04, 28), date(1466, 04, 28), '', '', False),
            self.RegestDate(
                date(1466, 05, 01), date(1466, 05, 01), '', '', True))
        self.__create_and_check_dates(
            '1466 [04-28/05-01] (c) St. Arnual', self.RegestDate(
                date(1466, 04, 28), date(1466, 04, 28), '', '', False),
            self.RegestDate(
                date(1466, 05, 01), date(1466, 05, 01), '', '', True))
        self.__create_and_check_dates(
            '1506-05 bzw. 11 (a) Diedenhofen', self.RegestDate(
                date(1506, 05, 01), date(1506, 05, 01), '', '', False),
            self.RegestDate(
                date(1506, 11, 01), date(1506, 11, 01), '', '', True))
        self.__create_and_check_dates(
            '1506-05-12 bzw. 10 (b) Frankfurt am Main', self.RegestDate(
                date(1506, 05, 12), date(1506, 05, 12), '', '', False),
            self.RegestDate(
                date(1506, 05, 10), date(1506, 05, 10), '', '', True))
        self.__create_and_check_dates(
            '1506-05-12 bzw. 11-10 (c) St. Arnual', self.RegestDate(
                date(1506, 05, 12), date(1506, 05, 12), '', '', False),
            self.RegestDate(
                date(1506, 11, 10), date(1506, 11, 10), '', '', True))
        self.__create_and_check_dates(
            '1506-05 bzw. 11 bzw. 12 (a) Diedenhofen', self.RegestDate(
                date(1506, 05, 01), date(1506, 05, 01), '', '', False),
            self.RegestDate(
                date(1506, 11, 01), date(1506, 11, 01), '', '', True),
            self.RegestDate(
                date(1506, 12, 01), date(1506, 12, 01), '', '', True))
        self.__create_and_check_dates(
            '1506-05-12 bzw. 10 bzw. 01 (b) Frankfurt am Main',
            self.RegestDate(
                date(1506, 05, 12), date(1506, 05, 12), '', '', False),
            self.RegestDate(
                date(1506, 05, 10), date(1506, 05, 10), '', '', True),
            self.RegestDate(
                date(1506, 05, 01), date(1506, 05, 01), '', '', True))
        self.__create_and_check_dates(
            '1506-05-12 bzw. 11-10 bzw. 12-01 (c) St. Arnual',
            self.RegestDate(
                date(1506, 05, 12), date(1506, 05, 12), '', '', False),
            self.RegestDate(
                date(1506, 11, 10), date(1506, 11, 10), '', '', True),
                self.RegestDate(
                    date(1506, 12, 01), date(1506, 12, 01), '', '', True))
        self.__create_and_check_dates(
            '1343-04 oder 05 (a) Diedenhofen', self.RegestDate(
                date(1343, 04, 01), date(1343, 04, 01), '', '', False),
            self.RegestDate(
                date(1343, 05, 01), date(1343, 05, 01), '', '', True))
        self.__create_and_check_dates(
            '1343-04-12 oder 19 (b) Frankfurt am Main', self.RegestDate(
                date(1343, 04, 12), date(1343, 04, 12), '', '', False),
            self.RegestDate(
                date(1343, 04, 19), date(1343, 04, 19), '', '', True))
        self.__create_and_check_dates(
            '1343-04-12 oder 05-19 (c) St. Arnual', self.RegestDate(
                date(1343, 04, 12), date(1343, 04, 12), '', '', False),
            self.RegestDate(
                date(1343, 05, 19), date(1343, 05, 19), '', '', True))

    def test_elliptical_alternatives_with_offset(self):
        '''
        Examples:
        - 1270-04/05 (vor)
        - 1270-04 / 05 (nach)
        - 1440-11-12/17 (um)
        - 1440-11-12 / 17 (ca.)
        - 1270-04-27/05-28 (kurz nach)
        - 1270-04-27 / 05-28 (post)

        - 1466 [04/05] (vor)
        - 1466 [04 / 05] (nach)
        - 1466-04 [28/29] (um)
        - 1466-04 [28 / 29] (ca.)
        - 1466 [04-28/05-01] (kurz nach)
        - 1466 [04-28 / 05-01] (post)

        - 1506-05 bzw. 11 (vor)
        - 1506-05-12 bzw. 10 (nach)
        - 1506-05-12 bzw. 11-10 (um)
        - 1506-05 bzw. 11 bzw. 12 (ca.)
        - 1506-05-12 bzw. 10 bzw. 01 (kurz nach)
        - 1506-05-12 bzw. 11-10 bzw. 12-01 (post)

        - 1343-04 oder 05 (um)
        - 1343-04-12 oder 19 (ca.)
        - 1343-04-12 oder 05-19 (kurz nach)
        '''
        self.__create_and_check_dates(
            '1270-04/05 (vor)', self.RegestDate(
                date(1270, 04, 01), date(1270, 04, 01), 'vor', 'vor', False),
            self.RegestDate(
                date(1270, 05, 01), date(1270, 05, 01), 'vor', 'vor', True))
        self.__create_and_check_dates(
            '1270-04 / 05 (nach)', self.RegestDate(
                date(1270, 04, 01), date(1270, 04, 01),
                'nach', 'nach', False),
            self.RegestDate(
                date(1270, 05, 01), date(1270, 05, 01), 'nach', 'nach', True))
        self.__create_and_check_dates(
            '1440-11-12/17 (um)', self.RegestDate(
                date(1440, 11, 12), date(1440, 11, 12), 'um', 'um', False),
            self.RegestDate(
                date(1440, 11, 17), date(1440, 11, 17), 'um', 'um', True))
        self.__create_and_check_dates(
            '1440-11-12 / 17 (ca.)', self.RegestDate(
                date(1440, 11, 12), date(1440, 11, 12), 'ca.', 'ca.', False),
            self.RegestDate(
                date(1440, 11, 17), date(1440, 11, 17), 'ca.', 'ca.', True))
        self.__create_and_check_dates(
            '1270-04-27/05-28 (kurz nach)', self.RegestDate(
                date(1270, 04, 27), date(1270, 04, 27),
                'kurz nach', 'kurz nach', False),
            self.RegestDate(
                date(1270, 05, 28), date(1270, 05, 28),
                'kurz nach', 'kurz nach', True))
        self.__create_and_check_dates(
            '1270-04-27 / 05-28 (post)', self.RegestDate(
                date(1270, 04, 27), date(1270, 04, 27),
                'post', 'post', False),
            self.RegestDate(
                date(1270, 05, 28), date(1270, 05, 28), 'post', 'post', True))
        self.__create_and_check_dates(
            '1466 [04/05] (vor)', self.RegestDate(
                date(1466, 04, 01), date(1466, 04, 01), 'vor', 'vor', False),
            self.RegestDate(
                date(1466, 05, 01), date(1466, 05, 01), 'vor', 'vor', True))
        self.__create_and_check_dates(
            '1466 [04 / 05] (nach)', self.RegestDate(
                date(1466, 04, 01), date(1466, 04, 01),
                'nach', 'nach', False),
            self.RegestDate(
                date(1466, 05, 01), date(1466, 05, 01), 'nach', 'nach', True))
        self.__create_and_check_dates(
            '1466-04 [28/29] (um)', self.RegestDate(
                date(1466, 04, 28), date(1466, 04, 28), 'um', 'um', False),
            self.RegestDate(
                date(1466, 04, 29), date(1466, 04, 29), 'um', 'um', True))
        self.__create_and_check_dates(
            '1466-04 [28 / 29] (ca.)', self.RegestDate(
                date(1466, 04, 28), date(1466, 04, 28), 'ca.', 'ca.', False),
            self.RegestDate(
                date(1466, 04, 29), date(1466, 04, 29), 'ca.', 'ca.', True))
        self.__create_and_check_dates(
            '1466 [04-28/05-01] (kurz nach)', self.RegestDate(
                date(1466, 04, 28), date(1466, 04, 28),
                'kurz nach', 'kurz nach', False),
            self.RegestDate(
                date(1466, 05, 01), date(1466, 05, 01),
                'kurz nach', 'kurz nach', True))
        self.__create_and_check_dates(
            '1466 [04-28/05-01] (post)', self.RegestDate(
                date(1466, 04, 28), date(1466, 04, 28),
                'post', 'post', False),
            self.RegestDate(
                date(1466, 05, 01), date(1466, 05, 01), 'post', 'post', True))
        self.__create_and_check_dates(
            '1506-05 bzw. 11 (vor)', self.RegestDate(
                date(1506, 05, 01), date(1506, 05, 01), 'vor', 'vor', False),
            self.RegestDate(
                date(1506, 11, 01), date(1506, 11, 01), 'vor', 'vor', True))
        self.__create_and_check_dates(
            '1506-05-12 bzw. 10 (nach)', self.RegestDate(
                date(1506, 05, 12), date(1506, 05, 12),
                'nach', 'nach', False),
            self.RegestDate(
                date(1506, 05, 10), date(1506, 05, 10), 'nach', 'nach', True))
        self.__create_and_check_dates(
            '1506-05-12 bzw. 11-10 (um)', self.RegestDate(
                date(1506, 05, 12), date(1506, 05, 12), 'um', 'um', False),
            self.RegestDate(
                date(1506, 11, 10), date(1506, 11, 10), 'um', 'um', True))
        self.__create_and_check_dates(
            '1506-05 bzw. 11 bzw. 12 (ca.)', self.RegestDate(
                date(1506, 05, 01), date(1506, 05, 01), 'ca.', 'ca.', False),
            self.RegestDate(
                date(1506, 11, 01), date(1506, 11, 01), 'ca.', 'ca.', True),
            self.RegestDate(
                date(1506, 12, 01), date(1506, 12, 01), 'ca.', 'ca.', True))
        self.__create_and_check_dates(
            '1506-05-12 bzw. 10 bzw. 01 (kurz nach)', self.RegestDate(
                date(1506, 05, 12), date(1506, 05, 12),
                'kurz nach', 'kurz nach', False),
            self.RegestDate(
                date(1506, 05, 10), date(1506, 05, 10),
                'kurz nach', 'kurz nach', True),
            self.RegestDate(
                date(1506, 05, 01), date(1506, 05, 01),
                'kurz nach', 'kurz nach', True))
        self.__create_and_check_dates(
            '1506-05-12 bzw. 11-10 bzw. 12-01 (post)', self.RegestDate(
                date(1506, 05, 12), date(1506, 05, 12),
                'post', 'post', False),
            self.RegestDate(
                date(1506, 11, 10), date(1506, 11, 10), 'post', 'post', True),
            self.RegestDate(
                date(1506, 12, 01), date(1506, 12, 01), 'post', 'post', True))
        self.__create_and_check_dates(
            '1343-04 oder 05 (um)', self.RegestDate(
                date(1343, 04, 01), date(1343, 04, 01), 'um', 'um', False),
            self.RegestDate(
                date(1343, 05, 01), date(1343, 05, 01), 'um', 'um', True))
        self.__create_and_check_dates(
            '1343-04-12 oder 19 (ca.)', self.RegestDate(
                date(1343, 04, 12), date(1343, 04, 12), 'ca.', 'ca.', False),
            self.RegestDate(
                date(1343, 04, 19), date(1343, 04, 19), 'ca.', 'ca.', True))
        self.__create_and_check_dates(
            '1343-04-12 oder 05-19 (kurz nach)', self.RegestDate(
                date(1343, 04, 12), date(1343, 04, 12),
                'kurz nach', 'kurz nach', False),
            self.RegestDate(
                date(1343, 05, 19), date(1343, 05, 19),
                'kurz nach', 'kurz nach', True))

    def test_simple_additions(self):
        '''
        Examples:
        - 1524 und 1525
        - 1419-05 und 1419-06
        - 1421-10-05 und 1422-10-04
        '''
        self.__create_and_check_dates(
            '1524 und 1525', self.RegestDate(
                date(1524, 01, 01), date(1524, 01, 01), '', '', False),
            self.RegestDate(
                date(1525, 01, 01), date(1525, 01, 01), '', '', False))
        self.__create_and_check_dates(
            '1419-05 und 1419-06', self.RegestDate(
                date(1419, 05, 01), date(1419, 05, 01), '', '', False),
            self.RegestDate(
                date(1419, 06, 01), date(1419, 06, 01), '', '', False))
        self.__create_and_check_dates(
            '1421-10-05 und 1422-10-04', self.RegestDate(
                date(1421, 10, 05), date(1421, 10, 05), '', '', False),
            self.RegestDate(
                date(1422, 10, 04), date(1422, 10, 04), '', '', False))

    def test_simple_additions_with_location(self):
        '''
        Examples:
        - 1524 und 1525 Diedenhofen
        - 1419-05 und 1419-06 Frankfurt am Main
        - 1421-10-05 und 1422-10-04 St. Arnual
        '''
        self.__create_and_check_dates(
            '1524 und 1525 Diedenhofen', self.RegestDate(
                date(1524, 01, 01), date(1524, 01, 01), '', '', False),
            self.RegestDate(
                date(1525, 01, 01), date(1525, 01, 01), '', '', False))
        self.__create_and_check_dates(
            '1419-05 und 1419-06 Frankfurt am Main', self.RegestDate(
                date(1419, 05, 01), date(1419, 05, 01), '', '', False),
            self.RegestDate(
                date(1419, 06, 01), date(1419, 06, 01), '', '', False))
        self.__create_and_check_dates(
            '1421-10-05 und 1422-10-04 St. Arnual', self.RegestDate(
                date(1421, 10, 05), date(1421, 10, 05), '', '', False),
            self.RegestDate(
                date(1422, 10, 04), date(1422, 10, 04), '', '', False))

    def test_simple_additions_with_duplicates(self):
        '''
        Examples:
        - 1524 und 1525 (a)
        - 1419-05 und 1419-06 (b)
        - 1421-10-05 und 1422-10-04 (c)
        '''
        self.__create_and_check_dates(
            '1524 und 1525 (a)', self.RegestDate(
                date(1524, 01, 01), date(1524, 01, 01), '', '', False),
            self.RegestDate(
                date(1525, 01, 01), date(1525, 01, 01), '', '', False))
        self.__create_and_check_dates(
            '1419-05 und 1419-06 (b)', self.RegestDate(
                date(1419, 05, 01), date(1419, 05, 01), '', '', False),
            self.RegestDate(
                date(1419, 06, 01), date(1419, 06, 01), '', '', False))
        self.__create_and_check_dates(
            '1421-10-05 und 1422-10-04 (c)', self.RegestDate(
                date(1421, 10, 05), date(1421, 10, 05), '', '', False),
            self.RegestDate(
                date(1422, 10, 04), date(1422, 10, 04), '', '', False))

    def test_simple_additions_with_duplicates_and_location(self):
        '''
        Examples:
        - 1524 und 1525 (a) Diedenhofen
        - 1419-05 und 1419-06 (b) Frankfurt am Main
        - 1421-10-05 und 1422-10-04 (c) St. Arnual
        '''
        self.__create_and_check_dates(
            '1524 und 1525 (a) Diedenhofen', self.RegestDate(
                date(1524, 01, 01), date(1524, 01, 01), '', '', False),
            self.RegestDate(
                date(1525, 01, 01), date(1525, 01, 01), '', '', False))
        self.__create_and_check_dates(
            '1419-05 und 1419-06 (b) Frankfurt am Main', self.RegestDate(
                date(1419, 05, 01), date(1419, 05, 01), '', '', False),
            self.RegestDate(
                date(1419, 06, 01), date(1419, 06, 01), '', '', False))
        self.__create_and_check_dates(
            '1421-10-05 und 1422-10-04 (c) St. Arnual', self.RegestDate(
                date(1421, 10, 05), date(1421, 10, 05), '', '', False),
            self.RegestDate(
                date(1422, 10, 04), date(1422, 10, 04), '', '', False))

    def test_simple_additions_with_offset(self):
        '''
        Examples:
        - 1524 und 1525 (um)
        - 1419-05 und 1419-06 (ca.)
        - 1421-10-05 und 1422-10-04 (kurz nach)
        '''
        self.__create_and_check_dates(
            '1524 und 1525 (um)', self.RegestDate(
                date(1524, 01, 01), date(1524, 01, 01), 'um', 'um', False),
            self.RegestDate(
                date(1525, 01, 01), date(1525, 01, 01), 'um', 'um', False))
        self.__create_and_check_dates(
            '1419-05 und 1419-06 (ca.)', self.RegestDate(
                date(1419, 05, 01), date(1419, 05, 01), 'ca.', 'ca.', False),
            self.RegestDate(
                date(1419, 06, 01), date(1419, 06, 01), 'ca.', 'ca.', False))
        self.__create_and_check_dates(
            '1421-10-05 und 1422-10-04 (kurz nach)', self.RegestDate(
                date(1421, 10, 05), date(1421, 10, 05),
                'kurz nach', 'kurz nach', False),
            self.RegestDate(
                date(1422, 10, 04), date(1422, 10, 04),
                'kurz nach', 'kurz nach', False))

    def test_elliptical_additions(self):
        '''
        Examples:
        - 1270-04 und 05 (month different, no day)
        - 1440-11-12 und 17 (day different)
        - 1270-04-27 und 05-28 (month *and* day different)
        '''
        self.__create_and_check_dates(
            '1270-04 und 05', self.RegestDate(
                date(1270, 04, 01), date(1270, 04, 01), '', '', False),
            self.RegestDate(
                date(1270, 05, 01), date(1270, 05, 01), '', '', False))
        self.__create_and_check_dates(
            '1440-11-12 und 17', self.RegestDate(
                date(1440, 11, 12), date(1440, 11, 12), '', '', False),
            self.RegestDate(
                date(1440, 11, 17), date(1440, 11, 17), '', '', False))
        self.__create_and_check_dates(
            '1270-04-27 und 05-28', self.RegestDate(
                date(1270, 04, 27), date(1270, 04, 27), '', '', False),
            self.RegestDate(
                date(1270, 05, 28), date(1270, 05, 28), '', '', False))

    def test_elliptical_additions_with_location(self):
        '''
        Examples:
        - 1270-04 und 05 Diedenhofen
        - 1440-11-12 und 17 Frankfurt am Main
        - 1270-04-27 und 05-28 St. Arnual
        '''
        self.__create_and_check_dates(
            '1270-04 und 05 Diedenhofen', self.RegestDate(
                date(1270, 04, 01), date(1270, 04, 01), '', '', False),
            self.RegestDate(
                date(1270, 05, 01), date(1270, 05, 01), '', '', False))
        self.__create_and_check_dates(
            '1440-11-12 und 17 Frankfurt am Main', self.RegestDate(
                date(1440, 11, 12), date(1440, 11, 12), '', '', False),
            self.RegestDate(
                date(1440, 11, 17), date(1440, 11, 17), '', '', False))
        self.__create_and_check_dates(
            '1270-04-27 und 05-28 St. Arnual', self.RegestDate(
                date(1270, 04, 27), date(1270, 04, 27), '', '', False),
            self.RegestDate(
                date(1270, 05, 28), date(1270, 05, 28), '', '', False))

    def test_elliptical_additions_with_duplicates(self):
        '''
        Examples:
        - 1270-04 und 05 (a)
        - 1440-11-12 und 17 (b)
        - 1270-04-27 und 05-28 (c)
        '''
        self.__create_and_check_dates(
            '1270-04 und 05 (a)', self.RegestDate(
                date(1270, 04, 01), date(1270, 04, 01), '', '', False),
            self.RegestDate(
                date(1270, 05, 01), date(1270, 05, 01), '', '', False))
        self.__create_and_check_dates(
            '1440-11-12 und 17 (b)', self.RegestDate(
                date(1440, 11, 12), date(1440, 11, 12), '', '', False),
            self.RegestDate(
                date(1440, 11, 17), date(1440, 11, 17), '', '', False))
        self.__create_and_check_dates(
            '1270-04-27 und 05-28 (c)', self.RegestDate(
                date(1270, 04, 27), date(1270, 04, 27), '', '', False),
            self.RegestDate(
                date(1270, 05, 28), date(1270, 05, 28), '', '', False))

    def test_elliptical_additions_with_duplicates_and_location(self):
        '''
        Examples:
        - 1270-04 und 05 (a) Diedenhofen
        - 1440-11-12 und 17 (b) Frankfurt am Main
        - 1270-04-27 und 05-28 (c) St. Arnual
        '''
        self.__create_and_check_dates(
            '1270-04 und 05 (a) Diedenhofen', self.RegestDate(
                date(1270, 04, 01), date(1270, 04, 01), '', '', False),
            self.RegestDate(
                date(1270, 05, 01), date(1270, 05, 01), '', '', False))
        self.__create_and_check_dates(
            '1440-11-12 und 17 (b) Frankfurt am Main', self.RegestDate(
                date(1440, 11, 12), date(1440, 11, 12), '', '', False),
            self.RegestDate(
                date(1440, 11, 17), date(1440, 11, 17), '', '', False))
        self.__create_and_check_dates(
            '1270-04-27 und 05-28 (c) St. Arnual', self.RegestDate(
                date(1270, 04, 27), date(1270, 04, 27), '', '', False),
            self.RegestDate(
                date(1270, 05, 28), date(1270, 05, 28), '', '', False))

    def test_elliptical_additions_with_offset(self):
        '''
        Examples:
        - 1270-04 und 05 (um)
        - 1440-11-12 und 17 (ca.)
        - 1270-04-27 und 05-28 (kurz nach)
        '''
        self.__create_and_check_dates(
            '1270-04 und 05 (um)', self.RegestDate(
                date(1270, 04, 01), date(1270, 04, 01), 'um', 'um', False),
            self.RegestDate(
                date(1270, 05, 01), date(1270, 05, 01), 'um', 'um', False))
        self.__create_and_check_dates(
            '1440-11-12 und 17 (ca.)', self.RegestDate(
                date(1440, 11, 12), date(1440, 11, 12), 'ca.', 'ca.', False),
            self.RegestDate(
                date(1440, 11, 17), date(1440, 11, 17), 'ca.', 'ca.', False))
        self.__create_and_check_dates(
            '1270-04-27 und 05-28 (kurz nach)', self.RegestDate(
                date(1270, 04, 27), date(1270, 04, 27),
                'kurz nach', 'kurz nach', False),
            self.RegestDate(
                date(1270, 05, 28), date(1270, 05, 28),
                'kurz nach', 'kurz nach', False))
