#!/usr/bin/env python3
"""
Script para verificar la conexión con Firebase
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LibreriaIA.settings')
django.setup()

from firebase_config import firebase
import firebase_admin

def test_firebase_connection():
    print("🔥 Verificando conexión con Firebase...")
    print("=" * 50)
    
    # 1. Verificar si Firebase está inicializado
    if firebase_admin._apps:
        print("✅ Firebase Admin SDK está inicializado")
        app = firebase_admin._apps.get('[DEFAULT]')
        if app:
            print(f"✅ Proyecto: {app.project_id}")
    else:
        print("❌ Firebase Admin SDK NO está inicializado")
        return False
    
    # 2. Verificar servicios
    if firebase.db:
        print("✅ Firestore Database conectado")
    else:
        print("❌ Firestore Database NO conectado")
    
    if firebase.auth:
        print("✅ Firebase Auth disponible")
    else:
        print("❌ Firebase Auth NO disponible")
    
    # 3. Intentar una operación simple
    try:
        # Intentar obtener una colección (aunque esté vacía)
        test_collection = firebase.get_collection('test_connection')
        print("✅ Conexión a Firestore exitosa")
        
        # Intentar agregar un documento de prueba
        test_doc = {
            'test': True,
            'timestamp': '2024-01-15',
            'message': 'Conexión exitosa desde Django'
        }
        
        result = firebase.add_document('test_connection', test_doc)
        if result:
            print("✅ Escritura en Firestore exitosa")
            # Limpiar documento de prueba
            firebase.delete_document('test_connection', result[1].id)
            print("✅ Documento de prueba eliminado")
        else:
            print("❌ Error al escribir en Firestore")
            
    except Exception as e:
        print(f"❌ Error en operación de Firestore: {e}")
        return False
    
    print("\n🎉 ¡Conexión con Firebase verificada exitosamente!")
    return True

if __name__ == "__main__":
    success = test_firebase_connection()
    if success:
        print("\n✅ Tu proyecto Django está conectado a Firebase")
    else:
        print("\n❌ Hay problemas con la conexión a Firebase") 