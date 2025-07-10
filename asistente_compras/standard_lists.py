"""
Listas predefinidas por etapa educacional para el asistente de compras.
Cada lista contiene los productos típicos necesarios para cada nivel educativo.
"""

STANDARD_LISTS = {
    'basica': {
        'name': 'Lista Básica - Educación Primaria',
        'description': 'Productos esenciales para estudiantes de educación básica (1° a 8° básico)',
        'items': [
            ('Cuaderno universitario 100 hojas', 5),
            ('Lápiz grafito HB', 10),
            ('Goma de borrar', 2),
            ('Sacapuntas', 1),
            ('Regla de 30 cm', 1),
            ('Tijeras escolares', 1),
            ('Pegamento en barra', 2),
            ('Caja de lápices de colores', 1),
            ('Mochila escolar', 1),
            ('Estuche para lápices', 1),
        ]
    },
    'media': {
        'name': 'Lista Media - Educación Secundaria',
        'description': 'Productos para estudiantes de educación media (1° a 4° medio)',
        'items': [
            ('Cuaderno universitario 100 hojas', 8),
            ('Lápiz grafito HB', 15),
            ('Goma de borrar', 3),
            ('Sacapuntas', 1),
            ('Regla de 30 cm', 1),
            ('Tijeras escolares', 1),
            ('Pegamento en barra', 2),
            ('Caja de lápices de colores', 1),
            ('Mochila escolar', 1),
            ('Estuche para lápices', 1),
            ('Calculadora científica', 1),
            ('Block de dibujo A4', 2),
            ('Lápiz grafito 2B', 5),
            ('Compás', 1),
            ('Transportador', 1),
        ]
    },
    'universidad': {
        'name': 'Lista Universitaria',
        'description': 'Productos para estudiantes universitarios',
        'items': [
            ('Cuaderno universitario 100 hojas', 10),
            ('Lápiz grafito HB', 20),
            ('Goma de borrar', 5),
            ('Sacapuntas', 2),
            ('Regla de 30 cm', 1),
            ('Tijeras escolares', 1),
            ('Pegamento en barra', 3),
            ('Caja de lápices de colores', 1),
            ('Mochila universitaria', 1),
            ('Estuche para lápices', 1),
            ('Calculadora científica avanzada', 1),
            ('Block de dibujo A4', 5),
            ('Lápiz grafito 2B', 10),
            ('Compás', 1),
            ('Transportador', 1),
            ('Marcadores de pizarra', 1),
            ('Post-it', 2),
            ('Carpeta con ganchos', 2),
            ('USB 16GB', 1),
            ('Cargador portátil', 1),
        ]
    },
    'preescolar': {
        'name': 'Lista Preescolar',
        'description': 'Productos para niños en etapa preescolar',
        'items': [
            ('Cuaderno de dibujo A4', 3),
            ('Lápiz grafito HB', 5),
            ('Goma de borrar', 2),
            ('Sacapuntas', 1),
            ('Caja de lápices de colores', 2),
            ('Caja de crayones', 1),
            ('Pegamento en barra', 2),
            ('Tijeras de punta roma', 1),
            ('Mochila pequeña', 1),
            ('Estuche para lápices', 1),
            ('Block de papel lustre', 1),
            ('Pinceles escolares', 1),
            ('Tempera escolar', 1),
        ]
    },
    'tecnico': {
        'name': 'Lista Técnica',
        'description': 'Productos para estudiantes de carreras técnicas',
        'items': [
            ('Cuaderno universitario 100 hojas', 8),
            ('Lápiz grafito HB', 15),
            ('Goma de borrar', 3),
            ('Sacapuntas', 1),
            ('Regla de 30 cm', 1),
            ('Tijeras escolares', 1),
            ('Pegamento en barra', 2),
            ('Caja de lápices de colores', 1),
            ('Mochila técnica', 1),
            ('Estuche para lápices', 1),
            ('Calculadora científica', 1),
            ('Block de dibujo A4', 3),
            ('Lápiz grafito 2B', 8),
            ('Compás', 1),
            ('Transportador', 1),
            ('Escuadra', 1),
            ('Cartabón', 1),
            ('Marcadores permanentes', 1),
            ('Cinta adhesiva', 1),
            ('USB 32GB', 1),
        ]
    }
}

def get_standard_list(list_type):
    """
    Obtiene una lista estándar por tipo.
    
    Args:
        list_type (str): Tipo de lista ('basica', 'media', 'universidad', 'preescolar', 'tecnico')
    
    Returns:
        dict: Diccionario con la información de la lista estándar
    """
    return STANDARD_LISTS.get(list_type, None)

def get_all_standard_lists():
    """
    Obtiene todas las listas estándar disponibles.
    
    Returns:
        dict: Diccionario con todas las listas estándar
    """
    return STANDARD_LISTS 