import json
import logging
from typing import Any, Dict, Optional
import re 
from jinja2 import Environment, FileSystemLoader
import ollama

# --- Configuración ---
OLLAMA_BASE_URL = "http://localhost:11434"

# Configuración del logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de Jinja2 (Debe estar en la ruta gwa_studio_llms/templates)
try:
    # Usamos ruta relativa para que Uvicorn lo encuentre desde la raíz del proyecto
    env = Environment(loader=FileSystemLoader("gwa_studio_llms/templates"), autoescape=True) 
except Exception as e:
    logger.error(f"Error al inicializar Jinja2: {e}.")
    env = None


class LLMAgentExecutor:
    
    def __init__(self):
        try:
            self.llm_client = ollama.Client(host=OLLAMA_BASE_URL)
            logger.info(f"Ollama Client inicializado en: {OLLAMA_BASE_URL}")
        except Exception as e:
            logger.error(f"No se pudo inicializar el cliente de Ollama: {e}")
            self.llm_client = None

    def _load_and_render_template(self, template_name: str, context: Dict[str, Any], user_prompt: str) -> str:
        if env is None:
            raise RuntimeError("Jinja2 Environment no está configurado.")

        try:
            template_file = f"{template_name}.jinja"
            template = env.get_template(template_file)
            system_prompt = template.render(context=context, user_prompt=user_prompt)
            return system_prompt
        except Exception as e:
            logger.error(f"Error al cargar o renderizar la plantilla {template_name}: {e}")
            raise

    def run_llm_agent(self, model_name: str, template_name: str, context: Dict[str, Any], user_prompt: str) -> Dict[str, Any]:
        if not self.llm_client:
            raise ConnectionError("El cliente de Ollama no se pudo inicializar o conectar.")

        system_prompt = self._load_and_render_template(template_name, context, user_prompt)
        
        # Este log es ligero y seguro
        logger.info(f"Ejecutando modelo: {model_name} con plantilla: {template_name}") 

        try:
            # Petición a Ollama
            response = self.llm_client.chat(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt}
                ],
                options={'temperature': 0.1}, 
                format='json'
            )

            raw_response_text = response['message']['content']
            
            # Procesamiento y Parseo de la Respuesta con limpieza agresiva (REGEX)
            try:
                cleaned_text = raw_response_text.strip()

                # Usa REGEX para encontrar el primer bloque que se parezca a un objeto JSON { ... }
                # Esto es crucial para limpiar el output del modelo (como "```json{}```")
                match = re.search(r'\{.*\}', cleaned_text, re.DOTALL)
                
                if match:
                    json_candidate = match.group(0).strip()
                    # Limpieza del bloque JSON si contiene las comillas triples
                    if json_candidate.startswith('```json'):
                        json_candidate = json_candidate[7:].strip() 
                    if json_candidate.endswith('```'):
                         json_candidate = json_candidate[:-3].strip() 
                else:
                    json_candidate = cleaned_text # Fallback
                
                result_json = json.loads(json_candidate)
                
                # RETORNO FINAL CORRECTO (EXITO) - Estructura Plana
                return {
                    "status": "ok",                       
                    "result_json": result_json,           
                    "model_used": model_name,
                    "prompt_template": template_name,
                    "raw_text": raw_response_text,        
                }
            
            except json.JSONDecodeError as e:
                logger.warning(f"JSON Decode Error: {e}")
                
                # RETORNO FINAL CORRECTO (FALLO DE PARSEO) - Estructura Plana
                return {
                    "status": "parse_fail",              
                    "raw_text": raw_response_text,       
                    "model_used": model_name,
                    "prompt_template": template_name,
                    "result_json": {},                   
                }

        except Exception as e:
            logger.error(f"Error en la llamada a Ollama: {e}")
            raise