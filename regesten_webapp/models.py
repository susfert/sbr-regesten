""" This module defines the data model of the Sbr Regesten webapp. """

from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType


class Regest(models.Model):
    """
    The Regest model represents a single regest.
    """

    title = models.OneToOneField("RegestTitle")
    date = models.OneToOneField("RegestDate")
    location = models.OneToOneField("RegestLocation", null=True)
    regest_type = models.OneToOneField("RegestType", null=True)
    content = models.OneToOneField("RegestContent")
    original_date = models.OneToOneField("OriginalDateInfo", null=True)
    seal = models.OneToOneField("SealInfo")
    archives = models.OneToOneField("ArchiveInfo")
    regest_print = models.OneToOneField("PrintInfo")
    translation = models.OneToOneField("TranslationInfo", null=True)
    original = models.OneToOneField("OriginalInfo")
    xml_repr = models.TextField()

    def __unicode__(self):
        return u'Regest {0}: {1}'.format(self.id, self.title)


class GenericInfo(models.Model):
    """
    Superclass for content types that contain plain text and footnotes
    only.

    TODO: Add examples
    """

    footnotes = generic.GenericRelation("Footnote")

    class Meta:
        """
        Specifies metadata and options for the GenericInfo model.
        """

        abstract = True


class RegestTitle(GenericInfo):
    """
    The RegestTitle model represents regest titles.

    TODO: Add examples
    """

    title = models.CharField(max_length=70)

    def __unicode__(self):
        return u'{0}'.format(self.title)


class RegestLocation(GenericInfo):
    """
    The RegestLocation model represents locations associated with
    regests.

    TODO: Add examples
    """

    name = models.CharField(max_length=70)

    def __unicode__(self):
        return u'{0}'.format(self.name)


class RegestType(GenericInfo):
    """
    The RegestType model represents regest types.

    TODO: Add examples
    """

    name = models.CharField(max_length=70)

    def __unicode__(self):
        return u'{0}'.format(self.name)


class ContentInfo(GenericInfo):
    """
    Superclass for content types that contain plain text, footnotes,
    and quotes.

    TODO: Add examples
    """

    content = models.OneToOneField("Content")

    class Meta:
        """
        Specifies metadata and options for the ContentInfo model.
        """

        abstract = True


class OriginalDateInfo(ContentInfo):
    """
    The OriginalDateInfo model represents information about regest
    dates as originally provided.

    TODO: Add examples
    """

    def __unicode__(self):
        return u'{0}'.format(self.content)


class SealInfo(ContentInfo):
    """
    The SealInfo model represents information about regest seals (such
    as the sealer).

    TODO: Add examples
    """

    sealers = models.ManyToManyField("Person", null=True)

    def __unicode__(self):
        return u'{0}'.format(self.content)


class ArchiveInfo(ContentInfo):
    """
    The ArchiveInfo model represents information about archives
    associated with regests.

    TODO: Add examples
    """

    def __unicode__(self):
        return u'{0}'.format(self.content)


class PrintInfo(ContentInfo):
    """
    The PrintInfo model represents print information for regests.

    TODO: Add examples
    """

    def __unicode__(self):
        return u'{0}'.format(self.content)


class TranslationInfo(ContentInfo):
    """
    The TranslationInfo model represents translation information for
    regests.

    TODO: Add examples
    """

    def __unicode__(self):
        return u'{0}'.format(self.content)


class OriginalInfo(ContentInfo):
    """
    The OriginalInfo model represents information about original
    regests.

    TODO: Add examples
    """

    def __unicode__(self):
        return u'{0}'.format(self.content)


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
        return u'\nStarts on {0}\nEnds on {1}\n\n---> ({2})'.format(
            self.start, self.end, 'exact' if self.exact else 'not exact')


class StartDate(models.Model):
    """
    The StartDate model represents the start date of the period of
    time covered by a regest.

    TODO: Add examples
    """

    date = models.DateField()
    offset = models.CharField(max_length=30, null=True)

    def __unicode__(self):
        startdate = u'{0}'.format(self.date)
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
        enddate = u'{0}'.format(self.date)
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
        return u'{0}'.format(self.content)


class RegestContent(GenericInfo, Content):
    """
    The RegestContent model represents the content of a single regest.
    """

    issuer = models.OneToOneField("Person")
    mentions = models.ManyToManyField("Concept", null=True)

    def __unicode__(self):
        return u'{0}'.format(self.content)


class Footnote(models.Model):
    """
    The footnote model represents footnotes referenced e.g. in the
    content of a regest.
    """

    content = models.OneToOneField("Content")
    __limit = models.Q(app_label='regesten_webapp', model='regesttitle') | \
              models.Q(app_label='regesten_webapp', model='regestlocation') | \
              models.Q(app_label='regesten_webapp', model='regesttype') | \
              models.Q(app_label='regesten_webapp', model='originaldateinfo') | \
              models.Q(app_label='regesten_webapp', model='sealinfo') | \
              models.Q(app_label='regesten_webapp', model='archiveinfo') | \
              models.Q(app_label='regesten_webapp', model='printinfo') | \
              models.Q(app_label='regesten_webapp', model='translationinfo') | \
              models.Q(app_label='regesten_webapp', model='originalinfo') | \
              models.Q(app_label='regesten_webapp', model='regestcontent') | \
              models.Q(app_label='regesten_webapp', model='quote')
    content_type = models.ForeignKey(ContentType, limit_choices_to=__limit)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return u'Footnote {0}:\n{1}\n\nReferenced in:\n{2}'.format(
            self.id, self.content, self.referenced_in)


class Quote(GenericInfo):
    """
    The Quote model represents quotes embedded in e.g. the content of
    a regest.
    """

    cited_in = models.ForeignKey("Content")
    content = models.TextField()
    mentions = models.ManyToManyField("Concept", null=True)

    def __unicode__(self):
        return u'{0}'.format(self.content)


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
            location += u' [{0}]'.format(self.location_type)
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
    xml_repr = models.TextField()

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
        return u'{0}: ({1})'.format(self.name, self.region_type)


class Country(models.Model):
    """
    The Country model represents countries mentioned in the (index of
    the) Sbr Regesten.
    """

    name = models.CharField(max_length=30)

    def __unicode__(self):
        return u'{0}'.format(self.name)

