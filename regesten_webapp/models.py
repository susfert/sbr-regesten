""" This module defines the data model of the Sbr Regesten webapp. """

from django.db import models

class Regest(models.Model):
    """
    The Regest model represents a single regest.
    """

    title = models.OneToOneField("ShortInfo", related_name="+")
    date = models.OneToOneField("RegestDate")
    location = models.OneToOneField("ShortInfo", null=True, related_name="+")
    regest_type = models.OneToOneField("ShortInfo", null=True, related_name="+")
    content = models.OneToOneField("RegestContent")
    original_date = models.OneToOneField(
        "ContentInfo", related_name="+")
    seal = models.OneToOneField("SealInfo")
    archives = models.OneToOneField("ContentInfo", related_name="+")
    regest_print = models.OneToOneField("ContentInfo", related_name="+")
    translation = models.OneToOneField(
        "ContentInfo", null=True, related_name="+")
    original = models.OneToOneField("ContentInfo", related_name="+")

    def __unicode__(self):
        return u'Regest {0}: {1}'.format(self.id, self.title)


class RegestInfo(models.Model):
    """
    Superclass for content type models.
    """

    def __unicode__(self):
        return self


class ShortInfo(RegestInfo):
    """
    Superclass for content types that contain plain text and footnotes
    only.

    TODO: Add examples
    """

    content = models.CharField(max_length=70)

    def __unicode__(self):
        return u'ShortInfo {0}: {1}'.format(self.id, self.content)


class ContentInfo(RegestInfo):
    """
    Superclass for content types that contain plain text, footnotes,
    and quotes.

    TODO: Add examples
    """

    content = models.OneToOneField("Content")

    def __unicode__(self):
        return u'ContentInfo {0}: {1}'.format(self.id, self.content)


class SealInfo(ContentInfo):
    """
    The SealInfo model represents information about the seal of a
    single regest (such as the sealer).

    TODO: Add examples
    """

    sealers = models.ManyToManyField("Person", null=True)

    def __unicode__(self):
        return u'SealInfo {0}: {1}'.format(self.id, self.content)


class RegestDate(models.Model):
    """
    The RegestDate model represents the date of a single regest.

    TODO: Add examples
    """

    start = models.OneToOneField("StartDate")
    end = models.OneToOneField("EndDate")
    alt_date = models.DateField(null=True)

    @property
    def exact(self):
        return not self.start.offset and not self.end.offset

    def __unicode__(self):
        return u'RegestDate {0} ({1}):\n\nStarts on {2}\nEnds on {3}\n'.format(
            self.id, 'exact' if self.exact else 'not exact',
            self.start, self.end)


class StartDate(models.Model):
    """
    The StartDate model represents the start date of the period of
    time covered by a regest.

    TODO: Add examples
    """

    date = models.DateField()
    offset = models.CharField(max_length=30, null=True)

    def __unicode__(self):
        startdate = u'StartDate {0}: {1}'.format(self.id, self.date)
        if self.offset:
            startdate += u' [{0}]'.format(self.offset)
        return startdate


class EndDate(models.Model):
    """
    The EndDate model represents the end date of the period of time
    covered by a regest.

    TODO: Add examples
    """

    date = models.DateField()
    offset = models.CharField(max_length=30, null=True)

    def __unicode__(self):
        enddate = u'EndDate {0}: {1}'.format(self.id, self.date)
        if self.offset:
            enddate += u' [{0}]'.format(self.offset)
        return enddate


class Content(models.Model):
    """
    The Content model represents any type of textual content
    containing one or more quotes.
    """

    content = models.TextField()

    def __unicode__(self):
        return u'Content {0}: {1}'.format(self.id, self.content)


class RegestContent(RegestInfo, Content):
    """
    The RegestContent model represents the content of a single regest.
    """

    issuer = models.OneToOneField("Person")
    mentions = models.ManyToManyField("Concept", null=True)

    def __unicode__(self):
        return u'RegestContent {0}: {1}'.format(self.id, self.content)


class Footnote(RegestInfo):
    """
    The footnote model represents footnotes referenced e.g. in the
    content of a regest.
    """

    referenced_in = models.ForeignKey("RegestInfo", related_name="footnotes")
    content = models.OneToOneField("Content")

    def __unicode__(self):
        return u'Footnote {0}:\n{1}\n\nReferenced in:\n{2}'.format(
            self.id, self.content, self.referenced_in)


