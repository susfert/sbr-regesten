"""
This module provides tests for non-trivial methods of the model layer.

They can be run via

python manage.py test regesten_webapp
"""

from datetime import date
from django.test import TestCase
from regesten_webapp.models import Regest


class RegestTest(TestCase):
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
        self.assertEqual(regest.regestdate.start, date(1009, 01, 01))
        self.assertEqual(regest.regestdate.end, date(1009, 01, 01))
        self.assertEqual(regest.regestdate.start_offset, '')
        self.assertEqual(regest.regestdate.end_offset, '')
        regest = Regest.objects.create(title='1009-10')
        self.assertEqual(regest.regestdate.start, date(1009, 10, 01))
        self.assertEqual(regest.regestdate.end, date(1009, 10, 01))
        self.assertEqual(regest.regestdate.start_offset, '')
        self.assertEqual(regest.regestdate.end_offset, '')
        regest = Regest.objects.create(title='1009-10-20')
        self.assertEqual(regest.regestdate.start, date(1009, 10, 20))
        self.assertEqual(regest.regestdate.end, date(1009, 10, 20))
        self.assertEqual(regest.regestdate.start_offset, '')
        self.assertEqual(regest.regestdate.end_offset, '')

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
        self.assertEqual(regest.regestdate.start, date(1009, 01, 01))
        self.assertEqual(regest.regestdate.end, date(1009, 01, 01))
        self.assertEqual(regest.regestdate.start_offset, '')
        self.assertEqual(regest.regestdate.end_offset, '')
        regest = Regest.objects.create(title='1009-10 Frankfurt am Main')
        self.assertEqual(regest.regestdate.start, date(1009, 10, 01))
        self.assertEqual(regest.regestdate.end, date(1009, 10, 01))
        self.assertEqual(regest.regestdate.start_offset, '')
        self.assertEqual(regest.regestdate.end_offset, '')
        regest = Regest.objects.create(title='1009-10-20 St. Arnual')
        self.assertEqual(regest.regestdate.start, date(1009, 10, 20))
        self.assertEqual(regest.regestdate.end, date(1009, 10, 20))
        self.assertEqual(regest.regestdate.start_offset, '')
        self.assertEqual(regest.regestdate.end_offset, '')

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
        self.assertEqual(regest.regestdate.start, date(1009, 01, 01))
        self.assertEqual(regest.regestdate.end, date(1009, 01, 01))
        self.assertEqual(regest.regestdate.start_offset, 'vor')
        self.assertEqual(regest.regestdate.end_offset, '')
        regest = Regest.objects.create(title='1009-10 (nach)')
        self.assertEqual(regest.regestdate.start, date(1009, 10, 01))
        self.assertEqual(regest.regestdate.end, date(1009, 10, 01))
        self.assertEqual(regest.regestdate.start_offset, 'nach')
        self.assertEqual(regest.regestdate.end_offset, '')
        regest = Regest.objects.create(title='1009-10-20 (ca.)')
        self.assertEqual(regest.regestdate.start, date(1009, 10, 20))
        self.assertEqual(regest.regestdate.end, date(1009, 10, 20))
        self.assertEqual(regest.regestdate.start_offset, 'ca.')
        self.assertEqual(regest.regestdate.end_offset, '')
        regest = Regest.objects.create(title='1009 (?)')
        self.assertEqual(regest.regestdate.start, date(1009, 01, 01))
        self.assertEqual(regest.regestdate.end, date(1009, 01, 01))
        self.assertEqual(regest.regestdate.start_offset, '')
        self.assertEqual(regest.regestdate.end_offset, '')
        regest = Regest.objects.create(title='1009-10 (?)')
        self.assertEqual(regest.regestdate.start, date(1009, 10, 01))
        self.assertEqual(regest.regestdate.end, date(1009, 10, 01))
        self.assertEqual(regest.regestdate.start_offset, '')
        self.assertEqual(regest.regestdate.end_offset, '')
        regest = Regest.objects.create(title='1009-10-20 (?)')
        self.assertEqual(regest.regestdate.start, date(1009, 10, 20))
        self.assertEqual(regest.regestdate.end, date(1009, 10, 20))
        self.assertEqual(regest.regestdate.start_offset, '')
        self.assertEqual(regest.regestdate.end_offset, '')

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
        self.assertEqual(regest.regestdate.start, date(1009, 01, 01))
        self.assertEqual(regest.regestdate.end, date(1009, 01, 01))
        self.assertEqual(regest.regestdate.start_offset, 'vor')
        self.assertEqual(regest.regestdate.end_offset, '')
        regest = Regest.objects.create(
            title='1009-10 (nach) Frankfurt am Main')
        self.assertEqual(regest.regestdate.start, date(1009, 10, 01))
        self.assertEqual(regest.regestdate.end, date(1009, 10, 01))
        self.assertEqual(regest.regestdate.start_offset, 'nach')
        self.assertEqual(regest.regestdate.end_offset, '')
        regest = Regest.objects.create(title='1009-10-20 (um) St. Arnual')
        self.assertEqual(regest.regestdate.start, date(1009, 10, 20))
        self.assertEqual(regest.regestdate.end, date(1009, 10, 20))
        self.assertEqual(regest.regestdate.start_offset, 'um')
        self.assertEqual(regest.regestdate.end_offset, '')
        regest = Regest.objects.create(title='1009 Diedenhofen (kurz nach)')
        self.assertEqual(regest.regestdate.start, date(1009, 01, 01))
        self.assertEqual(regest.regestdate.end, date(1009, 01, 01))
        self.assertEqual(regest.regestdate.start_offset, 'kurz nach')
        self.assertEqual(regest.regestdate.end_offset, '')
        regest = Regest.objects.create(
            title='1009-10 Frankfurt am Main (post)')
        self.assertEqual(regest.regestdate.start, date(1009, 10, 01))
        self.assertEqual(regest.regestdate.end, date(1009, 10, 01))
        self.assertEqual(regest.regestdate.start_offset, 'post')
        self.assertEqual(regest.regestdate.end_offset, '')
        regest = Regest.objects.create(title='1009-10-20 St. Arnual (ca.)')
        self.assertEqual(regest.regestdate.start, date(1009, 10, 20))
        self.assertEqual(regest.regestdate.end, date(1009, 10, 20))
        self.assertEqual(regest.regestdate.start_offset, 'ca.')
        self.assertEqual(regest.regestdate.end_offset, '')

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
        self.assertEqual(regest.regestdate.start, date(1273, 01, 01))
        self.assertEqual(regest.regestdate.end, date(1273, 01, 01))
        self.assertEqual(regest.regestdate.start_offset, '')
        self.assertEqual(regest.regestdate.end_offset, '')
        regest = Regest.objects.create(title='1270-07 (b)')
        self.assertEqual(regest.regestdate.start, date(1270, 07, 01))
        self.assertEqual(regest.regestdate.end, date(1270, 07, 01))
        self.assertEqual(regest.regestdate.start_offset, '')
        self.assertEqual(regest.regestdate.end_offset, '')
        regest = Regest.objects.create(title='1377-03-05 (c)')
        self.assertEqual(regest.regestdate.start, date(1377, 03, 05))
        self.assertEqual(regest.regestdate.end, date(1377, 03, 05))
        self.assertEqual(regest.regestdate.start_offset, '')
        self.assertEqual(regest.regestdate.end_offset, '')
        regest = Regest.objects.create(title='1424-06-03 (a) und (b)')
        self.assertEqual(regest.regestdate.start, date(1424, 06, 03))
        self.assertEqual(regest.regestdate.end, date(1424, 06, 03))
        self.assertEqual(regest.regestdate.start_offset, '')
        self.assertEqual(regest.regestdate.end_offset, '')

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
        self.assertEqual(regest.regestdate.start, date(1442, 01, 01))
        self.assertEqual(regest.regestdate.end, date(1442, 01, 01))
        self.assertEqual(regest.regestdate.start_offset, '')
        self.assertEqual(regest.regestdate.end_offset, '')
        regest = Regest.objects.create(
            title='1270-07 (b) Frankfurt am Main')
        self.assertEqual(regest.regestdate.start, date(1270, 07, 01))
        self.assertEqual(regest.regestdate.end, date(1270, 07, 01))
        self.assertEqual(regest.regestdate.start_offset, '')
        self.assertEqual(regest.regestdate.end_offset, '')
        regest = Regest.objects.create(title='1354-04-01 (c)')
        self.assertEqual(regest.regestdate.start, date(1354, 04, 01))
        self.assertEqual(regest.regestdate.end, date(1354, 04, 01))
        self.assertEqual(regest.regestdate.start_offset, '')
        self.assertEqual(regest.regestdate.end_offset, '')
        regest = Regest.objects.create(title='1424-06-03 (a) und (b)')
        self.assertEqual(regest.regestdate.start, date(1424, 06, 03))
        self.assertEqual(regest.regestdate.end, date(1424, 06, 03))
        self.assertEqual(regest.regestdate.start_offset, '')
        self.assertEqual(regest.regestdate.end_offset, '')

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
        self.assertEqual(regest.regestdate.start, date(1200, 01, 01))
        self.assertEqual(regest.regestdate.end, date(1200, 01, 01))
        self.assertEqual(regest.regestdate.start_offset, 'vor')
        self.assertEqual(regest.regestdate.end_offset, '')
        regest = Regest.objects.create(title='1200 (a) (vor)')
        self.assertEqual(regest.regestdate.start, date(1200, 01, 01))
        self.assertEqual(regest.regestdate.end, date(1200, 01, 01))
        self.assertEqual(regest.regestdate.start_offset, 'vor')
        self.assertEqual(regest.regestdate.end_offset, '')
        regest = Regest.objects.create(title='1200-03 (kurz nach) (b)')
        self.assertEqual(regest.regestdate.start, date(1200, 03, 01))
        self.assertEqual(regest.regestdate.end, date(1200, 03, 01))
        self.assertEqual(regest.regestdate.start_offset, 'kurz nach')
        self.assertEqual(regest.regestdate.end_offset, '')
        regest = Regest.objects.create(title='1200-03 (b) (kurz nach)')
        self.assertEqual(regest.regestdate.start, date(1200, 03, 01))
        self.assertEqual(regest.regestdate.end, date(1200, 03, 01))
        self.assertEqual(regest.regestdate.start_offset, 'kurz nach')
        self.assertEqual(regest.regestdate.end_offset, '')
        regest = Regest.objects.create(title='1200-03-12 (ca.) (c)')
        self.assertEqual(regest.regestdate.start, date(1200, 03, 12))
        self.assertEqual(regest.regestdate.end, date(1200, 03, 12))
        self.assertEqual(regest.regestdate.start_offset, 'ca.')
        self.assertEqual(regest.regestdate.end_offset, '')
        regest = Regest.objects.create(title='1200-03-12 (c) (ca.)')
        self.assertEqual(regest.regestdate.start, date(1200, 03, 12))
        self.assertEqual(regest.regestdate.end, date(1200, 03, 12))
        self.assertEqual(regest.regestdate.start_offset, 'ca.')
        self.assertEqual(regest.regestdate.end_offset, '')

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
        self.assertEqual(regest.regestdate.start, date(1024, 01, 01))
        self.assertEqual(regest.regestdate.end, date(1030, 01, 01))
        self.assertEqual(regest.regestdate.start_offset, '')
        self.assertEqual(regest.regestdate.end_offset, '')
        regest = Regest.objects.create(title='1024 - 1030')
        self.assertEqual(regest.regestdate.start, date(1024, 01, 01))
        self.assertEqual(regest.regestdate.end, date(1030, 01, 01))
        self.assertEqual(regest.regestdate.start_offset, '')
        self.assertEqual(regest.regestdate.end_offset, '')
        regest = Regest.objects.create(title='1419-05 - 1419-06')
        self.assertEqual(regest.regestdate.start, date(1419, 05, 01))
        self.assertEqual(regest.regestdate.end, date(1419, 06, 01))
        self.assertEqual(regest.regestdate.start_offset, '')
        self.assertEqual(regest.regestdate.end_offset, '')
        regest = Regest.objects.create(title='1419-05 bis 06')
        self.assertEqual(regest.regestdate.start, date(1419, 05, 01))
        self.assertEqual(regest.regestdate.end, date(1419, 06, 01))
        self.assertEqual(regest.regestdate.start_offset, '')
        self.assertEqual(regest.regestdate.end_offset, '')
        regest = Regest.objects.create(title='1484-07-16 - 1499-01-03')
        self.assertEqual(regest.regestdate.start, date(1484, 07, 16))
        self.assertEqual(regest.regestdate.end, date(1499, 01, 03))
        self.assertEqual(regest.regestdate.start_offset, '')
        self.assertEqual(regest.regestdate.end_offset, '')
        regest = Regest.objects.create(title='1419-05-10 bis 20')
        self.assertEqual(regest.regestdate.start, date(1419, 05, 10))
        self.assertEqual(regest.regestdate.end, date(1419, 05, 20))
        self.assertEqual(regest.regestdate.start_offset, '')
        self.assertEqual(regest.regestdate.end_offset, '')

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
        self.assertEqual(regest.regestdate.start, date(935, 01, 01))
        self.assertEqual(regest.regestdate.end, date(1000, 01, 01))
        self.assertEqual(regest.regestdate.start_offset, 'ca.')
        self.assertEqual(regest.regestdate.end_offset, 'ca.')
        regest = Regest.objects.create(title='1431 - 1459 (zwischen)')
        self.assertEqual(regest.regestdate.start, date(1431, 01, 01))
        self.assertEqual(regest.regestdate.end, date(1459, 01, 01))
        self.assertEqual(regest.regestdate.start_offset, 'nach')
        self.assertEqual(regest.regestdate.end_offset, 'vor')
        regest = Regest.objects.create(title='1419-05 - 1419-06 (um)')
        self.assertEqual(regest.regestdate.start, date(1419, 05, 01))
        self.assertEqual(regest.regestdate.end, date(1419, 06, 01))
        self.assertEqual(regest.regestdate.start_offset, 'um')
        self.assertEqual(regest.regestdate.end_offset, 'um')
        regest = Regest.objects.create(
            title='1419-05 (nach) - 1419-06 (vor)')
        self.assertEqual(regest.regestdate.start, date(1419, 05, 01))
        self.assertEqual(regest.regestdate.end, date(1419, 06, 01))
        self.assertEqual(regest.regestdate.start_offset, 'nach')
        self.assertEqual(regest.regestdate.end_offset, 'vor')
        regest = Regest.objects.create(title='1419-05 bis 06 (kurz nach)')
        self.assertEqual(regest.regestdate.start, date(1419, 05, 01))
        self.assertEqual(regest.regestdate.end, date(1419, 06, 01))
        self.assertEqual(regest.regestdate.start_offset, 'kurz nach')
        self.assertEqual(regest.regestdate.end_offset, 'kurz nach')
        regest = Regest.objects.create(
            title='1484-07-16 - 1499-01-03 (ca.)')
        self.assertEqual(regest.regestdate.start, date(1484, 07, 16))
        self.assertEqual(regest.regestdate.end, date(1499, 01, 03))
        self.assertEqual(regest.regestdate.start_offset, 'ca.')
        self.assertEqual(regest.regestdate.end_offset, 'ca.')
        regest = Regest.objects.create(
            title='1484-07-16 (nach) - 1499-01-03 (vor)')
        self.assertEqual(regest.regestdate.start, date(1484, 07, 16))
        self.assertEqual(regest.regestdate.end, date(1499, 01, 03))
        self.assertEqual(regest.regestdate.start_offset, 'nach')
        self.assertEqual(regest.regestdate.end_offset, 'vor')
        regest = Regest.objects.create(title='1419-05-10 bis 20 (ca.)')
        self.assertEqual(regest.regestdate.start, date(1419, 05, 10))
        self.assertEqual(regest.regestdate.end, date(1419, 05, 20))
        self.assertEqual(regest.regestdate.start_offset, 'ca.')
        self.assertEqual(regest.regestdate.end_offset, 'ca.')

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
        self.assertEqual(regest.regestdate.start, date(1460, 01, 01))
        self.assertEqual(regest.regestdate.end, date(1466, 01, 01))
        self.assertEqual(regest.regestdate.start_offset, 'ca.')
        self.assertEqual(regest.regestdate.end_offset, 'ca.')
        regest = Regest.objects.create(title='1460-1466 (ca.) (b)')
        self.assertEqual(regest.regestdate.start, date(1460, 01, 01))
        self.assertEqual(regest.regestdate.end, date(1466, 01, 01))
        self.assertEqual(regest.regestdate.start_offset, 'ca.')
        self.assertEqual(regest.regestdate.end_offset, 'ca.')
        regest = Regest.objects.create(title='1460-1466 (c) (ca.)')
        self.assertEqual(regest.regestdate.start, date(1460, 01, 01))
        self.assertEqual(regest.regestdate.end, date(1466, 01, 01))
        self.assertEqual(regest.regestdate.start_offset, 'ca.')
        self.assertEqual(regest.regestdate.end_offset, 'ca.')
        regest = Regest.objects.create(title='1419-05 - 1419-06 (a) um')
        self.assertEqual(regest.regestdate.start, date(1419, 05, 01))
        self.assertEqual(regest.regestdate.end, date(1419, 06, 01))
        self.assertEqual(regest.regestdate.start_offset, 'um')
        self.assertEqual(regest.regestdate.end_offset, 'um')
        regest = Regest.objects.create(title='1419-05 - 1419-06 (um) (b)')
        self.assertEqual(regest.regestdate.start, date(1419, 05, 01))
        self.assertEqual(regest.regestdate.end, date(1419, 06, 01))
        self.assertEqual(regest.regestdate.start_offset, 'um')
        self.assertEqual(regest.regestdate.end_offset, 'um')
        regest = Regest.objects.create(title='1419-05 - 1419-06 (c) (um)')
        self.assertEqual(regest.regestdate.start, date(1419, 05, 01))
        self.assertEqual(regest.regestdate.end, date(1419, 06, 01))
        self.assertEqual(regest.regestdate.start_offset, 'um')
        self.assertEqual(regest.regestdate.end_offset, 'um')
        regest = Regest.objects.create(
            title='1419-05 bis 06 (a) kurz nach')
        self.assertEqual(regest.regestdate.start, date(1419, 05, 01))
        self.assertEqual(regest.regestdate.end, date(1419, 06, 01))
        self.assertEqual(regest.regestdate.start_offset, 'kurz nach')
        self.assertEqual(regest.regestdate.end_offset, 'kurz nach')
        regest = Regest.objects.create(
            title='1419-05 bis 06 (kurz nach) (b)')
        self.assertEqual(regest.regestdate.start, date(1419, 05, 01))
        self.assertEqual(regest.regestdate.end, date(1419, 06, 01))
        self.assertEqual(regest.regestdate.start_offset, 'kurz nach')
        self.assertEqual(regest.regestdate.end_offset, 'kurz nach')
        regest = Regest.objects.create(
            title='1419-05 bis 06 (c) (kurz nach)')
        self.assertEqual(regest.regestdate.start, date(1419, 05, 01))
        self.assertEqual(regest.regestdate.end, date(1419, 06, 01))
        self.assertEqual(regest.regestdate.start_offset, 'kurz nach')
        self.assertEqual(regest.regestdate.end_offset, 'kurz nach')
        regest = Regest.objects.create(
            title='1484-07-16 - 1499-01-03 (a) ca.')
        self.assertEqual(regest.regestdate.start, date(1484, 07, 16))
        self.assertEqual(regest.regestdate.end, date(1499, 01, 03))
        self.assertEqual(regest.regestdate.start_offset, 'ca.')
        self.assertEqual(regest.regestdate.end_offset, 'ca.')
        regest = Regest.objects.create(
            title='1484-07-16 - 1499-01-03 (ca.) (b)')
        self.assertEqual(regest.regestdate.start, date(1484, 07, 16))
        self.assertEqual(regest.regestdate.end, date(1499, 01, 03))
        self.assertEqual(regest.regestdate.start_offset, 'ca.')
        self.assertEqual(regest.regestdate.end_offset, 'ca.')
        regest = Regest.objects.create(
            title='1484-07-16 - 1499-01-03 (c) (ca.)')
        self.assertEqual(regest.regestdate.start, date(1484, 07, 16))
        self.assertEqual(regest.regestdate.end, date(1499, 01, 03))
        self.assertEqual(regest.regestdate.start_offset, 'ca.')
        self.assertEqual(regest.regestdate.end_offset, 'ca.')
        regest = Regest.objects.create(title='1419-05-10 bis 20 (a) ca.')
        self.assertEqual(regest.regestdate.start, date(1419, 05, 10))
        self.assertEqual(regest.regestdate.end, date(1419, 05, 20))
        self.assertEqual(regest.regestdate.start_offset, 'ca.')
        self.assertEqual(regest.regestdate.end_offset, 'ca.')
        regest = Regest.objects.create(title='1419-05-10 bis 20 (ca.) (b)')
        self.assertEqual(regest.regestdate.start, date(1419, 05, 10))
        self.assertEqual(regest.regestdate.end, date(1419, 05, 20))
        self.assertEqual(regest.regestdate.start_offset, 'ca.')
        self.assertEqual(regest.regestdate.end_offset, 'ca.')
        regest = Regest.objects.create(title='1419-05-10 bis 20 (c) (ca.)')
        self.assertEqual(regest.regestdate.start, date(1419, 05, 10))
        self.assertEqual(regest.regestdate.end, date(1419, 05, 20))
        self.assertEqual(regest.regestdate.start_offset, 'ca.')
        self.assertEqual(regest.regestdate.end_offset, 'ca.')
        regest = Regest.objects.create(
            title='1484-07-16 (nach) - 1499-01-03 (vor) (a)')
        self.assertEqual(regest.regestdate.start, date(1484, 07, 16))
        self.assertEqual(regest.regestdate.end, date(1499, 01, 03))
        self.assertEqual(regest.regestdate.start_offset, 'nach')
        self.assertEqual(regest.regestdate.end_offset, 'vor')
