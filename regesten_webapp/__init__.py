# -*- coding: utf-8 -*-
"""
This module provides constants for the Sbr Regesten webapp.

Author: Tim Krones <tkrones@coli.uni-saarland.de>
"""

DAY_DEFAULT = 1
MONTH_DEFAULT = 1

class RegestTitleType(object):
    REGULAR = 0
    SIMPLE_RANGE = 1
    ELLIPTICAL_RANGE = 2
    SIMPLE_ALTERNATIVES = 3
    ELLIPTICAL_ALTERNATIVES = 4
    SIMPLE_ADDITIONS = 5
    ELLIPTICAL_ADDITIONS = 6

RANGE_TYPES = (
    RegestTitleType.SIMPLE_RANGE,
    RegestTitleType.ELLIPTICAL_RANGE
    )
NON_RANGE_TYPES = (
    RegestTitleType.REGULAR,
    RegestTitleType.SIMPLE_ALTERNATIVES,
    RegestTitleType.ELLIPTICAL_ALTERNATIVES,
    RegestTitleType.SIMPLE_ADDITIONS,
    RegestTitleType.ELLIPTICAL_ADDITIONS
    )

class EllipsisType(object):
    MONTH_DIFFERENT_NO_DAY = 0
    DAY_DIFFERENT = 1
    MONTH_AND_DAY_DIFFERENT = 2

AUTHORS = (
    ('Ed', 'Irmtraut Eder-Stein, Koblenz'),
    ('He', 'Hans-Walter Herrmann, Saarbrücken'),
    ('Jac', 'Fritz Jakob, Saarbrücken'),
    ('Kl', 'Hanns Klein, Saarbrücken / Wellesweiler'))

COUNTRIES = (
    ('Frankreich', 'Frankreich'),
    ('Deutschland', 'Deutschland'),
    ('Belgien', 'Belgien'),
    ('Niederlande', 'Niederlande'),
    ('Luxemburg', 'Luxemburg'),
    ('Schweiz', 'Schweiz'),
    ('Italien', 'Italien'),
    ('Spanien', 'Spanien'),
    ('Türkei', 'Türkei'))

OFFSET_TYPES = (
    ('vor', 'vor'),
    ('nach', 'nach'),
    ('um', 'um'),
    ('ca.', 'ca.'),
    ('kurz nach', 'kurz nach'),
    ('post', 'post'))

REGION_TYPES = (
    ('Bundesland', 'Bundesland'),
    ('Departement', 'Departement'),
    ('Provinz', 'Provinz'))
