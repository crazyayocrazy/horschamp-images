"""Make a 9:16 Instagram reel from a carousel spec: slow zoom + ambient particles + text.
usage: python3 reel.py spec.json effect out.mp4
effect: petals | snow | rain | steam | digital | dust | sand
"""
import sys, json, math, random, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, SEC, FADE = 1080, 1920, 30, 5.0, 0.6
IMG_W, IMG_H, IMG_Y = 960, 1200, 620
INK = (67, 48, 44)
SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"
SERIF_B = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"

def jp(p, s):
    for i in range(10):
        try:
            f = ImageFont.truetype(p, s, index=i)
            if "JP" in f.getname()[0]:
                return f
        except Exception:
            break
    return ImageFont.truetype(p, s)

F_TITLE = jp(SERIF_B, 46); F_HEAD = jp(SERIF_B, 40); F_LINE = jp(SERIF, 36); F_SIGN = jp(SERIF, 26)

spec = json.load(open(sys.argv[1])); effect = sys.argv[2]; out = sys.argv[3]
slides = spec["slides"]
film_title = next((s["title"] for s in slides if s.get("title") and s["title"].startswith("『")), "")
srcs = [Image.open(s["src"]).convert("RGB") for s in slides]
paper = tuple(int(v) for v in np.asarray(srcs[0])[:40, :40].reshape(-1, 3).mean(0))

COLORS = {"petals": (236, 170, 178), "snow": (255, 255, 255), "rain": (200, 212, 226),
          "steam": (255, 255, 255), "digital": (150, 235, 120), "dust": (255, 244, 220), "sand": (214, 128, 62)}
rng = random.Random(7)
N = {"petals": 38, "snow": 120, "rain": 140, "steam": 18, "digital": 60, "dust": 50, "sand": 110}[effect]
parts = [dict(x=rng.uniform(0, W), y=rng.uniform(0, H), s=rng.uniform(0.5, 1.4),
              ph=rng.uniform(0, 6.28), sp=rng.uniform(0.6, 1.4)) for _ in range(N)]

def particles(t):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    c = COLORS[effect]
    for p in parts:
        if effect == "petals":
            y = (p["y"] + t * 90 * p["sp"]) % (H + 60) - 30
            x = (p["x"] + math.sin(t * 1.3 + p["ph"]) * 40 + t * 25) % W
            r = 9 * p["s"]; a = math.sin(t * 2 + p["ph"]) * 0.5 + 0.5
            d.ellipse([x - r, y - r * (0.4 + 0.5 * a), x + r, y + r * (0.4 + 0.5 * a)], fill=c + (170,))
        elif effect == "snow":
            y = (p["y"] + t * 70 * p["sp"]) % H
            x = (p["x"] + math.sin(t * 0.9 + p["ph"]) * 18) % W
            r = 3.2 * p["s"]; d.ellipse([x - r, y - r, x + r, y + r], fill=c + (215,))
        elif effect == "rain":
            y = (p["y"] + t * 1300 * p["sp"]) % H
            x = (p["x"] - t * 120) % W; L = 34 * p["s"]
            d.line([x, y, x - 4, y + L], fill=c + (120,), width=2)
        elif effect == "steam":
            y = H - ((p["y"] + t * 45 * p["sp"]) % (H * 0.7)) - 100
            x = p["x"] + math.sin(t * 0.7 + p["ph"]) * 50
            life = ((p["y"] + t * 45 * p["sp"]) % (H * 0.7)) / (H * 0.7)
            r = 60 + 120 * life; al = int(55 * math.sin(math.pi * life))
            d.ellipse([x - r, y - r, x + r, y + r], fill=c + (al,))
        elif effect == "digital":
            y = (p["y"] - t * 60 * p["sp"]) % H
            on = math.sin(t * 6 * p["sp"] + p["ph"]) > 0
            if on:
                s = 7 * p["s"]; d.rectangle([p["x"], y, p["x"] + s, y + s], fill=c + (170,))
        elif effect == "sand":
            x = (p["x"] + t * 620 * p["sp"]) % (W + 80) - 40
            y = (p["y"] + math.sin(t * 1.7 + p["ph"]) * 26 - t * 30 * p["sp"]) % H
            L = 26 * p["s"]; d.line([x, y, x + L, y - L * 0.22], fill=c + (120,), width=2)
        else:
            y = (p["y"] - t * 25 * p["sp"]) % H
            x = (p["x"] + math.sin(t + p["ph"]) * 20) % W
            r = 2.5 * p["s"]; al = int(150 * (0.5 + 0.5 * math.sin(t * 2 + p["ph"])))
            d.ellipse([x - r, y - r, x + r, y + r], fill=c + (al,))
    if effect == "steam":
        from PIL import ImageFilter
        lay = lay.filter(ImageFilter.GaussianBlur(30))
    return lay

