# HEAMON — Multimodal Contactless Health Monitoring

**Experimental webcam-based monitoring of cardiovascular, ocular, and respiratory signals.** Created as a research prototype for the NASA Space Apps Challenge 2026 astronaut health-monitoring theme.

> **Research prototype, not a medical device.** Blood pressure values, heart-rate estimates, breathing-rate estimates, and fatigue/drowsiness scores from a webcam are **not clinically validated**. Never use HEAMON for diagnosis, treatment, fitness-for-duty decisions, or safety-critical monitoring.

## Features

HEAMON provides an **English-first interface with an English / Español switch**. Both dashboards share one browser-controlled camera, requested at 1920 × 1080 and 30 FPS (actual performance depends on your hardware).

| Module | Outputs | Implementation and limitations |
| --- | --- | --- |
| Cardiovascular | Heart rate (BPM), spectral peak concentration, rPPG waveform, experimental systolic/diastolic blood pressure (SBP/DBP) | RGB facial rPPG + spectral analysis + optional pre-trained LSTM from Schrumpf et al. **The LSTM was trained on contact PPG; accuracy on webcam-derived rPPG is unverified.** |
| Eye behavior / fatigue indicators | EAR, approximate PERCLOS, blink count/rate, mean eye-closure duration, head movement, heuristic index | MediaPipe landmarks + time-based rules. Weights and thresholds are **demonstration parameters, not validated clinical scales**. |
| Breathing | Estimated breaths per minute, observed cycles and quality | Experimental vertical optical flow of the torso, with luminance as backup. Sensitive to framing, clothing and motion. |
| FatigueSense (optional) | CNN-based eye/mouth scores and temporal BiGRU focus score | Requires separate third-party code/checkpoints, subject to dependency compatibility and real-world testing. Focus score is not a clinical fatigue measurement. |

The heuristic fatigue index assigns breathing a **15% demonstration weight** when adequate signals are available. The original FatigueSense BiGRU **does not include our breathing signal**. These outputs remain separate.

## Project structure

```text
index.html                 Shared camera and EN/ES language selector
heamon_i18n.js             Local UI translations and live status translation
camara_dashboard.html      Cardiovascular tab
fatiga_respiracion.html    Visual-fatigue and breathing tab
servidor_camara.py         Local HTTP server and inference endpoints
presion_arterial/          Signal processing and optional trained-model adapter
fatiguesense_bridge.py     Optional FatigueSense adapter
descargar_checkpoint.py    Obtain research checkpoint from Zenodo
requirements.txt          Core dependencies
requirements_dl.txt       Legacy deep-learning dependency guidance
README_INICIO.md          Additional setup details
README_MODELO_FABIAN.md   Pressure-model details
docs/DATASETS.md            Research dataset references
tests/                      Pipeline tests
```

## Quick start — Windows PowerShell (Python 3.13)

```powershell
cd "C:\Users\User\Downloads\NASA 2026\prueba_2\Presion-Arterial"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install "tensorflow==2.20.0" "tf-keras==2.20.1"
.\.venv\Scripts\python.exe descargar_checkpoint.py
$env:TF_USE_LEGACY_KERAS = '1'
.\.venv\Scripts\python.exe servidor_camara.py --fabian-model modelos\lstm_ppg_nonmixed.h5
```

Open **http://127.0.0.1:8765/index.html** and allow camera access. The interface starts in **English** unless the browser has previously saved your choice of Spanish. Use **Language / Idioma** in the top bar to switch languages immediately. Reload the page if you need a clean analysis session.

The model may require a compatibility adjustment to load legacy Keras `.h5` data. It was successfully loaded in the user's Windows environment using TensorFlow 2.20 and `TF_USE_LEGACY_KERAS=1`, but the current distribution has not been medically validated.

### Optional FatigueSense

