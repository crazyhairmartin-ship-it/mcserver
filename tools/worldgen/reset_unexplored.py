"""Reset chunks nobody has explored, so they regenerate with the new worldgen (issue #1's "unexplored-chunk reset",
done by script instead of MCA Selector).

    python tools/worldgen/reset_unexplored.py <world folder> [--apply] [--minutes 1] [--buffer 2] [--claim-buffer 2]
                                             [--full nether]

For the overworld, the Nether and the End:
- keeps every chunk players have spent at least --minutes in (the chunk's InhabitedTime), plus --buffer chunks around
  them so terrain and structures don't end in a cliff at the seam, plus every Open Parties and Claims claim and
  --claim-buffer chunks around it;
- resets everything else: the chunk is removed from region/, entities/ and poi/ (region files that end up empty are
  deleted), and Minecraft generates it again with the current mods the next time it's loaded;
- in kept chunks, turns the removed Ars Nouveau biome (ars_nouveau:archwood_forest) into minecraft:forest, and relabels
  archwood chests as vanilla chests so their items survive.
Without --apply nothing is changed. Either way it writes reset_map_<dimension>.png next to the world: kept chunks
green, claimed blue, reset grey. ALWAYS run it on a stopped server and a backed-up world.
"""
import argparse
import os
import re
import struct
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import nbt  # noqa: E402

DIMENSIONS = {'overworld': ('', 'minecraft:overworld'), 'nether': ('DIM-1', 'minecraft:the_nether'),
              'end': ('DIM1', 'minecraft:the_end')}
INHABITED = b'\x04\x00\x0dInhabitedTime'
BIOME_SWAPS = {'ars_nouveau:archwood_forest': 'minecraft:forest'}
# block entities of removed mods whose contents a vanilla block can keep (the block itself is swapped by fotfskills'
# RemovedBlocks aliases); without this the game drops the unknown block entity, and the items with it
BLOCK_ENTITY_SWAPS = {'ars_nouveau:archwood_chest': 'minecraft:chest'}


def region_files(folder):
    for f in sorted(Path(folder).glob('r.*.*.mca')):
        m = re.match(r'r\.(-?\d+)\.(-?\d+)\.mca$', f.name)
        if m and f.stat().st_size >= 8192:
            yield f, int(m.group(1)), int(m.group(2))


def chunks(data):
    """(index, decompressed chunk data, sector offset, sector count) for every chunk in a region file."""
    for i in range(1024):
        loc = struct.unpack('>I', data[i * 4:i * 4 + 4])[0]
        off, count = loc >> 8, loc & 0xFF
        if not off:
            continue
        p = off * 4096
        length = struct.unpack('>I', data[p:p + 4])[0]
        if data[p + 4] != 2:
            continue                                    # only zlib chunks (the default)
        try:
            yield i, zlib.decompress(data[p + 5:p + 4 + length]), off, count
        except zlib.error:
            continue


def inhabited(chunk):
    k = chunk.find(INHABITED)
    return struct.unpack('>q', chunk[k + len(INHABITED):k + len(INHABITED) + 8])[0] if k >= 0 else 0


def claims(world, dim_key):
    out = set()
    folder = Path(world) / 'data' / 'openpartiesandclaims' / 'player-claims'
    for f in folder.glob('*.nbt'):
        try:
            root = nbt.loads(f.read_bytes())
        except Exception:
            continue
        dims = root.get('dimensions', (nbt.COMPOUND, {}))[1]
        for claim in dims.get(dim_key, (nbt.COMPOUND, {}))[1].get('claims', (nbt.LIST, (nbt.COMPOUND, [])))[1][1]:
            for pos in claim.get('positions', (nbt.LIST, (nbt.COMPOUND, [])))[1][1]:
                out.add((pos['x'][1], pos['z'][1]))
    return out


def grow(cells, radius):
    return {(x + dx, z + dz) for x, z in cells for dx in range(-radius, radius + 1) for dz in range(-radius, radius + 1)}


def swap_biomes(chunk):
    """The chunk with removed biomes renamed in every section's biome palette and removed mods' chests relabelled as
    vanilla chests (items kept), or None if it has neither."""
    if not any(old.encode() in chunk for old in list(BIOME_SWAPS) + list(BLOCK_ENTITY_SWAPS)):
        return None
    root = nbt.loads(chunk)
    for be in root.get('block_entities', (nbt.LIST, (nbt.COMPOUND, [])))[1][1]:
        if be.get('id', (nbt.STRING, ''))[1] in BLOCK_ENTITY_SWAPS:
            be['id'] = (nbt.STRING, BLOCK_ENTITY_SWAPS[be['id'][1]])
    for section in root.get('sections', (nbt.LIST, (nbt.COMPOUND, [])))[1][1]:
        biomes = section.get('biomes')
        if biomes:
            et, palette = biomes[1]['palette'][1]
            biomes[1]['palette'] = (nbt.LIST, (et, [BIOME_SWAPS.get(b, b) for b in palette]))
    return nbt.dumps(root)


