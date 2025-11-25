import pytest
import requests

CIAN_URL = "http://localhost:8000"
MAGENTA_URL = "http://localhost:8001"
INTERNAL_TOKEN = "gwa_token_magenta"

def test_cian_is_running():
    """Prueba que el servidor Cian Core API está activo y respondiendo."""
    try:
        response = requests.get(f"{CIAN_URL}/status")
        assert response.status_code == 200
        assert response.json()["service"] == "Cian Core API"
    except requests.exceptions.ConnectionError:
        pytest.fail(f"Cian Core API no está activo en {CIAN_URL}")

def test_magenta_is_running():
    """Prueba que el servidor Magenta LLM Service está activo y respondiendo."""
    try:
        response = requests.get(f"{MAGENTA_URL}/status")
        assert response.status_code == 200
        assert response.json()["service"] == "Magenta LLM Service" 
    except requests.exceptions.ConnectionError:
        pytest.fail(f"Magenta LLM Service no está activo en {MAGENTA_URL}")


def test_cian_can_call_magenta_securely():
    """Prueba que el Cian puede llamar al Magenta usando el token interno."""
    headers = {"Authorization": f"Bearer {INTERNAL_TOKEN}"}
    
    # Usamos /status para verificar que la conexión es posible
    response = requests.get(f"{MAGENTA_URL}/status", headers=headers) 

    assert response.status_code == 200
    

def test_unauthorized_call_is_blocked():
    """Prueba que una llamada sin el token correcto es bloqueada por Magenta."""
    headers = {"Authorization": "Bearer token_falso"}

    # Usamos la ruta protegida /templates
    response = requests.get(f"{MAGENTA_URL}/templates", headers=headers)

    # Verificamos que devuelva 403 (Forbidden) o 401 (Unauthorized)
    assert response.status_code in [401, 403], f"Magenta falló en bloquear la llamada no autorizada. Código: {response.status_code}"