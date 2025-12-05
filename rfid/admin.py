from django.contrib import admin
from django.apps import apps
from django.db import models

# admin.py for app "rfid"
# Enregistrement automatique des modèles de l'application avec réglages par défaut
# Conçu pour être générique : adapte list_display, search_fields, list_filter, readonly_fields.


APP_LABEL = "rfid"


def _field_names_for_list_display(model, limit=10):
   fields = [f.name for f in model._meta.fields]
   # Exclure champs trop volumineux (BinaryField, TextField long) si besoin
   filtered = []
   for name in fields:
      f = model._meta.get_field(name)
      if isinstance(f, models.BinaryField):
         continue
      filtered.append(name)
      if len(filtered) >= limit:
         break
   return tuple(filtered) or ("__str__",)


def _search_fields(model):
   names = []
   text_field_classes = (models.CharField, models.TextField, models.EmailField, models.SlugField, models.UUIDField)
   for f in model._meta.fields:
      if isinstance(f, text_field_classes):
         names.append(f.name)
   return tuple(names)


def _list_filter(model):
   names = []
   filter_field_classes = (models.BooleanField, models.DateField, models.DateTimeField, models.ForeignKey, models.IntegerField, models.DecimalField, models.FloatField)
   for f in model._meta.fields:
      if isinstance(f, filter_field_classes):
         names.append(f.name)
   return tuple(names)


def _readonly_fields(model):
   names = []
   for f in model._meta.fields:
      if getattr(f, "primary_key", False) or getattr(f, "auto_now", False) or getattr(f, "auto_now_add", False):
         names.append(f.name)
   return tuple(names)


def _ordering(model):
   # Utiliser le premier champ non-auto comme ordre si possible
   for f in model._meta.fields:
      if not (getattr(f, "auto_created", False) or getattr(f, "auto_now", False) or getattr(f, "auto_now_add", False)):
         return (f.name,)
   return ()


def register_app_models(app_label=APP_LABEL):
   try:
      app_config = apps.get_app_config(app_label)
   except LookupError:
      return

   for model in app_config.get_models():
      admin_attrs = {
         "list_display": _field_names_for_list_display(model),
         "search_fields": _search_fields(model),
         "list_filter": _list_filter(model),
         "readonly_fields": _readonly_fields(model),
         "ordering": _ordering(model),
         # Permettre affichage compact d'objets liés dans l'admin
         "raw_id_fields": tuple(
            f.name for f in model._meta.fields if isinstance(f, models.ForeignKey)
         ),
      }

      # Nettoyage des attributs vides (pour éviter d'avoir des tuples vides)
      admin_attrs = {k: v for k, v in admin_attrs.items() if v}

      admin_class = type(f"{model.__name__}Admin", (admin.ModelAdmin,), admin_attrs)

      try:
         admin.site.register(model, admin_class)
      except admin.sites.AlreadyRegistered:
         # Si déjà enregistré, on skippe pour éviter erreur lors du reload
         continue


# Appel à l'import pour auto-enregistrer les modèles
register_app_models()