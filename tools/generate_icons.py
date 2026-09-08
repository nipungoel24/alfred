"""Generate the Alfred placeholder app icon set (PIL).

NOTE: this is a generated PLACEHOLDER derived from the app's own design
tokens (violet gradient + letterform) until the approved Alfred brand
asset is provided. Re-run this script after dropping the real
alfred-icon.png into frontend/public/.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ICONS = ROOT / "desktop" / "src-tauri" / "icons"
ICONS.mkdir(parents=True, exist_ok=True)

SIZE = 1024
img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Violet gradient (matches the design tokens accent ramp)
top = (157, 143, 248)
bottom = (81, 64, 192)
for y in range(SIZE):
    t = y / SIZE
    color = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    draw.line([(0, y), (SIZE, y)], fill=color + (255,))

# Rounded-square mask (radius 220)
mask = Image.new("L", (SIZE, SIZE), 0)
md = ImageDraw.Draw(mask)
md.rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=220, fill=255)
img.putalpha(mask)

# White letterform
font = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 640)
draw = ImageDraw.Draw(img)
bbox = draw.textbbox((0, 0), "A", font=font)
w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
draw.text(((SIZE - w) / 2 - bbox[0], (SIZE - h) / 2 - bbox[1]), "A", font=font, fill=(255, 255, 255, 255))

img.save(ICONS / "icon.png")
img.resize((512, 512), Image.LANCZOS).save(ICONS / "512x512.png")
img.resize((256, 256), Image.LANCZOS).save(ICONS / "128x128@2x.png")
img.resize((128, 128), Image.LANCZOS).save(ICONS / "128x128.png")
img.resize((64, 64), Image.LANCZOS).save(ICONS / "64x64.png")
img.resize((32, 32), Image.LANCZOS).save(ICONS / "32x32.png")

# ICO generation: build manually for deterministic multi-size output.
# PIL ICO writer can produce identical blobs; this approach ensures
# each regeneration produces a valid ICO with all required sizes.
import struct
sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
pngs = []
for sz in sizes:
    resized = img.resize(sz, Image.LANCZOS)
    import io
    buf = io.BytesIO()
    resized.save(buf, format='PNG', optimize=False)
    pngs.append((sz[0], buf.getvalue()))

header = struct.pack('<HHH', 0, 1, len(pngs))
data_offset = 6 + len(pngs) * 16
entries = b''
all_data = b''
for w, png_data in pngs:
    h = w
    # ICO uses 0 to represent 256
    ico_w = w if w < 256 else 0
    ico_h = w if w < 256 else 0
    entry = struct.pack('<BBBBHHII', ico_w, ico_h, 0, 0, 1, 32, len(png_data), data_offset)
    entries += entry
    all_data += png_data
    data_offset += len(png_data)

(ICONS / "icon.ico").write_bytes(header + entries + all_data)
print("generated:", sorted(p.name for p in ICONS.iterdir()))
