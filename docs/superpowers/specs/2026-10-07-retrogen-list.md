# Retrogen feature list (for FOTF Retrogen, issue #1)

FOTF Retrogen lives on branch `claude/cloud-session-setup-epiuzy` (`extras/fotfretrogen`). When it's brought into the
pack, its `config/fotfskills-retrogen.json` `"features"` list should include these, so already-generated forests get
them too (new chunks get them from the biome modifiers):

- `fotf:forest_fireflies_dense`: Twilight Forest fireflies on tree trunks in magical forests (`#fotf:fairy/uncommon`),
  every chunk. Defined in `kubejs/data/fotf/worldgen/`, added by `kubejs/data/fotf/forge/biome_modifier/fireflies_magical.json`.
- `fotf:forest_fireflies_sparse`: the same in every other forest (`#fotf:wildlife/forest`), about 1 chunk in 4
  (`fireflies_forest.json`).
- `realmrpg_skeletons:*`: Realm RPG: Fallen Adventurers (added in this update).

Both firefly features carry a `minecraft:biome` filter, so Retrogen only places them in biomes that list them.
