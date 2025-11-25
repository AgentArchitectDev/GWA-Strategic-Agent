from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Configuración del Core (Cian)
    CIAN_PORT: int = 8000
    
    # Configuración del Servicio LLM (Magenta)
    MAGENTA_PORT: int = 8001
    MAGENTA_URL: str = "http://localhost:8001"
    
    # Token de Seguridad Interna (Cian controla a Magenta)
    INTERNAL_TOKEN: str = "token_interno_cian_a_magenta"

settings = Settings()