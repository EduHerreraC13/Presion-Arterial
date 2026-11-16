# Experimental spectral cardiovascular frequency

**Status: isolated research branch. Not merged into `web-roi-ampliado`.**

This branch is an intentionally cautious alternative to YanqhayCare's fast, raw live FFT readout, created after manual experiments reported jumps such as 86 → 50 → 70 → 130 → 140 BPM even under direct illumination and minimal head motion.

## What changes

1. **Keep the existing 15 forehead + 4 cheek ROIs** (19 polygons in total), their FaceLandmarker tracking, spatial channel aggregation and landmark EMA. No changes to breathing or anthropometry.
2. Preserve camera updates roughly every **2 seconds** and an initial **~9-second** signal accumulation window.
3. Ask the backend for the quality-gated spectral estimator using `mode: 'spectral_experimental'`. The old unfiltered `mode: 'live'` path remains available in the code and in the **main branch**, but is not used by this experiment's UI.
4. The existing backend estimator applies log-parabolic spectral peak refinement, concentration/SNR thresholds, and (after ~18 seconds) consistency among 18- and overlapping 12-second windows.
5. Introduce additional **client-side temporal consensus**: two mutually consistent quality-gated candidates must arrive before the very first BPM is displayed; abrupt new candidates more than 18 BPM from the last accepted value must also be repeated within 7 seconds and agree within 10 BPM.
6. Detect large frame-to-frame translation of the nose relative to face width (threshold 0.055). When motion is detected, discard the **current acquisition buffer** and gather a fresh window; do not smooth corrupted RGB into a plausible-looking signal.
7. Explicit statuses: provisional `~`, accepted (no suffix), held `·` for the previous accepted reading for at most eight seconds, verifying, or unavailable. A held BPM is never added to the 15-second medians.
8. Preserve the two cardiovascular readouts and the **15-second median**, but only newly accepted experimental readings contribute to median BPM/quality. Experimental BP is only presented from quality-confirmed spectral backend results and is not fabricated when the checkpoint is unavailable.
9. Update English/Spanish headings and explanations on the cardiovascular view.

## Tradeoffs and non-goals

This branch prioritizes rejecting implausible spectral changes over displaying a number continuously. It can require **longer initial acquisition**, display more blank/held values, or reset after excessive motion. It is a deliberately different operating mode, not necessarily a universal improvement.

A passing spectral quality threshold is **not clinical validation**, and these modifications do not establish ±6–8 BPM error. Constant-frequency artifacts, strong lighting flicker or repeated harmonics can sometimes pass basic consistency checks. If a person genuinely changes heart rate rapidly, the temporal gate may delay the display of that change.

No raw face video is uploaded to the /api/estimate endpoint; it receives aggregated RGB time series.

## Test plan (compare with the main branch, without merging)

1. Run `python -m pytest -q tests/test_experimental_spectral_cardio.py` and the existing tests.
2. Deploy this experimental branch **separately**, or run it on localhost. A branch alone does not modify an existing Render deployment configured for `web-roi-ampliado`.
3. Do the same stationary, low-motion, and fixed-light tests on both versions using similar camera conditions. Keep the forehead and both cheeks visible.
4. Compare simultaneously with a pulse oximeter or other verified heart-rate reference. Record MAE, median absolute error, percentage of windows with a fresh BPM, 20+ BPM jumps, and total periods where the reading was unavailable or held.
5. If stability improves but reference error does not, do not adopt the change. If the system suppresses genuine heart-rate changes, adjust the gate only after reference-based analysis.

**Safe rollback:** remain on `web-roi-ampliado`; this experimental branch has no effect on it unless a pull request is explicitly merged.
