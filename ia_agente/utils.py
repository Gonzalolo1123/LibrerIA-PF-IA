from asistente_compras.models import Product

def get_products_for_embeddings():
    productos = Product.objects.all()
    return [
        {
            "id": p.id,
            "text": f"{p.name} de {p.brand}. {p.description}",
            "metadata": {
                "price": float(p.price),
                "stock": p.stock,
                "quality": p.quality_category
            }
        }
        for p in productos
    ] 