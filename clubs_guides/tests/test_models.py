from factory import Faker
from django.test import TestCase

from clubs_guides.tests.test_factory import ClubsGuideFactory, CategoryFactory
from clubs_guides.models import Category


class TestCategoryListView(TestCase):
    def setUp(self):
        self.categories = []
        for i in range(2):
            self.categories.append(CategoryFactory())
            self.categories[i].save()

        self.clubs_guides = []
        for i in range(3):
            guide = ClubsGuideFactory()
            # Assign categories alternately to the list of clubs guides
            guide.category = self.categories[i % 2]
            guide.save()
            self.clubs_guides.append(guide)

        self.fr_clubs_guide = ClubsGuideFactory(
            title=" ".join(Faker("words", locale="fr_FR", nb=4).generate({})),
            category=self.clubs_guides[0].category,
            translation_of=self.clubs_guides[0],
            language=u"Fran\xe7ais",
        )
        self.fr_clubs_guide.save()

    def test_queryset_collate_clubs_guides(self):
        """
        Test if the `collate_clubs_guides` filter on the queryset
        returns only the untranslated clubs guides for each category
        """
        result = Category.objects.collate_clubs_guides()

        self.assertEqual(len(self.categories), len(result))

        for category in self.categories:
            self.assertIn(category, result)

        for category in result:
            self.assertNotIn(self.fr_clubs_guide, category.clubs_guides.all())
