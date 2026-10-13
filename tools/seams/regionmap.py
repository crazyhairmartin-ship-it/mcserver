"""Old-era map: python tools/seams/regionmap.py <live_world> <fresh_world> <out.png> cx0 cz0 cx1 cz1 [x,z ...]
One pixel block per chunk over a chunk range: red = biomes differ from current generation (old era), green = match,
dark = not generated in one of the worlds, white dot = chunk has player builds or long inhabited time. x,z marks spots.
Also writes <out>.txt listing old-era chunks."""
import sys
from PIL import Image, ImageDraw
from compare import biome_cells
from survey import load

NATURAL = ("lootr:", "twilightforest:firefly", "minecraft:mob_spawner", "minecraft:beehive", "minecraft:bee_nest",
           "minecraft:sculk", "minecraft:campfire", "minecraft:bed", "minecraft:bell", "minecraft:brushable",
           "minecraft:chest", "minecraft:barrel", "minecraft:suspicious", "minecraft:sign", "minecraft:hanging_sign")
S = 6


def main():
    live, fresh, out = sys.argv[1:4]
    cx0, cz0, cx1, cz1 = (int(v) for v in sys.argv[4:8])
    spots = [tuple(int(v) for v in a.split(",")) for a in sys.argv[8:]]
    img = Image.new("RGB", ((cx1 - cx0 + 1) * S, (cz1 - cz0 + 1) * S), (25, 25, 25))
    d = ImageDraw.Draw(img)
    lc, fc, old, built = {}, {}, [], []
    for cx in range(cx0, cx1 + 1):
        for cz in range(cz0, cz1 + 1):
            a, b = load(live, cx, cz, lc), load(fresh, cx, cz, fc)
            if a is None or b is None:
                continue
            ca, cb = biome_cells(a), biome_cells(b)
            keys = ca.keys() & cb.keys()
            diff = sum(ca[k] != cb[k] for k in keys) / max(1, len(keys))
            ox, oz = (cx - cx0) * S, (cz - cz0) * S
            d.rectangle([ox, oz, ox + S - 1, oz + S - 1], fill=(200, 50, 50) if diff > 0.05 else (50, 150, 70))
            if diff > 0.05:
                old.append((cx, cz))
            bes = [e.get("id", "?") for e in a.get("block_entities", []) if not e.get("id", "?").startswith(NATURAL)]
            if bes or a.get("InhabitedTime", 0) > 20 * 60 * 30:
                built.append((cx, cz, a.get("InhabitedTime", 0) // 1200, bes[:4]))
                d.rectangle([ox + 2, oz + 2, ox + S - 3, oz + S - 3], fill=(255, 255, 255))
    for x, z in spots:
        px, pz = ((x >> 4) - cx0) * S + S // 2, ((z >> 4) - cz0) * S + S // 2
        d.ellipse([px - 7, pz - 7, px + 7, pz + 7], outline=(255, 255, 0), width=2)
    img.save(out)
    with open(out + ".txt", "w") as f:
        f.write("\n".join(f"{c},{z}" for c, z in old))
    print(f"old-era {len(old)} chunks; chunks with builds/inhabited: {len(built)}")
    for b in built[:40]:
        print("  built", b)


if __name__ == "__main__":
    main()