def text_block(i):
    s = slides[i]
    lines = [l for l in s["lines"] if l]
    head = s.get("title") if s.get("title") and not s["title"].startswith("『") else None
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    y = 250
    if film_title:
        w = d.textlength(film_title, font=F_TITLE); d.text(((W - w) / 2, y), film_title, font=F_TITLE, fill=INK + (255,))
        y += 92
    if head:
        w = d.textlength(head, font=F_HEAD); d.text(((W - w) / 2, y), head, font=F_HEAD, fill=INK + (255,)); y += 62
    for l in lines:
        w = d.textlength(l, font=F_LINE); d.text(((W - w) / 2, y), l, font=F_LINE, fill=INK + (235,)); y += 56
    t = f"Hors Champ  {i + 1}/{len(slides)}"
    w = d.textlength(t, font=F_SIGN); d.text((W - w - 70, IMG_Y + IMG_H + 18), t, font=F_SIGN, fill=INK + (190,))
    return lay

TEXT = [text_block(i) for i in range(len(slides))]
_m = np.ones((IMG_H, IMG_W), np.float32); E = 48
ramp = np.linspace(0, 1, E, dtype=np.float32)
_m[:E] *= ramp[:, None]; _m[-E:] *= ramp[::-1][:, None]; _m[:, :E] *= ramp[None]; _m[:, -E:] *= ramp[::-1][None]
MASK = Image.fromarray((_m * 255).astype(np.uint8))

def slide_frame(i, lt):
    src = srcs[i]; sw, sh = src.size
    z = 1.0 + 0.07 * (lt / SEC)
    cw, ch = sw / z, sh / z
    cx = sw / 2 + (sw - cw) / 2 * (0.4 if i % 2 else -0.4) * (lt / SEC)
    cy = sh / 2
    im = src.resize((IMG_W, IMG_H), Image.BILINEAR, box=(cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2))
    fr = Image.new("RGBA", (W, H), paper + (255,))
    fr.paste(im, ((W - IMG_W) // 2, IMG_Y), MASK)
    txt = TEXT[i]
    a = min(1.0, lt / 0.6)
    if a < 1:
        txt = txt.copy(); txt.putalpha(txt.getchannel("A").point(lambda v: int(v * a)))
    fr.alpha_composite(txt)
    return fr

total = int(SEC * len(slides) * FPS)
ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                       "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
                       "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
for f in range(total):
    t = f / FPS; i = min(int(t // SEC), len(slides) - 1); lt = t - i * SEC
    fr = slide_frame(i, lt)
    if i + 1 < len(slides) and lt > SEC - FADE:
        nx = slide_frame(i + 1, 0.0)
        fr = Image.blend(fr, nx, (lt - (SEC - FADE)) / FADE)
    fr.alpha_composite(particles(t))
    ff.stdin.write(fr.convert("RGB").tobytes())
ff.stdin.close(); ff.wait()
print("ok", out)
