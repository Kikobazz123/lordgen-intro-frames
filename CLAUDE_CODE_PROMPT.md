# LordGen Brand Intro — Claude Code Production Prompt

Paste everything below into Claude Code, opened in this repo.

---

You are producer/editor for the LORDGEN LIMITED brand intro (owl → skyline → logo, MGM-style, premium). Mark is director: he generates the AI shots in Higgsfield on his laptop and approves takes. Go all out on polish; keep files lean.

## Rule 0 — preflight first, build nothing yet
Before running anything, print TABLE A and TABLE B with a status column (✅ ready / ❌ missing / ⏳ waiting on Mark), checking each item yourself (`which`, `python -c import`, file exists). Then STOP and wait for Mark to say "go".

### TABLE A — tools & connections
| # | Item | Needed for | Check |
|---|------|-----------|-------|
| 1 | Python 3.10+, pip pkgs: playwright numpy scipy pillow | render, score | `pip install playwright numpy scipy pillow && playwright install chromium` |
| 2 | ffmpeg (with libx264, aac) | encode, grade, assembly | `ffmpeg -version` |
| 3 | Higgsfield (Mark, laptop) — Seedance 2.0, fallback Kling | shots 1–2 | Mark confirms credits |
| 4 | Higgsfield MCP (optional) | lets Claude queue shots | Higgsfield help: "connect Higgsfield to Claude" |
| 5 | Flowframes (RIFE), Windows | smooth AI clips to 60fps | Mark installs from nmkd.itch.io/flowframes |
| 6 | DaVinci Resolve (free) | optional final polish | Mark |
| 7 | Gemini TTS (optional) | voice tag, only if Mark wants one | Mark supplies key / clip |
| 8 | Music | Mark supplies final song later; until then use `project/score.py` | — |

### TABLE B — shot list (9:16, 1080×1920, 30fps master)
| Shot | Dur | Source | First frame | Last frame | Tool | Status |
|---|---|---|---|---|---|---|
| 1 Flight + landing | 5s | AI | frames/k1_wide.jpg | frames/k2_perch.jpg | Higgsfield · Seedance 2.0 (start+end frame) | ⏳ |
| 2 Lens push 185→35mm | 2–3s | AI | frames/k2_perch.jpg | frames/k3_close.jpg | Higgsfield · Seedance 2.0 | ⏳ |
| 3 Eye glint → particle morph → logo build → hold | ~5.3s | Code | comp t=6.65 | comp t=12.0 | `project/index.html` | ✅ |

Expected clips: `clips/shot1.mp4`, `clips/shot2.mp4` (Mark drops best takes there).

## Prompts for Mark (Higgsfield)
Shot 1:
> Cinematic golden-hour skyline over a river. A white snowy owl flies in from the lower-left foreground, close to camera and slightly out of focus, wings beating powerfully with realistic feather flex. It glides up over the river and lands on the tip of the tallest skyscraper, wings flaring then folding. 185mm telephoto, compressed perspective, smooth slow tilt up. Warm rim light, rippling water reflections, photoreal, no text.

Shot 2:
> Fast, smooth push-in onto the owl perched on the skyscraper tip, like a lens change from 185mm to 35mm. The city falls into soft bokeh while the owl stays sharp and fills the frame. The owl settles its feathers and looks straight into camera, amber eyes catching a gold glint. Photoreal, shallow depth of field, no text.

Ask for 2–3 takes each. Reject takes where the owl morphs, gains extra wings, or the last frame drifts from the key frame.

## Repo map
- `source/` originals: city.jpg, owl.jpg, logo.png
- `frames/` key frames given to Higgsfield
- `project/index.html` deterministic canvas comp, `seek(t)`, 0–12s. Flags: `window.NOFADE`, `NOFLY`, `FORCEOWL`; dust is off by default.
- `project/prep.py` rebuilds `project/assets/` from `source/` (owl cutout already in assets)
- `project/render.py` frames → ffmpeg; `project/score.py` synth score (48kHz, owned); `project/keys.py` key frames

## Build steps (after "go" and both clips present)
1. Probe clips (`ffprobe`). Conform each to 1080×1920 30fps: scale+crop cover, `-c:v libx264 -crf 16 -preset veryfast`. If Mark ran Flowframes, conform the 60fps files instead.
2. Trim: shot1 → its best 5.0s ending on the landing; shot2 → 2.2s ending on the close-up. Speed-ramp shot2 if needed so the push accelerates then eases (setpts with a curve, or split into 2 segments).
3. Render the tail from the comp: add `?start=6.65` support to render.py (seek t = 6.65 + f/30, NOFLY=true), 160 frames → `out/tail.mp4`. The first tail frame must match shot2's last frame; crossfade 8 frames inside one file.
4. Grade shots 1–2 to the comp: shadows → green #0E3B2E, highlights → gold #A9843A, subtle (ffmpeg `colorbalance` + `curves`), add fine grain (`noise=alls=6:allf=t`) and a soft vignette. Then compare a frame of each shot against `frames/` and match exposure.
5. Concat (concat demuxer, `-c copy`, identical encoder settings) → `out/picture.mp4` ≈ 12.5s.
6. Score: parametrise score.py with an offset so events from 6.65 onward shift to their new place (impact = logo landing). Add wing-flap hits synced to shot1's visible downstrokes (inspect frames). Mux: `-c:v copy -c:a aac -b:a 256k` → `out/LordGen_Intro_v2.mp4`.
7. QC: contact sheet of 14 frames, check for no watermark, no warped logo (logo must come only from the comp), no flash frames at cuts, peak audio ≤ −1 dBFS. Show Mark the sheet before the final export.
8. Deliver the master plus a 16:9 version (outpaint the plates and re-key only if Mark asks).

## Brand
LORDGEN LIMITED. Green #0E3B2E, gold #A9843A, cream #FAF7EF. Never let an AI model render the logo or text; the logo build comes from the comp only.
