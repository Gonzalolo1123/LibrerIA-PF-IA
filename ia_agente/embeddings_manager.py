import os
import pickle
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import numpy as np
from .utils import get_products_for_embeddings

class EmbeddingsManager:
    """
    Gestor modular de embeddings que permite cambiar entre diferentes proveedores.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Inicializa el gestor de embeddings.
        
        Args:
            model_name: Nombre del modelo de embeddings a usar
        """
        self.model_name = model_name
        self.model = None
        self.vector_store = None
        self.products_data = None
        self.index_path = "ia_agente/embeddings_index.pkl"
        
    def load_model(self):
        """Carga el modelo de embeddings."""
        try:
            self.model = SentenceTransformer(self.model_name)
            print(f"Modelo de embeddings cargado: {self.model_name}")
        except Exception as e:
            print(f"Error cargando modelo: {e}")
            # Fallback a un modelo más simple
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Genera embeddings para una lista de textos."""
        if not self.model:
            self.load_model()
        return self.model.encode(texts, show_progress_bar=True)
    
    def create_vector_store(self):
        """Crea y guarda el índice vectorial de productos."""
        print("Generando embeddings para productos...")
        
        # Obtener datos de productos
        self.products_data = get_products_for_embeddings()
        texts = [product["text"] for product in self.products_data]
        
        # Generar embeddings
        embeddings = self.generate_embeddings(texts)
        
        # Crear índice FAISS
        import faiss
        dimension = embeddings.shape[1]
        self.vector_store = faiss.IndexFlatIP(dimension)
        self.vector_store.add(embeddings.astype('float32'))
        
        # Guardar índice y datos
        self.save_index()
        print(f"Índice vectorial creado con {len(texts)} productos")
    
    def save_index(self):
        """Guarda el índice vectorial y los datos de productos."""
        if self.vector_store and self.products_data:
            index_data = {
                'index': self.vector_store,
                'products_data': self.products_data
            }
            with open(self.index_path, 'wb') as f:
                pickle.dump(index_data, f)
            print(f"Índice guardado en {self.index_path}")
    
    def load_index(self):
        """Carga el índice vectorial guardado."""
        try:
            with open(self.index_path, 'rb') as f:
                index_data = pickle.load(f)
            self.vector_store = index_data['index']
            self.products_data = index_data['products_data']
            print(f"Índice cargado con {len(self.products_data)} productos")
            return True
        except FileNotFoundError:
            print("Índice no encontrado, creando nuevo...")
            self.create_vector_store()
            return False
    
    def search_similar(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Busca productos similares a la consulta.
        
        Args:
            query: Texto de consulta
            k: Número de resultados a retornar
            
        Returns:
            Lista de productos más similares
        """
        if not self.vector_store or not self.products_data:
            self.load_index()
        
        # Generar embedding de la consulta
        query_embedding = self.generate_embeddings([query])
        
        # Buscar en el índice
        scores, indices = self.vector_store.search(
            query_embedding.astype('float32'), k
        )
        
        # Retornar productos con sus scores
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.products_data):
                product = self.products_data[idx].copy()
                product['similarity_score'] = float(score)
                results.append(product)
        
        return results

# Instancia global del gestor
embeddings_manager = EmbeddingsManager() 