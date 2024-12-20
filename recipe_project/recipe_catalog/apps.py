from django.apps import AppConfig
import requests
from IPython.display import Image
from IPython.core.display import HTML


class RecipeCatalogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipe_catalog'
