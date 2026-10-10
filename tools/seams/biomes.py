"""Biome survey: python tools/seams/biomes.py <world> <out_dir> x,z [x,z ...]
Renders the surface biome of the chunks around each spot (one colour per biome, 4x4-block cells, chunk grid drawn) and
lists the biomes present, to tell chunk-aligned biome seams (old terrain next to newer terrain) from natural borders."""
import colorsys, hashlib, os, sys
from PIL import Image, ImageDraw
import anvil

R = 6
PX = 3


def biome_colour(name):
    h = int(hashlib.md5(name.encode()).hexdigest()[:6], 16) / 0xFFFFFF
    r, g, b = colorsys.hsv_to_rgb(h, 0.55, 0.9)
    return int(r * 255), int(g * 255), int(b * 255)


def cell_biomes(chunk):
    """{(section_y): (palette, data)} -> function(bx4, by_abs, bz4) giving the biome name."""
    secs = {}
    for s in chunk.get("sections", []):
        b = s.get("biomes")
        if b:
            secs[s["Y"]] = (b.get("palette", []), b.get("data"))

    def at(qx, y, qz):
        sy = y >> 4
        if sy not in secs:
            return None
        pal, data = secs[sy]
        if len(pal) == 1 or not data:
            return pal[0] if pal else None
        bits = max(1, (len(pal) - 1).bit_length())
        per = 64 // bits
        qy = (y & 15) >> 2
        i = (qy * 4 + qz) * 4 + qx
        word = data[i // per] & ((1 << 64) - 1)
        return pal[(word >> ((i % per) * bits)) & ((1 << bits) - 1)]
    return at


def survey(world, out, x, z):
    ccx, ccz = x >> 4, z >> 4
    n = 2 * R + 1
    img = Image.new("RGB", (n * 16 * PX, n * 16 * PX + 200), (20, 20, 20))
    d = ImageDraw.Draw(img)
    cache, seen = {}, {}
    for cx in range(ccx - R, ccx + R + 1):
        for cz in range(ccz - R, ccz + R + 1):
            key = (cx >> 5, cz >> 5)
            if key not in cache:
                p = anvil.region_path(world, "region", cx, cz)
                cache[key] = anvil.Region(p) if os.path.exists(p) else None
            reg = cache[key]
            if reg is None or not reg.has(cx, cz):
                continue
            c = anvil.plain(reg.read(cx, cz))
            hm = anvil.heightmap(c, "MOTION_BLOCKING_NO_LEAVES") or anvil.heightmap(c)
            at = cell_biomes(c)
            ox, oz = (cx - ccx + R) * 16 * PX, (cz - ccz + R) * 16 * PX
            for qz in range(4):
                for qx in range(4):
                    y = hm[qz * 4 + 2][qx * 4 + 2] - 1 if hm else 64
                    name = at(qx, y, qz) or "?"
                    seen[name] = seen.get(name, 0) + 1
                    d.rectangle([ox + qx * 4 * PX, oz + qz * 4 * PX, ox + (qx + 1) * 4 * PX - 1, oz + (qz + 1) * 4 * PX - 1],
                                fill=biome_colour(name))
    for i in range(n + 1):
        d.line([i * 16 * PX, 0, i * 16 * PX, n * 16 * PX], fill=(40, 40, 40))
        d.line([0, i * 16 * PX, n * 16 * PX, i * 16 * PX], fill=(40, 40, 40))
    sx, sz = (x - (ccx - R) * 16) * PX, (z - (ccz - R) * 16) * PX
    d.ellipse([sx - 6, sz - 6, sx + 6, sz + 6], outline=(0, 0, 0), width=3)
    ly = n * 16 * PX + 6
    for i, (name, count) in enumerate(sorted(seen.items(), key=lambda kv: -kv[1])[:16]):
        col, row = i % 2, i // 2
        d.rectangle([6 + col * 310, ly + row * 24, 24 + col * 310, ly + row * 24 + 18], fill=biome_colour(name))
        d.text((30 + col * 310, ly + row * 24 + 3), f"{name} ({count})", fill=(255, 255, 255))
    path = os.path.join(out, f"biome_{x}_{z}.png")
    img.save(path)
    print(f"== {x},{z}: {path}")
    for name, count in sorted(seen.items(), key=lambda kv: -kv[1]):
        print(f"   {name}: {count}")


if __name__ == "__main__":
    world, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    for arg in sys.argv[3:]:
        x, z = (int(v) for v in arg.split(","))
        survey(world, out, x, z)