```powershell
New-Item -ItemType Directory -Force terceros | Out-Null
git clone https://github.com/Fatigue-Sense/fatigue-sense.git terceros\fatigue-sense
.\.venv\Scripts\python.exe -m pip install -r terceros\fatigue-sense\requirements.txt
$env:TF_USE_LEGACY_KERAS = '1'
.\.venv\Scripts\python.exe servidor_camara.py --fabian-model modelos\lstm_ppg_nonmixed.h5 --fatiguesense-root terceros\fatigue-sense
```

**Note:** optional third-party models can have conflicting requirements; FatigueSense inference has not been verified in this environment. The eye-landmark and breathing modules remain available without it.

## Why these signals?

- **Heart rate:** pulse-related skin-color fluctuations can be approximated using remote photoplethysmography (rPPG).
- **SBP / DBP:** exploratory regression from pulse waveform to blood-pressure reference readings; the source and target signal modalities differ, requiring independent validation.
- **EAR and PERCLOS:** quantify eye aperture and proportion of detected closed-eye time, often studied as visible signs associated with drowsiness.
- **Blink rate / closure duration:** complementary, non-diagnostic eye-behavior measures.
- **Head movement:** posture/motion cue and capture-artifact indicator.
- **Breathing rate:** non-contact physiological context. Breathing patterns vary for many reasons other than fatigue and must not be treated as a diagnostic label.

## Research datasets and references

- [Schrumpf et al., blood-pressure prediction with PPG/rPPG](https://github.com/Fabian-Sc85/non-invasive-bp-estimation-using-deep-learning) — source of the optional LSTM checkpoint (research project distributed under GPL-3.0).
- [Schrumpf model artifacts on Zenodo](https://zenodo.org/records/5590603) — download and provenance of `lstm_ppg_nonmixed.h5`.
- [MediaPipe Face Landmarker](https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker) — landmark tracking.
- [FatigueSense](https://github.com/Fatigue-Sense/fatigue-sense) — optional CNN and BiGRU integration; third-party weights and licenses must be checked individually.
- [J0R0W/Breathing](https://github.com/J0R0W/Breathing) — *technical reference only*, not copied into HEAMON.
- [rPPG-Toolbox](https://github.com/ubicomplab/rPPG-Toolbox) and [UBFC-rPPG](https://sites.google.com/view/ybenezeth/ubfcrppg) — future evaluation of pulse estimation.
- [COHFACE](https://www.idiap.ch/en/scientific-research/data/cohface) — research dataset with physiological recordings.
- [UTA-RLDD](https://sites.google.com/view/utarldd/home) — video dataset for studying drowsiness-related behaviors.
- [NASA Human Research Program — Spaceflight Hazards](https://www.nasa.gov/hrp/hazards/) — application context, not model-training data.

These external datasets are **references or prospective validation resources**, not necessarily datasets used to train the models shipped with HEAMON. Subject-independent testing and comparison against reference instruments are still required.

## Reproducibility and testing

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The project's pipeline has been tested on synthetic signals. These tests are **software checks, not evidence of clinical accuracy**. Actual capture FPS, facial-lighting effects, error statistics against synchronized reference instruments, and generalization across participants have not been established.

## Privacy, license, and attribution

The camera stream stays in the browser. The cardiovascular module sends RGB averages/timestamps to the **local Python server**; when optional FatigueSense is enabled, reduced JPEG frames are sent to that same local server. MediaPipe dependencies are initially downloaded from external sources. Avoid storing or publishing face recordings or physiological data without appropriate consent and review.

Do not upload `.venv/`, downloaded weights (`modelos/`), datasets, videos, API secrets, or third-party repositories: these are excluded by `.gitignore`. Review upstream licensing and attribution, especially the GPL-3.0 terms of the blood-pressure research code, before choosing an overall redistribution license.

## Status

**Implemented:** shared camera UI; EN/ES interface; cardiovascular estimators; optional legacy BP checkpoint adapter; eye/respiration heuristics; FatigueSense adapter.

**Not demonstrated:** clinical BP accuracy, validated fatigue diagnosis, reliable breathing under all movement conditions, astronaut-specific validation, or fully tested FatigueSense performance across devices.
