from django.db import models


class CategoryQuerySet(models.query.QuerySet):
    """
    A custom queryset class for Category
    """
    def collate_clubs_guides(self):
        return self.prefetch_related(
            models.Prefetch(
                "clubs_guides",
                queryset=ClubsGuide.objects.filter(
                    translation_of__isnull=True
                )
            )
        )


class Category(models.Model):
    """
    Category a Mozilla Club's resource guide belongs to
    """
    name = models.CharField(max_length=200)

    objects = CategoryQuerySet.as_manager()

    class Meta:
        verbose_name_plural = "categories"

    def __unicode__(self):
        return unicode(self.name)


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

    def __unicode__(self):
        return unicode(self.title)
