"""
This module contains utility classes and functions for the Sbr
Regesten webapp.
"""

import re

class RegestTitleParser(object):
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
        return re.match('^\d{4}-\d{2}(-\d{2})? bis \d{2}(\D.*|)$', string)
