from django.db import models

class Regest(models.Model):
    """
    The Regest model represents a single regest.
    """

    title = models.OneToOneField("RegestTitle")
    date = models.OneToOneField("RegestDate")
    location = models.OneToOneField("RegestLocation")
    regest_type = models.OneToOneField("RegestType")
    content = models.OneToOneField("RegestContent")
    original_date = models.OneToOneField("OriginalDateInfo")
    seal = models.OneToOneField("SealInfo")
    archives = models.OneToOneField("ArchiveInfo")
    regest_print = models.OneToOneField("PrintInfo")
    translation = models.OneToOneField("TranslationInfo")
    original = models.OneToOneField("OriginalInfo")

    def __unicode__(self):
        return self


class RegestInfo(models.Model):
    """
    Abstract superclass for models representing different types of
    information about a regest.
    """

    class Meta:
        abstract = True

    def __unicode__(self):
        return self


class RegestTitle(RegestInfo):
    """
    The RegestTitle model represents the title of a single regest.

    TODO: Add examples
    """

    def __unicode__(self):
        return self


class RegestLocation(RegestInfo):
    """
    The RegestLocation models represents the location of a single
    regest.

    TODO: Add examples
    """

    def __unicode__(self):
        return self


class RegestType(RegestInfo):
    """
    The RegestType model represents the type of a single regest.

    TODO: Add examples
    """

    def __unicode__(self):
        return self


class OriginalDateInfo(RegestInfo):
    """
    The OriginalDateInfo represents information about the date of a
    single regest as originally provided.

    TODO: Add examples
    """

    def __unicode__(self):
        return self


class SealInfo(RegestInfo):
    """
    The SealInfo model represents information about the seal of a
    single regest (such as the sealer).

    TODO: Add examples
    """

    def __unicode__(self):
        return self


class ArchiveInfo(RegestInfo):
    """
    The RegestArchive model represents an archive associated with a
    regest.

    TODO: Add examples
    """

    def __unicode__(self):
        return self


class PrintInfo(RegestInfo):
    """
    The PrintInfo model represents print information about a regest.

    TODO: Add examples
    """

    def __unicode__(self):
        return self


class TranslationInfo(RegestInfo):
    """
    The TranslationInfo model represents translation information about
    a regest.

    TODO: Add examples
    """

    def __unicode__(self):
        return self


class OriginalInfo(RegestInfo):
    """
    The OriginalInfo model represents information about the original
    version of a specific regest.

    TODO: Add examples
    """

    def __unicode__(self):
        return self


class RegestDate(models.Model):
    """
    The RegestDate model represents the date of a single regest.

    TODO: Add examples
    """

    def __unicode__(self):
        return self


class StartDate(models.Model):
    """
    The StartDate model represents the start date of the period of
    time covered by a regest.

    TODO: Add examples
    """

    def __unicode__(self):
        return self


class EndDate(models.Model):
    """
    The EndDate model represents the end date of the period of time
    covered by a regest.

    TODO: Add examples
    """

    def __unicode__(self):
        return self


class Content(models.Model):
    """
    The Content model represents any type of textual content
    containing one or more quotes.
    """

    def __unicode__(self):
        return self


class RegestContent(Content):
    """
    The RegestContent model represents the content of a single regest.
    """

    def __unicode__(self):
        return self


class Footnote(models.Model):
    """
    The footnote model represents footnotes referenced e.g. in the
    content of a regest.
    """

    def __unicode__(self):
        return self


class Quote(models.Model):
    """
    The Quote model represents quotes embedded in e.g. the content of
    a regest.
    """

    def __unicode__(self):
        return self


class Concept(models.Model):
    """
    The Concept model represents any type of (underspecified) concept
    introduced in the index of the Sbr Regesten.
    """

    def __unicode__(self):
        return self


class SpecificConcept(Concept):
    """
    Superclass that defines attributes common to all types of specific
    concepts introduced in the index of the Sbr Regesten.
    """

    def __unicode__(self):
        return self


class Landmark(SpecificConcept):
    """
    The landmark model represents a single landmark listed or
    mentioned in the index of the Sbr Regesten.
    """

    def __unicode__(self):
        return self


class Location(SpecificConcept):
    """
    The Location model represents a single location listed or
    mentioned in the index of the Sbr Regesten.
    """

    def __unicode__(self):
        return self


class Person(SpecificConcept):
    """
    The Person model represents a single individual listed or
    mentioned in the index of the Sbr Regesten.
    """

    def __unicode__(self):
        return self


class PersonGroup(SpecificConcept):
    """
    The PersonGroup model represents a single group of people related
    e.g. by their profession.
    """

    def __unicode__(self):
        return self


class Family(PersonGroup):
    """
    The family model represents a single family.
    """

    def __unicode__(self):
        return self


class IndexEntry(models.Model):
    """
    The IndexEntry model represents a single entry in the index of the
    Sbr Regesten.
    """

    def __unicode__(self):
        return self
