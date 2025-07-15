import os
from django.conf import settings

# Inicializar Firebase solo si estamos en producción
if not settings.DEBUG:
    import firebase_admin
    from firebase_admin import credentials, firestore
    # ... tu código de inicialización de Firebase aquí ...
    # Ejemplo:
    # cred = credentials.Certificate('ruta/a/tu/credencial.json')
    # firebase_admin.initialize_app(cred)
    # db = firestore.client()
else:
    # En desarrollo, puedes usar una base de datos local o mockear Firebase
    db = None 