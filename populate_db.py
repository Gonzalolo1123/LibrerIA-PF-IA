#!/usr/bin/env python
"""
Script para poblar la base de datos con productos de ejemplo.
Ejecutar con: python manage.py shell < populate_db.py
"""

from asistente_compras.models import Product
from decimal import Decimal

def create_sample_products():
    """Crea productos de ejemplo para el catálogo de la librería."""
    
    products_data = [
        # Cuadernos
        {
            'name': 'Cuaderno A4 Espiral 100 hojas',
            'description': 'Cuaderno económico ideal para uso escolar con espiral metálico y 100 hojas rayadas',
            'price': Decimal('450.00'),
            'brand': 'Rivadavia',
            'quality_category': 'economico',
            'stock': 50
        },
        {
            'name': 'Cuaderno A4 Tapa Dura 200 hojas',
            'description': 'Cuaderno de calidad intermedia con tapa dura y 200 hojas rayadas',
            'price': Decimal('1200.00'),
            'brand': 'Faber-Castell',
            'quality_category': 'intermedio',
            'stock': 30
        },
        {
            'name': 'Cuaderno A4 Premium 300 hojas',
            'description': 'Cuaderno premium con papel de alta calidad, 300 hojas y tapa dura',
            'price': Decimal('2500.00'),
            'brand': 'Oxford',
            'quality_category': 'calidad',
            'stock': 15
        },
        
        # Lápices
        {
            'name': 'Lápiz HB N°2 Caja x12',
            'description': 'Lápices escolares básicos HB N°2 en caja de 12 unidades',
            'price': Decimal('350.00'),
            'brand': 'Faber-Castell',
            'quality_category': 'economico',
            'stock': 100
        },
        {
            'name': 'Lápiz HB Ecológico x10',
            'description': 'Lápices ecológicos de calidad media, caja de 10 unidades',
            'price': Decimal('800.00'),
            'brand': 'Staedtler',
            'quality_category': 'intermedio',
            'stock': 60
        },
        {
            'name': 'Lápiz HB Premium x6',
            'description': 'Lápices premium de alta calidad, caja de 6 unidades',
            'price': Decimal('1500.00'),
            'brand': 'Caran d\'Ache',
            'quality_category': 'calidad',
            'stock': 25
        },
        
        # Mochilas
        {
            'name': 'Mochila Escolar Básica',
            'description': 'Mochila escolar básica con múltiples compartimentos y correas ajustables',
            'price': Decimal('2500.00'),
            'brand': 'Genérica',
            'quality_category': 'economico',
            'stock': 25
        },
        {
            'name': 'Mochila Escolar Intermedia',
            'description': 'Mochila escolar de calidad media con refuerzos y diseño ergonómico',
            'price': Decimal('4500.00'),
            'brand': 'Samsonite',
            'quality_category': 'intermedio',
            'stock': 20
        },
        {
            'name': 'Mochila Escolar con Ruedas',
            'description': 'Mochila de alta calidad con sistema de ruedas y múltiples compartimentos',
            'price': Decimal('8500.00'),
            'brand': 'Samsonite',
            'quality_category': 'calidad',
            'stock': 10
        },
        
        # Carpetas
        {
            'name': 'Carpeta A4 Básica',
            'description': 'Carpeta básica A4 con anillos y funda plástica',
            'price': Decimal('200.00'),
            'brand': 'Genérica',
            'quality_category': 'economico',
            'stock': 80
        },
        {
            'name': 'Carpeta A4 con Anillos',
            'description': 'Carpeta A4 con anillos metálicos y funda resistente',
            'price': Decimal('450.00'),
            'brand': 'Faber-Castell',
            'quality_category': 'intermedio',
            'stock': 40
        },
        {
            'name': 'Carpeta A4 Premium',
            'description': 'Carpeta premium con anillos de alta calidad y diseño profesional',
            'price': Decimal('1200.00'),
            'brand': 'Oxford',
            'quality_category': 'calidad',
            'stock': 20
        },
        
        # Calculadoras
        {
            'name': 'Calculadora Básica',
            'description': 'Calculadora básica con funciones matemáticas simples',
            'price': Decimal('800.00'),
            'brand': 'Casio',
            'quality_category': 'economico',
            'stock': 35
        },
        {
            'name': 'Calculadora Científica',
            'description': 'Calculadora científica con funciones avanzadas para secundaria',
            'price': Decimal('2500.00'),
            'brand': 'Casio',
            'quality_category': 'intermedio',
            'stock': 25
        },
        {
            'name': 'Calculadora Gráfica',
            'description': 'Calculadora gráfica avanzada para estudios superiores',
            'price': Decimal('15000.00'),
            'brand': 'Texas Instruments',
            'quality_category': 'calidad',
            'stock': 8
        },
        
        # Otros útiles
        {
            'name': 'Regla 30cm Básica',
            'description': 'Regla de plástico de 30cm con marcas claras',
            'price': Decimal('150.00'),
            'brand': 'Genérica',
            'quality_category': 'economico',
            'stock': 120
        },
        {
            'name': 'Regla 30cm Metálica',
            'description': 'Regla metálica de 30cm con precisión milimétrica',
            'price': Decimal('350.00'),
            'brand': 'Staedtler',
            'quality_category': 'intermedio',
            'stock': 60
        },
        {
            'name': 'Estuche Escolar Básico',
            'description': 'Estuche escolar básico con múltiples compartimentos',
            'price': Decimal('400.00'),
            'brand': 'Genérica',
            'quality_category': 'economico',
            'stock': 45
        },
        {
            'name': 'Estuche Escolar Premium',
            'description': 'Estuche escolar premium con materiales de alta calidad',
            'price': Decimal('1200.00'),
            'brand': 'Faber-Castell',
            'quality_category': 'calidad',
            'stock': 20
        },
        {
            'name': 'Goma de Borrar Básica',
            'description': 'Goma de borrar blanca básica para lápiz',
            'price': Decimal('50.00'),
            'brand': 'Genérica',
            'quality_category': 'economico',
            'stock': 200
        },
        {
            'name': 'Goma de Borrar Premium',
            'description': 'Goma de borrar premium que no mancha el papel',
            'price': Decimal('200.00'),
            'brand': 'Faber-Castell',
            'quality_category': 'intermedio',
            'stock': 80
        }
    ]
    
    created_count = 0
    for product_data in products_data:
        # Verificar si el producto ya existe
        existing_product = Product.objects.filter(
            name=product_data['name'],
            brand=product_data['brand']
        ).first()
        
        if not existing_product:
            Product.objects.create(**product_data)
            created_count += 1
            print(f"✓ Creado: {product_data['name']}")
        else:
            print(f"⚠ Ya existe: {product_data['name']}")
    
    print(f"\n✅ Se crearon {created_count} productos nuevos.")
    print(f"📊 Total de productos en la base de datos: {Product.objects.count()}")

if __name__ == '__main__':
    create_sample_products() 