import os
import json
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from fastapi import HTTPException
from google import genai
from google.genai import types

try:
    # Asegúrate de que esta ruta de importación sea correcta para tu proyecto
    from .prompt_manager import prompt_manager 
except ImportError:
    print("ERROR: No se pudo importar 'prompt_manager'.")
    prompt_manager = None 

# --- Modelos Pydantic (Sin cambios) ---
class AgentExecutionRequest(BaseModel):
    model_name: str = Field(..., description="El modelo LLM a ejecutar (Gemini).")
    template_name: str = Field(..., description="Nombre de la plantilla de prompt a usar.")
    context: Dict[str, Any] = Field(..., description="Variables de contexto para inyectar.")
    user_prompt: str = Field(..., description="Instrucción específica del usuario (el 'pront trivial').")

class AgentOutput(BaseModel):
    status: str = Field(..., description="Estado de la ejecución: 'ok' o 'parse_fail'.")
    raw_text: str = Field(..., description="Texto crudo de la respuesta del LLM.")
    result_json: Dict[str, Any] = Field(..., description="El output JSON estructurado.")
    model_used: str = Field(..., description="Modelo LLM utilizado.")
    prompt_template: str = Field(..., description="Nombre de la plantilla de prompt utilizada.")


# --- Configuración del Cliente Gemini (CON LIMPIEZA DE CLAVE) ---

GEMINI_API_KEY_RAW = os.environ.get("GEMINI_API_KEY")
GEMINI_API_KEY = None 
gemini_client = None 

if GEMINI_API_KEY_RAW:
    # 🚨 LIMPIEZA CRÍTICA: Elimina espacios, newlines y comillas.
    GEMINI_API_KEY = GEMINI_API_KEY_RAW.strip().replace('"', '').replace("'", '')
    
    try:
        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        print("INFO: Cliente Gemini inicializado con éxito. Clave limpiada y lista.")
    except Exception as e:
        print(f"ERROR: No se pudo inicializar el cliente Gemini. Revise la clave. {e}")
else:
    print("ADVERTENCIA: GEMINI_API_KEY no configurada. El servicio MAGENTA fallará con 500.")


class AgentService:
    def __init__(self, prompt_manager_instance):
        if not prompt_manager_instance:
             raise Exception("No se pudo inicializar AgentService: Falta la instancia de prompt_manager.")
        self.prompt_manager = prompt_manager_instance
        
    def run_agent(self, request: AgentExecutionRequest) -> AgentOutput:
        
        if not gemini_client:
             raise HTTPException(
                status_code=500,
                detail="GEMINI_API_KEY no está configurada o es inválida. La inferencia Gemini no puede comenzar."
            )

        # 🚀 MODIFICACIÓN CRÍTICA: INYECTAR EL PRONT TRIVIAL EN EL CONTEXTO
        # ----------------------------------------------------------------------
        # 1. Copiamos el contexto base.
        processing_context = request.context.copy()
        # 2. Inyectamos la solicitud del usuario bajo una clave específica.
        processing_context["user_prompt_trivial"] = request.user_prompt
        # ----------------------------------------------------------------------
        
        # 3. Corrección: Solo pasar template_name y el contexto enriquecido.
        try:
             final_prompt = self.prompt_manager.render_prompt(
                request.template_name,
                processing_context # Usamos el contexto con el pront trivial
             ) 
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error al renderizar el prompt: {e}. Revise la definición de render_prompt en prompt_manager.py."
            )

        try:
            # 4. Llamada a la API de Gemini. Se fuerza la salida JSON.
            response = gemini_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=final_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json" 
                )
            )
            
            raw_text = response.text 
            
            # 5. Procesar la Salida JSON
            # ... (Resto del código de procesamiento JSON)
            try:
                result_json = json.loads(raw_text)
                status = "ok"
            except json.JSONDecodeError:
                result_json = {"error": "El modelo no pudo generar un JSON válido. Texto crudo en 'raw_text'."}
                status = "parse_fail"

            # 6. Devolver el resultado
            return AgentOutput(
                status=status,
                raw_text=raw_text,
                result_json=result_json,
                model_used='gemini-2.5-flash', 
                prompt_template=request.template_name,
            )

        except Exception as e:
            print(f"Error al llamar a la API de Gemini: {e}")
            raise HTTPException(
                status_code=500, 
                detail=f"Error al ejecutar el modelo Gemini (API): {e}"
            )

# Creación de la INSTANCIA
agent_service = None
if prompt_manager:
    try:
        agent_service = AgentService(prompt_manager_instance=prompt_manager)
    except Exception as e:
        print(f"ERROR: Falló la creación de agent_service: {e}")