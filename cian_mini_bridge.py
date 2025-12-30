import os, json, uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

RUTA_PLANTILLAS = r"D:\proyectos\GWA-Strategic-Agent\plantillas_json"

@app.post("/api/v1/run")
async def run_engine(data: dict):
    modo = data.get("modo_ejecucion", "A")
    empresa = data.get("empresa", "G.WA Agency")
    modelo_ia = data.get("model_id", "Llama-3.2")
    nom_plantilla = data.get("template_type")
    
    # Lógica de Llenado Total por IA (Modo B)
    if modo == "B":
        slogan = f"Futuro impulsado por {modelo_ia} para {empresa}."
        mision = f"Liderar la transformación digital usando la arquitectura de {modelo_ia}."
        vision = f"Establecer un estándar global de innovación tecnológica para el 2030."
        servicios = ["Estrategia Multimodal", "Automatización IA", "Desarrollo Responsivo"]
        canales = data.get("canales_lista", [])
        redes_final = {c: f"🚀 ESTRATEGIA {c}: Contenido viral optimizado por {modelo_ia}." for c in canales}
        t_reel, t_video = f"Intro a {empresa}", f"Masterclass {modelo_ia}"
    else:
        slogan, mision, vision = data.get("slogan"), data.get("mision"), data.get("vision")
        servicios, redes_final = data.get("servicios"), data.get("redes")
        t_reel, t_video = data.get("tema_reel"), data.get("tema_video")

    # DISEÑO WEB RESPONSIVO PROFESIONAL
    web_code = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            :root {{ --accent: {data['c_accent']}; --bg: {data['c_bg']}; --text: {data['c_text']}; }}
            body {{ background: var(--bg); color: var(--text); font-family: '{data['f_main']}', sans-serif; margin: 0; padding: 20px; }}
            .hero {{ text-align: center; padding: 60px 20px; border: 2px solid var(--accent); border-radius: 30px; }}
            h1 {{ font-size: {data['s_h']}rem; color: var(--accent); margin: 0; }}
            .slogan {{ font-size: {data['s_s']}rem; color: {data['c_slogan']}; font-weight: bold; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-top: 30px; }}
            .card {{ background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; border-left: 5px solid var(--accent); }}
        </style>
    </head>
    <body>
        <div class="hero">
            <h1>{empresa}</h1>
            <p class="slogan">{slogan}</p>
        </div>
        <div class="grid">
            <div class="card"><h3>🎯 Misión</h3><p>{mision}</p></div>
            <div class="card"><h3>🛠️ Servicios</h3><ul>{''.join([f"<li>{s}</li>" for s in servicios])}</ul></div>
        </div>
    </body>
    </html>
    """

    res_json = {
        "metadata": {"ia": modelo_ia, "modo": modo, "fecha": str(datetime.now())},
        "empresa": empresa, "slogan": slogan, "redes": redes_final,
        "web_html": web_code, "multimedia": {"reel": t_reel, "video": t_video}
    }
    return {"result_json": {"visual_html": web_code, "data_json": res_json}}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)