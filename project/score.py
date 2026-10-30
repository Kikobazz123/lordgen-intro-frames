import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile
SR = 48000; DUR = 12.0; N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(5)
L = np.zeros(N); Rr = np.zeros(N)

def env(a, b, att, rel, curve=1.0):
    e = np.zeros(N); i0, i1 = int(a * SR), min(N, int(b * SR))
    x = t[i0:i1] - a; d = b - a
    e[i0:i1] = np.clip(x / max(att, 1e-4), 0, 1) ** curve * np.clip((d - x) / max(rel, 1e-4), 0, 1)
    return e
def bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo, hi], 'band', fs=SR, output='sos'), x)
def lp(x, f, o=2): return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)
def add(x, g=1.0, pan=0.0):
    global L, Rr
    pan = max(-1.0, min(1.0, pan))
    L += x * g * np.sqrt(0.5 * (1 - pan)); Rr += x * g * np.sqrt(0.5 * (1 + pan))
def note(n): return 440 * 2 ** ((n - 69) / 12)
def tone(f, e, bright=0.55, nh=14, vib=0.003, det=0.0):
    out = np.zeros(N); ph = 2 * np.pi * f * (1 + det) * t + vib * 2 * np.pi * np.sin(2 * np.pi * 5.1 * t) * 3
    for n in range(1, nh + 1):
        if f * n > 16000: break
        out += (bright ** (n - 1)) / n * np.sin(n * ph)
    return out * e
def pad(notes, a, b, att, rel, g, bright=0.5, pan_spread=0.5):
    e = env(a, b, att, rel, 1.6)
    for i, n in enumerate(notes):
        f = note(n); p = (i / max(1, len(notes) - 1) - 0.5) * 2 * pan_spread
        for d in (-0.004, 0.0, 0.0045):
            add(tone(f, e, bright, det=d), g / len(notes), p + d * 40)
noise = rng.standard_normal(N)

# --- wind ambience & sub drone
wind = lp(bp(noise, 150, 1400), 900) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.23 * t + 1))
add(wind * env(0, 7.2, 1.5, 1.2), 0.16, -0.2)
sub = np.sin(2 * np.pi * note(26) * t) + 0.5 * np.sin(2 * np.pi * note(33) * t)
add(sub * env(0, 8.4, 2.5, 0.4), 0.22)
# --- strings: Dm -> Bb -> Asus (tension) ; brass D major on impact
pad([50, 53, 57, 62], 0.2, 4.6, 2.2, 0.6, 0.16, 0.5)
pad([46, 50, 53, 58], 4.3, 6.9, 0.6, 0.5, 0.2, 0.58)
pad([45, 50, 52, 57, 64], 6.6, 8.55, 0.8, 0.12, 0.22, 0.62)
pad([38, 45, 50, 54, 57, 62, 66], 8.5, 12.0, 0.04, 2.6, 0.42, 0.72)   # brass hit
pad([62, 66, 69, 74], 8.6, 12.0, 0.6, 2.8, 0.1, 0.35, 0.9)            # high strings bloom

# --- wing flaps (downstrokes), louder when owl is near camera
flaps = [0.5 + (k + 0.5) / 2.4 for k in range(6)] + [3.9 + (k + 0.5) / 3.8 for k in range(2)]
for i, ft in enumerate(flaps):
    near = max(0.25, 1 - (ft - 0.5) / 3.4)
    e = env(ft - 0.05, ft + 0.22, 0.05, 0.17, 0.8)
    add(bp(noise, 180, 1300) * e, 0.55 * near, -0.6 + 0.5 * ft / 4.4)
    add(lp(noise, 160) * e, 0.9 * near)

# --- push: riser + whoosh
ri = env(4.2, 6.75, 2.2, 0.15, 2.0)
sweep = np.zeros(N); i0, i1 = int(4.2 * SR), int(6.75 * SR); seg = noise[i0:i1]
for k, (lo, hi) in enumerate([(300, 900), (700, 2200), (1600, 5000), (3500, 9000)]):
    a = 4.2 + k * 0.62; sweep += bp(noise, lo, hi) * env(a - 0.3, a + 0.9, 0.5, 0.4)
add(sweep * ri, 0.32)
fr = 110 * np.exp(np.clip(t - 4.2, 0, 2.5) * 0.9)
add(np.sin(2 * np.pi * np.cumsum(fr) / SR) * ri, 0.07)
wh = env(5.0, 6.3, 0.5, 0.8, 1.4); add(bp(noise, 400, 5000) * wh, 0.38, 0.1)

# --- eye glint bells
for k, (bt, n) in enumerate([(6.75, 86), (6.9, 93), (7.1, 98)]):
    e = env(bt, 12, 0.003, 11.0 - bt) * np.exp(-np.clip(t - bt, 0, None) * 1.6)
    f = note(n); b = sum(a * np.sin(2 * np.pi * f * m * t) for m, a in [(1, 1), (2.76, .4), (5.4, .2), (8.9, .1)])
    add(b * e, 0.09, -0.4 + 0.4 * k)
# --- reverse cymbal into impact
rc = env(7.3, 8.5, 1.2, 0.01, 3.0); add(hp(noise, 4000) * rc, 0.22)
# --- impact
it = 8.5; x = np.clip(t - it, 0, None); on = (t >= it)
boom = np.sin(2 * np.pi * np.cumsum(np.where(on, 30 + 45 * np.exp(-x * 9), 0)) / SR) * np.exp(-x * 2.0) * on
add(boom, 1.0)
add(lp(noise, 2500) * np.exp(-x * 14) * on, 0.5)
add(hp(noise, 6000) * np.exp(-x * 3.5) * on, 0.07)   # cymbal tail
# --- letter plucks (pentatonic) + LIMITED shimmer + sweep
pent = [74, 76, 78, 81, 83, 86, 88]
for i in range(7):
    lt = 8.75 + i * 0.065; e = env(lt, 12, 0.002, 0.5) * np.exp(-np.clip(t - lt, 0, None) * 5)
    add(tone(note(pent[i]), e, 0.3, 6, 0), 0.05, -0.6 + i * 0.2)
for i in range(7):
    lt = 9.45 + i * 0.06; e = env(lt, 12, 0.002, 0.3) * np.exp(-np.clip(t - lt, 0, None) * 4)
    add(np.sin(2 * np.pi * note(93 + (i % 3) * 2) * t) * e, 0.025, 0.6 - i * 0.2)
sw = env(9.9, 11.2, 0.5, 0.8, 1.5); add(bp(noise, 5000, 12000) * sw, 0.12, 0.3)

# --- reverb
ir_n = int(2.8 * SR); it_ = np.arange(ir_n) / SR
irL = rng.standard_normal(ir_n) * np.exp(-it_ * 2.3); irR = rng.standard_normal(ir_n) * np.exp(-it_ * 2.3)
irL = lp(irL, 7000); irR = lp(irR, 7000); irL /= np.abs(irL).sum() ** 0.5 * 9; irR /= np.abs(irR).sum() ** 0.5 * 9
wetL = fftconvolve(L, irL)[:N]; wetR = fftconvolve(Rr, irR)[:N]
oL = L + wetL * 0.9; oR = Rr + wetR * 0.9
fade = np.clip((12.0 - t) / 0.55, 0, 1) * np.clip(t / 0.05, 0, 1)
out = np.stack([oL, oR], 1) * fade[:, None]
out = np.tanh(out / np.abs(out).max() * 1.4); out = out / np.abs(out).max() * 0.9
wavfile.write('score.wav', SR, (out * 32767).astype(np.int16))
print('score ok', np.abs(out).max())