class Quote(RegestInfo):
    """
    The Quote model represents quotes embedded in e.g. the content of
    a regest.
    """

    cited_in = models.ForeignKey("Content")
    content = models.TextField()
    mentions = models.ManyToManyField("Concept", null=True)

    def __unicode__(self):
        return u'Quote {0}: {1}'.format(self.id, self.content)


class Concept(models.Model):
    """
    The Concept model represents any type of (underspecified) concept
    introduced in the index of the Sbr Regesten.
    """

    name = models.OneToOneField("Content")
    related_concepts = models.ManyToManyField("self", null=True)

    def __unicode__(self):
        return u'Concept {0}: {1}'.format(self.id, self.name)


class SpecificConcept(Concept):
    """
    Superclass that defines attributes common to all types of specific
    concepts introduced in the index of the Sbr Regesten.
    """

    add_names = models.TextField(null=True)

    def __unicode__(self):
        return u'SpecificConcept {0}: {1}'.format(self.id, self.name)


class Landmark(SpecificConcept):
    """
    The landmark model represents a single landmark listed or
    mentioned in the index of the Sbr Regesten.
    """

    landmark_type = models.CharField(max_length=30, null=True)

    def __unicode__(self):
        landmark =  u'Landmark {0}: {1}'.format(self.id, self.name)
        if self.landmark_type:
            landmark += u' [{0}]'.format(self.landmark_type)
        return landmark


class Location(SpecificConcept):
    """
    The Location model represents a single location listed or
    mentioned in the index of the Sbr Regesten.
    """

    location_type = models.CharField(max_length=30, null=True)
    w = models.NullBooleanField()
    w_ref = models.CharField(max_length=100, null=True)
    reference_point = models.CharField(max_length=100, null=True)
    district = models.CharField(max_length=70, null=True)
    region = models.ForeignKey("Region", null=True)
    country = models.ForeignKey("Country", null=True)

    def __unicode__(self):
        location = u'Location {0}: {1}'.format(self.id, self.name)
        if self.location_type:
            location += u' [{0}]'.format(self.landmark_type)
        return location


class Person(SpecificConcept):
    """
    The Person model represents a single individual listed or
    mentioned in the index of the Sbr Regesten.
    """

    forename = models.CharField(max_length=70, null=True)
    surname = models.CharField(max_length=70, null=True)
    genname = models.CharField(max_length=30, null=True)
    maidenname = models.CharField(max_length=70, null=True)
    info = models.OneToOneField("Content", null=True)
    profession = models.CharField(max_length=30, null=True)
    resident_of = models.ForeignKey("Location", null=True)

    def __unicode__(self):
        return u'Person {0}: {1}'.format(self.id, self.name)


class PersonGroup(SpecificConcept):
    """
    The PersonGroup model represents a single group of people related
    e.g. by their profession.
    """

    members = models.ManyToManyField("Person")

    def __unicode__(self):
        return u'PersonGroup {0}: {1}'.format(self.id, self.name)


class Family(PersonGroup):
    """
    The family model represents a single family.
    """

    location = models.ForeignKey("Location", null=True)

    def __unicode__(self):
        return u'Family {0}: {1}'.format(self.id, self.name)


class IndexEntry(models.Model):
    """
    The IndexEntry model represents a single entry in the index of the
    Sbr Regesten.
    """

    defines = models.OneToOneField("SpecificConcept")
    related_entries = models.OneToOneField("self", null=True)

    def __unicode__(self):
        return u'IndexEntry {0}\n\n{1}'.format(self.id, self.defines)


class Region(models.Model):
    """
    The Region model represents regions mentioned in the (index of
    the) Sbr Regesten.
    """

    REGION_TYPES = (
        ('Bundesland', 'A state / province of Germany'),
        ('Departement', 'A state / province of France'),
        ('Provinz', 'A state / province of Belgium'))

    name = models.CharField(max_length=70)
    region_type = models.CharField(max_length=30, choices=REGION_TYPES)

    def __unicode__(self):
        return u'Region {0}: {1} ({2})'.format(
            self.id, self.name, self.region_type)


class Country(models.Model):
    """
    The Country model represents countries mentioned in the (index of
    the) Sbr Regesten.
    """

    name = models.CharField(max_length=30)

    def __unicode__(self):
        return u'Country {0}: {1}'.format(self.id, self.name)

