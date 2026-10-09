"""Overrides Sky Villages' house and bridge pools: drops pieces whose structure files neither the mod nor the pack ship
(they place nothing and leave bridges dangling) and makes the waystone island (make_waystone_island.py) common.
Usage: python tools/skyvillage/make_pools.py <SkyVillages jar>"""
import json, sys, zipfile, os
jar = zipfile.ZipFile(sys.argv[1])
shipped = {n[len("data/skyvillages/structures/"):-4] for n in jar.namelist() if n.startswith("data/skyvillages/structures/")}
shipped |= {"waystones/" + f[:-4] for f in os.listdir("kubejs/data/skyvillages/structures/waystones")}
WAYSTONE_WEIGHT = 200          # vs 50 per normal house: roughly 1 in 4 house slots, so nearly every village has one
for pool in ("skyvillage_houses", "skyvillage_bridges"):
    d = json.loads(jar.read(f"data/skyvillages/worldgen/template_pool/{pool}.json"))
    kept = []
    for e in d["elements"]:
        loc = e["element"].get("location", "")
        if not loc.startswith("skyvillages:") or loc.split(":", 1)[1] not in shipped:
            continue
        if loc == "skyvillages:waystones/waystone_0_fabric":
            continue                                           # same piece as _forge; one entry carries the weight
        if loc == "skyvillages:waystones/waystone_0_forge":
            e["weight"] = WAYSTONE_WEIGHT
        kept.append(e)
    print(pool, len(d["elements"]), "->", len(kept), [e["element"]["location"].split(":")[1] for e in kept])
    d["elements"] = kept
    with open(f"kubejs/data/skyvillages/worldgen/template_pool/{pool}.json", "w", newline="\n") as f:
        json.dump(d, f, indent=2)
