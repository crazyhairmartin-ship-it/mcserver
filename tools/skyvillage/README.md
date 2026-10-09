Sky Villages overrides (kubejs/data/skyvillages):
- structures/waystones/*.nbt: the waystone island the mod's pool names but doesn't ship (make_waystone_island.py)
- worldgen/template_pool: pools without pieces the mod doesn't ship, waystone island at weight 100 (make_pools.py)
- worldgen/structure/skyvillage.json: start 185 above the surface at the village centre (was 150)
- tags/worldgen/biome/has_structure/skyvillage.json: oceans and rivers only (was also forests/jungles), so the centre
  is at sea level and the village sits around y 248-290, clear of Tectonic's hills and under the 320 build limit