def write_chunk(data, i, off, count, chunk):
    """Rewrite one chunk in place (only when it still fits in its sectors; a rename only shrinks it)."""
    packed = zlib.compress(chunk)
    if len(packed) + 5 > count * 4096:
        return False
    p = off * 4096
    data[p:p + count * 4096] = b'\0' * (count * 4096)
    data[p:p + 5 + len(packed)] = struct.pack('>IB', len(packed) + 1, 2) + packed
    return True


def remove(folder, rx, rz, gone):
    """Remove chunks from one region-format file (region/, entities/ or poi/); delete it if nothing is left."""
    f = Path(folder) / f'r.{rx}.{rz}.mca'
    if not f.exists() or f.stat().st_size < 8192:
        return
    data = bytearray(f.read_bytes())
    for i in gone:
        data[i * 4:i * 4 + 4] = b'\0\0\0\0'
        data[4096 + i * 4:4096 + i * 4 + 4] = b'\0\0\0\0'
    if not any(data[:4096]):
        f.unlink()
    else:
        f.write_bytes(bytes(data))


def draw(path, present, keep, claimed):
    try:
        from PIL import Image
    except ImportError:
        return
    xs = sorted(x for x, _ in present)
    zs = sorted(z for _, z in present)
    if not xs:
        return
    cut = len(xs) // 1000                               # ignore a few stray far-off chunks when framing the map
    x0, x1, z0, z1 = xs[cut], xs[-1 - cut], zs[cut], zs[-1 - cut]
    img = Image.new('RGB', (x1 - x0 + 1, z1 - z0 + 1), (20, 20, 20))
    for x, z in present:
        if not (x0 <= x <= x1 and z0 <= z <= z1):
            continue
        colour = (60, 110, 230) if (x, z) in claimed else (70, 190, 90) if (x, z) in keep else (110, 110, 110)
        img.putpixel((x - x0, z - z0), colour)
    scale = max(1, 1200 // max(img.size))
    img.resize((img.width * scale, img.height * scale), Image.NEAREST).save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('world')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--minutes', type=float, default=1)
    ap.add_argument('--buffer', type=int, default=2)
    ap.add_argument('--claim-buffer', type=int, default=2)
    ap.add_argument('--full', nargs='*', default=[], choices=list(DIMENSIONS),
                    help='dimensions reset completely, explored chunks too (claims are still kept)')
    a = ap.parse_args()
    world = Path(a.world)
    for name, (sub, key) in DIMENSIONS.items():
        base = world / sub if sub else world
        present, explored, renamed = {}, set(), 0
        for f, rx, rz in region_files(base / 'region'):
            for i, chunk, _, _ in chunks(f.read_bytes()):
                pos = (rx * 32 + i % 32, rz * 32 + i // 32)
                present[pos] = (rx, rz, i)
                if inhabited(chunk) >= a.minutes * 1200:
                    explored.add(pos)
        claimed = claims(world, key)
        if name in a.full:
            explored = set()                            # full reset: only claims survive
        keep = grow(explored, a.buffer) | grow(claimed, a.claim_buffer)
        reset = [p for p in present if p not in keep]
        draw(world.parent / f'reset_map_{name}.png', present, keep, claimed)
        print(f'{name}: {len(present)} chunks, {len(explored)} explored, {len(claimed)} claimed, '
              f'{len(present) - len(reset)} kept, {len(reset)} reset')
        if not a.apply:
            continue
        by_region = {}
        for p in reset:
            rx, rz, i = present[p]
            by_region.setdefault((rx, rz), []).append(i)
        for f, rx, rz in list(region_files(base / 'region')):     # rename removed biomes in kept chunks first
            data = bytearray(f.read_bytes())
            gone = set(by_region.get((rx, rz), []))
            changed = False
            for i, chunk, off, count in chunks(bytes(data)):
                if i in gone:
                    continue
                swapped = swap_biomes(chunk)
                if swapped is not None and write_chunk(data, i, off, count, swapped):
                    changed = True
                    renamed += 1
            if changed:
                f.write_bytes(bytes(data))
        for (rx, rz), gone in by_region.items():
            for folder in ('region', 'entities', 'poi'):
                remove(base / folder, rx, rz, gone)
        print(f'  applied: {len(reset)} chunks reset, {renamed} kept chunks fixed (archwood biome, archwood chests)')


if __name__ == '__main__':
    main()
