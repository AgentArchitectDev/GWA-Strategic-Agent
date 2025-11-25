# main.py (CIAN - VERSIÓN FINAL Y COMPROBADA)

from fastapi import FastAPI, HTTPException, Request
from gwa_studio_core.core_api import llm_proxy 
# 💥 ¡ESTA LÍNEA DE IMPORTACIÓN FALLIDA FUE ELIMINADA!
from starlette.middleware.cors import CORSMiddleware
import logging
import time

# --- Inicialización de FastAPI ---
app = FastAPI(
    title="Cian Core API - API Gateway de GWA Studio",
    version="1.2.0",
    description="Servidor de entrada (Proxy)."
)

# --- Middleware CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 💥 REGISTRO DE RUTA: Define el prefijo /api/v1 💥
app.include_router(llm_proxy.router, tags=["LLM Proxy"], prefix="/api/v1")


# --- Endpoints Base ---

@app.get("/status", tags=["Base"])
def get_status():
    """Endpoint de estado para verificar que el servicio está activo."""
    return {"status": "ok", "service": "Cian Core API"}