from factory import Factory, Faker, LazyAttribute

from clubs_guides.models import ClubsGuide, Category


class ClubsGuideFactory(Factory):
    title = LazyAttribute(lambda o: ' '.join(Faker("words", nb=4).generate({})))
    url = Faker("url")

    class Meta:
        model = ClubsGuide


class CategoryFactory(Factory):
    name = LazyAttribute(lambda o: ' '.join(Faker("words", nb=4).generate({})))

    class Meta:
        model = Category
