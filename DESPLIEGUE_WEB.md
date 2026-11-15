# HEAMON on the web — Docker / Render

## Goal
A visitor opens an HTTPS URL and permits the webcam. **No Python installation is needed on the visitor computer**. The existing Python signal analysis runs on the web server; the browser performs facial tracking and sends RGB averages/timestamps to `/api/estimate`. The base eye/breathing module executes in-browser; optional FatigueSense is **not** included in the minimal web image.

## What changed (and what did not)
- Preserved `infer()` rPPG / BPM / LSTM inference and all HTML/JS algorithms, including the English/Spanish switch.
- Added `--host` and `PORT` support, while keeping localhost the default for Windows.
- Restricted downloadable paths to the four browser assets; source code, models, `.env` and datasets are not served.
- Added same-origin check for API requests and a 2-request concurrency limit.
- Added `GET /api/health` for the host's health check.
- Container is configured with Python 3.13, TensorFlow 2.20.0 and tf-keras 2.20.1.
- Downloads and checksum-verifies the external Schrumpf LSTM artifact at Docker build time. Check its license/terms before deployment. **The Docker build requires Internet access to Zenodo and will fail if the download fails.**
- Kept `--low-fps` enabled for cloud run to permit the experimental 7–12 FPS mode, with the existing cautionary messages.

## Publish on Render
1. Commit these files to a **separate branch** (e.g. `web-deployment`) first to preserve the known-good local release. Do not upload `.venv/`, local model weights, recordings or datasets.
2. On Render choose **New > Web Service > Build and deploy from a Git repository**, then select `EduHerreraC13/Presion-Arterial` and the deployment branch.
3. Select **Docker** runtime; the repository root contains `Dockerfile`.
4. Choose a compute plan with **at least 2 GB RAM as a starting point** (1c-2g on Render). This is a starting recommendation, not a measured minimum. Free / 512 MB plans are unlikely to accommodate TensorFlow reliably. Costs apply; check current Render prices before confirming.
5. Health check path: `/api/health`. The platform automatically provides TLS/HTTPS and a `PORT`; no local Python is needed for viewers.
6. Deploy. Build installs inference requirements and fetches the checkpoint. After deploy, open the generated HTTPS URL, allow camera, and test both tabs.

## Local smoke test (if Docker Desktop is installed)
```powershell
docker build -t heamon-web .
docker run --rm -p 10000:10000 heamon-web
```
Open http://localhost:10000/ and test the camera. On Windows `localhost` is a secure context for webcam permissions.

## Existing local Windows startup still works
```powershell
$env:TF_USE_LEGACY_KERAS='1'
.\.venv\Scripts\python.exe servidor_camara.py --fabian-model modelos\lstm_ppg_nonmixed.h5 --low-fps
```
It still binds to 127.0.0.1:8765 by default and the original inference behavior is preserved.

## Limitations and safeguards
- **Experimental research demonstration only**, not for medical diagnosis, health decisions or safety-critical monitoring. The LSTM was trained with contact PPG; predictions from webcam signals remain unvalidated.
- The cardiovascular endpoint receives RGB samples and timestamps; the optional FatigueSense endpoint accepts JPEG frames only if explicitly enabled, which is not part of this Docker image. Treat all submitted health-related information as sensitive, use a privacy notice and informed consent before inviting participants.
- The webcam can be opened from the public site because Render serves HTTPS; MediaPipe vision WASM/model still download from external CDNs at first use.
- The current server uses a Python thread-per-request HTTP server and a global model instance, not a mature multi-tenant clinical backend. A two-request semaphore limits concurrent inference but **does not replace** rate limiting, abuse protection, authentication, monitoring or a server architecture designed for many concurrent users.
- Protect the public URL during early testing or add an authentication gateway before sharing broadly. Limit concurrency to one or a few trusted evaluators; more serious deployment warrants replacing the serving layer with a hardened production web framework.
- Hosting RAM/CPU may bottleneck throughput. High frame-rate analysis occurs in the visitor browser and could still produce low effective FPS.
- Availability and resource requirements have not been verified on Render from this environment.
