from django.apps import AppConfig


class LandingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'landing'

    def ready(self):
        # Warm up the spell checker data on startup
        try:
            from .spell_checker_advanced import warmup
            warmup()
            
            # Warm up transliterator
            from .transliterator import get_transliterator
            get_transliterator()
            print("Warmup complete: Spell checker & Transliterator loaded.")
        except Exception as e:
            print(f"Warning: Failed to warm up spell checker: {e}")
