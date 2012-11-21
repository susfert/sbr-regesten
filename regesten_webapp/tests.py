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
        regest = Regest.objects.create(title='1009-10')
        self.assertEqual(regest.regestdate.start, date(1009, 10, 01))
        self.assertEqual(regest.regestdate.end, date(1009, 10, 01))
        self.assertEqual(regest.regestdate.start_offset, '')
        regest = Regest.objects.create(title='1009-10-20')
        self.assertEqual(regest.regestdate.start, date(1009, 10, 20))
        self.assertEqual(regest.regestdate.end, date(1009, 10, 20))
        self.assertEqual(regest.regestdate.start_offset, '')

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
        regest = Regest.objects.create(title='1009-10 Frankfurt am Main')
        self.assertEqual(regest.regestdate.start, date(1009, 10, 01))
        self.assertEqual(regest.regestdate.end, date(1009, 10, 01))
        self.assertEqual(regest.regestdate.start_offset, '')
        regest = Regest.objects.create(title='1009-10-20 St. Arnual')
        self.assertEqual(regest.regestdate.start, date(1009, 10, 20))
        self.assertEqual(regest.regestdate.end, date(1009, 10, 20))
        self.assertEqual(regest.regestdate.start_offset, '')

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
        regest = Regest.objects.create(title='1009-10 (nach)')
        self.assertEqual(regest.regestdate.start, date(1009, 10, 01))
        self.assertEqual(regest.regestdate.end, date(1009, 10, 01))
        self.assertEqual(regest.regestdate.start_offset, 'nach')
        regest = Regest.objects.create(title='1009-10-20 (ca.)')
        self.assertEqual(regest.regestdate.start, date(1009, 10, 20))
        self.assertEqual(regest.regestdate.end, date(1009, 10, 20))
        self.assertEqual(regest.regestdate.start_offset, 'ca.')
        regest = Regest.objects.create(title='1009 (?)')
        self.assertEqual(regest.regestdate.start, date(1009, 01, 01))
        self.assertEqual(regest.regestdate.end, date(1009, 01, 01))
        self.assertEqual(regest.regestdate.start_offset, '')
        regest = Regest.objects.create(title='1009-10 (?)')
        self.assertEqual(regest.regestdate.start, date(1009, 10, 01))
        self.assertEqual(regest.regestdate.end, date(1009, 10, 01))
        self.assertEqual(regest.regestdate.start_offset, '')
        regest = Regest.objects.create(title='1009-10-20 (?)')
        self.assertEqual(regest.regestdate.start, date(1009, 10, 20))
        self.assertEqual(regest.regestdate.end, date(1009, 10, 20))
        self.assertEqual(regest.regestdate.start_offset, '')

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
        regest = Regest.objects.create(
            title='1009-10 (nach) Frankfurt am Main')
        self.assertEqual(regest.regestdate.start, date(1009, 10, 01))
        self.assertEqual(regest.regestdate.end, date(1009, 10, 01))
        self.assertEqual(regest.regestdate.start_offset, 'nach')
        regest = Regest.objects.create(title='1009-10-20 (um) St. Arnual')
        self.assertEqual(regest.regestdate.start, date(1009, 10, 20))
        self.assertEqual(regest.regestdate.end, date(1009, 10, 20))
        self.assertEqual(regest.regestdate.start_offset, 'um')
        regest = Regest.objects.create(title='1009 Diedenhofen (kurz nach)')
        self.assertEqual(regest.regestdate.start, date(1009, 01, 01))
        self.assertEqual(regest.regestdate.end, date(1009, 01, 01))
        self.assertEqual(regest.regestdate.start_offset, 'kurz nach')
        regest = Regest.objects.create(
            title='1009-10 Frankfurt am Main (post)')
        self.assertEqual(regest.regestdate.start, date(1009, 10, 01))
        self.assertEqual(regest.regestdate.end, date(1009, 10, 01))
        self.assertEqual(regest.regestdate.start_offset, 'post')
        regest = Regest.objects.create(title='1009-10-20 St. Arnual (ca.)')
        self.assertEqual(regest.regestdate.start, date(1009, 10, 20))
        self.assertEqual(regest.regestdate.end, date(1009, 10, 20))
        self.assertEqual(regest.regestdate.start_offset, 'ca.')

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
        regest = Regest.objects.create(title='1270-07 (b)')
        self.assertEqual(regest.regestdate.start, date(1270, 07, 01))
        self.assertEqual(regest.regestdate.end, date(1270, 07, 01))
        self.assertEqual(regest.regestdate.start_offset, '')
        regest = Regest.objects.create(title='1377-03-05 (c)')
        self.assertEqual(regest.regestdate.start, date(1377, 03, 05))
        self.assertEqual(regest.regestdate.end, date(1377, 03, 05))
        self.assertEqual(regest.regestdate.start_offset, '')
        regest = Regest.objects.create(title='1424-06-03 (a) und (b)')
        self.assertEqual(regest.regestdate.start, date(1424, 06, 03))
        self.assertEqual(regest.regestdate.end, date(1424, 06, 03))
        self.assertEqual(regest.regestdate.start_offset, '')

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
        regest = Regest.objects.create(
            title='1270-07 (b) Frankfurt am Main')
        self.assertEqual(regest.regestdate.start, date(1270, 07, 01))
        self.assertEqual(regest.regestdate.end, date(1270, 07, 01))
        self.assertEqual(regest.regestdate.start_offset, '')
        regest = Regest.objects.create(title='1354-04-01 (c)')
        self.assertEqual(regest.regestdate.start, date(1354, 04, 01))
        self.assertEqual(regest.regestdate.end, date(1354, 04, 01))
        self.assertEqual(regest.regestdate.start_offset, '')
        regest = Regest.objects.create(title='1424-06-03 (a) und (b)')
        self.assertEqual(regest.regestdate.start, date(1424, 06, 03))
        self.assertEqual(regest.regestdate.end, date(1424, 06, 03))
        self.assertEqual(regest.regestdate.start_offset, '')

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
        regest = Regest.objects.create(title='1200 (a) (vor)')
        self.assertEqual(regest.regestdate.start, date(1200, 01, 01))
        self.assertEqual(regest.regestdate.end, date(1200, 01, 01))
        self.assertEqual(regest.regestdate.start_offset, 'vor')
        regest = Regest.objects.create(title='1200-03 (kurz nach) (b)')
        self.assertEqual(regest.regestdate.start, date(1200, 03, 01))
        self.assertEqual(regest.regestdate.end, date(1200, 03, 01))
        self.assertEqual(regest.regestdate.start_offset, 'kurz nach')
        regest = Regest.objects.create(title='1200-03 (b) (kurz nach)')
        self.assertEqual(regest.regestdate.start, date(1200, 03, 01))
        self.assertEqual(regest.regestdate.end, date(1200, 03, 01))
        self.assertEqual(regest.regestdate.start_offset, 'kurz nach')
        regest = Regest.objects.create(title='1200-03-12 (ca.) (c)')
        self.assertEqual(regest.regestdate.start, date(1200, 03, 12))
        self.assertEqual(regest.regestdate.end, date(1200, 03, 12))
        self.assertEqual(regest.regestdate.start_offset, 'ca.')
        regest = Regest.objects.create(title='1200-03-12 (c) (ca.)')
        self.assertEqual(regest.regestdate.start, date(1200, 03, 12))
        self.assertEqual(regest.regestdate.end, date(1200, 03, 12))
        self.assertEqual(regest.regestdate.start_offset, 'ca.')


