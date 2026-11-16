# Cardiovascular ROI & BPM stabilization — VitaSense-inspired patch

Target: `web-roi-ampliado`. Changes are isolated in `feature/cardio-vitasense-stability`.

## Source comparison

- `web-deployment`: single narrow forehead rectangular ROI; immediate per-window FFT peak. Both were vulnerable to spatial noise and spectral peak switches.
- `web-roi-ampliado`: **already** uses 15 forehead tiles and 4 cheek tiles, median RGB per group, weights 60/20/20, and a presentation-only median/confirmation filter.
- `braytwing/VitaSense`: MediaPipe mesh polygon and cheeks, temporal EMA of facial landmark positions, YCrCb skin mask (potentially camera/skin dependent), interpolated FFT peak, SNR heuristic and quality-dependent scalar tracking. These are research design patterns, not certified accuracy claims.

## Applied

1. Keep the existing 15 forehead + 4 cheek polygons, which already have broader coverage than the original branch; do not expand into hair, glasses or background.
2. EMA on *landmark coordinates only* (0.55 current + 0.45 previous), leaving RGB pulse fluctuations unsmoothed. Reset ROI coordinates if face is lost and on camera start/stop.
3. Backend uses an 18-second recent pulse window, 4x zero-padding (minimum 4096 FFT points), log-parabolic peak interpolation, fixed-width concentration and spectral SNR heuristics, and compares two overlapping 12-second segments. If the peaks disagree by >15 BPM or the signal is weak, BPM is returned as `null`.
4. Front-end warm-up now matches the 18 s window. Existing display-only anti-jump check remains and explicitly flags held values.
5. Synthetic regression tests for 72 and 120 BPM, flat/no signal, insufficient duration and sudden frequency changes.

## Limitations

- No claim of improved **accuracy** without independent reference data. Smoother outputs may still be wrong.
- The two 12-second segments overlap; agreement is a consistency heuristic, not an independent validation.
- No skin-color thresholds were introduced, because a fixed YCrCb mask may exclude valid skin appearances or fail under different lighting.
- A sudden real pulse-rate change may not be displayed until enough fresh data agrees; this is a deliberate research trade-off, not suitable for urgent monitoring.
- More quality gating may reduce coverage (number of times BPM is available).
- The BP deep-learning model and the respiratory/anthropometry modules are unchanged.

## Validation plan

Record, for each 2-minute session, simultaneous reference pulse-oximeter BPM and HEAMON BPM with timestamps; test multiple users, camera distances and lighting levels. Report MAE, median absolute error, fraction of valid windows, stale/held-output rate, and 20+ BPM false jumps. Compare old and new code against the same input video with ground truth. Avoid selecting the better algorithm only by visual smoothness.

Run the existing tests plus `pytest -q tests/test_hr_stability.py`, and manual tests of cameras and translations. The current tests are synthetic only; live-camera validation remains pending.
