# YanqhayCare
### Multimodal Camera-Based Health Awareness for Space Missions

**A camera-first, accessible research prototype that turns ordinary visual observations into useful health and wellbeing indicators for space-mission scenarios.**

YanqhayCare was developed in the context of the **NASA Space Apps Challenge 2026**, addressing the challenge of helping crews observe their condition during demanding missions. Instead of requiring a collection of dedicated measurement devices for every demonstration, it brings several non-contact and visually assisted assessments together in one browser interface.

> **Our mission:** Make it easier to observe, track, and understand changes in a crew member's present condition—quickly, from a camera, with clear on-screen information that supports situational awareness and decisions about when closer assessment may be useful.

The prototype combines **cardiovascular monitoring**, **visual fatigue and breathing observation**, and **anthropometric assessment**. It is designed for demonstrations, education, exploratory testing, and research into future space-health interfaces.

**Research scope:** YanqhayCare provides experimental estimates and observational indicators, **not a clinical diagnosis or an assessment of fitness for duty**. Any medical or mission-critical conclusion requires properly validated instruments, professional interpretation, and suitable operational protocols.

## Experience at a glance

| Module | What it helps you observe | Main interaction |
| --- | --- | --- |
| **1. Cardiovascular** | Estimated heart rate (BPM), signal quality, an rPPG waveform, and optional experimental blood-pressure model outputs | Face the camera in steady light and let the signal accumulate |
| **2. Visual Fatigue & Breathing** | Blinks, eye closure, head movement, a contextual fatigue-related index, and estimated breathing rate | Keep the face and upper torso visible and run the timed analysis |
| **3. Anthropometry** | Approximate camera-to-band distance, body height, arm length, band position and orientation, and repeatable color-marker calibration | Wear a known-size colored reference band; use the camera or upload photos/videos |

All three modules are available from the same home page. The interface **starts in English** in a new browser session; **Español** is available via the language selector. Your selection can be remembered by the browser.

## The challenge and our approach

Understanding health and physical condition becomes particularly important in constrained environments such as a spacecraft, where time, equipment, space, and connectivity can be limited. YanqhayCare explores a complementary solution: a single visual workspace that combines several indicators without interrupting the user's activity more than necessary.

**The workflow is intentionally simple:**

1. Open YanqhayCare on a device with a browser and camera.
2. Choose the aspect of health or physical condition to observe.
3. Follow the short capture instructions.
4. Review measurements, quality indicators, and changes over the session.
5. Repeat the observation or seek a reference measurement when a signal is uncertain.

Rather than treating one camera estimate as a definitive diagnosis, the interface helps users **notice patterns**, **interpret measurement readiness**, and **recognize when additional evaluation may be needed**.

## Getting started

### Option A — Hosted web application

Open the project's deployed website, if available. Select **English** or **Español** in the top-right language menu. Allow camera permission when prompted.

- **Start shared camera** activates the main browser camera for the cardiovascular and visual fatigue/breathing modules.
- **Stop** releases that shared camera.
- Switch between **Cardiovascular**, **Visual Fatigue & Breathing**, and **Anthropometry** using the three numbered tabs.
- Anthropometry has its **own camera and file controls**. If the camera is busy, stop the shared camera before starting anthropometry's camera.

For browser camera permissions, use an **HTTPS** website or **localhost**. MediaPipe models and client libraries are downloaded when first needed; an initial internet connection is typically required. Once loaded, camera-based analysis takes place in the browser or project backend, depending on the module.

### Option B — Run the project locally

**Requirements:** Python 3.13, a compatible browser such as Chrome or Edge, a webcam or supported video file, and internet access for the initial model/dependency setup.

The project's web-specific dependencies can be installed in a virtual environment:

```bash
git clone https://github.com/EduHerreraC13/Presion-Arterial.git
cd Presion-Arterial
git switch web-roi-ampliado
python -m venv .venv
```

