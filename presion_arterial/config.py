"""Constantes del modelo. Coinciden con el contrato de VitaSense (ventana de 6 s)."""
FS_MODEL = 30.0                 # Hz: frecuencia de muestreo que la webcam realmente entrega
WIN_S = 6.0                     # s por ventana (igual que make_bp_window de VitaSense)
WIN_N = int(round(WIN_S * FS_MODEL))   # 180 muestras
BAND_HZ = (0.7, 3.0)            # banda del pulso rPPG (42-180 lpm), igual que VitaSense
IN_CH = 3                       # canales: P (pulso), V (1ª derivada), A (2ª derivada)
