"""Adaptador a los módulos ORIGINALES publicados por FatigueSense.

No reemplaza ninguna red entrenada con reglas: exige código y checkpoints oficiales
al ejecutar el servidor con --fatiguesense-root.

IMPORTANTE: El envío HTTP de JPEG reduce el FPS efectivo respecto al de la webcam.
Por tanto, el score temporal puede no reproducir las condiciones del estudio.
No es un diagnóstico.
"""
from __future__ import annotations
from collections import deque
from pathlib import Path
import sys
import time
import threading
import numpy as np

class FatigueSenseBridge:
    def __init__(self, repo_root: str, fps: float = 10.0):
        root=Path(repo_root).expanduser().resolve()
        if not (root/'fatigue_pipeline'/'inference_pipeline.py').is_file():
            raise FileNotFoundError(f'No aparece el código original FatigueSense en {root}')
        sys.path.insert(0,str(root))
        import torch
        from fatigue_pipeline import FatiguePipeline, FeatureAggregator
        from fatigue_pipeline.pose_estimator import PoseEstimator
        from model_architecture.models.bigru_temporal import load_temporal_checkpoint
        from model_architecture.utils.normalization import load_normalization
        from scripts.weights_path import (LANDMARKER_PATH,EYE_CKPT,MOUTH_CKPT,
            POSE_MODEL_PATH,TEMPORAL_MODEL_PATH,NORMALIZATION_PATH,resolve_asset)
        device='cuda' if torch.cuda.is_available() else 'cpu'
        self.device=device
        self.torch=torch
        self.fps=float(fps)
        self.pipe=FatiguePipeline(
            face_landmarker_path=str(resolve_asset(LANDMARKER_PATH)),
            eye_classifier_path=str(resolve_asset(EYE_CKPT)),
            mouth_classifier_path=str(resolve_asset(MOUTH_CKPT)),
            device=device, fps=fps)
        # Full model: real YOLO weights and BiGRU. No silently substituted model.
        self.pose=PoseEstimator(str(resolve_asset(POSE_MODEL_PATH)), device=device)
        self.agg=FeatureAggregator(fps=fps, sub_window_s=60.0, step_stride_s=1.0)
        self.model=load_temporal_checkpoint(str(resolve_asset(TEMPORAL_MODEL_PATH)),device=device)
        self.norm=load_normalization(Path(resolve_asset(NORMALIZATION_PATH)))
        self.rows=deque(maxlen=30)
        self.frames=0
        self.first_at=None
        self.last_at=None
        self.focus=None
        self.lock=threading.Lock()

    def process_jpeg(self, jpeg:bytes):
        import cv2
        if len(jpeg)>350000 or len(jpeg)<100: raise ValueError('JPEG fuera de los límites aceptados')
        arr=np.frombuffer(jpeg,dtype=np.uint8)
        img=cv2.imdecode(arr,cv2.IMREAD_COLOR)
        if img is None: raise ValueError('No se pudo decodificar JPEG')
        h,w=img.shape[:2]
        if min(h,w)<100 or max(h,w)>1280: raise ValueError('Fotograma fuera de tamaño permitido')
        with self.lock:
            now=time.monotonic()
            if self.last_at is not None and now-self.last_at>8:
                self.reset()
            self.last_at=now
            if self.first_at is None:self.first_at=now
            probs=self.pipe.process_frame(img)
            probs.keypoints=self.pose.predict(img)
            step=self.agg.add(probs)
            self.frames+=1
            if step is not None and step.features.valid:
                vec=step.features.to_array()
                if np.all(np.isfinite(vec)):
                    self.rows.append(vec)
                    if len(self.rows)==30:
                        x=np.asarray(self.rows,dtype=np.float32)
                        mean=self.norm['mean'];std=np.where(self.norm['std']<1e-6,1.0,self.norm['std'])
                        if mean.shape!=(17,) or std.shape!=(17,):raise ValueError('Normalización incompatible con 17 características')
                        x=np.nan_to_num((x-mean)/std,nan=0.0,posinf=0.0,neginf=0.0)
                        with self.torch.no_grad():
                            pred=self.model(self.torch.from_numpy(x[None]).to(self.device))
                            self.focus=float(pred.reshape(-1)[0].item())
            elapsed=max(now-self.first_at,0.01)
            effective_fps=(self.frames-1)/elapsed
            focus=self.focus
            # The temporal model was built on real-time features; reject interpretation if too few frames.
            # still show score marked degraded when rate diverges from selected aggregator rate.
            note=(f'FatigueSense CNN + YOLO activos; {effective_fps:.1f} FPS recibidos. '
                  + ('BiGRU acumulando (~90 s con FPS suficientes).' if focus is None else
                     'BiGRU experimental: cadencia de captura y dominio diferentes del entrenamiento.'))
            return {
                'status':'experimental', 'eye_left':_float(probs.p_eye_left_closed),
                'eye_right':_float(probs.p_eye_right_closed),'mouth':_float(probs.p_mouth_open),
                'focus':_float(focus), 'fps_server':round(effective_fps,1),
                'blink_count':int(self.agg.blink_total),'yawn_count':int(self.agg.yawn_total),
                'note':note}

    def reset(self):
        self.pipe.reset(fps=self.fps)
        self.agg.reset(fps=self.fps)
        self.rows.clear()
        self.frames=0
        self.first_at=None
        self.last_at=None
        self.focus=None

def _float(x):
    return float(x) if x is not None and np.isfinite(x) else None