On **Windows PowerShell**:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements_web.txt
.\.venv\Scripts\python.exe servidor_camara.py
```

On **Linux/macOS**:

```bash
./.venv/bin/python -m pip install -r requirements_web.txt
./.venv/bin/python servidor_camara.py
```

Then open **http://127.0.0.1:8765/index.html**.

The core modules can run without the optional blood-pressure checkpoint. To experiment with that separate model, see [README_MODELO_FABIAN.md](README_MODELO_FABIAN.md) and [DESPLIEGUE_WEB.md](DESPLIEGUE_WEB.md). Model installation and legacy deep-learning dependencies can vary by platform.

### Option C — Docker deployment

The included `Dockerfile` provides a web deployment path used by the project. It packages the home page, the three module pages, their language assets, and the Python inference backend. See [DESPLIEGUE_WEB.md](DESPLIEGUE_WEB.md) for deployment information.

The deployment can download the optional research blood-pressure checkpoint during image construction; this may increase build time, image size, and resource requirements.

---

## Module 1 — Cardiovascular monitoring

### Purpose

Observe a pulse-related optical signal using **remote photoplethysmography (rPPG)**. Subtle changes in reflected light from the skin are sampled over time to estimate a heart-rate frequency, displayed in **beats per minute (BPM)**.

### How to use it

1. Open **1 · Cardiovascular**.
2. Start the shared camera from the top bar, or activate the camera inside the module.
3. Face the camera and keep the **forehead and cheeks unobstructed**.
4. Use relatively even, stable lighting and minimize unnecessary head movement.
5. Allow roughly **9 seconds** of usable signal to accumulate, then watch the **Live Monitoring** figures update approximately every 2 seconds.
6. Compare the live readings with the **Estimated Monitoring — 15-second Median** panel. It refreshes after each 15-second group of received readings.
7. Stop the camera when finished.

### How the readings are produced

YanqhayCare tracks multiple skin regions: **15 sectors across the forehead and four sectors across the cheekbones**. The system combines RGB information from usable regions, stabilizes facial landmark positions, and processes the resulting time series using an rPPG approach.

The cardiovascular screen now offers **two complementary readouts**:

| Panel | Update interval | What it shows |
| --- | --- | --- |
| **Live Monitoring** | Approximately every **2 seconds**, after about **9 seconds** of usable signal | The latest experimental FFT-based heart-rate estimate, spectral peak concentration, and optional experimental systolic/diastolic blood-pressure estimates. These values can change noticeably from update to update. |
| **Estimated Monitoring — 15-second Median** | One new summary for each **15-second** group of received live readings | Separately calculated medians of BPM, spectral peak concentration (%), systolic pressure, and diastolic pressure. Missing values are excluded from each metric. |

**How the median is calculated:** for every available numerical indicator, the application orders that interval's received values and selects the middle one (or the average of the two middle values when there is an even number). For example, BPM readings **80, 90, 120, 40, 50** produce a median of **80 BPM**. This makes the summary less sensitive to occasional extreme values, but **does not establish medical accuracy**.

The **percentage is spectral peak concentration**, a signal-characteristic indicator; it is **not oxygen saturation, confidence in a diagnosis, or percent accuracy**. The blood-pressure fields show a dash if the optional research checkpoint is unavailable or does not produce a usable estimate. The median does not fill in missing values with invented numbers.

Because the live panel follows the fast, minimally gated FFT-style output of the earlier web implementation, it is expected to be more responsive and also **more variable**. The median provides a convenient temporal summary, not a more advanced or independent measurement. The previous quality-gated estimator remains available in the backend for research comparison; this dashboard uses live mode.

**Experimental blood pressure:** SBP/DBP requires a compatible optional research checkpoint trained on contact PPG signals. Webcam-derived rPPG is a different modality, so these numbers are exploratory estimates and are not equivalent to a cuff measurement. No part of this feature should be used to diagnose a medical condition or make an operational safety decision.

---

## Module 2 — Visual fatigue and breathing

### Purpose

Provide an accessible snapshot of visual behavior and breathing-related patterns that may be relevant when observing comfort, attentiveness, and wellbeing during a session.

The camera-derived indicators include:

- **Blink count and blink rate**
- **Eye Aspect Ratio (EAR)**, eye closure and approximate **PERCLOS**
- **Mean eye-closure duration**
- **Head movement**
- **Estimated breaths per minute**, inferred primarily from visible torso movement
- A **heuristic comparison/index** summarizing the observed signals

### How to use it

1. Open **2 · Visual Fatigue & Breathing**.
2. Start the camera and position your **face and upper torso** within the frame.
3. Stay in consistent lighting, ideally without strong backlighting.
4. Allow the interface to establish its initial baseline, approximately **10 seconds** when capture conditions permit.
5. Select **Start Analysis · 30 s**. Observe the progress bar and avoid unnecessary movement.
6. When the window completes, review the indicator breakdown and the comparison against a previous analysis.
7. Use the session history and advanced metrics to compare changes; optionally enable automatic repeated 30-second analyses.

### Interpreting the output

The module is designed to communicate **observed signal patterns**, not to declare that a person has a medical condition. Differences in blinking, eye aperture, respiratory movement, or head motion can have several explanations, including the lighting, posture, task, and environmental conditions.

A separate, optional **FatigueSense** adapter can contribute pre-trained neural-network eye/mouth scores when its external dependencies and models are installed. Its outputs remain distinct from YanqhayCare's native breathing estimate.

---

## Module 3 — Anthropometry: comprehensive user guide

### Purpose

Anthropometry explores how a regular camera, **a visible two-color reference band of known physical dimensions**, and an AI body-landmark model can estimate geometric measurements. It can be used to demonstrate body-position-aware measurements without specialized distance sensors.

The module can display **distance to the reference band, estimated height, shoulder-to-wrist arm length, image position, band orientation**, and information about calibration and the reliability of the detected marker. It also accepts **recorded photos and videos**, making it especially useful for repeatable demonstrations.

### Before you begin: prepare the reference band

The detector expects a **reference band with two colored stripes and a central neutral/checker section**. The band wraps around the arm, so the entire design does not need to face the camera at once. Its measured **height along the arm** provides a physical scale in the image.

- Use the specific printed band corresponding to the detection palette, preferably the **green/pink printed** design if that matches your demonstration material.
- **Measure the actual total height of the physical band** and enter it in the **Band total height (mm)** setting. The software's default is **145 mm**; use that value only when your physical band truly matches it.
- Place the band where the camera can distinguish both colored stripes, with moderate contrast and no strong glare.
- For body-height observations, stand where the camera can see as much of the body as possible, including head and feet.
- If the band is noticeably nearer to the camera than the person's torso, its image scale may differ from the scale of the body; the module includes an optional depth-correction control.

**A reference object is essential:** camera pixels alone do not determine real-world centimeters reliably. Incorrect band dimensions or a poor calibration will affect all derived distances and lengths.

### Step-by-step: live camera measurements

1. Open **3 · Anthropometry** in the main YanqhayCare interface.
2. If the shared camera is active and the new camera fails to start, select **Stop** in the top bar first.
3. Under the module's camera controls, choose **Automatic camera** (or select laptop webcam, phone rear camera, or front camera as appropriate).
4. Press **Start camera** and allow the browser to access the camera.
5. In **Colors & Detection**, select the palette that matches the printed band. The detector has presets, including printed green/pink and several brighter or pastel combinations.
6. Check the **Band total height (mm)** value in **Distance & Height Calibration** and replace the default with your measured band size when necessary.
7. Position the band in view and look for the detector's colored overlay and status information. Try steadier lighting or adjust the palette if the marker is not detected.
8. Enable **Body AI (MediaPipe Pose Landmarker)** when you want height and skeleton-based body measurements. The first activation can require the model to download.
9. Keep the body and band visible, remain fairly still, and inspect the **Result** and **Distance & Height** panels.

The detector shows useful context such as marker position, visible width, band height, orientation, matching score, and consistency. **A visible result is an estimate**, not a guarantee of accurate scale.

### Step-by-step: calibrate distance

This is one of the most important steps for more meaningful measurements.

1. Measure the **real distance between the camera and the band** using a tape measure.
2. Enter that distance in **Measured real distance (cm): camera to band**.
3. Wait until the marker is detected clearly and **Add point** becomes available.
4. Click **Add point** to save the distance reference.
5. Repeat from **two or three known distances** when practical, for example 50, 100, and 150 cm, while maintaining stable capture conditions.
6. Review the calibration-point list and its indicated errors. Remove a point if it was captured during poor detection, and recalibrate if the camera setup changes.

The program estimates the effective camera focal scale using the stored reference points. Recalibrate when changing the camera, its zoom/FOV, or the physical marker.

### Step-by-step: estimate body height

1. Turn on **Body AI**.
2. Enable **Measure head-to-feet with silhouette** for a direct whole-body estimate where supported.
3. Fit the **entire person** into the frame, with a little margin above the head and below the feet.
4. Keep the camera relatively level, avoid excessive perspective distortion, and enter the **camera pitch** if known.
5. Enter a **shoe-height correction** if appropriate; 0 cm is intended for barefoot measurements.
6. Maintain a similar camera depth for the band and body when possible. If not, explore the **Body depth correction** setting and compare results with measurements taken at a known distance.
7. If the actual height of a reference person is known, enter it in **Actual height (cm)** and use **Calibrate height** once a valid estimate is available.
8. Read the resulting **estimated height** together with the measurement status and the **How it was calculated** section.

When the entire silhouette cannot be observed, the program may fall back to a **body-proportion estimate**. That method is more sensitive to individual anatomy, posture, and perspective.

### Step-by-step: use the extended-arm method

The detector also supports an alternative when the entire body cannot fit in the picture.

1. Keep **Body AI** enabled and select **Measure with extended arm**.
2. Position the arm so that the shoulder, elbow, wrist, and reference band can be detected clearly.
3. In **Height based on**, choose **Body + arm combined** or **Extended arm only**.
4. If the wrist-to-shoulder pose appears tilted toward the camera, try **Compensate arm tilt using 3D body AI**, then compare the estimate against a known measurement.
5. For personal arm-length calibration, measure the actual **shoulder-to-wrist length in centimeters**, enter it, and use **Calibrate measurement** when enabled.
6. For a personalized arm-to-height proportion, enter an actual height and save the proportion under **Arm-to-height ratio**.
7. Review estimated arm length and height while changing pose carefully.

The default arm-to-height ratio is approximately **0.332** and represents an **approximation**, not a universal anatomical constant. Individual calibration is preferable when measuring a specific person repeatedly.

### Step-by-step: analyze saved photos and videos

This path is ideal for demos, tests, and comparisons of the *same* recording:

1. Click **Photos / videos…** or **Add…** and choose one or several local image/video files.
2. Review the items in the file queue.
3. Select the video analysis sampling rate: **2, 4, or 8 analyzed frames per second**.
4. Click **Process** (or enable automatic processing when adding files).
5. Review the result dashboard, per-file status, and playback/timeline controls. The module analyzes a maximum of **480 frames per video**, spacing samples more widely on longer recordings.
6. Use **Reprocess all** after changing marker colors or calibration settings when the processing requires a fresh analysis.
7. Export results with **Export CSV** or **Export JSON** for further study.
8. For a live-style playback demonstration, use **Video as camera** with a selected video file.

Photos and video files selected by the user are processed locally in the browser by the detector; there is no video-upload endpoint for this anthropometry workflow in the provided implementation.

### Step-by-step: calibrate the band's colors

Printed color often differs from the on-screen reference because of the printer, paper, camera, and illumination.

1. Pause the camera/video or select a clear photo.
2. In **Calibrate colors — eyedropper**, select **Stripe A** and click or drag over its actual printed area.
3. Repeat for **Stripe B**.
4. Choose **Test on this frame** and observe whether the colored stripes are detected more reliably.
5. Save the calibrated colors under a recognizable name, or download the detector's generated JavaScript/JSON/Python color configuration.
6. Use **Reprocess files with these colors** if previous files were processed using another palette.

For repeatable setups, use **Download configuration (.json)** and **Load configuration…**. The configuration can store marker colors, band dimensions, distance calibration, height/arm settings, and related options. Avoid using configurations from a different physical camera/band without checking calibration first.

### What affects anthropometry estimates?

The camera can produce useful geometric estimates when the reference marker is known and the scene is sufficiently visible. The most important factors are: **real marker dimensions, camera perspective, marker visibility, body posture, illumination, camera-to-body distance, and whether the whole body appears in frame**. Using the app's calibration controls helps make repeat observations more meaningful.

---

## Technology and architecture

YanqhayCare is built as a browser-based experience with a Python backend for selected signal-processing and model-inference tasks:

```text
YanqhayCare home (index.html)
├── 1. Cardiovascular (camara_dashboard.html)
│   ├── MediaPipe face landmarks
│   ├── Forehead + cheek RGB sampling
│   └── /api/estimate → Python rPPG / experimental BP
├── 2. Visual Fatigue & Breathing (fatiga_respiracion.html)
│   ├── Eye, face and torso signal processing
│   └── Optional local FatigueSense backend adapter
└── 3. Anthropometry (anthropometry.html)
    ├── Two-color band detection and marker calibration
    ├── MediaPipe Pose Landmarker
    └── In-browser analysis of camera, photos and videos

