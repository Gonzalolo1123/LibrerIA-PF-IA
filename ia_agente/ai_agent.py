import os
import requests
from typing import List, Dict, Any
from .embeddings_manager import embeddings_manager
from .models import ConsultaIALog
from huggingface_hub import InferenceClient
import markdown2
import json
import re

class AIAgent:
    """
    Agente IA modular que puede trabajar con diferentes proveedores de LLM.
    """
    
    def __init__(self, llm_provider: str = "huggingface"):
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
            try:
                # Configuración para HuggingFace
                self.llm = HuggingFaceLLM()
            except Exception as e:
                raise  # Forzar excepción para no hacer fallback silencioso
        else:
            raise ValueError(f"Proveedor no soportado: {self.llm_provider}")
    
    def process_query(self, query: str) -> dict:
        """
        Procesa una consulta del usuario y genera una respuesta.
        Devuelve un diccionario con la lista de productos sugeridos o un mensaje de error.
        """
        try:
            relevant_products = embeddings_manager.search_similar(query, k=5)
            context = self._prepare_context(query, relevant_products)
            response = self.llm.generate_response(context)
            print("[DEPURACIÓN] Respuesta cruda del agente IA:\n", response)
            # Intentar decodificar el JSON directamente
            try:
                productos = json.loads(response)
                if not isinstance(productos, list):
                    raise ValueError('El JSON no es una lista')
                return {"productos": productos, "error": None}
            except Exception:
                # Intentar extraer el primer bloque de lista JSON con regex
                match = re.search(r'(\[.*?\])', response, re.DOTALL)
                if match:
                    try:
                        productos = json.loads(match.group(1))
                        if not isinstance(productos, list):
                            raise ValueError('El JSON extraído no es una lista')
                        return {"productos": productos, "error": None}
                    except Exception:
                        pass
                return {"productos": [], "error": "No se pudo interpretar la respuesta del agente IA. Intenta de nuevo."}
        except Exception as e:
            return {"productos": [], "error": f"Error procesando consulta: {str(e)}"}
    
    def _prepare_context(self, query: str, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepara el contexto para el LLM."""
        context = {
            "query": query,
            "products": products,
            "system_prompt": (
                "Eres un asistente de librería especializado en útiles escolares. "
                "Responde siempre en español latino. "
                "Cuando el cliente haga una consulta, responde SOLO con una lista en formato JSON válido (usa comillas dobles), sin ningún texto antes o después. "
                "El JSON debe ser una lista de objetos con las claves: 'producto', 'marca', 'precio', 'calidad', 'stock', 'cantidad_sugerida'. "
                "Incluye solo los productos más relevantes para la consulta y ajusta la cantidad sugerida según lo que el cliente pide. "
                "No incluyas comentarios, saludos ni explicaciones. No formules preguntas. No agregues texto fuera del JSON. "
                "Ejemplo de respuesta válida: [{\"producto\": \"Lápiz HB\", \"marca\": \"Faber-Castell\", \"precio\": 350, \"calidad\": \"Económico\", \"stock\": 100, \"cantidad_sugerida\": 2}] "
            )
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
        """Genera una respuesta simulada basada en productos relevantes."""
        # Implementación futura para OpenAI
        return "Integración con OpenAI pendiente de configuración."


class HuggingFaceLLM:
    """LLM usando HuggingFace (configuración futura)."""
    
    def __init__(self):
        """Inicializa el cliente de HuggingFace."""
        self.api_token = os.environ.get("HF_TOKEN")
        if not self.api_token:
            raise ValueError("No se encontró el token de HuggingFace en la variable HF_TOKEN")
        self.client = InferenceClient(token=self.api_token)
        self.model = "HuggingFaceH4/zephyr-7b-beta"  # Modelo público gratuito

    def generate_response(self, context: Dict[str, Any]) -> str:
        """Genera una respuesta real usando el modelo de HuggingFace."""
        prompt = self._build_prompt(context)
        try:
            response = self.client.chat_completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=512,  # Aumentado para maximizar la longitud de respuesta
                temperature=0.7,
            )
            # El resultado es un objeto con choices[0].message.content
            return response.choices[0].message.content
        except Exception as e:
            raise

    def _build_prompt(self, context: Dict[str, Any]) -> str:
        """Construye el prompt para el modelo de HuggingFace."""
        productos = context["products"]
        productos_str = "\n".join([
            f"- {p['text']} (Precio: ${p['metadata']['price']}, Stock: {p['metadata']['stock']}, Calidad: {p['metadata']['quality']})"
            for p in productos
        ])
        prompt = (
            f"{context['system_prompt']}\n"
            f"Consulta del cliente: {context['query']}\n"
            f"Productos relevantes:\n{productos_str}\n"
            "Responde de forma clara, útil y en español latino."
        )
        return prompt

# Instancia global del agente
ai_agent = AIAgent("huggingface") 