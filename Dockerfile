# The interpreter and ML packages live on the server, not the visitor's PC.
FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TF_USE_LEGACY_KERAS=1 \
    TF_CPP_MIN_LOG_LEVEL=2 \
    OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    TF_NUM_INTRAOP_THREADS=1 \
    TF_NUM_INTEROP_THREADS=1 \
    PORT=10000
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY requirements_web.txt ./
RUN python -m pip install --no-cache-dir -r requirements_web.txt
COPY servidor_camara.py descargar_checkpoint.py ./
COPY presion_arterial/ ./presion_arterial/
COPY index.html camara_dashboard.html fatiga_respiracion.html heamon_i18n.js anthropometry.html anthropometry-i18n.js ./
# Original research artifact is downloaded at build time, checksum checked.
# This makes the checkpoint available without committing the pretrained weights to Git.
ARG INCLUDE_BP_MODEL=1
RUN if [ "$INCLUDE_BP_MODEL" = "1" ]; then python descargar_checkpoint.py; fi
EXPOSE 10000
CMD ["sh", "-c", "python servidor_camara.py --host 0.0.0.0 --port ${PORT:-10000} --low-fps --fabian-model modelos/lstm_ppg_nonmixed.h5"]
