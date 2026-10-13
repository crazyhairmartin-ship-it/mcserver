"""Seam survey: python tools/seams/survey.py <world> <out_dir> x,z [x,z ...]
For each spot, renders the surface heights of the chunks around it (2 px per block, chunk grid drawn, chunk borders
whose height jump is far above the terrain's own steepness in red) and prints per-chunk facts that matter before
regenerating anything: block entities (builds, chests), named/owned entities, inhabited time."""
import os, sys, statistics
from PIL import Image, ImageDraw
import anvil

R = 6          # chunks around the spot
PX = 3


LO, HI = 40, 260


def colour(h):
    t = max(0.0, min(1.0, (h - LO) / max(1, HI - LO)))
    if t < 0.5:
        a = t / 0.5
        return (int(40 + 60 * a), int(110 + 90 * a), int(40 + 20 * a))
    a = (t - 0.5) / 0.5
    return (int(100 + 155 * a), int(200 + 55 * a), int(60 + 195 * a))


def load(world, cx, cz, cache):
    key = (cx >> 5, cz >> 5)
    if key not in cache:
        p = anvil.region_path(world, "region", cx, cz)
        cache[key] = anvil.Region(p) if os.path.exists(p) else None
    reg = cache[key]
    if reg is None or not reg.has(cx, cz):
        return None
    return anvil.plain(reg.read(cx, cz))


def entities(world, cx, cz, cache):
    key = ("e", cx >> 5, cz >> 5)
    if key not in cache:
        p = anvil.region_path(world, "entities", cx, cz)
        cache[key] = anvil.Region(p) if os.path.exists(p) else None
    reg = cache[key]
    if reg is None or not reg.has(cx, cz):
        return []
    return anvil.plain(reg.read(cx, cz)).get("Entities", [])


def survey(world, out, x, z):
    ccx, ccz = x >> 4, z >> 4
    cache, heights, facts = {}, {}, {}
    for cx in range(ccx - R, ccx + R + 1):
        for cz in range(ccz - R, ccz + R + 1):
            c = load(world, cx, cz, cache)
            if c is None:
                continue
            hm = anvil.heightmap(c, "MOTION_BLOCKING_NO_LEAVES") or anvil.heightmap(c)
            if hm:
                heights[(cx, cz)] = hm
            bes = [b.get("id", "?") for b in c.get("block_entities", [])]
            ents = entities(world, cx, cz, cache)
            keep = [e.get("id") for e in ents if "CustomName" in e or "Owner" in e or e.get("PersistenceRequired")]
            facts[(cx, cz)] = (c.get("InhabitedTime", 0), bes, keep)
    global LO, HI
    every = [v for hm in heights.values() for row in hm for v in row]
    LO, HI = (min(every), max(every)) if every else (40, 260)
    n = 2 * R + 1
    img = Image.new("RGB", (n * 16 * PX, n * 16 * PX), (0, 0, 0))
    d = ImageDraw.Draw(img)
    for (cx, cz), hm in heights.items():
        ox, oz = (cx - ccx + R) * 16 * PX, (cz - ccz + R) * 16 * PX
        for bz in range(16):
            for bx in range(16):
                d.rectangle([ox + bx * PX, oz + bz * PX, ox + bx * PX + PX - 1, oz + bz * PX + PX - 1], fill=colour(hm[bz][bx]))
    for i in range(n + 1):
        d.line([i * 16 * PX, 0, i * 16 * PX, n * 16 * PX], fill=(60, 60, 60), width=1)
        d.line([0, i * 16 * PX, n * 16 * PX, i * 16 * PX], fill=(60, 60, 60), width=1)
    # border jumps vs the terrain's own block-to-block steepness
    inner = []
    for hm in heights.values():
        for bz in range(16):
            for bx in range(15):
                inner.append(abs(hm[bz][bx + 1] - hm[bz][bx]))
    base = max(1.0, statistics.mean(inner) if inner else 1.0)
    seams = []
    for (cx, cz), hm in heights.items():
        for dx, dz in ((1, 0), (0, 1)):
            other = heights.get((cx + dx, cz + dz))
            if other is None:
                continue
            if dx:
                jumps = [abs(other[i][0] - hm[i][15]) for i in range(16)]
            else:
                jumps = [abs(other[0][i] - hm[15][i]) for i in range(16)]
            score = statistics.mean(jumps) / base
            if score >= 4:
                seams.append(((cx, cz), (cx + dx, cz + dz), round(score, 1), round(statistics.mean(jumps), 1)))
                ox, oz = (cx - ccx + R) * 16 * PX, (cz - ccz + R) * 16 * PX
                if dx:
                    d.line([ox + 16 * PX, oz, ox + 16 * PX, oz + 16 * PX - 1], fill=(255, 0, 0), width=3)
                else:
                    d.line([ox, oz + 16 * PX, ox + 16 * PX - 1, oz + 16 * PX], fill=(255, 0, 0), width=3)
    sx, sz = (x - (ccx - R) * 16) * PX, (z - (ccz - R) * 16) * PX
    d.ellipse([sx - 5, sz - 5, sx + 5, sz + 5], outline=(255, 0, 255), width=2)
    path = os.path.join(out, f"seam_{x}_{z}.png")
    img.save(path)
    print(f"== {x},{z} (chunk {ccx},{ccz}) heights {LO}-{HI}, base steepness {base:.2f}  image {os.path.basename(path)}")
    for a, b, score, mean in sorted(seams, key=lambda s: -s[2]):
        print(f"   seam {a}->{b} jump {mean} blocks ({score}x)")
    natural = ("lootr:", "twilightforest:firefly", "minecraft:mob_spawner", "minecraft:beehive", "minecraft:bee_nest",
               "minecraft:sculk", "minecraft:campfire", "minecraft:bed", "minecraft:bell", "minecraft:brushable")
    built = {k: (v[0], [b for b in v[1] if not b.startswith(natural)], v[2]) for k, v in facts.items()}
    built = {k: v for k, v in built.items() if v[1] or v[2] or v[0] > 20 * 60 * 30}
    for k, (inh, bes, keep) in sorted(built.items()):
        print(f"   chunk {k}: inhabited {inh // 20 // 60} min, block entities {bes[:6]}{'...' if len(bes) > 6 else ''}, kept mobs {keep[:4]}")


if __name__ == "__main__":
    world, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    for arg in sys.argv[3:]:
        x, z = (int(v) for v in arg.split(","))
        survey(world, out, x, z)
