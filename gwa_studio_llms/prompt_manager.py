import json
from pathlib import Path
from string import Template
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

# Definición de la ruta base para las plantillas de prompts.
BASE_DIR = Path(__file__).parent / "templates"

class TemplateNotFoundError(Exception):
    """Excepción levantada cuando una plantilla solicitada no existe."""
    pass

class PromptManager:
    """
    Gestiona la carga de plantillas de prompts desde archivos JSON
    y la inyección de datos dinámicos usando Template de Python.
    """
    
    def __init__(self):
        """Inicializa el manager y asegura que el directorio de plantillas exista."""
        if not BASE_DIR.is_dir():
            BASE_DIR.mkdir(exist_ok=True)
            logger.info(f"Directorio de plantillas creado: {BASE_DIR}")

    def load_template(self, template_name: str) -> Dict[str, Any]:
        """Carga la plantilla JSON completa por su nombre."""
        file_path = BASE_DIR / f"{template_name}.json"
        
        if not file_path.is_file():
            raise TemplateNotFoundError(f"Plantilla '{template_name}.json' no encontrada en {BASE_DIR}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def render_prompt(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Carga una plantilla, le inyecta las variables de contexto y devuelve el prompt renderizado.
        """
        template_data = self.load_template(template_name)
        template_string = template_data.get("prompt", "")

        if not template_string:
            raise ValueError(f"La plantilla '{template_name}' no contiene la clave 'prompt'.")

        template = Template(template_string)
        
        # Sustituimos las variables.
        # Si falta alguna en 'context' (como la que causó el error 400), Template levantará un KeyError
        # que es capturado por la capa superior y devuelto como 400.
        rendered_prompt = template.substitute(context)
        
        return rendered_prompt

    # CORRECCIÓN: Renombrada para coincidir con la llamada en main_service.py
    def get_template_names(self) -> List[str]: 
        """Lista todos los nombres de plantillas disponibles (sin extensión)."""
        return [f.stem for f in BASE_DIR.glob("*.json")]

# Instancia única para ser utilizada por el servicio
prompt_manager = PromptManager()