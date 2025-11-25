# llm_proxy.py (VERSIÓN FINAL Y CORREGIDA PARA ELIMINAR COMILLAS)

import os
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel, Field
import requests
from requests.exceptions import ConnectionError, Timeout, RequestException
import json

router = APIRouter()

# --- 1. Definición de Modelos Pydantic para el Proxy ---
class ProxyAgentExecutionRequest(BaseModel):
    template_name: str = Field(..., description="Nombre de la plantilla de prompt a usar.")
    context: Dict[str, Any] = Field(..., description="Variables de contexto para inyectar en la plantilla.")
    user_prompt: str = Field(..., description="La pregunta o instrucción específica del usuario.")

class AgentOutput(BaseModel):
    status: str = Field(..., description="Estado de la ejecución: 'ok' o 'parse_fail'.")
    raw_text: str = Field(..., description="Texto crudo de la respuesta del LLM.")
    result_json: Dict[str, Any] = Field(..., description="El output JSON estructurado.")
    model_used: str = Field(..., description="Modelo LLM utilizado.")
    prompt_template: str = Field(..., description="Nombre de la plantilla de prompt utilizada.")


# --- 2. URLs y Configuración de Conexión ---
# 💥 CORRECCIÓN CRÍTICA: Elimina comillas y espacios al leer la variable de entorno.
MAGENTA_BASE_URL = os.environ.get("MAGENTA_BASE_URL", "http://localhost:8001").strip(' "') 
FIXED_INTERNAL_TOKEN = "gwa_token_magenta" 

INTERNAL_HEADERS = {
    "Authorization": f"Bearer {FIXED_INTERNAL_TOKEN}",
    "Content-Type": "application/json"
}


# --- 3. Endpoints del Proxy (CIAN) ---

@router.get("/llm/templates", response_model=List[str], summary="Obtiene la lista de plantillas disponibles del servicio Magenta")
def list_available_templates_via_proxy():
    """Proxy que llama al endpoint /templates de Magenta."""
    raise HTTPException(status_code=501, detail="Endpoint de plantillas no implementado en MAGENTA.")


# RUTA FINAL: /run (que se convierte en /api/v1/run)
@router.post("/run", response_model=AgentOutput, summary="Ejecuta el Agente LLM con plantillas")
def run_agent_inference_via_proxy( 
    request: ProxyAgentExecutionRequest
):
    model_name = "gemini-2.5-flash"
    
    magenta_payload = {
        "model_name": model_name,
        "template_name": request.template_name,
        "context": request.context,
        "user_prompt": request.user_prompt
    }

    magenta_url = f"{MAGENTA_BASE_URL}/agent/run"
    
    try:
        response = requests.post(
            magenta_url, 
            json=magenta_payload, 
            headers=INTERNAL_HEADERS,
            timeout=600.0
        )

        if response.status_code != 200:
            error_detail = response.json().get("detail", f"Error desconocido en Magenta Service. Código: {response.status_code}")
            raise HTTPException(
                status_code=response.status_code, 
                detail=error_detail
            )

        return response.json()
        
    except ConnectionError:
        raise HTTPException(
            status_code=503, 
            detail="Error de conexión con Magenta LLM Service. Asegúrese de que el servicio esté corriendo en puerto 8001."
        )
    except RequestException as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Error de conexión con el servicio API (MAGENTA): {e}"
        )