# HEAMON cardiovascular: fast + quality-gated hybrid (experimental)

**Motivation:** The old `web-deployment` showed early continuous updates from a small forehead ROI but could jump ~40 BPM. The later `web-roi-ampliado` already sampled 15 forehead + 4 cheek sectors (landmark EMA and weighted medians) and gated BPM, but the UI submitted only 450 frames: at 30 FPS that is **15 seconds**, less than the backend's required 18-second window. This prevented normal confirmation.

The VitaSense repo contains landmark EMA, forehead and cheek ROIs, log-parabolic spectral peak refinement, an SNR heuristic and quality-aware scalar tracking. No independent test here supports any universal ±6–8 BPM error claim.

## Hybrid design

- **Camera capture:** preserve existing HEAMON 15 forehead + 4 cheek sectors, with landmark smoothing only (never artificially flatten RGB pulse).
- **Data transfer:** retain up to 24 seconds of RGB traces and post up to 800 samples every ~2 seconds after ~9 seconds; capture remains asynchronous. On normal 30 FPS that permits the full 18-second confirmation window.
- **Early state (~9s):** `hr_state=provisional` with `bpm` only if a short 9-second spectral peak has adequate signal concentration/SNR. The UI labels the value with **~**. It is not confirmed.
- **Confirmed state (18s+):** `hr_state=confirmed` only if an 18-second peak agrees with overlapping 12-second segments to within 12 BPM and passes stronger signal checks. The UI's temporal anti-jump logic still requires repeat candidates for large steps.
- **Weak signal:** `hr_state=unavailable` and `bpm=null` (not zero). The UI may show the most recent accepted value for no longer than ten seconds, marked **·**, or show "Signal unavailable" when outdated.
- **Blood pressure:** only present the research BP model's output alongside a freshly confirmed BPM; never treat a provisional or held estimate as a confirmed medical result.
- **Languages:** newly introduced status messages have English/Spanish variants.

## Important technical trade-offs

A display that updates often is not necessarily accurate. The fast number is explicitly provisional; a high-confidence value can take longer or may not be available. Spectrum concentration, SNR and agreement are **quality heuristics**, not a confidence interval. Overlapping windows are correlated. Even confirmed results are not clinically validated.

The detector is intentionally not forced to produce BPM from weak signals. No 6–8 BPM maximum error guarantee is possible without measuring against synchronized reference readings.

## Validation

1. Run `pytest -q tests/test_hr_stability.py` and the existing test suite; test all branches of the API on the deployment.
2. Verify first plausible provisional reading around 9–12 seconds under clean lighting and frequent refresh every ~2 seconds. In low-FPS mode a 9-second window needs at least 60 RGB samples.
3. Verify confirmed status after >=18 seconds when signal quality supports it.
4. Compare simultaneous readings over 2 minutes against a real pulse oximeter and report median/mean absolute error, valid-window percentage, and proportion of held/provisional/confirmed readings.
5. Stress test head movements, intermittent face loss, camera exposure changes, 7–12 FPS and 30 FPS. Treat false steadiness as a failure, not an improvement.

**Review status:** source updated and synthetic math checked separately; full integration, CI, live-camera, and reference measurements are still required before claiming gains.
