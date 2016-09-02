(function() {
    var $ = django.jQuery.bind(django.jQuery);

    function showTranslationPicker() {
        $(".field-category").hide();
        $(".field-translation_of").show();
    }

    function showCategoryPicker() {
        $(".field-category").show();
        $(".field-translation_of").hide();
    }

    $(document).ready(function() {
        var translationOf = $("#id_is_translation_0");
        var useCategory = $("#id_is_translation_1");

        if(translationOf.is(":checked")) {
            showTranslationPicker();
        } else {
            showCategoryPicker();
        }

        translationOf.click(showTranslationPicker);
        useCategory.click(showCategoryPicker);
    });
}());
