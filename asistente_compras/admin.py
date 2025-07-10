from django.contrib import admin
from .models import Product, ShoppingList, ShoppingListItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Product.
    """
    list_display = ('name', 'brand', 'price', 'quality_category', 'stock', 'created_at')
    list_filter = ('quality_category', 'brand', 'created_at')
    search_fields = ('name', 'description', 'brand')
    list_editable = ('price', 'stock')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'brand')
        }),
        ('Precio y Stock', {
            'fields': ('price', 'stock')
        }),
        ('Categorización', {
            'fields': ('quality_category', 'image_url')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo ShoppingList.
    """
    list_display = ('name', 'user', 'get_total_items', 'get_total_estimated_cost', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Información de la Lista', {
            'fields': ('name', 'user')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    def get_total_items(self, obj):
        return obj.get_total_items()
    get_total_items.short_description = 'Total de Ítems'
    
    def get_total_estimated_cost(self, obj):
        return f"${obj.get_total_estimated_cost():.2f}"
    get_total_estimated_cost.short_description = 'Costo Estimado'


@admin.register(ShoppingListItem)
class ShoppingListItemAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo ShoppingListItem.
    """
    list_display = ('item_name_raw', 'shopping_list', 'quantity_requested', 'suggested_product', 'get_estimated_cost', 'created_at')
    list_filter = ('created_at', 'updated_at', 'suggested_product__quality_category')
    search_fields = ('item_name_raw', 'shopping_list__name', 'suggested_product__name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Información del Ítem', {
            'fields': ('shopping_list', 'item_name_raw', 'quantity_requested')
        }),
        ('Sugerencias de IA', {
            'fields': ('suggested_product', 'ai_suggestions_json'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('shopping_list', 'suggested_product')
    
    def get_estimated_cost(self, obj):
        return f"${obj.get_estimated_cost():.2f}"
    get_estimated_cost.short_description = 'Costo Estimado'


# Configuración personalizada del admin
admin.site.site_header = "Administración de Librería IA"
admin.site.site_title = "Librería IA Admin"
admin.site.index_title = "Panel de Administración - Asistente de Compras con IA"
