import streamlit as st
import httpx
import json
from typing import Dict, Any

# ----------------------------------------------------
# CONFIGURACIÓN
# ----------------------------------------------------
CIAN_BASE_URL = "http://localhost:8000"
TIMEOUT = 125 
ENDPOINT = f"{CIAN_BASE_URL}/api/v1/run" 

st.set_page_config(
    page_title="G.WA - Agente de Contenido Estratégico",
    layout="wide"
)

# ----------------------------------------------------
# LÓGICA DE INTERACCIÓN Y GENERACIÓN DE ARCHIVO
# ----------------------------------------------------

def crear_html_reporte(plan: Dict[str, Any]) -> str:
    """Genera una cadena de texto en formato HTML para el archivo descargable."""
    pasos_html = "".join([f"<li>{step}</li>" for step in plan.get('action_steps', [])])
    
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: auto; padding: 20px; }}
            .header {{ background-color: #00f2ff; padding: 10px; text-align: center; border-radius: 8px; }}
            .content {{ background: #f9f9f9; padding: 20px; border-radius: 8px; border: 1px solid #ddd; margin-top: 20px; }}
            h1 {{ color: #0056b3; }}
            h2 {{ color: #007bff; border-bottom: 2px solid #00f2ff; padding-bottom: 5px; }}
            ul {{ padding-left: 20px; }}
            .footer {{ margin-top: 30px; font-size: 0.8em; color: #777; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="header"><h1>G.WA Strategist Report</h1></div>
        <div class="content">
            <h1>{plan.get('title', 'Plan Estratégico')}</h1>
            <h2>Resumen Ejecutivo</h2>
            <p>{plan.get('summary', 'Sin resumen disponible.')}</p>
            <h2>Pasos de Acción</h2>
            <ul>{pasos_html}</ul>
        </div>
        <div class="footer">Generado por GWA-Strategic-Agent - Microservicios CIAN/MAGENTA</div>
    </body>
    </html>
    """
    return html

def send_request(query: str) -> Dict[str, Any] | None:
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
    except Exception as e:
        st.error(f"Error: {e}")
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
        with st.spinner("Generando plan con el Agente IA..."):
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
            plan = item['response']
            with st.expander(f"**Solicitud:** {item['query'][:80]}...", expanded=True): 
                st.markdown(f"### 📄 {plan['title']}")
                st.info(f"**Resumen Ejecutivo:** {plan['summary']}")
                
                st.markdown("#### Pasos de Acción:")
                for i, step in enumerate(plan['action_steps'], 1):
                    st.markdown(f"{i}. {step}")
                
                # --- BOTÓN DE DESCARGA AGREGADO AQUÍ ---
                html_data = crear_html_reporte(plan)
                st.download_button(
                    label="📥 Descargar este Plan (HTML)",
                    data=html_data,
                    file_name=f"Plan_{plan['title'].replace(' ', '_')}.html",
                    mime="text/html",
                    key=f"dl_{plan['title']}_{item['query'][:10]}" # Key única para evitar errores
                )
        else:
            with st.expander(f"**Error de Parseo:** {item['query'][:80]}...", expanded=False):
                st.error("Formato JSON incorrecto.")
                st.json(item['response']) 
else:
    st.info("Aún no se ha generado ningún plan estratégico.")
