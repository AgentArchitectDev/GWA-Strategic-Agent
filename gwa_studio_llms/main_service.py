# main_service.py

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# ----------------------------------------------------
# CONFIGURACIÓN
# ----------------------------------------------------
# La clave API se lee de la variable de entorno (CRÍTICO para la seguridad)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY no encontrada. Asegúrate de configurarla.")

try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    raise RuntimeError(f"Error al inicializar cliente Gemini: {e}")

app = FastAPI(
    title="MAGENTA - Agente de Contenido Estratégico",
    description="Servicio backend que aloja la lógica del Agente IA y el acceso a Gemini.",
)

# ----------------------------------------------------
# MODELOS DE DATOS (Pydantic)
# ----------------------------------------------------

# El formato que esperamos del cliente (CIAN)
class RequestPayload(BaseModel):
    user_query: str = Field(..., description="La pregunta o tarea del usuario.")

# El formato estructurado que queremos que Gemini devuelva
class StrategicContent(BaseModel):
    title: str = Field(..., description="Título del contenido estratégico propuesto.")
    summary: str = Field(..., description="Resumen ejecutivo del plan.")
    action_steps: list[str] = Field(..., description="Lista de pasos concretos a seguir.")

# ----------------------------------------------------
# ENDPOINT PRINCIPAL
# ----------------------------------------------------

@app.post("/generate_content", response_model=StrategicContent)
async def generate_content(payload: RequestPayload):
    """Genera contenido estratégico utilizando el modelo Gemini."""
    
    # 1. Definición del Agente IA (Gem Personalizado)
    system_instruction = (
        "Eres un Agente de Contenido Estratégico (ACE). Tu misión es tomar la "
        "solicitud del usuario, analizarla y devolver un plan de acción "
        "detallado, concreto y aplicable. Sé formal, profesional y enfocado a "
        "resultados. DEBES responder ÚNICAMENTE en formato JSON, adhiriéndote "
        "estrictamente al esquema de salida (StrategicContent)."
    )
    
    # 2. Configuración del Modelo
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        response_mime_type="application/json",
        response_schema=StrategicContent,
        temperature=0.3
    )
    
    try:
        # 3. Llamada al Modelo
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=payload.user_query,
            config=config,
        )
        
        # 4. Parseo y Devolución (FastAPI valida automáticamente el JSON)
        return response.text
    
    except Exception as e:
        print(f"Error en la llamada a Gemini: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Error en el procesamiento del modelo LLM (MAGENTA)."
        )

# ----------------------------------------------------
# COMANDO DE EJECUCIÓN (Ventana 1)
# ----------------------------------------------------
# cd C:\gwa_project_v1
# set GEMINI_API_KEY="TU_CLAVE_API_DE_GEMINI_AQUI"
# gwa_env\Scripts\python.exe -m uvicorn gwa_studio_llms.main_service:app --host 0.0.0.0 --port 8001