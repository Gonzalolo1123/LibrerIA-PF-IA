#!/usr/bin/env python3
"""
Script para configurar Firebase automáticamente
"""
import json
import os
from pathlib import Path

def setup_firebase():
    print("🔥 Configuración de Firebase para LibreriaIA")
    print("=" * 50)
    
    # Verificar si existe el archivo de credenciales
    cred_file = input("📁 Ruta al archivo JSON de credenciales de Firebase (o presiona Enter para saltar): ").strip()
    
    if cred_file and os.path.exists(cred_file):
        try:
            with open(cred_file, 'r') as f:
                creds = json.load(f)
            
            # Crear archivo .env
            env_content = f"""# Configuración de Firebase
FIREBASE_PROJECT_ID={creds.get('project_id', 'tu-proyecto-id')}
FIREBASE_PRIVATE_KEY_ID={creds.get('private_key_id', 'tu-private-key-id')}
FIREBASE_PRIVATE_KEY="{creds.get('private_key', 'tu-clave-privada').replace(chr(10), '\\n')}"
FIREBASE_CLIENT_EMAIL={creds.get('client_email', 'tu-client-email')}
FIREBASE_CLIENT_ID={creds.get('client_id', 'tu-client-id')}
FIREBASE_CLIENT_CERT_URL={creds.get('client_x509_cert_url', 'tu-cert-url')}

# Configuración de Django
SECRET_KEY=django-insecure-{os.urandom(32).hex()}
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
"""
            
            with open('.env', 'w') as f:
                f.write(env_content)
            
            print("✅ Archivo .env creado exitosamente!")
            print("📝 Variables configuradas:")
            print(f"   - Project ID: {creds.get('project_id')}")
            print(f"   - Client Email: {creds.get('client_email')}")
            
        except Exception as e:
            print(f"❌ Error leyendo el archivo: {e}")
    else:
        print("⚠️  No se proporcionó archivo de credenciales.")
        print("📝 Crea manualmente un archivo .env con las variables de firebase_env_example.txt")
    
    print("\n📋 Próximos pasos:")
    print("1. ✅ Crear proyecto en Firebase Console")
    print("2. ✅ Habilitar Firestore Database")
    print("3. ✅ Descargar credenciales JSON")
    print("4. ✅ Configurar variables de entorno")
    print("5. 🔄 Ejecutar: python manage.py sync_firebase --all")
    print("6. 🚀 ¡Listo para usar Firebase!")

if __name__ == "__main__":
    setup_firebase() 