from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Category(models.Model):
    """
    Category a Mozilla Club's resource guide belongs to
    """
    name = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class ClubsGuide(models.Model):
    """
    Resource guides for Mozilla Clubs
    """
    title = models.CharField(
        help_text="The descriptive title for the club guide",
        max_length=150,
    )
    url = models.URLField(
        help_text="Website link to the guide's content",
        max_length=500,
    )
    language = models.CharField(
        help_text="The language this guide is in",
        max_length=150,
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        Category,
        help_text="Clubs Guide category this guide belongs to",
        related_name="clubs_guides",
        on_delete=models.CASCADE,
    )
    translation_of = models.ForeignKey(
        "self",
        help_text="The main guide that this guide is a translation of, if any",
        related_name="translations",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.title
