# HEAMON — Language selection / Selección de idioma

This package is based on the `Presion-Arterial` project provided in `Monitoring_Health.rar`.

- The default language for a new browser profile is **English**.
- Select **English** or **Español** from the top of the main dashboard (`index.html`).
- Your choice is stored in localStorage (`heamon-language`) and is shared with the cardiovascular and fatigue/respiration panels.
- If the dashboard still appears in Spanish after opening the updated version, choose **English** in the selector or clear the saved `heamon-language` key.
- Keep `heamon_i18n.js` beside the three HTML files.
- The Python inference code, checkpoints, sampling, heuristics, and webcam routing are unchanged.
- Start the app from `http://127.0.0.1:8765/index.html`, not directly from the filesystem.

Note: The user interface is translated dynamically. Technical library messages and some third-party errors may remain in their original language. The BP and fatigue outputs remain experimental and are not medical measurements.

## Español

Esta versión conserva la aplicación original y agrega el selector de idioma arriba. El idioma predeterminado en un navegador sin preferencias guardadas es inglés. La elección se conserva al volver a abrir la página. No se modifican los algoritmos ni los modelos.
