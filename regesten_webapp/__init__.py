# -*- coding: utf-8 -*-

DAY_DEFAULT = 1
MONTH_DEFAULT = 1

class RegestTitleType(object):
    REGULAR = 'regular'
    SIMPLE_RANGE = 'simple range'
    ELLIPTICAL_RANGE = 'elliptical range'
    SIMPLE_ALTERNATIVES = 'simple alternatives'
    ELLIPTICAL_ALTERNATIVES = 'elliptical alternatives'

AUTHORS = (
    ('Ed', 'Irmtraut Eder-Stein, Koblenz'),
    ('He', 'Hans-Walter Herrmann, Saarbrücken'),
    ('Jac', 'Fritz Jakob, Saarbrücken'),
    ('Kl', 'Hanns Klein, Saarbrücken / Wellesweiler'))

COUNTRIES = (
    ('Frankreich', 'Frankreich'),
    ('Deutschland', 'Deutschland'),
    ('Belgien', 'Belgien'))

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
