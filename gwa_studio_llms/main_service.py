import os
from fastapi import FastAPI
from pydantic import BaseModel

# #################################################
# CORRECCIÓN CRÍTICA:
# El SDK de Gemini debe importarse como 'google.generativeai', no como 'google.genai'
# La línea siguiente corrige el error "ImportError: cannot import name 'genai' from 'google'"
# #################################################
import google.generativeai as genai 
# #################################################

# --- Configuración de la API ---
# Levanta la clave API de Gemini desde el entorno. Si no está, lanza un error de configuración.
# Nota: La clave se inyecta correctamente desde el docker-compose.yml
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY no encontrada. Asegúrate de configurarla.")

# Inicializar el cliente de Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# Inicializar la aplicación FastAPI
app = FastAPI()

# --- Modelos Pydantic ---
# Define el esquema de la solicitud (request body)
class PromptRequest(BaseModel):
    prompt: str

# Define el esquema de la respuesta (response body)
class PromptResponse(BaseModel):
    response: str

# --- Endpoint para Generación de Contenido (MAGENTA Service) ---
@app.post("/generate", response_model=PromptResponse)
async def generate_content(request: PromptRequest):
    """
    Recibe un prompt y utiliza el modelo Gemini para generar una respuesta.
    """
    try:
        # 1. Generar el contenido usando el modelo
        response = model.generate_content(request.prompt)

        # 2. Devolver solo el texto de la respuesta
        return PromptResponse(response=response.text)

    except Exception as e:
        # En caso de error (e.g., clave API inválida, error del modelo)
        return PromptResponse(response=f"Error en el procesamiento de Gemini: {e}")

# Endpoint de verificación de estado
@app.get("/status")
async def get_status():
    return {"status": "ok", "service": "MAGENTA (LLMs Service)"}

# --- Punto de entrada del servidor Uvicorn (FastAPI) ---
# Se define en el CMD de Docker: uvicorn gwa_studio_llms.main_service:app --host 0.0.0.0 --port 8001