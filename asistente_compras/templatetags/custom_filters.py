from django import template

register = template.Library()

@register.filter
def quality_badge_color(quality_category):
    """
    Filtro personalizado para obtener el color del badge según la categoría de calidad.
    """
    color_map = {
        'economico': 'success',
        'intermedio': 'warning',
        'calidad': 'danger',
    }
    return color_map.get(quality_category, 'secondary') 