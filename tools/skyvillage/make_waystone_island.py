"""Writes the Sky Villages waystone pieces the mod's house pool names but doesn't ship
(skyvillages:waystones/waystone_0_forge and _fabric): a small floating island with a waystone, a plank path from the
bridge and two lanterns. Its jigsaw matches the sky village houses' (skyvillages:house <- skyvillages:bridge).
Run from the pack root:  PYTHONPATH=<dir with nbtio.py> python tools/skyvillage/make_waystone_island.py"""
import math, nbtio
from nbtio import BYTE, INT, STR, LIST, COMP

SIZE = (9, 7, 9)
CX, CZ = 4, 4
FLOOR = 4
palette, index, blocks = [], {}, []


def state(name, **props):
    key = (name, tuple(sorted(props.items())))
    if key not in index:
        entry = {"Name": (STR, name)}
        if props:
            entry["Properties"] = (COMP, {k: (STR, v) for k, v in props.items()})
        index[key] = len(palette)
        palette.append(entry)
    return index[key]


def put(x, y, z, st, nbt=None):
    b = {"pos": (LIST, (INT, [x, y, z])), "state": (INT, st)}
    if nbt is not None:
        b["nbt"] = (COMP, nbt)
    blocks.append(b)


def disc(y, r, st):
    for x in range(SIZE[0]):
        for z in range(SIZE[2]):
            if math.hypot(x - CX, z - CZ) <= r and not (y == FLOOR and x == 0):
                put(x, y, z, st)


grass, dirt, stone = state("minecraft:grass_block", snowy="false"), state("minecraft:dirt"), state("minecraft:stone")
planks = state("minecraft:spruce_planks")
disc(0, 0.5, stone); disc(1, 1.5, stone); disc(2, 2.5, stone); disc(3, 3.2, dirt)
for x in range(SIZE[0]):                                   # floor: grass, with a plank path in from the bridge
    for z in range(SIZE[2]):
        if 0 < x and math.hypot(x - CX, z - CZ) <= 3.7:
            put(x, FLOOR, z, planks if z == CZ and x <= 3 else grass)
put(0, FLOOR, CZ, state("minecraft:jigsaw", orientation="west_up"), {
    "id": (STR, "minecraft:jigsaw"), "name": (STR, "skyvillages:house"), "target": (STR, "skyvillages:bridge"),
    "pool": (STR, "minecraft:empty"), "final_state": (STR, "minecraft:spruce_planks"), "joint": (STR, "rollable")})
ws = {"id": (STR, "waystones:waystone")}
put(5, FLOOR + 1, CZ, state("waystones:waystone", half="lower", origin="village", facing="west"), dict(ws))
put(5, FLOOR + 2, CZ, state("waystones:waystone", half="upper", origin="village", facing="west"), dict(ws))
fence = state("minecraft:spruce_fence", east="false", north="false", south="false", west="false", waterlogged="false")
lantern = state("minecraft:lantern", hanging="false", waterlogged="false")
for z in (CZ - 2, CZ + 2):
    put(2, FLOOR + 1, z, fence)
    put(2, FLOOR + 2, z, lantern)

tag = (COMP, {
    "DataVersion": (INT, 3465),
    "size": (LIST, (INT, list(SIZE))),
    "palette": (LIST, (COMP, palette)),
    "blocks": (LIST, (COMP, blocks)),
    "entities": (LIST, (COMP, [])),
})
for name in ("waystone_0_forge", "waystone_0_fabric"):
    nbtio.save(f"kubejs/data/skyvillages/structures/waystones/{name}.nbt", tag)
print(len(blocks), "blocks,", len(palette), "states")
