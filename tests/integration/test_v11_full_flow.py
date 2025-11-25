import pytest
import requests
import json
from typing import Dict, Any

# --- Configuraciones ---
CIAN_URL = "http://localhost:8000"
MAGENTA_URL = "http://localhost:8001"
INTERNAL_TOKEN = "gwa_token_magenta" 

TEST_MODEL = "llama3:8b" 
TEST_TEMPLATE_NAME = "template_empresa_melanoma" 
# CONTEXTO COMPLETO Y FINAL
TEST_CONTEXT = {
    "nombre_empresa": "GWA Digital",
    "nombre_ciudad": "Córdoba",
    "ubicacion": "Córdoba", 
    "sector": "Marketing Digital y Tecnología" 
}
TEST_USER_PROMPT = "Genera un plan de marketing digital de 3 puntos para esta empresa."

# --- Pruebas ---

def test_01_check_all_services_are_up():
    """Verifica que ambos servicios (Cian y Magenta) estén activos antes de ejecutar el flujo."""
    try:
        cian_status = requests.get(f"{CIAN_URL}/status").status_code
        magenta_status = requests.get(f"{MAGENTA_URL}/status").status_code
        
        assert cian_status == 200
        assert magenta_status == 200
    except requests.exceptions.ConnectionError as e:
        pytest.fail(f"Uno o ambos servicios están caídos: {e}")

def test_02_full_llm_flow_with_templates():
    """Verifica el flujo completo Cian -> Magenta (seguro) -> Ollama."""

    proxy_url = f"{CIAN_URL}/llm/run_agent/{TEST_MODEL}"
    payload = {
        "template_name": TEST_TEMPLATE_NAME,
        "context": TEST_CONTEXT,
        "user_prompt": TEST_USER_PROMPT
    }

    print(f"\n--- Ejecutando Flujo con Plantillas: {TEST_TEMPLATE_NAME} ---")

    try:
        # CORRECCIÓN FINAL: Timeout ajustado a 180.0 segundos.
        response = requests.post(proxy_url, json=payload, timeout=180.0) 
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Error en la llamada del Proxy Cian al Magenta: {e}")
        return

    assert response.status_code == 200, \
        f"Fallo en la respuesta final. Código: {response.status_code}, Detalle: {response.text}"
        
    data = response.json()
    assert "result_json" in data
    assert data["model_used"] == TEST_MODEL
    assert isinstance(data["result_json"], dict)


def test_03_magenta_blocks_unauthorized_external_call():
    """Verifica que el endpoint de Magenta es inaccesible sin el token interno del Cian."""
    unauthorized_headers = {"Authorization": "Bearer token_malo_externo"}
    valid_dummy_payload = {
        "model_name": TEST_MODEL,
        "template_name": TEST_TEMPLATE_NAME,
        "context": TEST_CONTEXT,
        "user_prompt": "security_test"
    }

    response = requests.post(f"{MAGENTA_URL}/agent/run", json=valid_dummy_payload, headers=unauthorized_headers)

    assert response.status_code in [401, 403], "Magenta falló en bloquear la llamada no autorizada."


def test_04_cian_proxy_lists_templates():
    """Verifica que el Cian Proxy pueda llamar a Magenta y listar las plantillas disponibles."""
    proxy_templates_url = f"{CIAN_URL}/llm/templates"

    try:
        response = requests.get(proxy_templates_url, timeout=10) 
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Error al conectar con Cian para listar plantillas: {e}")
        return

    assert response.status_code == 200, \
        f"Fallo al obtener la lista de plantillas a través del proxy. Código: {response.status_code}"
    
    templates = response.json()
    assert isinstance(templates, list)
    assert TEST_TEMPLATE_NAME in templates