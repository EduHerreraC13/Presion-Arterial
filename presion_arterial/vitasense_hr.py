"""Estimador experimental de FC inspirado en técnicas públicas de VitaSense.

Implementación propia de POS/CHROM, pico parabólico, SNR, ventanas y antiarmónicos.
No es un modelo de IA ni una validación médica. Conserva CHROM para el adaptador DL.
"""
from __future__ import annotations
import numpy as np
from scipy.signal import butter, sosfiltfilt, find_peaks

_EPS = 1e-9

def _fft_metrics(z, fs):
    z = np.asarray(z, float)
    if len(z) < 64 or np.std(z) < 1e-5:
        return None
    nfft = max(4096, 1 << int(np.ceil(np.log2(len(z)*4))))
    p = np.abs(np.fft.rfft((z-np.mean(z))*np.hanning(len(z)), n=nfft))**2
    f = np.fft.rfftfreq(nfft, 1/fs)
    valid = (f >= 0.75) & (f <= 2.95)
    inds=np.flatnonzero(valid)
    if not len(inds): return None
    peaks,_=find_peaks(p)
    peaks=[i for i in peaks if valid[i]]
    if not peaks: peaks=[inds[int(np.argmax(p[valid]))]]
    # Los armónicos 2f pueden producir saltos 80->160. Penalizar un máximo
    # de frecuencia alta cuando hay un subarmónico considerable.
    best=None
    for idx in sorted(peaks,key=lambda i:p[i],reverse=True)[:12]:
        f0=f[idx]
        if f0>=1.5:
            half=np.where((f>=f0/2-0.08)&(f<=f0/2+0.08)&valid)[0]
            if len(half) and float(p[half].max()) > 0.78*float(p[idx]):
                continue
        # Interpolación parabólica del pico espectral de VitaSense.
        freq=float(f0)
        if 0<idx<len(p)-1:
            a,b,c=np.log(p[idx-1:idx+2]+1e-20)
            den=a-2*b+c
            if abs(den)>1e-12:
                freq+=float(np.clip(.5*(a-c)/den,-1,1))*(f[1]-f[0])
        width=max(.09,1.0/(len(z)/fs))
        signal=((abs(f-freq)<=width) | (abs(f-2*freq)<=width)) & valid
        noise=valid & ~signal
        snr=float(10*np.log10((p[signal].sum()+_EPS)/(p[noise].sum()+_EPS)))
        fraction=float(p[signal].sum()/(p[valid].sum()+_EPS))
        score=snr+3*fraction
        if best is None or score>best['score']:
            best={'bpm':freq*60, 'peak_fraction':fraction,'snr_db':snr,'score':score}
    return best

def _chrom(rgb,fs):
    x=rgb/(rgb.mean(axis=0,keepdims=True)+_EPS)
    r,g,b=x.T
    X=3*r-2*g;Y=1.5*r+g-1.5*b
    return X-(X.std()/(Y.std()+_EPS))*Y

def _pos(rgb,fs):
    # Ventanas deslizantes cortas (POS, como en VitaSense), overlap-add.
    n=len(rgb);win=max(12,int(1.6*fs));out=np.zeros(n);count=np.zeros(n)
    for end in range(win,n+1, max(1,int(fs/6))):
        a=end-win;c=rgb[a:end].T
        cn=c/(c.mean(axis=1,keepdims=True)+_EPS)
        u=cn[1]-cn[2];v=-2*cn[0]+cn[1]+cn[2]
        h=u+(u.std()/(v.std()+_EPS))*v
        out[a:end]+=h-h.mean();count[a:end]+=1
    if not np.any(count):return None
    return out/np.maximum(count,1)

def estimate_region(ts,rgb,fs):
    ts=np.asarray(ts,float);rgb=np.asarray(rgb,float)
    if len(ts)<90:return None
    grid=np.arange(ts[0],ts[-1],1/fs)
    if len(grid)<int(11.5*fs):return None
    z=np.column_stack([np.interp(grid,ts,rgb[:,j]) for j in range(3)])
    base=z.mean(axis=0)
    if np.min(base)<25 or np.max(base)>240 or np.std(z,axis=0).max()>34:return None
    sos=butter(3,[.72,2.95],btype='bandpass',fs=fs,output='sos')
    chrom=sosfiltfilt(sos,_chrom(z,fs))
    chrom=(chrom-chrom.mean())/(chrom.std()+_EPS)
    choices=[]
    for name,pulse in [('CHROM',chrom),('POS',_pos(z,fs))]:
        if pulse is None: continue
        if name=='POS':pulse=sosfiltfilt(sos,pulse)
        pulse=(pulse-np.mean(pulse))/(np.std(pulse)+_EPS)
        tail=pulse[-min(len(pulse),int(22*fs)):]
        full=_fft_metrics(tail,fs)
        if not full:continue
        # VitaSense también evalúa SNR y estabilidad; cada mitad debe coincidir.
        mid=len(tail)//2
        a=_fft_metrics(tail[:mid],fs);b=_fft_metrics(tail[mid:],fs)
        if a is None or b is None:continue
        # Si ambas mitades encuentran el mismo pulso y la ventana larga
        # selecciona su subarmónico, recuperar el candidato confirmado.
        half_mean=(a['bpm']+b['bpm'])/2
        if (abs(a['bpm']-b['bpm'])<9 and half_mean>80 and
            abs(half_mean-2*full['bpm'])<12):
            full['bpm']=half_mean
        gap=abs(a['bpm']-b['bpm'])
        if gap>13:
            # Ante confusión subarmónica 2:1 en ventanas cortas, exigir que
            # la FFT completa y al menos una mitad coincidan. El consenso
            # entre regiones sigue siendo obligatorio en infer().
            harmonic=(abs(2*a['bpm']-b['bpm'])<10 or abs(2*b['bpm']-a['bpm'])<10)
            whole_agrees=(abs(full['bpm']-a['bpm'])<10 or abs(full['bpm']-b['bpm'])<10)
            if not (harmonic and whole_agrees):continue
        if full['peak_fraction']<0.15 or full['snr_db']< -0.5:continue
        full.update(algorithm=name)
        choices.append(full)
    if not choices:return None
    chosen=max(choices,key=lambda m:m['score'])
    return {'bpm':chosen['bpm'],'peak_fraction':chosen['peak_fraction'],
            'snr_db':chosen['snr_db'],'algorithm':chosen['algorithm'],
            # Siempre onda CHROM, no BPM suavizado, al checkpoint original.
            'pulse':chrom}
