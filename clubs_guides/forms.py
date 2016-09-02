from django import forms
from django.forms import widgets
from django.core.exceptions import ValidationError
from django.forms.fields import Field

from clubs_guides.models import ClubsGuide, Category


class ClubsGuideForm(forms.ModelForm):
    # Explicitly specifying the cateogry field allows two behavioural
    # implications:
    # 1. We get to control the error handling logic so that we can dynamically
    #    populate the category if `is_translation` is set to `True` and show
    #    errors regarding missing information accordingly.
    # 2. We get to disable the ability to "add new categories" on the fly
    #    through this form since the default for value for `can_add_related`
    #    for the `Select` widget is `None` (Django admin explicitly sets this
    #    to `True` unless you specify the field yourself)
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label="Category",
        help_text=ClubsGuide.category.field.help_text,
        required=False,
    )
    is_translation = forms.ChoiceField(
        label="Is this guide a translation of another guide?",
        widget=widgets.RadioSelect,
        choices=(
            (True, "Yes"),
            (False, "No"),
        ),
        initial=False,
    )

    def __init__(self, *args, **kwargs):
        super(ClubsGuideForm, self).__init__(*args, **kwargs)

        if "instance" in kwargs and kwargs["instance"] is not None:
            self.fields["is_translation"].initial = (
                kwargs["instance"].translation_of is not None
            )

    def clean_category(self):
        cleaned_data = self.cleaned_data
        category = cleaned_data.get("category")
        is_translation = cleaned_data.get("is_translation") == "True"
        if is_translation is not True and category is None:
            raise ValidationError(
                Field.default_error_messages["required"],
                code="required",
            )
        if is_translation is True:
            category = self.clean_translation_of().category
        return category

    def clean_translation_of(self):
        cleaned_data = self.cleaned_data
        translation_of = cleaned_data.get("translation_of")
        is_translation = cleaned_data.get("is_translation") == "True"
        if is_translation is True and translation_of is None:
            raise ValidationError(
                Field.default_error_messages["required"],
                code="required",
            )
        if is_translation is not True:
            translation_of = None
        return translation_of

    class Meta:
        model = ClubsGuide
        fields = [
            "title",
            "url",
            "language",
            "is_translation",
            "translation_of",
            "category",
        ]
