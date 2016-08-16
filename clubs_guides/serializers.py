from rest_framework import serializers

from clubs_guides.models import ClubsGuide, Category


class ClubsGuideBaseSerializer(serializers.ModelSerializer):
    """
    Serializes a clubs guide with only the basic information
    directly relevant to a clubs guide
    """
    class Meta:
        model = ClubsGuide
        fields = ("title", "url", "language",)


class ClubsGuideSerializer(ClubsGuideBaseSerializer):
    """
    Serializes a clubs guide
    """
    category = serializers.StringRelatedField()
    translation_of = serializers.StringRelatedField()

    class Meta(ClubsGuideBaseSerializer.Meta):
        fields = (
            ClubsGuideBaseSerializer.Meta.fields +
            ("category", "translation_of",)
        )


class ClubsGuideWithTranslationsSerializer(ClubsGuideBaseSerializer):
    """
    Serializes a clubs guide and also includes other related clubs
    guides that are direct translations of it
    """
    translations = ClubsGuideBaseSerializer(many=True)

    class Meta(ClubsGuideBaseSerializer.Meta):
        fields = (
            ClubsGuideBaseSerializer.Meta.fields +
            ("translations",)
        )


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializes a clubs guide category
    """
    class Meta:
        model = Category
        fields = ("name",)


class CategoryWithClubsGuideSerializer(serializers.ModelSerializer):
    """
    Serializes a clubs guide category and includes the clubs guides
    associated with that category
    """
    category = serializers.CharField(source="name")
    guides = ClubsGuideWithTranslationsSerializer(
        source="clubs_guides",
        many=True,
    )

    class Meta:
        model = Category
        fields = ("category", "guides",)
