import os
from typing import List, Dict, Any
from .embeddings_manager import embeddings_manager
from .models import ConsultaIALog

class AIAgent:
    """
    Agente IA modular que puede trabajar con diferentes proveedores de LLM.
    """
    
    def __init__(self, llm_provider: str = "mock"):
        """
        Inicializa el agente IA.
        
        Args:
            llm_provider: Proveedor de LLM ("openai", "huggingface", "mock")
        """
        self.llm_provider = llm_provider
        self.llm = None
        self.setup_llm()
    
    def setup_llm(self):
        """Configura el LLM según el proveedor."""
        if self.llm_provider == "mock":
            # LLM simulado para desarrollo
            self.llm = MockLLM()
        elif self.llm_provider == "openai":
            # Configuración para OpenAI
            self.llm = OpenAILLM()
        elif self.llm_provider == "huggingface":
            # Configuración para HuggingFace
            self.llm = HuggingFaceLLM()
        else:
            raise ValueError(f"Proveedor no soportado: {self.llm_provider}")
    
    def process_query(self, query: str) -> str:
        """
        Procesa una consulta del usuario y genera una respuesta.
        
        Args:
            query: Consulta del usuario
            
        Returns:
            Respuesta generada por el agente
        """
        try:
            # 1. Buscar productos relevantes
            relevant_products = embeddings_manager.search_similar(query, k=5)
            
            # 2. Preparar contexto para el LLM
            context = self._prepare_context(query, relevant_products)
            
            # 3. Generar respuesta
            response = self.llm.generate_response(context)
            
            # 4. Log de la consulta
            self._log_query(query, response)
            
            return response
            
        except Exception as e:
            error_msg = f"Error procesando consulta: {str(e)}"
            print(error_msg)
            return f"Lo siento, tuve un problema procesando tu consulta. Por favor, intenta de nuevo."
    
    def _prepare_context(self, query: str, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepara el contexto para el LLM."""
        context = {
            "query": query,
            "products": products,
            "system_prompt": """
            Eres un asistente de librería especializado en útiles escolares. 
            Tu trabajo es ayudar a los clientes a encontrar los productos que necesitan.
            
            Instrucciones:
            1. Analiza la consulta del cliente
            2. Sugiere productos relevantes de la lista proporcionada
            3. Explica por qué cada producto es adecuado
            4. Sé amigable y útil
            5. Si no hay productos relevantes, sugiere alternativas o pide más detalles
            """
        }
        return context
    
    def _log_query(self, query: str, response: str):
        """Registra la consulta y respuesta en la base de datos."""
        try:
            ConsultaIALog.objects.create(
                consulta=query,
                respuesta=response
            )
        except Exception as e:
            print(f"Error guardando log: {e}")


class MockLLM:
    """LLM simulado para desarrollo y pruebas."""
    
    def generate_response(self, context: Dict[str, Any]) -> str:
        """Genera una respuesta simulada basada en productos relevantes."""
        query = context["query"]
        products = context["products"]
        
        if not products:
            return "No encontré productos específicos para tu consulta. ¿Podrías ser más específico sobre qué necesitas?"
        
        response = f"Basándome en tu consulta: '{query}', te sugiero los siguientes productos:\n\n"
        
        for i, product in enumerate(products[:3], 1):
            response += f"{i}. **{product.get('text', 'Producto')}**\n"
            response += f"   - Precio: ${product.get('metadata', {}).get('price', 0)}\n"
            response += f"   - Stock: {product.get('metadata', {}).get('stock', 0)} unidades\n"
            response += f"   - Calidad: {product.get('metadata', {}).get('quality', 'N/A')}\n\n"
        
        response += "Estos productos parecen ser los más relevantes para tu necesidad. ¿Te gustaría que te ayude con algo más específico?"
        
        return response


class OpenAILLM:
    """LLM usando OpenAI (configuración futura)."""
    
    def generate_response(self, context: Dict[str, Any]) -> str:
        # Implementación futura para OpenAI
        return "Integración con OpenAI pendiente de configuración."


class HuggingFaceLLM:
    """LLM usando HuggingFace (configuración futura)."""
    
    def generate_response(self, context: Dict[str, Any]) -> str:
        # Implementación futura para HuggingFace
        return "Integración con HuggingFace pendiente de configuración."


# Instancia global del agente
ai_agent = AIAgent() 