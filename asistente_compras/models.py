from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
import json


class Product(models.Model):
    """
    Modelo para representar productos del catálogo de la librería.
    La IA sugerirá productos de este catálogo para los ítems de la lista de compras.
    """
    name = models.CharField(max_length=200, verbose_name="Nombre del producto")
    description = models.TextField(verbose_name="Descripción detallada")
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Precio",
        validators=[MinValueValidator(0)]
    )
    brand = models.CharField(max_length=100, verbose_name="Marca")
    
    QUALITY_CHOICES = [
        ('economico', 'Económico'),
        ('intermedio', 'Intermedio'),
        ('calidad', 'Calidad'),
    ]
    quality_category = models.CharField(
        max_length=20,
        choices=QUALITY_CHOICES,
        verbose_name="Categoría de calidad"
    )
    
    image_url = models.URLField(
        blank=True, 
        null=True, 
        verbose_name="URL de la imagen"
    )
    stock = models.IntegerField(
        default=0,
        verbose_name="Stock disponible",
        validators=[MinValueValidator(0)]
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.brand} ({self.get_quality_category_display()})"


class ShoppingList(models.Model):
    """
    Modelo para representar una lista de compras creada por un usuario.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True,
        blank=True,
        verbose_name="Usuario"
    )
    name = models.CharField(
        max_length=200, 
        verbose_name="Nombre de la lista"
    )
    
    QUALITY_PREFERENCE_CHOICES = [
        ('cualquiera', 'Cualquier calidad'),
        ('economico', 'Solo económicos'),
        ('intermedio', 'Solo intermedios'),
        ('calidad', 'Solo de calidad'),
    ]
    quality_preference = models.CharField(
        max_length=20,
        choices=QUALITY_PREFERENCE_CHOICES,
        default='cualquiera',
        verbose_name="Preferencia de calidad"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Fecha de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="Última actualización"
    )
    
    class Meta:
        verbose_name = "Lista de Compras"
        verbose_name_plural = "Listas de Compras"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
    def get_total_items(self):
        """Retorna el total de ítems en la lista"""
        return self.shoppinglistitem_set.count()
    
    def get_total_estimated_cost(self):
        """Calcula el costo estimado total de la lista"""
        total = 0
        for item in self.shoppinglistitem_set.all():
            if item.suggested_product:
                total += item.suggested_product.price * item.quantity_requested
        return total


class ShoppingListItem(models.Model):
    """
    Modelo para representar un ítem individual en una lista de compras.
    Contiene la información del ítem tal como lo ingresó el usuario y las sugerencias de la IA.
    """
    shopping_list = models.ForeignKey(
        ShoppingList, 
        on_delete=models.CASCADE, 
        verbose_name="Lista de compras"
    )
    item_name_raw = models.CharField(
        max_length=300, 
        verbose_name="Nombre del artículo (texto original)"
    )
    quantity_requested = models.IntegerField(
        default=1,
        verbose_name="Cantidad solicitada",
        validators=[MinValueValidator(1)]
    )
    suggested_product = models.ForeignKey(
        Product, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Producto sugerido por la IA"
    )
    ai_suggestions_json = models.JSONField(
        null=True, 
        blank=True, 
        verbose_name="Sugerencias de IA en formato JSON"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    
    class Meta:
        verbose_name = "Ítem de Lista de Compras"
        verbose_name_plural = "Ítems de Lista de Compras"
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.item_name_raw} (x{self.quantity_requested})"
    
    def get_ai_suggestions(self):
        """Retorna las sugerencias de IA como diccionario Python"""
        if self.ai_suggestions_json:
            return self.ai_suggestions_json
        return {}
    
    def set_ai_suggestions(self, suggestions_dict):
        """Establece las sugerencias de IA desde un diccionario Python"""
        self.ai_suggestions_json = suggestions_dict
    
    def get_estimated_cost(self):
        """Calcula el costo estimado para este ítem"""
        if self.suggested_product:
            return self.suggested_product.price * self.quantity_requested
        return 0
