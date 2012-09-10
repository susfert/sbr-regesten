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
        return self


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
    """

    content = models.CharField(max_length=70)

    def __unicode__(self):
        return self


class ContentInfo(RegestInfo):
    """
    Superclass for content types that contain plain text, footnotes,
    and quotes.
    """

    content = models.OneToOneField("Content")

    def __unicode__(self):
        return self


class SealInfo(ContentInfo):
    """
    The SealInfo model represents information about the seal of a
    single regest (such as the sealer).

    TODO: Add examples
    """

    sealers = models.ManyToManyField("Person", null=True)

    def __unicode__(self):
        return self


class RegestDate(models.Model):
    """
    The RegestDate model represents the date of a single regest.

    TODO: Add examples
    """

    start = models.OneToOneField("StartDate")
    end = models.OneToOneField("EndDate")
    alt_date = models.DateField(null=True)
    exact = models.BooleanField()

    def __unicode__(self):
        return self


class StartDate(models.Model):
    """
    The StartDate model represents the start date of the period of
    time covered by a regest.

    TODO: Add examples
    """

    date = models.DateField()
    offset = models.CharField(max_length=30, null=True)

    def __unicode__(self):
        return self


class EndDate(models.Model):
    """
    The EndDate model represents the end date of the period of time
    covered by a regest.

    TODO: Add examples
    """

    date = models.DateField()
    offset = models.CharField(max_length=30, null=True)

    def __unicode__(self):
        return self


class Content(models.Model):
    """
    The Content model represents any type of textual content
    containing one or more quotes.
    """

    content = models.TextField()

    def __unicode__(self):
        return self


class RegestContent(RegestInfo, Content):
    """
    The RegestContent model represents the content of a single regest.
    """

    issuer = models.OneToOneField("Person")
    mentions = models.ManyToManyField("Concept", null=True)

    def __unicode__(self):
        return self


class Footnote(RegestInfo):
    """
    The footnote model represents footnotes referenced e.g. in the
    content of a regest.
    """

    referenced_in = models.ForeignKey("RegestInfo", related_name="footnotes")
    content = models.OneToOneField("Content")

    def __unicode__(self):
        return self


class Quote(RegestInfo):
    """
    The Quote model represents quotes embedded in e.g. the content of
    a regest.
    """

    cited_in = models.ForeignKey("Content")
    content = models.TextField()
    mentions = models.ManyToManyField("Concept", null=True)

    def __unicode__(self):
        return self


class Concept(models.Model):
    """
    The Concept model represents any type of (underspecified) concept
    introduced in the index of the Sbr Regesten.
    """

    name = models.OneToOneField("Content")
    related_concepts = models.ManyToManyField("self", null=True)

    def __unicode__(self):
        return self


class SpecificConcept(Concept):
    """
    Superclass that defines attributes common to all types of specific
    concepts introduced in the index of the Sbr Regesten.
    """

    add_names = models.TextField(null=True)

    def __unicode__(self):
        return self


class Landmark(SpecificConcept):
    """
    The landmark model represents a single landmark listed or
    mentioned in the index of the Sbr Regesten.
    """

    landmark_type = models.CharField(max_length=30, null=True)

    def __unicode__(self):
        return self


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
        return self


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
        return self


class PersonGroup(SpecificConcept):
    """
    The PersonGroup model represents a single group of people related
    e.g. by their profession.
    """

    members = models.ManyToManyField("Person")

    def __unicode__(self):
        return self


class Family(PersonGroup):
    """
    The family model represents a single family.
    """

    location = models.ForeignKey("Location", null=True)

    def __unicode__(self):
        return self


class IndexEntry(models.Model):
    """
    The IndexEntry model represents a single entry in the index of the
    Sbr Regesten.
    """

    defines = models.OneToOneField("SpecificConcept")
    related_entries = models.OneToOneField("self", null=True)

    def __unicode__(self):
        return self


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
        return self


class Country(models.Model):
    """
    The Country model represents countries mentioned in the (index of
    the) Sbr Regesten.
    """

    name = models.CharField(max_length=30)

    def __unicode__(self):
        return self