Shared bilingual interface: heamon_i18n.js + anthropometry-i18n.js
Web server: servidor_camara.py
```

The filenames and a few internal event/API identifiers retain the original project prefix for **backward compatibility**; the product displayed to users is **YanqhayCare**.

### Privacy-oriented design

The system aims to minimize unnecessary transfer of camera content:

- **Cardiovascular:** the browser derives regional RGB means and timestamps. Those numerical signals are submitted to the YanqhayCare Python server, rather than sending raw webcam frames through that endpoint.
- **Visual fatigue and breathing:** core visual processing is local to the browser. If optional FatigueSense is enabled, reduced JPEG frames may be sent to the project's own backend for model inference.
- **Anthropometry:** selected images/videos and live frames are analyzed in the browser; exports are initiated by the user.
- **External dependencies:** some MediaPipe code/models require a first-time download over the internet. The deployment's server may be remote, so the privacy boundary depends on where it is hosted.

Avoid collecting or sharing identifiable participant recordings without consent.

## Scope, current strengths, and opportunities for improvement

**Current strengths**

- Three complementary modules in one navigable camera-first interface.
- No specialized pulse sensor required to demonstrate visual pulse and breathing research methods.
- Wider facial sampling, quality-aware BPM status, and explicit distinction between early and confirmed algorithmic readings.
- Reusable color-band calibration and video/photo support for repeatable anthropometry demonstrations.
- English-first interface with a Spanish option and configurable local/deployed operation.

**Where further testing will help**

- **Reference comparisons:** establish error statistics for BPM and other estimates against appropriately synchronized instruments.
- **Capture robustness:** investigate a wider range of lighting, motion, skin appearances, cameras, clothing, and distances.
- **Anthropometry calibration:** quantify the effect of marker dimensions, perspective, occlusion, and body-proportion variation.
- **Space-specific conditions:** test in realistic mission settings; Earth-based footage does not automatically establish performance during microgravity or actual astronaut operations.
- **Interpretation:** improve uncertainty displays and evaluate how users understand provisional versus quality-checked estimates.

These are development and validation opportunities, not reasons to overlook the prototype's value as a fast, integrated **health-awareness concept**.

### Medical and operational use

YanqhayCare is a **research demonstration**. It does not detect disease or provide a verified clinical diagnosis. A result that passes internal quality checks is **not** proof of a specific accuracy margin. If observations suggest concern, obtain an appropriate reference measurement and follow established medical or mission protocols.

## Further reading and acknowledgments

- [NASA Human Research Program — Spaceflight Hazards](https://www.nasa.gov/hrp/hazards/) — motivation and mission-health context.
- [Google MediaPipe Face Landmarker](https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker) and [Pose Landmarker](https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker) — facial and body landmarks.
- [VitaSense by braytwing](https://github.com/braytwing/VitaSense) — reference for rPPG ROI tracking and quality-aware heart-rate estimation patterns.
- [Schrumpf et al., non-invasive BP estimation research](https://github.com/Fabian-Sc85/non-invasive-bp-estimation-using-deep-learning) and [Zenodo model artifacts](https://zenodo.org/records/5590603) — optional experimental BP checkpoint.
- [FatigueSense](https://github.com/Fatigue-Sense/fatigue-sense) — optional third-party eye/mouth and temporal-model integration.
- [rPPG-Toolbox](https://github.com/ubicomplab/rPPG-Toolbox) — research reference for remote pulse analysis.

Third-party resources remain subject to their respective license and model-use terms. Their inclusion as references does not imply endorsement or clinical verification.

## Project files and testing

| Path | Purpose |
| --- | --- |
| `index.html` | YanqhayCare navigation, shared camera, language selector |
| `camara_dashboard.html` | Cardiovascular UI, facial regions and signal collection |
| `fatiga_respiracion.html` | Eye-behavior and breathing monitor |
| `anthropometry.html` | Color-band detector, calibration, body/arm assessment |
| `anthropometry-i18n.js` | Anthropometry English/Spanish text |
| `heamon_i18n.js` | Main and legacy-module English/Spanish text; original internal filename preserved |
| `servidor_camara.py` | Python web server and selected inference endpoints |
| `presion_arterial/hr_stability.py` | Fast provisional and quality-gated HR spectral estimator |
| `tests/` | Software regression checks and research pipeline tests |
| `Dockerfile` | Reproducible deployment configuration |

To run tests after installing development dependencies:

```bash
python -m pytest -q
```

Unit tests check software behavior using synthetic or controlled inputs. **They are not a substitute for studies with real participants and reference instruments.**

---

**YanqhayCare — making camera-based health awareness more approachable for the next generation of space missions.**
