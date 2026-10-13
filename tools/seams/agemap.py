"""Chunk-age map of a whole world: python tools/seams/agemap.py <world> <out.png>
One pixel per chunk: green = generated after the fotfskills retrogen release (epoch 0), orange = existed before it
(epoch -1), red = existed before and never loaded since (no tag), blue = inhabited > 30 min. Spawn marked white."""
import os, sys
from PIL import Image, ImageDraw
import anvil


def main():
    world, out = sys.argv[1:3]
    files = [f for f in os.listdir(os.path.join(world, "region")) if f.endswith(".mca")]
    rs = [tuple(int(v) for v in f.split(".")[1:3]) for f in files]
    rx0, rx1 = min(r[0] for r in rs), max(r[0] for r in rs)
    rz0, rz1 = min(r[1] for r in rs), max(r[1] for r in rs)
    img = Image.new("RGB", ((rx1 - rx0 + 1) * 32, (rz1 - rz0 + 1) * 32), (15, 15, 15))
    px = img.load()
    counts = {}
    for rx, rz in rs:
        reg = anvil.Region(os.path.join(world, "region", f"r.{rx}.{rz}.mca"))
        for i in range(32):
            for j in range(32):
                cx, cz = rx * 32 + i, rz * 32 + j
                if not reg.has(cx, cz):
                    continue
                try:
                    c = anvil.plain(reg.read(cx, cz))
                except Exception:
                    continue
                r = c.get("fotfskills_retrogen")
                kind = "new" if r and r.get("epoch") == 0 else "pre" if r else "untouched"
                if c.get("InhabitedTime", 0) > 20 * 60 * 30:
                    kind = "lived"
                counts[kind] = counts.get(kind, 0) + 1
                px[(rx - rx0) * 32 + i, (rz - rz0) * 32 + j] = {"new": (50, 150, 70), "pre": (230, 140, 40),
                                                               "untouched": (200, 40, 40), "lived": (70, 120, 255)}[kind]
    d = ImageDraw.Draw(img)
    sx, sz = -rx0 * 32, -rz0 * 32
    d.ellipse([sx - 4, sz - 4, sx + 4, sz + 4], outline=(255, 255, 255))
    img.save(out)
    print(f"regions x {rx0}..{rx1} z {rz0}..{rz1}", counts)


if __name__ == "__main__":
    main()
