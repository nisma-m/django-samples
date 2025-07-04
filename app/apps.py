from django.apps import AppConfig

class LibraryAppConfig(AppConfig):  # Give it a unique name
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'  # This should match your app folder name

    def ready(self):
        import app.signals  # Import your signals here

