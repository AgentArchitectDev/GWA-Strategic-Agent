import streamlit as st
import httpx, os, json
import streamlit.components.v1 as components

st.set_page_config(page_title="G.WA Multi-AI Control", layout="wide")

# --- ESCANEO DE PLANTILLAS ---
PATH_PLANTILLAS = r"D:\proyectos\GWA-Strategic-Agent\plantillas_json"
if not os.path.exists(PATH_PLANTILLAS): os.makedirs(PATH_PLANTILLAS)
plantillas = [f for f in os.listdir(PATH_PLANTILLAS) if f.endswith('.json')]

# --- HUB DE +300 MODELOS ---
HUB_IA = {
    "OpenRouter (+300 Modelos)": ["Auto-Select Best", "Claude 3.5 Sonnet", "DeepSeek V3", "Llama 3.1 405B", "Qwen 2.5 72B"],
    "Meta (Llama)": ["Llama 3.2 90B Vision", "Llama 3.2 11B", "Llama 3.1 70B"],
    "OpenAI": ["GPT-4o", "GPT-4o Mini", "o1-Preview"],
    "Grok (xAI)": ["Grok-2", "Grok-1.5"],
    "Google (Gemini)": ["Gemini 2.0 Flash", "Gemini 1.5 Pro"]
}

with st.sidebar:
    st.title("🛡️ G.WA Control Center")
    prov = st.selectbox("🏢 Proveedor de IA", list(HUB_IA.keys()))
    mod_ia = st.selectbox("🧠 Cerebro Activo", HUB_IA[prov])
    st.divider()
    sel_temp = st.selectbox(f"📋 Plantillas ({len(plantillas)})", plantillas if plantillas else ["Sin archivos"])

st.title("G.WA | Strategic Agent Multimodal")
vía = st.radio("Metodología:", ["OPCIÓN A: Manual (Edición Profunda)", "OPCIÓN B: Automática (IA Total)"], horizontal=True)
modo_id = "A" if "OPCIÓN A" in vía else "B"

col_ed, col_prev = st.columns([1, 1.2])

with col_ed:
    with st.expander("🛠️ Cliente e Identidad", expanded=True):
        empresa = st.text_input("Nombre de Empresa", "G.WA Agency")
        if modo_id == "A":
            slogan = st.text_input("Slogan Corporativo")
            mision = st.text_area("Misión")
            vision = st.text_area("Visión")
            servicios = st.text_area("Servicios (uno por línea)", "Consultoría IA\nDesarrollo Web")
        else:
            st.success("🤖 IA Llenará Slogan, Misión y Visión automáticamente.")
            slogan, mision, vision, servicios = "", "", "", ""

    with st.expander("🌐 Matriz de 16 Redes Sociales", expanded=False):
        canales = ["TikTok", "X", "Instagram", "GitHub", "Twitch", "LinkedIn", "Kwai", "WA Business", "Facebook", "Telegram", "Threads", "Telegram X", "Reddit", "Pinterest", "WeChat", "Discord"]
        redes_dict = {c: st.text_input(f"Estrategia {c}", "Plan...") for c in canales} if modo_id == "A" else {}

    with st.expander("🎨 Tuneo de Estilo & Visualización", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        c_bg, c_acc, c_txt, c_slo = c1.color_picker("Fondo", "#0f111a"), c2.color_picker("Acento", "#00fbff"), c3.color_picker("Texto", "#ffffff"), c4.color_picker("Slogan", "#ffcc00")
        f_main = st.selectbox("Fuente", ["Inter", "Space Grotesk", "Montserrat", "Roboto"])
        s_h = st.slider("Tamaño Header", 1.0, 10.0, 5.0)
        s_s = st.slider("Tamaño Slogan", 0.5, 5.0, 2.0)

# --- EJECUCIÓN ---
if st.button("🚀 INICIAR PROCESAMIENTO G.WA", type="primary", use_container_width=True):
    payload = {
        "modo_ejecucion": modo_id, "empresa": empresa, "model_id": mod_ia,
        "slogan": slogan, "mision": mision, "vision": vision,
        "servicios": servicios.split("\n") if modo_id == "A" else [],
        "redes": redes_dict, "canales_lista": canales,
        "c_bg": c_bg, "c_accent": c_acc, "c_text": c_txt, "c_slogan": c_slo,
        "f_main": f_main, "s_h": s_h, "s_s": s_s, "template_type": sel_temp
    }
    r = httpx.post("http://localhost:8000/api/v1/run", json=payload, timeout=60)
    st.session_state.gwa = r.json()["result_json"]

if "gwa" in st.session_state:
    res = st.session_state.gwa
    t1, t2 = st.tabs(["🖼️ Vista Web Responsiva", "💾 Exportación"])
    with t1: components.html(res["visual_html"], height=500, scrolling=True)
    with t2:
        st.download_button("🌐 Descargar HTML", res["visual_html"], f"{empresa}.html", "text/html")
        st.download_button("💾 Descargar Pack JSON", json.dumps(res["data_json"]), f"{empresa}.json", "application/json")