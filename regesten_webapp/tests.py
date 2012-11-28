"""
This module provides tests for non-trivial methods of the model layer.

They can be run via

python manage.py test regesten_webapp
"""

from datetime import date
from django.test import TestCase
from regesten_webapp.models import Regest


class RegestTest(TestCase):
    def __check_date(
        self, regest, start, end, start_offset, end_offset):
        regest_date = regest.regestdate_set.get(
            regest=regest, start=start, end=end,
            start_offset=start_offset, end_offset=end_offset)
        self.assertEqual(regest_date.start, start)
        self.assertEqual(regest_date.end, end)
        self.assertEqual(regest_date.start_offset, start_offset)
        self.assertEqual(regest_date.end_offset, end_offset)

    def test_regular_dates(self):
        '''
        Tests whether or not *regular dates* are extracted correctly
        from the title of a given regest.

        Regular dates include:
        - 1009 (year only)
        - 1009-10 (year and month)
        - 1009-10-20 (year, month, and day)
        '''
        regest = Regest.objects.create(title='1009')
        self.__check_date(
            regest, start=date(1009, 01, 01), end=date(1009, 01, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(title='1009-10')
        self.__check_date(
            regest, start=date(1009, 10, 01), end=date(1009, 10, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(title='1009-10-20')
        self.__check_date(
            regest, start=date(1009, 10, 20), end=date(1009, 10, 20),
            start_offset='', end_offset='')

    def test_regular_dates_with_location(self):
        '''
        Tests whether or not regular dates are extracted correctly
        from titles that include a location.

        Examples:
        - 1009 Diedenhofen
        - 1009-10 Frankfurt am Main
        - 1009-10-20 St. Arnual
        '''
        regest = Regest.objects.create(title='1009 Diedenhofen')
        self.__check_date(
            regest, start=date(1009, 01, 01), end=date(1009, 01, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(title='1009-10 Frankfurt am Main')
        self.__check_date(
            regest, start=date(1009, 10, 01), end=date(1009, 10, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(title='1009-10-20 St. Arnual')
        self.__check_date(
            regest, start=date(1009, 10, 20), end=date(1009, 10, 20),
            start_offset='', end_offset='')

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
        regest = Regest.objects.create(title='1009 (vor)')
        self.__check_date(
            regest, start=date(1009, 01, 01), end=date(1009, 01, 01),
            start_offset='vor', end_offset='')
        regest = Regest.objects.create(title='1009-10 (nach)')
        self.__check_date(
            regest, start=date(1009, 10, 01), end=date(1009, 10, 01),
            start_offset='nach', end_offset='')
        regest = Regest.objects.create(title='1009-10-20 (ca.)')
        self.__check_date(
            regest, start=date(1009, 10, 20), end=date(1009, 10, 20),
            start_offset='ca.', end_offset='')
        regest = Regest.objects.create(title='1009 (?)')
        self.__check_date(
            regest, start=date(1009, 01, 01), end=date(1009, 01, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(title='1009-10 (?)')
        self.__check_date(
            regest, start=date(1009, 10, 01), end=date(1009, 10, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(title='1009-10-20 (?)')
        self.__check_date(
            regest, start=date(1009, 10, 20), end=date(1009, 10, 20),
            start_offset='', end_offset='')

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
        regest = Regest.objects.create(title='1009 (vor) Diedenhofen')
        self.__check_date(
            regest, start=date(1009, 01, 01), end=date(1009, 01, 01),
            start_offset='vor', end_offset='')
        regest = Regest.objects.create(
            title='1009-10 (nach) Frankfurt am Main')
        self.__check_date(
            regest, start=date(1009, 10, 01), end=date(1009, 10, 01),
            start_offset='nach', end_offset='')
        regest = Regest.objects.create(title='1009-10-20 (um) St. Arnual')
        self.__check_date(
            regest, start=date(1009, 10, 20), end=date(1009, 10, 20),
            start_offset='um', end_offset='')
        regest = Regest.objects.create(title='1009 Diedenhofen (kurz nach)')
        self.__check_date(
            regest, start=date(1009, 01, 01), end=date(1009, 01, 01),
            start_offset='kurz nach', end_offset='')
        regest = Regest.objects.create(
            title='1009-10 Frankfurt am Main (post)')
        self.__check_date(
            regest, start=date(1009, 10, 01), end=date(1009, 10, 01),
            start_offset='post', end_offset='')
        regest = Regest.objects.create(title='1009-10-20 St. Arnual (ca.)')
        self.__check_date(
            regest, start=date(1009, 10, 20), end=date(1009, 10, 20),
            start_offset='ca.', end_offset='')

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
        regest = Regest.objects.create(title='1273 (a)')
        self.__check_date(
            regest, start=date(1273, 01, 01), end=date(1273, 01, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(title='1270-07 (b)')
        self.__check_date(
            regest, start=date(1270, 07, 01), end=date(1270, 07, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(title='1377-03-05 (c)')
        self.__check_date(
            regest, start=date(1377, 03, 05), end=date(1377, 03, 05),
            start_offset='', end_offset='')
        regest = Regest.objects.create(title='1424-06-03 (a) und (b)')
        self.__check_date(
            regest, start=date(1424, 06, 03), end=date(1424, 06, 03),
            start_offset='', end_offset='')

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
        regest = Regest.objects.create(title='1442 (a) Diedenhofen')
        self.__check_date(
            regest, start=date(1442, 01, 01), end=date(1442, 01, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(
            title='1270-07 (b) Frankfurt am Main')
        self.__check_date(
            regest, start=date(1270, 07, 01), end=date(1270, 07, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(title='1354-04-01 (c)')
        self.__check_date(
            regest, start=date(1354, 04, 01), end=date(1354, 04, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(title='1424-06-03 (a) und (b)')
        self.__check_date(
            regest, start=date(1424, 06, 03), end=date(1424, 06, 03),
            start_offset='', end_offset='')

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
        regest = Regest.objects.create(title='1200 (vor) (a)')
        self.__check_date(
            regest, start=date(1200, 01, 01), end=date(1200, 01, 01),
            start_offset='vor', end_offset='')
        regest = Regest.objects.create(title='1200 (a) (vor)')
        self.__check_date(
            regest, start=date(1200, 01, 01), end=date(1200, 01, 01),
            start_offset='vor', end_offset='')
        regest = Regest.objects.create(title='1200-03 (kurz nach) (b)')
        self.__check_date(
            regest, start=date(1200, 03, 01), end=date(1200, 03, 01),
            start_offset='kurz nach', end_offset='')
        regest = Regest.objects.create(title='1200-03 (b) (kurz nach)')
        self.__check_date(
            regest, start=date(1200, 03, 01), end=date(1200, 03, 01),
            start_offset='kurz nach', end_offset='')
        regest = Regest.objects.create(title='1200-03-12 (ca.) (c)')
        self.__check_date(
            regest, start=date(1200, 03, 12), end=date(1200, 03, 12),
            start_offset='ca.', end_offset='')
        regest = Regest.objects.create(title='1200-03-12 (c) (ca.)')
        self.__check_date(
            regest, start=date(1200, 03, 12), end=date(1200, 03, 12),
            start_offset='ca.', end_offset='')

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
        regest = Regest.objects.create(title='1024-1030')
        self.__check_date(
            regest, start=date(1024, 01, 01), end=date(1030, 01, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(title='1024 - 1030')
        self.__check_date(
            regest, start=date(1024, 01, 01), end=date(1030, 01, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(title='1419-05 - 1419-06')
        self.__check_date(
            regest, start=date(1419, 05, 01), end=date(1419, 06, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(title='1419-05 bis 06')
        self.__check_date(
            regest, start=date(1419, 05, 01), end=date(1419, 06, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(title='1484-07-16 - 1499-01-03')
        self.__check_date(
            regest, start=date(1484, 07, 16), end=date(1499, 01, 03),
            start_offset='', end_offset='')
        regest = Regest.objects.create(title='1419-05-10 bis 20')
        self.__check_date(
            regest, start=date(1419, 05, 10), end=date(1419, 05, 20),
            start_offset='', end_offset='')

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
        regest = Regest.objects.create(title='0935-1000 (ca.)')
        self.__check_date(
            regest, start=date(935, 01, 01), end=date(1000, 01, 01),
            start_offset='ca.', end_offset='ca.')
        regest = Regest.objects.create(title='1431 - 1459 (zwischen)')
        self.__check_date(
            regest, start=date(1431, 01, 01), end=date(1459, 01, 01),
            start_offset='nach', end_offset='vor')
        regest = Regest.objects.create(title='1419-05 - 1419-06 (um)')
        self.__check_date(
            regest, start=date(1419, 05, 01), end=date(1419, 06, 01),
            start_offset='um', end_offset='um')
        regest = Regest.objects.create(
            title='1419-05 (nach) - 1419-06 (vor)')
        self.__check_date(
            regest, start=date(1419, 05, 01), end=date(1419, 06, 01),
            start_offset='nach', end_offset='vor')
        regest = Regest.objects.create(title='1419-05 bis 06 (kurz nach)')
        self.__check_date(
            regest, start=date(1419, 05, 01), end=date(1419, 06, 01),
            start_offset='kurz nach', end_offset='kurz nach')
        regest = Regest.objects.create(
            title='1484-07-16 - 1499-01-03 (ca.)')
        self.__check_date(
            regest, start=date(1484, 07, 16), end=date(1499, 01, 03),
            start_offset='ca.', end_offset='ca.')
        regest = Regest.objects.create(
            title='1484-07-16 (nach) - 1499-01-03 (vor)')
        self.__check_date(
            regest, start=date(1484, 07, 16), end=date(1499, 01, 03),
            start_offset='nach', end_offset='vor')
        regest = Regest.objects.create(title='1419-05-10 bis 20 (ca.)')
        self.__check_date(
            regest, start=date(1419, 05, 10), end=date(1419, 05, 20),
            start_offset='ca.', end_offset='ca.')

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
        regest = Regest.objects.create(title='1460-1466 (a) ca.')
        self.__check_date(
            regest, start=date(1460, 01, 01), end=date(1466, 01, 01),
            start_offset='ca.', end_offset='ca.')
        regest = Regest.objects.create(title='1460-1466 (ca.) (b)')
        self.__check_date(
            regest, start=date(1460, 01, 01), end=date(1466, 01, 01),
            start_offset='ca.', end_offset='ca.')
        regest = Regest.objects.create(title='1460-1466 (c) (ca.)')
        self.__check_date(
            regest, start=date(1460, 01, 01), end=date(1466, 01, 01),
            start_offset='ca.', end_offset='ca.')
        regest = Regest.objects.create(title='1419-05 - 1419-06 (a) um')
        self.__check_date(
            regest, start=date(1419, 05, 01), end=date(1419, 06, 01),
            start_offset='um', end_offset='um')
        regest = Regest.objects.create(title='1419-05 - 1419-06 (um) (b)')
        self.__check_date(
            regest, start=date(1419, 05, 01), end=date(1419, 06, 01),
            start_offset='um', end_offset='um')
        regest = Regest.objects.create(title='1419-05 - 1419-06 (c) (um)')
        self.__check_date(
            regest, start=date(1419, 05, 01), end=date(1419, 06, 01),
            start_offset='um', end_offset='um')
        regest = Regest.objects.create(
            title='1419-05 bis 06 (a) kurz nach')
        self.__check_date(
            regest, start=date(1419, 05, 01), end=date(1419, 06, 01),
            start_offset='kurz nach', end_offset='kurz nach')
        regest = Regest.objects.create(
            title='1419-05 bis 06 (kurz nach) (b)')
        self.__check_date(
            regest, start=date(1419, 05, 01), end=date(1419, 06, 01),
            start_offset='kurz nach', end_offset='kurz nach')
        regest = Regest.objects.create(
            title='1419-05 bis 06 (c) (kurz nach)')
        self.__check_date(
            regest, start=date(1419, 05, 01), end=date(1419, 06, 01),
            start_offset='kurz nach', end_offset='kurz nach')
        regest = Regest.objects.create(
            title='1484-07-16 - 1499-01-03 (a) ca.')
        self.__check_date(
            regest, start=date(1484, 07, 16), end=date(1499, 01, 03),
            start_offset='ca.', end_offset='ca.')
        regest = Regest.objects.create(
            title='1484-07-16 - 1499-01-03 (ca.) (b)')
        self.__check_date(
            regest, start=date(1484, 07, 16), end=date(1499, 01, 03),
            start_offset='ca.', end_offset='ca.')
        regest = Regest.objects.create(
            title='1484-07-16 - 1499-01-03 (c) (ca.)')
        self.__check_date(
            regest, start=date(1484, 07, 16), end=date(1499, 01, 03),
            start_offset='ca.', end_offset='ca.')
        regest = Regest.objects.create(title='1419-05-10 bis 20 (a) ca.')
        self.__check_date(
            regest, start=date(1419, 05, 10), end=date(1419, 05, 20),
            start_offset='ca.', end_offset='ca.')
        regest = Regest.objects.create(title='1419-05-10 bis 20 (ca.) (b)')
        self.__check_date(
            regest, start=date(1419, 05, 10), end=date(1419, 05, 20),
            start_offset='ca.', end_offset='ca.')
        regest = Regest.objects.create(title='1419-05-10 bis 20 (c) (ca.)')
        self.__check_date(
            regest, start=date(1419, 05, 10), end=date(1419, 05, 20),
            start_offset='ca.', end_offset='ca.')
        regest = Regest.objects.create(
            title='1484-07-16 (nach) - 1499-01-03 (vor) (a)')
        self.__check_date(
            regest, start=date(1484, 07, 16), end=date(1499, 01, 03),
            start_offset='nach', end_offset='vor')

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
        '''
        regest = Regest.objects.create(title='1524/1525')
        self.__check_date(
            regest, start=date(1524, 01, 01), end=date(1524, 01, 01),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1525, 01, 01), end=date(1525, 01, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(
            title='1524 / 1525')
        self.__check_date(
            regest, start=date(1524, 01, 01), end=date(1524, 01, 01),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1525, 01, 01), end=date(1525, 01, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(
            title='1419-05/1419-06')
        self.__check_date(
            regest, start=date(1419, 05, 01), end=date(1419, 05, 01),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1419, 06, 01), end=date(1419, 06, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(
            title='1419-05 / 1419-06')
        self.__check_date(
            regest, start=date(1419, 05, 01), end=date(1419, 05, 01),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1419, 06, 01), end=date(1419, 06, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(
            title='1421-10-05/1422-10-04')
        self.__check_date(
            regest, start=date(1421, 10, 05), end=date(1421, 10, 05),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1422, 10, 04), end=date(1422, 10, 04),
            start_offset='', end_offset='')
        regest = Regest.objects.create(
            title='1421-10-05 / 1422-10-04')
        self.__check_date(
            regest, start=date(1421, 10, 05), end=date(1421, 10, 05),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1422, 10, 04), end=date(1422, 10, 04),
            start_offset='', end_offset='')
        regest = Regest.objects.create(
            title='1502 (1503)')
        self.__check_date(
            regest, start=date(1502, 01, 01), end=date(1502, 01, 01),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1503, 01, 01), end=date(1503, 01, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(
            title='1502-11 (1503-02)')
        self.__check_date(
            regest, start=date(1502, 11, 01), end=date(1502, 11, 01),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1503, 02, 01), end=date(1503, 02, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(
            title='1502-11-22 (1503-02-07)')
        self.__check_date(
            regest, start=date(1502, 11, 22), end=date(1502, 11, 22),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1503, 02, 07), end=date(1503, 02, 07),
            start_offset='', end_offset='')
        regest = Regest.objects.create(
            title='1520 [bzw. 1519]')
        self.__check_date(
            regest, start=date(1520, 01, 01), end=date(1520, 01, 01),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1519, 01, 01), end=date(1519, 01, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(
            title='1520-02 [bzw. 1519-03]')
        self.__check_date(
            regest, start=date(1520, 02, 01), end=date(1520, 02, 01),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1519, 03, 01), end=date(1519, 03, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(
            title='1520-02-18 [bzw. 1519-03-06]')
        self.__check_date(
            regest, start=date(1520, 02, 18), end=date(1520, 02, 18),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1519, 03, 06), end=date(1519, 03, 06),
            start_offset='', end_offset='')
        regest = Regest.objects.create(
            title='1520 bzw. 1519')
        self.__check_date(
            regest, start=date(1520, 01, 01), end=date(1520, 01, 01),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1519, 01, 01), end=date(1519, 01, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(
            title='1520-02 bzw. 1519-03')
        self.__check_date(
            regest, start=date(1520, 02, 01), end=date(1520, 02, 01),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1519, 03, 01), end=date(1519, 03, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(
            title='1520-02-18 bzw. 1519-03-06')
        self.__check_date(
            regest, start=date(1520, 02, 18), end=date(1520, 02, 18),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1519, 03, 06), end=date(1519, 03, 06),
            start_offset='', end_offset='')

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
        '''
        regest = Regest.objects.create(title='1524/1525 Diedenhofen')
        self.__check_date(
            regest, start=date(1524, 01, 01), end=date(1524, 01, 01),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1525, 01, 01), end=date(1525, 01, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(
            title='1524 / 1525 Frankfurt am Main')
        self.__check_date(
            regest, start=date(1524, 01, 01), end=date(1524, 01, 01),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1525, 01, 01), end=date(1525, 01, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(
            title='1419-05/1419-06 St. Arnual')
        self.__check_date(
            regest, start=date(1419, 05, 01), end=date(1419, 05, 01),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1419, 06, 01), end=date(1419, 06, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(
            title='1419-05 / 1419-06 Diedenhofen')
        self.__check_date(
            regest, start=date(1419, 05, 01), end=date(1419, 05, 01),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1419, 06, 01), end=date(1419, 06, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(
            title='1421-10-05/1422-10-04 Frankfurt am Main')
        self.__check_date(
            regest, start=date(1421, 10, 05), end=date(1421, 10, 05),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1422, 10, 04), end=date(1422, 10, 04),
            start_offset='', end_offset='')
        regest = Regest.objects.create(
            title='1421-10-05 / 1422-10-04 St. Arnual')
        self.__check_date(
            regest, start=date(1421, 10, 05), end=date(1421, 10, 05),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1422, 10, 04), end=date(1422, 10, 04),
            start_offset='', end_offset='')
        regest = Regest.objects.create(
            title='1502 (1503) Diedenhofen')
        self.__check_date(
            regest, start=date(1502, 01, 01), end=date(1502, 01, 01),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1503, 01, 01), end=date(1503, 01, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(
            title='1502-11 (1503-02) Frankfurt am Main')
        self.__check_date(
            regest, start=date(1502, 11, 01), end=date(1502, 11, 01),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1503, 02, 01), end=date(1503, 02, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(
            title='1502-11-22 (1503-02-07) St. Arnual')
        self.__check_date(
            regest, start=date(1502, 11, 22), end=date(1502, 11, 22),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1503, 02, 07), end=date(1503, 02, 07),
            start_offset='', end_offset='')
        regest = Regest.objects.create(
            title='1520 [bzw. 1519] Diedenhofen')
        self.__check_date(
            regest, start=date(1520, 01, 01), end=date(1520, 01, 01),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1519, 01, 01), end=date(1519, 01, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(
            title='1520-02 [bzw. 1519-03] Frankfurt am Main')
        self.__check_date(
            regest, start=date(1520, 02, 01), end=date(1520, 02, 01),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1519, 03, 01), end=date(1519, 03, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(
            title='1520-02-18 [bzw. 1519-03-06] St. Arnual')
        self.__check_date(
            regest, start=date(1520, 02, 18), end=date(1520, 02, 18),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1519, 03, 06), end=date(1519, 03, 06),
            start_offset='', end_offset='')
        regest = Regest.objects.create(
            title='1520 bzw. 1519 Diedenhofen')
        self.__check_date(
            regest, start=date(1520, 01, 01), end=date(1520, 01, 01),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1519, 01, 01), end=date(1519, 01, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(
            title='1520-02 bzw. 1519-03 Frankfurt am Main')
        self.__check_date(
            regest, start=date(1520, 02, 01), end=date(1520, 02, 01),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1519, 03, 01), end=date(1519, 03, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(
            title='1520-02-18 bzw. 1519-03-06 St. Arnual')
        self.__check_date(
            regest, start=date(1520, 02, 18), end=date(1520, 02, 18),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1519, 03, 06), end=date(1519, 03, 06),
            start_offset='', end_offset='')

    def test_elliptical_alternatives(self):
        '''
        Examples:
        - 1270-04-27/04-28
        - 1466 [04-28 / 05-01]
        - 1440-11-12/17
        - 1506-05-12 bzw. 11-10 bzw. 12-01
        - 1343-04-12 oder 19
        '''
        regest = Regest.objects.create(
            title='1270-04-27/04-28')
        self.__check_date(
            regest, start=date(1270, 04, 27), end=date(1270, 04, 27),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1270, 04, 28), end=date(1270, 04, 28),
            start_offset='', end_offset='')
        regest = Regest.objects.create(
            title='1466 [04-28 / 05-01]')
        self.__check_date(
            regest, start=date(1466, 04, 28), end=date(1466, 04, 28),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1466, 05, 01), end=date(1466, 05, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(
            title='1440-11-12/17')
        self.__check_date(
            regest, start=date(1440, 11, 12), end=date(1440, 11, 12),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1440, 11, 17), end=date(1440, 11, 17),
            start_offset='', end_offset='')
        regest = Regest.objects.create(
            title='1506-05-12 bzw. 11-10 bzw. 12-01')
        self.__check_date(
            regest, start=date(1506, 05, 12), end=date(1506, 05, 12),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1506, 11, 10), end=date(1506, 11, 10),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1506, 12, 01), end=date(1506, 12, 01),
            start_offset='', end_offset='')
        regest = Regest.objects.create(
            title='1343-04-12 oder 19')
        self.__check_date(
            regest, start=date(1343, 04, 12), end=date(1343, 04, 12),
            start_offset='', end_offset='')
        self.__check_date(
            regest, start=date(1343, 04, 19), end=date(1343, 04, 19),
            start_offset='', end_offset='')
