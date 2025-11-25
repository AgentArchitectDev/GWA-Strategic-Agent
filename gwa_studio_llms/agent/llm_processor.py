import requests
import json
from typing import Dict, Any, List
from pydantic import BaseModel

# 1. Definición de la salida requerida del Agente (JSON)
class AgentOutput(BaseModel):
    model_used: str
    processed_prompt: str
    result_json: Dict[str, Any]
    execution_time_ms: int

# 2. Endpoints y Configuración
OLLAMA_URL = "http://localhost:11434/api/generate"
FALLBACK_RESPONSE = {"status": "ERROR_FALLBACK", "message": "Fallo de inferencia o JSON inválido. Se usó el fallback."}

class LLMProcessor:
    """Clase que maneja la conexión a Ollama y la ejecución del Agente O/S."""
    
    def __init__(self, model_name: str = "llama3:8b"):
        self.model_name = model_name

    def process_request(self, system_prompt: str, user_prompt: str) -> AgentOutput:
        """
        Ejecuta el modelo O/S con un prompt CoT para obtener una respuesta JSON.
        Incluye un robusto try/except para el fallback.
        """
        import time
        start_time = time.time()
        
        # 3. Armado del Prompt (Chain-of-Thought simplificado)
        full_prompt = (
            f"SYSTEM: {system_prompt}\n\n"
            "INSTRUCCIONES: Responde ÚNICAMENTE con un objeto JSON válido. Nunca texto antes o después del JSON. "
            "Asegura que todas las llaves y valores sean cadenas o números válidos.\n\n"
            f"PROMPT DEL USUARIO: {user_prompt}"
        )

        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.5,
                "num_ctx": 4096
            }
        }
        
        try:
            # 4. Conexión a la capa de inferencia local (Ollama)
            response = requests.post(OLLAMA_URL, json=payload, timeout=180.0)
            response.raise_for_status() 
            
            response_data = response.json()
            raw_response_text = response_data.get("response", "")
            
            # 5. Extracción y Parsing del JSON (Robusto ante charla del LLM)
            json_start = raw_response_text.find('{')
            json_end = raw_response_text.rfind('}') + 1
            
            if json_start != -1 and json_end != -1 and json_end > json_start:
                json_string = raw_response_text[json_start:json_end]
                result_data = json.loads(json_string)
            else:
                # 5.1. Fallback si el JSON no se encuentra
                result_data = FALLBACK_RESPONSE
                result_data["raw_output"] = raw_response_text
                
        except requests.exceptions.RequestException as e:
            # 6. Fallback si Ollama está caído o hay un error de red
            print(f"Error de conexión con Ollama: {e}")
            result_data = FALLBACK_RESPONSE
            result_data["error_detail"] = str(e)
            
        except json.JSONDecodeError:
            # 7. Fallback si el JSON está malformado
            print("Error: JSON malformado por el modelo.")
            result_data = FALLBACK_RESPONSE
            result_data["raw_output"] = raw_response_text
            
        end_time = time.time()
        
        return AgentOutput(
            model_used=self.model_name,
            processed_prompt=user_prompt,
            result_json=result_data,
            execution_time_ms=int((end_time - start_time) * 1000)
        )