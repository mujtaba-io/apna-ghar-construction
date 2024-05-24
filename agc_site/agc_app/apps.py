from django.apps import AppConfig

# python manage.py makemigrations agc_app ------- use this command to tell django that
# you have made changes to your app layout.

class AgcAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agc_app'
