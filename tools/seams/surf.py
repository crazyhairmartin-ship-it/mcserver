"""Surface block + biome census: python tools/seams/surf.py <world> x0 z0 x1 z1"""
import sys
from collections import Counter
import anvil
from biomes import cell_biomes
from survey import load


def block_at(chunk, x, y, z):
    for s in chunk.get("sections", []):
        if s["Y"] == y >> 4:
            bs = s.get("block_states", {}); pal = bs.get("palette", []); data = bs.get("data")
            if not data:
                return pal[0]["Name"] if pal else None
            bits = max(4, (len(pal) - 1).bit_length()); per = 64 // bits
            i = ((y & 15) * 16 + (z & 15)) * 16 + (x & 15)
            w = data[i // per] & ((1 << 64) - 1)
            return pal[(w >> ((i % per) * bits)) & ((1 << bits) - 1)]["Name"]


def main():
    world = sys.argv[1]; x0, z0, x1, z1 = (int(v) for v in sys.argv[2:6])
    c, blocks, biomes = {}, Counter(), Counter()
    for cx in range(x0 >> 4, (x1 >> 4) + 1):
        for cz in range(z0 >> 4, (z1 >> 4) + 1):
            a = load(world, cx, cz, c)
            if a is None: continue
            hm = anvil.heightmap(a, "OCEAN_FLOOR"); at = cell_biomes(a)
            for bz in range(0, 16, 2):
                for bx in range(0, 16, 2):
                    y = hm[bz][bx] - 1
                    blocks[block_at(a, bx, y, bz)] += 1
                    biomes[at(bx >> 2, y, bz >> 2)] += 1
    print("biomes", biomes.most_common(8)); print("surface", blocks.most_common(10))


if __name__ == "__main__":
    main()
