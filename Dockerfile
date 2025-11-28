# Dockerfile: Entorno unificado para CIAN (8000) y MAGENTA (8001)

# Usar una imagen base oficial de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar el archivo de requisitos e instalar las dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código del proyecto al contenedor
COPY . /app

# Exponer los puertos que usaremos
EXPOSE 8000
EXPOSE 8001

# Comando de ejecución: Inicia MAGENTA y CIAN
CMD ["/bin/bash", "-c", " \
    # 1. Configurar la clave de Gemini (se inyectará como variable de entorno) \
    export GEMINI_API_KEY=$GEMINI_API_KEY && \
    \
    # 2. Configurar el Proxy (CIAN sabe dónde buscar a MAGENTA) \
    export MAGENTA_BASE_URL=http://localhost:8001 && \
    \
    # 3. Iniciar MAGENTA (8001) en segundo plano \
    nohup uvicorn gwa_studio_llms.main_service:app --host 0.0.0.0 --port 8001 & \
    \
    # 4. Iniciar CIAN (8000) en primer plano (y el Frontend Streamlit) \
    uvicorn gwa_studio_core.core_api.main:app --host 0.0.0.0 --port 8000 && \
    \
    streamlit run app_frontend.py --server.port 8501 --server.enableCORS=false \
    "]
