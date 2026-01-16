from django.urls import path
# Force reload
from .views import home, transliterate, spell_checker_page, spell_check_api, extract_file_text

urlpatterns = [
    path('', home, name='home'),
    path('transliterate/', transliterate, name='transliterate'),
    path('spell-checker/', spell_checker_page, name='spell_checker_page'),
    path('api/spell-check/', spell_check_api, name='spell_check_api'),
    path('api/extract-file-text/', extract_file_text, name='extract_file_text'),
]
