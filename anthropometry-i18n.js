/* Anthropometry language layer. Default: English; switch: Español.
   The original measurement algorithm remains untouched. */
(() => {
 'use strict';
 const translations = {
  "Detector de banda · distancia y estatura": "Anthropometry · distance and height",
  "v9 · cámara, fotos y videos + IA de cuerpo (MediaPipe Pose Landmarker)": "v9 · camera, photos and videos + body AI (MediaPipe Pose Landmarker)",
  "La banda se enrolla en el brazo: nunca se ve completa, pero": "The band wraps around the arm: it is never fully visible, but",
  "su alto no se deforma": "its height remains unchanged",
  ". Por eso se mide el alto de las dos franjas de color y la separación entre ellas. Carga las fotos o videos que quieras: se procesan en tu equipo y nada se sube a internet.": ". That is why the system measures the two colored stripes and the gap between them. Your photos and videos are processed locally; the application does not upload them.",
  "Sin fuente de video": "No video source",
  "Suelta aquí tus fotos o videos": "Drop your photos or videos here",
  "Iniciar cámara": "Start camera",
  "Detener": "Stop",
  "Cámara automática": "Automatic camera",
  "Laptop / webcam": "Laptop / webcam",
  "Celular · trasera": "Phone · rear camera",
  "Celular · frontal (selfie)": "Phone · front camera (selfie)",
  "Vertical 9:16 (TikTok)": "Vertical 9:16 (TikTok)",
  "Cambiar cámara": "Switch camera",
  "Pausar": "Pause",
  "Video como cámara": "Video as camera",
  "Fotos / videos…": "Photos / videos…",
  "Elegir color A": "Pick color A",
  "Elegir color B": "Pick color B",
  "Regla (2 clics)": "Ruler (2 clicks)",
  "Ver máscara": "Show mask",
  "Repetir video-cámara": "Loop video camera",
  "Archivos · fotos y videos": "Files · photos and videos",
  "Agregar…": "Add…",
  "Procesar": "Process",
  "Reprocesar todo": "Reprocess all",
  "Quitar todo": "Remove all",
  "Exportar CSV": "Export CSV",
  "Exportar JSON": "Export JSON",
  "Muestreo de video (fotogramas analizados por segundo)": "Video sampling (frames analyzed per second)",
  "2 por segundo – rápido": "2 per second – fast",
  "4 por segundo – normal": "4 per second – normal",
  "8 por segundo – fino": "8 per second – detailed",
  "Máximo 480 fotogramas por video: en videos largos se espacian más. Más fotogramas = más precisión y más tiempo.": "Maximum 480 frames per video; long videos are sampled more sparsely. More frames may improve measurement stability but require more processing time.",
  "Procesar automáticamente al agregar archivos": "Process files automatically when added",
  "Sin archivos.": "No files.",
  "Sin archivos procesados.": "No processed files.",
  "Panel · distancia y estatura": "Dashboard · distance and height",
  "Copiar datos": "Copy data",
  "Distancia a la cámara": "Distance to camera",
  "Estatura de la persona": "Person height",
  "Referencia y calibración": "Reference and calibration",
  "Cómo se calculó": "Calculation details",
  "Estado": "Status",
  "Ocultar": "Hide",
  "Banda:": "Band:",
  "Cuerpo:": "Body:",
  "Estatura:": "Height:",
  "IA apagada": "AI disabled",
  "Resultado": "Results",
  "Distancia a la banda": "Distance to band",
  "Estatura estimada (promedio de muchas medidas)": "Estimated height (averaged measurements)",
  "Largo del brazo estirado (hombro → muñeca)": "Extended arm length (shoulder → wrist)",
  "Posición X (der +)": "X position (right +)",
  "Posición Y (abajo +)": "Y position (down +)",
  "Ancho visible (≈ Ø brazo)": "Visible width (≈ arm diameter)",
  "Alto de la banda": "Band height",
  "Orientación (A arriba = 0°)": "Orientation (A at top = 0°)",
  "Coincidencia": "Match score",
  "Consistencia (±)": "Consistency (±)",
  "Franja central": "Center stripe",
  "Calibración · distancia y estatura": "Calibration · distance and height",
  "Distancia real medida con cinta (cm): de la cámara a la banda": "Actual tape-measured distance (cm): camera to band",
  "Agregar punto": "Add point",
  "Sin puntos de calibración.": "No calibration points.",
  "Quitar último": "Remove last",
  "Borrar puntos": "Clear points",
  "Agrega 2-3 puntos (p. ej. 50, 100 y 150 cm) con la cámara o con fotos / videos donde la persona esté quieta a una distancia conocida. En un archivo, el punto se agrega con el archivo seleccionado. La focal se ajusta sola con la mediana y cada punto muestra su error.": "Add 2–3 calibration points (e.g., 50, 100 and 150 cm) while the person stands still at a known distance. For files, use the selected file. Focal length is fitted using the median; each point displays its error.",
  "Estatura": "Height",
  "Estatura real (cm, opcional)": "Actual height (cm, optional)",
  "Calibrar estatura": "Calibrate height",
  "Quitar calibración": "Remove calibration",
  "Corregir profundidad del cuerpo (usa el 3D de la IA)": "Correct body depth (uses AI 3D data)",
  "Referencia:": "Reference:",
  "la banda (mide exactamente su alto real) da la escala; el cuerpo solo aporta los píxeles de altura. Si la banda está más cerca de la cámara que el cuerpo (brazo estirado, botella en la mano), la corrección de profundidad ajusta la escala. Si conoces tu estatura real, «Calibrar estatura» elimina el error que quede.": "The known band height establishes image scale; body landmarks provide the height in pixels. Depth correction compensates when the band and body are at different distances. Calibrating against a known height can reduce systematic error.",
  "Ajustes avanzados": "Advanced settings",
  "Alto TOTAL de la banda (mm) · por defecto 145": "TOTAL band height (mm) · default 145",
  "Campo de visión horiz. (°)": "Horizontal field of view (°)",
  "Focal (px a 1280 de lado largo)": "Focal length (px, at 1280 long side)",
  "Corrección distancia (%)": "Distance correction (%)",
  "Ø del brazo (mm, opcional)": "Arm diameter (mm, optional)",
  "Compensar inclinación": "Compensate for tilt",
  "Origen de la focal": "Focal length source",
  "Inclinación del brazo (con Ø)": "Arm tilt (with diameter)",
  "Colores y detección": "Colors and detection",
  "Paleta impresa": "Printed palette",
  "Modo colores opacos / pastel (siempre activo)": "Muted / pastel colors mode (always enabled)",
  "Para bandas de colores apagados (menta, rosa, beige…) y tablero gris claro. Acepta colores poco saturados y menos contraste en el tablero; ignora los colores muy vivos.": "For muted-color bands (mint, pink, beige) and light-gray reference patterns. Accepts less saturated colors and lower contrast; excludes overly vivid colors.",
  "Balance de blancos automático": "Automatic white balance",
  "Corrige el tinte amarillo/azul de la cámara antes de buscar los colores.": "Corrects yellow/blue camera color casts before detection.",
  "Franja A": "Stripe A",
  "Franja B": "Stripe B",
  "° matiz": "° hue",
  "Tu impresora no reproduce el color exacto: usa el": "Your printer may change the exact color: use the",
  "cuentagotas": "eyedropper",
  "de la tarjeta de abajo (o": "in the card below (or",
  ") y haz clic sobre cada franja de la imagen. Es el ajuste que más mejora la detección. En archivos ya procesados, después de cambiar colores pulsa «Reprocesar todo».": ") and click each stripe in the image. This often improves detection. After modifying colors, reprocess previously analyzed files.",
  "Aceptar una sola franja (si la otra está tapada)": "Accept a single stripe (when the other is occluded)",
  "Resolución de análisis": "Analysis resolution",
  "640 px – rápida": "640 px – fast",
  "960 px – equilibrada": "960 px – balanced",
  "1280 px – máximo alcance": "1280 px – maximum range",
  "Restablecer valores": "Reset values",
  "Calibrar colores · cuentagotas": "Calibrate colors · eyedropper",
  "1) Pausa el video (o carga una foto). 2) Elige el cuentagotas de la franja A y haz clic, o pinta arrastrando, sobre esa franja en la imagen. 3) Repite con la franja B. La detección se prueba al instante, y puedes guardar los colores o copiar el código para tu proyecto.": "1) Pause the video (or load a photo). 2) Select the stripe A eyedropper, then click or drag across that stripe. 3) Repeat for stripe B. You can test the detector, save colors, or copy the configuration.",
  "💧 Cuentagotas · franja A": "💧 Eyedropper · stripe A",
  "💧 Cuentagotas · franja B": "💧 Eyedropper · stripe B",
  "Tamaño del pincel": "Brush size",
  "Probar en este fotograma": "Test on this frame",
  "Reprocesar archivos con estos colores": "Reprocess files with these colors",
  "Colores guardados": "Saved colors",
  "Guardar": "Save",
  "Código para tu proyecto": "Code for your project",
  "JavaScript (para este detector)": "JavaScript (for this detector)",
  "JSON (colores)": "JSON (colors)",
  "Configuración completa (JSON por defecto)": "Full configuration (default JSON)",
  "Copiar código": "Copy code",
  "Descargar": "Download",
  "El código siempre refleja los colores que están en uso ahora. Los colores guardados se quedan en este navegador; usa «Usar» para volver a aplicarlos. En la imagen, la franja A se marca en rosa y la B en verde: son colores de marcado, no los de tu banda.": "The code reflects currently selected colors. Saved colors stay in this browser; choose Use to restore them. In the preview, stripe A is highlighted pink and stripe B green; these are overlay colors, not necessarily your band colors.",
  "Configuración · descargar y dejar por defecto": "Configuration · export and defaults",
  "Guarda en un archivo los": "Save a file containing the",
  "colores A y B": "stripe A and B colors",
  "banda (145 mm)": "band (145 mm)",
  "calibración de distancia": "distance calibration",
  "medición del brazo": "arm measurement",
  ", la estatura y las demás opciones. Luego puedes cargarlo otra vez o dejarlo": " , height, and other settings. You can reload it later or set it as the",
  "por defecto": "default",
  "en la página.": "for the page.",
  "Descargar configuración (.json)": "Download configuration (.json)",
  "Cargar configuración…": "Load configuration…",
  "Descargar página con estos valores por defecto": "Download page with these defaults",
  "Volver a los valores por defecto del archivo": "Restore file defaults",
  "Dos formas de dejarlo por defecto:": "Two ways to set defaults:",
  "«Descargar página…» crea una copia de esta misma página que arranca ya con tu configuración.": "“Download page…” creates a copy of this page that starts with your configuration.",
  "En el código de arriba elige «Configuración completa» y pega ese JSON entre las etiquetas": "In the code above, select “Full configuration” and paste that JSON between the tags",
  "de tu archivo. Una configuración nueva por defecto se aplica una sola vez al abrir la página; después tus cambios se siguen guardando en este navegador.": "in your file. A new default configuration is applied on first page load; subsequent changes remain stored in this browser.",
  "Cuerpo · IA (MediaPipe Pose Landmarker)": "Body AI (MediaPipe Pose Landmarker)",
  "Activar IA de cuerpo": "Enable body AI",
  "Detecta el esqueleto (33 puntos) con el SDK Pose Landmarker. La primera vez descarga el modelo de internet. Sirve para limitar la búsqueda al cuerpo y para estimar la estatura. Si hay varias personas, se usa la que está más cerca de la banda.": "Detects 33 pose landmarks using Pose Landmarker. The model must be downloaded on first use. Body landmarks help constrain band detection and estimate height. If several people appear, the subject nearest the band is selected.",
  "Buscar la banda solo dentro del cuerpo": "Search for the band only within the body area",
  "Ignora todo lo que quede fuera de la silueta (cojines, carteles, plantas, fondo). La banda puede estar en cualquier parte del cuerpo.": "Ignores regions outside the subject area (furniture, signs, plants, background). The band may be located anywhere on the body.",
  "Modelo": "Model",
  "Lite – rápido": "Lite – fast",
  "Full – equilibrado": "Full – balanced",
  "Heavy – más preciso, más lento": "Heavy – more detailed, slower",
  "Margen alrededor del cuerpo (% del torso)": "Margin around body (% of torso)",
  "Dibujar esqueleto y zona ignorada (oscurecida)": "Draw skeleton and excluded area (dimmed)",
  "Si no veo el cuerpo, buscar en toda la imagen": "If no body is detected, search the entire image",
  "Altura · de pies a cabeza": "Height · head to feet",
  "Medir de pies a cabeza con la silueta (recomendado)": "Measure head-to-toe using the silhouette (recommended)",
  "En vez de calcular la altura con proporciones del cuerpo (que varían ±5 % entre personas), mide directamente desde la suela / talón hasta la punta de la cabeza usando la silueta que detecta la IA. Si no se ve el cuerpo completo, usa las proporciones como respaldo.": "Instead of relying only on body proportions, measure from heel/sole to the top of the head using the estimated silhouette. If the full body is not visible, fall back to approximate proportions.",
  "Calzado a restar (cm) · 0 = descalzo": "Shoe allowance to subtract (cm) · 0 = barefoot",
  "Inclinación de la cámara (°) · + mira hacia arriba": "Camera pitch (°) · positive = pointing upward",
  "Usar modelo Heavy (más preciso)": "Use Heavy model (more detailed)",
  "Reiniciar promedio": "Reset average",
  "La banda es la regla: convierte los píxeles de la altura (cima de la cabeza → suela) a centímetros. Para la mejor precisión: de pie, recto y quieto; cuerpo completo con margen arriba y abajo; descalzo (o resta el calzado); cámara nivelada a la altura del pecho (si está inclinada, escribe los grados); banda a una distancia parecida a la del cuerpo; modelo Heavy; y calibra la estatura una vez con una persona de altura conocida a la misma distancia. Sin silueta (o con el cuerpo cortado) la altura se aproxima con proporciones y es menos exacta. Con pelo voluminoso o gorro, la cima sube unos cm.": "The band provides a reference scale for converting pixels to centimeters. For more consistent estimates, stand straight and still with the full body in frame, position the camera level, account for shoes, keep the band at approximately the same depth as the body, and calibrate against a known height. Incomplete views, hair and headwear can introduce error.",
  "Brazo estirado · medida con la banda": "Extended arm · band-based measurement",
  "Medir con el brazo estirado": "Measure an extended arm",
  "Cuando la banda está en un brazo recto (al frente, al costado o colgando), se mide el largo del brazo (hombro → muñeca) usando la banda como regla, y con él se estima la estatura. Sirve aunque el cuerpo no se vea completo. Necesita la IA de cuerpo.": "When the band is on a straight arm, measure shoulder-to-wrist length using the band as a scale; body height can then be approximated. This may work with a partially visible body. Requires body AI.",
  "Estatura basada en": "Height estimate based on",
  "Cuerpo + brazo combinados (recomendado)": "Body and arm combined (recommended)",
  "Solo el brazo estirado": "Extended arm only",
  "Codo mínimo para considerar el brazo estirado": "Minimum elbow angle for an extended arm",
  "Compensar la inclinación del brazo con el 3D de la IA (corrige distancia y cuerpo)": "Compensate arm tilt using AI 3D landmarks (distance/body correction)",
  "Medición del brazo": "Arm measurement",
  "Largo real de tu brazo, hombro → muñeca (cm)": "Actual shoulder-to-wrist arm length (cm)",
  "Calibrar medición": "Calibrate measurement",
  "Quitar corrección": "Remove correction",
  "Proporción brazo / estatura": "Arm-to-height ratio",
  "Tu estatura real (cm)": "Your actual height (cm)",
  "Guardar proporción": "Save ratio",
  "Usar la proporción media (0.332)": "Use average ratio (0.332)",
  "Si el brazo apunta hacia la cámara, la escala de la banda se alarga y la distancia sale mayor; la compensación con el 3D la corrige (recomendado). El largo del brazo no se ve afectado: la banda va en el mismo brazo, así que su alto y el largo del brazo se acortan igual y se cancelan. «Calibrar medición» corrige el sesgo de los puntos del esqueleto con tu largo real de brazo (cinta métrica). La estatura que sale del brazo usa una proporción media (hombro → muñeca ≈ 0.332 de la estatura, ±5 % entre personas); si escribes tu estatura real y guardas la proporción, pasa a ser una estimación personal más exacta. Los cambios de esta tarjeta se aplican al instante a los archivos ya procesados, sin reprocesar.": "Arm orientation can change the apparent scale. The model offers a 3D tilt correction, but it must be validated. Calibrate arm length with a tape measure to reduce landmark bias. Height inferred from arm length uses an approximate population ratio (0.332); personal calibration can improve consistency. These settings update already processed results.",
  "Registro": "Log",
  "Nombre (p. ej. Mi banda)": "Name (e.g., My band)",
  "p. ej. 172": "e.g., 172",
  "0 = no usar": "0 = disabled"
};
 const replacements = Object.entries(translations).filter(([a]) => a.length > 10).sort((a,b) => b[0].length - a[0].length);
 const originalText = new WeakMap();
 const originalAttr = new WeakMap();
 const SKIP = new Set(['SCRIPT','STYLE','TEXTAREA','CODE','PRE','NOSCRIPT']);
 let lang = localStorage.getItem('anthropometry_language') === 'es' ? 'es' : 'en';
 let busy = false;
 const exact = x => translations[x] || x;
 function translate(x) {
   let out = exact(x);
   if (out !== x) return out;
   // Partial translation of changing status messages, preserving measured numbers.
   for (const [es,en] of replacements) if (out.includes(es)) out=out.split(es).join(en);
   return out;
 }
 function visit(node) {
   if (node.nodeType === Node.TEXT_NODE) {
     if (node.parentElement && (SKIP.has(node.parentElement.tagName) || node.parentElement.closest('[data-i18n-ignore]'))) return;
     const value = node.nodeValue;
     if (!value || !value.trim()) return;
     let old = originalText.get(node);
     if (old === undefined || (value !== old && value !== translate(old))) { old=value; originalText.set(node, old); }
     const result = lang==='en' ? translate(old.trim()) : old.trim();
     const lead=old.match(/^\s*/)[0],trail=old.match(/\s*$/)[0];
     const next=lead+result+trail;
     if (node.nodeValue!==next) node.nodeValue=next;
   } else if (node.nodeType === Node.ELEMENT_NODE) {
     if (SKIP.has(node.tagName) || node.closest('[data-i18n-ignore]')) return;
     for (const attr of ['title','placeholder','aria-label']) {
       if (!node.hasAttribute(attr)) continue;
       let originals=originalAttr.get(node);
       if(!originals) {originals={};originalAttr.set(node,originals);}
       const current=node.getAttribute(attr);
       if (!(attr in originals) || (current!==originals[attr] && current!==translate(originals[attr]))) originals[attr]=current;
       const next=lang==='en'?translate(originals[attr]):originals[attr];
       if(current!==next) node.setAttribute(attr,next);
     }
     for (const child of node.childNodes) visit(child);
   }
 }
 function update() {
   if (busy) return;
   busy=true;
   try {
     document.documentElement.lang=lang;
     document.title=lang==='en'?'Anthropometry | Space Health Monitor':'Antropometría | Monitor de salud espacial';
     visit(document.body);
     const en=document.getElementById('anthro-lang-en'),es=document.getElementById('anthro-lang-es');
     if(en) {en.setAttribute('aria-pressed',String(lang==='en'));en.classList.toggle('selected',lang==='en');}
     if(es) {es.setAttribute('aria-pressed',String(lang==='es'));es.classList.toggle('selected',lang==='es');}
   } finally {busy=false;}
 }
 const style=document.createElement('style');
 style.textContent=`#anthro-topnav {max-width:1400px;margin:0 auto 12px;padding:12px 16px;background:#141b34;color:#e8ecff;border:1px solid #2a3560;border-radius:14px;display:flex;gap:12px;justify-content:space-between;align-items:center;flex-wrap:wrap;font:13px system-ui,sans-serif}
 #anthro-topnav a{color:#4fd1ff;text-decoration:none}#anthro-topnav button{padding:5px 12px;cursor:pointer;border-radius:8px}
 #anthro-topnav button.selected{background:#4fd1ff;color:#061526;font-weight:700}#anthro-disclaimer{max-width:1400px;margin:0 auto 12px;padding:10px 16px;border-left:3px solid #ffd166;color:#e8ecff;background:#141b34;font:12px/1.45 system-ui,sans-serif}`;
 document.head.appendChild(style);
 const bar=document.createElement('nav');bar.id='anthro-topnav';bar.setAttribute('aria-label','Monitoring and language navigation');
 bar.setAttribute('data-i18n-ignore','');
 bar.innerHTML=`<span><a href="index.html" id="anthro-back">← <span id="anthro-back-label">Monitoring dashboard</span></a> &nbsp; / &nbsp; <b id="anthro-mod-label">03 · Anthropometry</b></span><span><span id="anthro-language-label">Language:</span> <button id="anthro-lang-en" type="button">EN</button> <button id="anthro-lang-es" type="button">ES</button></span>`;
 const note=document.createElement('div');note.id='anthro-disclaimer';
 note.setAttribute('data-i18n-ignore','');
 document.body.prepend(note);document.body.prepend(bar);
 const langStatic=()=>{
   const set=(id,value)=>{const el=document.getElementById(id);if(el.textContent!==value)el.textContent=value;};
   set('anthro-back-label',lang==='en'?'Monitoring dashboard':'Panel de monitoreo');
   set('anthro-mod-label',lang==='en'?'03 · Anthropometry':'03 · Antropometría');
   set('anthro-language-label',lang==='en'?'Language:':'Idioma:');
   const warning=lang==='en'?'Research prototype only. Height and distance are estimates, not clinically validated measurements. MediaPipe requires internet access for its first model download.':'Solo prototipo de investigación. La estatura y la distancia son estimaciones, no mediciones validadas clínicamente. MediaPipe necesita internet para descargar el modelo inicialmente.';
   if(note.textContent!==warning)note.textContent=warning;
 };
 document.getElementById('anthro-lang-en').addEventListener('click',()=>{lang='en';localStorage.setItem('anthropometry_language',lang);update();langStatic();});
 document.getElementById('anthro-lang-es').addEventListener('click',()=>{lang='es';localStorage.setItem('anthropometry_language',lang);update();langStatic();});
 // DOM updates from the original detection engine may generate new text: re-translate it.
 const mo=new MutationObserver(()=>{if(!busy){update();langStatic();}});
 mo.observe(document.body,{childList:true,subtree:true,characterData:true,attributes:true,attributeFilter:['title','placeholder','aria-label']});
 update();langStatic();
})();