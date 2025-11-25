# app_frontend.py (VERSIÓN FINAL Y COMPROBADA)

import streamlit as st
import httpx
import json
from typing import Dict, Any

# ----------------------------------------------------
# CONFIGURACIÓN (Ruta Correcta para 404)
# ----------------------------------------------------
CIAN_BASE_URL = "http://localhost:8000"
TIMEOUT = 125 

# RUTA CORRECTA: http://localhost:8000/api/v1/run
ENDPOINT = f"{CIAN_BASE_URL}/api/v1/run" 

st.set_page_config(
    page_title="G.WA - Agente de Contenido Estratégico",
    layout="wide"
)

# ----------------------------------------------------
# LÓGICA DE INTERACCIÓN
# ----------------------------------------------------

def send_request(query: str) -> Dict[str, Any] | None:
    """Envía la consulta al endpoint corregido de CIAN."""
    
    # 💥 LÍNEA DE VERIFICACIÓN: Muestra la URL que Streamlit está usando.
    st.info(f"Conectando a: {ENDPOINT}")
    
    payload = {
        "template_name": "GWA_STRATEGIC_PLAN", 
        "context": {}, 
        "user_prompt": query 
    }
    
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            response = client.post(ENDPOINT, json=payload)
            response.raise_for_status() 

            agent_output = response.json()
            return agent_output.get("result_json", None)
            
    except httpx.HTTPStatusError as e:
        st.error(f"Error del servidor ({e.response.status_code}): {e.response.text}")
    except httpx.ConnectError:
        st.error(f"Error 503: No se pudo conectar a CIAN en {CIAN_BASE_URL}. ¿Están CIAN (8000) y MAGENTA (8001) corriendo?")
    except Exception as e:
        st.error(f"Ocurrió un error inesperado: {e}")
    return None

# ----------------------------------------------------
# INTERFAZ DE USUARIO (Streamlit)
# ----------------------------------------------------

st.title("G.WA | Generador de Contenido Estratégico 🤖")
st.markdown("---")

if 'history' not in st.session_state:
    st.session_state.history = []

query = st.text_area(
    "Escribe tu solicitud (ej: 'Diseña un plan de marketing para lanzar un producto SaaS enfocado en Pymes')", 
    height=150
)

if st.button("Generar Plan Estratégico", type="primary"):
    if query:
        with st.spinner("Generando plan con el Agente IA... (puede tardar)"):
            result = send_request(query)
        
        if result:
            st.session_state.history.insert(0, {"query": query, "response": result})
            st.toast("¡Plan generado con éxito!", icon="✅")
    else:
        st.warning("Por favor, introduce una solicitud.")

st.markdown("---")
st.subheader("Historial de Planes Generados")

if st.session_state.history:
    for item in st.session_state.history:
        
        if isinstance(item['response'], dict) and 'title' in item['response']:
            with st.expander(f"**Solicitud:** {item['query'][:80]}...", expanded=True): 
                st.markdown(f"### 📄 {item['response']['title']}")
                
                st.info(f"**Resumen Ejecutivo:** {item['response']['summary']}")
                
                st.markdown("#### Pasos de Acción:")
                for i, step in enumerate(item['response']['action_steps'], 1):
                    st.markdown(f"{i}. {step}")
        else:
            with st.expander(f"**Solicitud (Error de Parseo):** {item['query'][:80]}...", expanded=False):
                st.error("Error: MAGENTA no devolvió la estructura JSON correcta.")
                st.json(item['response']) 
                
else:
    st.info("Aún no se ha generado ningún plan estratégico.")