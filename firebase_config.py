import firebase_admin
from firebase_admin import credentials, firestore, auth, storage
import os
from django.conf import settings
import json

class FirebaseConfig:
    """Configuración y utilidades para Firebase en Django"""
    
    def __init__(self):
        self.db = None
        self.auth = None
        self.storage = None
        if not settings.DEBUG:
            self._initialize_firebase()
        else:
            print("⚠️ Firebase deshabilitado en modo desarrollo (DEBUG=True)")
    
    def _initialize_firebase(self):
        """Inicializa Firebase Admin SDK"""
        try:
            if not firebase_admin._apps:
                json_file_path = os.path.join(os.path.dirname(__file__), 'proyecto1-d6fb7-firebase-adminsdk-bz4ej-2bbed03ae6.json')
                if os.path.exists(json_file_path):
                    cred = credentials.Certificate(json_file_path)
                    print(f"✅ Usando archivo JSON: {json_file_path}")
                else:
                    private_key = os.getenv('FIREBASE_PRIVATE_KEY', '')
                    if private_key:
                        private_key = private_key.replace('\\n', '\n').replace('"', '')
                    cred = credentials.Certificate({
                        "type": "service_account",
                        "project_id": os.getenv('FIREBASE_PROJECT_ID'),
                        "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
                        "private_key": private_key,
                        "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
                        "client_id": os.getenv('FIREBASE_CLIENT_ID'),
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_CERT_URL')
                    })
                    print("✅ Usando variables de entorno")
                firebase_admin.initialize_app(cred, {'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET')})
                print("✅ Firebase inicializado correctamente")
            self.db = firestore.client()
            self.auth = auth
            self.storage = storage.bucket()
        except Exception as e:
            print(f"❌ Error inicializando Firebase: {e}")
            print("💡 Asegúrate de que el archivo JSON de credenciales esté en la raíz del proyecto")
    
    def get_collection(self, collection_name):
        if settings.DEBUG:
            print("⚠️ Firebase deshabilitado en modo desarrollo (DEBUG=True)")
            return None
        if self.db is None:
            print("❌ Firebase no está inicializado")
            return None
        return self.db.collection(collection_name)
    
    def add_document(self, collection_name, data, doc_id=None):
        if settings.DEBUG:
            print("⚠️ Firebase deshabilitado en modo desarrollo (DEBUG=True)")
            return False
        collection = self.get_collection(collection_name)
        if collection is None:
            return False
        try:
            if doc_id:
                result = collection.document(doc_id).set(data)
                print(f"✅ Firestore: Documento '{doc_id}' en colección '{collection_name}' agregado/actualizado.")
                return result
            else:
                update_time, doc_ref = collection.add(data)
                print(f"✅ Firestore: Documento '{doc_ref.id}' en colección '{collection_name}' agregado.")
                return update_time, doc_ref
        except Exception as e:
            print(f"❌ Error agregando documento a Firestore: {e}")
            return False
    
    def get_document(self, collection_name, doc_id):
        if settings.DEBUG:
            print("⚠️ Firebase deshabilitado en modo desarrollo (DEBUG=True)")
            return None
        collection = self.get_collection(collection_name)
        if collection is None:
            return None
        doc = collection.document(doc_id).get()
        if doc.exists:
            print(f"✅ Firestore: Documento '{doc_id}' en colección '{collection_name}' obtenido.")
        else:
            print(f"ℹ️ Firestore: Documento '{doc_id}' no encontrado en colección '{collection_name}'.")
        return doc
    
    def update_document(self, collection_name, doc_id, data):
        if settings.DEBUG:
            print("⚠️ Firebase deshabilitado en modo desarrollo (DEBUG=True)")
            return False
        collection = self.get_collection(collection_name)
        if collection is None:
            return False
        try:
            result = collection.document(doc_id).update(data)
            print(f"✅ Firestore: Documento '{doc_id}' en colección '{collection_name}' actualizado.")
            return result
        except Exception as e:
            print(f"❌ Error actualizando documento en Firestore: {e}")
            return False
    
    def delete_document(self, collection_name, doc_id):
        if settings.DEBUG:
            print("⚠️ Firebase deshabilitado en modo desarrollo (DEBUG=True)")
            return False
        collection = self.get_collection(collection_name)
        if collection is None:
            return False
        try:
            collection.document(doc_id).delete()
            print(f"✅ Firestore: Documento '{doc_id}' en colección '{collection_name}' eliminado.")
            return True
        except Exception as e:
            print(f"❌ Error eliminando documento de Firestore: {e}")
            return False

# Instancia global
firebase = FirebaseConfig() 