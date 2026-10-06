# FOTF Retrogen

Server-side Forge 1.20.1 mod (47.x) that adds worldgen from newly installed mods to chunks generated before
those mods were added, as the chunks load. It used to live inside fotfskills; it's separate so fotfskills
can be updated or rolled back freely while Retrogen is in use.

- **Placed features** (ores, decorations): placed exactly like `ChunkGenerator.applyBiomeDecoration`, with the
  same biomes, step order and seeds. Tested.
- **Structure sets** (WIP, not tested yet): starts structures where worldgen would have, and fills in pieces
  of nearby ones.
- Each chunk records its worldgen epoch and what Retrogen has added to it, so nothing is added twice. The
  world keeps its epoch history in `world/data/fotfskills_retrogen.json`.
- It skips chunks that players have spent time near (`maxInhabitedTicks`) and chunks near Open Parties and
  Claims claims (optional dependency).
- Config: `config/fotfskills-retrogen.json`, off by default. Commands: `/fotfskills retrogen status|reload` (ops).
- The chunk tag, config, world file and command keep their fotfskills names from before the split, so worlds
  that already used it carry on.

Never run a world that Retrogen is working on without this mod. Minecraft drops the chunk records of a mod
that isn't loaded, and those chunks would then get the listed features again.

Build: `./build.sh` (same setup as fotfskills). Test: `./test.sh`.
