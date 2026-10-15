"""Chapter: discovery_sky_and_underground, above and below: floating islands, airships, the deep dark and buried places.
Plan: src/plans/quests/discovery_sky_and_underground.json. Quests with a "discover" stay hidden until the player gets
there; a toast announces them."""
from common import chapter, quest, talk_villager, item, reward_item, skill, encounter


def enc(lines, title=None, **spec):
    t = encounter(lines, **spec)
    if title:
        t["title"] = title
    return t


def fight(entity, count, at, name, title, wave=4, **extra):
    spawn = {"at": {"structure": at}, "wave": wave, "name": name}
    spawn.update(extra)
    return {"kill": entity, "count": count, "spawn": spawn, "title": title}


def sample(name, from_mobs, chance, count=1, texture="minecraft:item/paper", tooltip="Needed for the job"):
    return {"drop": {"from": from_mobs, "chance": chance,
                     "item": {"name": name, "texture": texture, "tooltip": tooltip}},
            "count": count, "consume": False, "title": "Take " + name}


def search(at, count, name, found, texture="minecraft:item/paper", title=None):
    return {"search": {"at": {"structure": at}, "count": count,
                       "item": {"name": name, "texture": texture}, "found": found},
            "title": title or ("Search for " + name)}


Q = [
    quest("islands_in_the_sky", "Islands in the Sky", icon="grapplemod:grapplinghook",
          discover={"item": "minecraft:spyglass"},
          text=["Through the spyglass you can see them: islands hanging in the sky, small huts and whole forests among the "
                "clouds. The Couriers would give a lot to know how to reach one."],
          tasks=[{"structure": "#moog_sky_islands", "title": "Get up to a floating island by any means"}],
          rewards=[reward_item("grapplemod:grapplinghook"), reward_item("minecraft:ender_pearl", 4), skill("agility", 150)]),

    quest("sky_hopper", "Sky Hopper", icon="minecraft:feather", after=["islands_in_the_sky"],
          text=["One island is a story. Five is a map. The Couriers want to know how the islands connect, so hop "
                "between five different ones."],
          tasks=[{"structure": "mss:small_tower", "title": "Land on a small tower island"},
                 {"structure": "mss:spruce_huts", "title": "Land on the spruce huts island"},
                 {"structure": "mss:small_oak_house", "title": "Land on a small house island"},
                 {"structure": "mss:taiga", "title": "Land on a taiga forest island"},
                 {"structure": "mss:jungle", "title": "Land on a jungle island"}],
          rewards=[reward_item("minecraft:leather_boots", name="Sky Hoppers", lore=["Five islands, no falls."],
                               enchant={"minecraft:feather_falling": 3}), skill("agility", 200)]),

    quest("volcano_in_the_sky", "Fire Overhead", icon="minecraft:magma_block",
          discover={"structure": "mss:volcano"},
          text=["A volcano floats in the sky, dripping lava over its edge. The Miners' Guild wants magma and ore "
                "from its core, if you can reach it without falling through."],
          tasks=[item("minecraft:magma_block", 4, title="Chip magma from the crater's core"),
                 search("mss:volcano", 2, "Core Ore Sample", "A lump of ore, still hot from the core.",
                        texture="minecraft:item/raw_gold", title="Search the volcano for ore samples")],
          rewards=[reward_item("minecraft:obsidian", 8), reward_item("minecraft:magma_cream", 4), skill("mining", 220)]),

    quest("castle_in_the_clouds", "Castle in the Clouds", icon="minecraft:white_banner",
          discover={"structure": "mss:castle_tower"},
          text=["A ruined castle and towers float above the land, held by skeletons. Storm it, and take the banner "
                "from its highest tower."],
          tasks=[fight("minecraft:skeleton", 8, "mss:castle_tower", "Castle Garrison", "Storm the castle past its skeleton garrison"),
                 search("mss:castle_tower", 1, "the Castle Banner", "A torn banner, still bearing the castle's arms.",
                        texture="minecraft:item/white_banner")],
          rewards=[reward_item("minecraft:bow", name="Cloud-Piercer", lore=["Taken from a floating garrison."],
                               enchant={"minecraft:power": 3, "minecraft:punch": 1}),
                   reward_item("minecraft:white_banner"), skill("attack", 250)]),

    quest("pyramid_aloft", "The Pyramid Aloft", icon="minecraft:sandstone",
          discover={"structure": "mss:desert_pyramid"},
          text=["A desert pyramid floats over the dunes, its sand somehow holding. Its tomb is sealed by a ritual of "
                "lights. Kindle its candles and the chests unseal."],
          tasks=[{"use": "minecraft:light_gray_candle", "count": 1, "at": {"structure": "mss:desert_pyramid"},
                  "holding": "minecraft:flint_and_steel", "consume": False, "title": "Kindle the tomb's candles"},
                 search("mss:desert_pyramid", 1, "Tomb Hoard", "The tomb's seal gives, and the hoard glints.",
                        texture="minecraft:item/gold_ingot")],
          rewards=[reward_item("minecraft:gold_ingot", 10), reward_item("minecraft:sandstone", 32), skill("mining", 200)]),

    quest("sky_garden", "The Sky Garden", icon="minecraft:jungle_sapling",
          discover={"structure": "mss:jungle"},
          text=["Forests float in the sky, jungle, taiga and mangrove among them. The Herbalists want saplings from "
                "three sky forests, planted at home."],
          tasks=[{"structure": "mss:taiga", "title": "Visit a floating taiga"},
                 {"structure": "mss:mangrove", "title": "Visit a floating mangrove"},
                 item("minecraft:jungle_sapling", title="Take a jungle sapling"),
                 item("minecraft:spruce_sapling", title="Take a spruce sapling"),
                 item("minecraft:mangrove_propagule", title="Take a mangrove propagule"),
                 {"build": {"blocks": {"minecraft:jungle_sapling": 1, "minecraft:spruce_sapling": 1,
                                       "minecraft:mangrove_propagule": 1}, "radius": 12},
                  "title": "Plant the saplings at home"}],
          rewards=[reward_item("minecraft:bone_meal", 16), skill("forage", 180)]),

    quest("sky_hermit", "The Sky Hermit", icon="minecraft:bread",
          discover={"structure": "mss:spruce_huts"},
          text=["Small houses float in the sky, and one still has a hermit who never comes down. He's out of "
                "supplies. Bring him some from the ground."],
          tasks=[item("minecraft:bread", 8, consume=True, title="Bring bread up from the ground"),
                 item("minecraft:cooked_beef", 4, consume=True, title="Bring meat up from the ground"),
                 enc(["Real food! I've lived on cloud berries a year.", "Take this feather. Lightest thing I own."],
                     entity="minecraft:villager", name="Sky Hermit", title="Hand over the supplies and hear his story")],
          rewards=[reward_item("minecraft:feather", 8), reward_item("minecraft:golden_carrot", 4), skill("agility", 150)]),

    quest("airship_boarding", "Boarding Party", icon="minecraft:crossbow",
          discover={"structure": "#airships"},
          text=["An airship drifts overhead, crewed by illagers. Get aboard, clear the decks and take the captain's "
                "chest before it sails away."],
          tasks=[fight("minecraft:pillager", 8, "#airships", "Airship Crew", "Clear the airship's decks"),
                 search("#airships", 1, "the Captain's Hoard", "The captain's strongbox, heavy with plunder.",
                        texture="minecraft:item/gold_ingot")],
          rewards=[reward_item("minecraft:crossbow", name="Deckclearer", lore=["Taken from an illager airship."],
                               enchant={"minecraft:multishot": 1, "minecraft:quick_charge": 2}),
                   reward_item("minecraft:firework_rocket", 16), skill("range", 300)]),

    quest("the_drifting_blimp", "The Drifting Blimp", icon="immersive_aircraft:airship",
          discover={"structure": "dungeons_arise:small_blimp"},
          text=["A small blimp floats unmanned above the hills. The pilot scratched engine notes into the cabin walls; "
                "climb aboard, study them, and use them to build your own aircraft."],
          tasks=[{"structure": "dungeons_arise:small_blimp", "title": "Climb aboard and study the pilot's notes"},
                 item("immersive_aircraft:engine", crafted=True, title="Build an engine from the pilot's notes"),
                 item("immersive_aircraft:airship", crafted=True, title="Build your own airship")],
          rewards=[reward_item("immersive_aircraft:propeller", 2), reward_item("immersive_aircraft:hull", 4),
                   skill("craft", 220)]),

    quest("highest_point", "The Highest Point", icon="minecraft:firework_rocket", after=["islands_in_the_sky"],
          text=["The Couriers keep a record of those who have stood at the very top of the world. Icarus wings, "
                "an aircraft or a pillar of dirt all count."],
          tasks=[{"be": {"above_y": 300}, "title": "Climb to the build limit and look down"}],
          rewards=[reward_item("minecraft:firework_rocket", 16), skill("agility", 300)]),

    quest("the_ancient_city", "The Silent City", icon="minecraft:sculk_shrieker",
          discover={"structure": "minecraft:ancient_city"},
          text=["You've found an ancient city in the deep dark. Cross it to the great portal frame on the far side "
                "without waking the Warden, sneaking past every shrieker."],
          tasks=[{"timed": {"seconds": 300,
                            "goal": {"structure": "minecraft:ancient_city", "label": "the far side of the city", "away": 60},
                            "lines": ["Quiet. If anything touches you, the city knows you're here."],
                            "start": "Begin the crossing", "no": ["hurt"]},
                  "title": "Cross the city without being touched"}],
          rewards=[reward_item("minecraft:enchanted_book", name="Silent Step", enchant={"minecraft:swift_sneak": 3}),
                   reward_item("minecraft:echo_shard", 4), skill("magic", 300)]),

    quest("echo_shards", "Echoes", icon="minecraft:recovery_compass",
          discover={"item": "minecraft:echo_shard"},
          text=["An echo shard hums when you hold it. Gather eight, and a recovery compass will point you back "
                "to wherever you last fell."],
          tasks=[item("minecraft:echo_shard", 8, title="Gather eight echo shards from the city's chests"),
                 item("minecraft:recovery_compass", crafted=True, title="Craft a recovery compass")],
          rewards=[reward_item("minecraft:recovery_compass"), skill("magic", 250)]),

    quest("disc_fragments", "Fragments of a Song", icon="minecraft:music_disc_5", after=["the_ancient_city"],
          discover={"item": "minecraft:disc_fragment_5"},
          text=["A disc fragment hums with a half-remembered tune. Nine of them make a whole disc. Assemble it, then "
                "play it somewhere quiet."],
          tasks=[item("minecraft:disc_fragment_5", 9, title="Gather nine disc fragments from the city"),
                 item("minecraft:music_disc_5", crafted=True, title="Assemble the strange disc"),
                 {"use": "minecraft:jukebox", "count": 1, "holding": "minecraft:music_disc_5", "consume": False,
                  "title": "Play the disc in a jukebox somewhere quiet"}],
          rewards=[reward_item("minecraft:jukebox"), reward_item("minecraft:sculk", 8), skill("magic", 250)]),

    quest("the_bunker", "The Bunker", icon="minecraft:redstone",
          discover={"structure": "nova_structures:bunker"},
          text=["A sealed bunker lies under the hills, its vault door on a power lock. The bunker's fuses are "
                "scattered through its storerooms. Gather them, wire in lamps and open the vault."],
          tasks=[search("nova_structures:bunker", 3, "Bunker Fuse", "A fuse, still wrapped in oiled cloth.",
                        texture="minecraft:item/redstone", title="Search the storerooms for the bunker's fuses"),
                 item("minecraft:redstone_lamp", 3, title="Bring lamps to wire into the lock"),
                 {"build": {"blocks": {"minecraft:redstone_lamp": 3}, "radius": 12}, "title": "Wire the lamps into the lock"},
                 search("nova_structures:bunker", 1, "Vault Hoard", "The vault door grinds open on a hoard.",
                        title="Open the vault")],
          rewards=[reward_item("minecraft:redstone", 16), reward_item("minecraft:iron_ingot", 16), skill("craft", 200)]),

    quest("underground_house", "A House Underground", icon="minecraft:iron_pickaxe",
          discover={"structure": "nova_structures:underground_house"},
          text=["A house buried under the ground, lit and furnished, with nobody in it. Its owner's diary says who "
                "dug it, and where he left his pickaxe."],
          tasks=[search("nova_structures:underground_house", 2, "Owner's Diary Page", "A diary page, dated years back.",
                        title="Read the diary pages left in the house"),
                 search("nova_structures:underground_house", 1, "Owner's Pickaxe", "A worn pickaxe, wrapped in cloth.",
                        texture="minecraft:item/iron_pickaxe", title="Find the owner's lost pickaxe")],
          rewards=[reward_item("minecraft:torch", 32), reward_item("minecraft:iron_pickaxe"), skill("mining", 150)]),

    quest("the_cave_tablet", "A Carved Tablet", icon="alexscaves:cave_tablet",
          discover={"item": "alexscaves:cave_tablet"},
          text=["A tablet carved with a place far below. A cartographer in some village will know what it's worth."],
          tasks=[talk_villager("minecraft:cartographer", ["A cave deeper than any I've charted. Magnets, acid, strange light.", "Here, a map. Keep the tablet."],
                               title="Show the tablet to a cartographer")],
          rewards=[reward_item("minecraft:map"), skill("mining", 200)]),

    quest("glittering_nest", "The Glittering Nest", icon="minecraft:amethyst_block",
          discover={"structure": "cataclysm:amethyst_nest"},
          text=["An amethyst nest grows in a lush cave, guarded by amethyst crabs. One of them carries a perfect "
                "geode heart."],
          tasks=[fight("cataclysm:amethyst_crab", 4, "cataclysm:amethyst_nest", "Nest Crabs", "Hunt the nest's crabs", wave=2),
                 sample("a Perfect Geode Heart", ["cataclysm:amethyst_crab"], 0.5, texture="minecraft:item/amethyst_shard",
                        tooltip="The heart of the nest")],
          rewards=[reward_item("minecraft:amethyst_block", 8), reward_item("minecraft:spyglass"), skill("mining", 300)]),

    quest("biome_deep_dark", "Into the Deep Dark", icon="minecraft:sculk_sensor",
          discover={"biome": "minecraft:deep_dark"},
          text=["The deep dark: silence, sculk and something listening. The Arcane Order want a sculk sensor from "
                "it, taken without setting off a shrieker."],
          tasks=[{"be": {"biomes": ["minecraft:deep_dark"]}, "title": "Creep through the deep dark"},
                 item("minecraft:sculk_sensor", title="Take a sculk sensor without waking a shrieker")],
          rewards=[reward_item("minecraft:sculk", 8), skill("mining", 300)]),

    quest("biome_lush_caves", "Lush Caves", icon="minecraft:glow_berries",
          discover={"biome": "minecraft:lush_caves"},
          text=["Lush caves hang with glow berries and hold axolotls in their pools. The Sanctuary keepers would "
                "love both."],
          tasks=[item("minecraft:glow_berries", 4, title="Pick glow berries from the vines"),
                 item("minecraft:axolotl_bucket", title="Catch an axolotl in a bucket")],
          rewards=[reward_item("minecraft:axolotl_bucket"), skill("forage", 150)]),

    quest("biome_dripstone", "Teeth of Stone", icon="minecraft:pointed_dripstone",
          discover={"biome": "minecraft:dripstone_caves"},
          text=["Dripstone caves, a forest of stone teeth. The Miners' Guild wants pointed dripstone, and a cauldron "
                "filled drip by drip beneath a stalactite."],
          tasks=[item("minecraft:pointed_dripstone", 4, title="Collect pointed dripstone"),
                 item("minecraft:cauldron", crafted=True, title="Make a cauldron to catch the drips"),
                 {"build": {"blocks": {"minecraft:cauldron": 1}, "radius": 12},
                  "title": "Set the cauldron under a dripstone to fill"}],
          rewards=[reward_item("minecraft:cauldron"), skill("mining", 150)]),

    quest("biome_redstone_caves", "Red Veins", icon="regions_unexplored:redstone_bud",
          discover={"biome": "regions_unexplored:redstone_caves"},
          text=["Redstone grows from the walls of these caves like crystal. The Crafters' guild wants a harvest."],
          tasks=[item("regions_unexplored:redstone_bud", 4, title="Mine redstone buds from the walls"),
                 item("regions_unexplored:pointed_redstone", 4, title="Mine pointed redstone")],
          rewards=[reward_item("minecraft:redstone", 32), skill("mining", 150)]),

    quest("biome_prismachasm", "The Prismachasm", icon="regions_unexplored:prismaglass",
          discover={"biome": "regions_unexplored:prismachasm"},
          text=["A chasm of prismatic glass and glowing moss. The Crafters' guild would pay well for its shining "
                "crystals."],
          tasks=[item("regions_unexplored:prismaglass", 4, title="Bring back prismatic glass"),
                 item("regions_unexplored:prismoss", 4, title="Bring back prismoss")],
          rewards=[reward_item("regions_unexplored:prismoss", 8), skill("mining", 150)]),

    quest("biome_spider_nest", "Webs Everywhere", icon="minecraft:cobweb",
          discover={"biome": "biomesoplenty:spider_nest"},
          text=["You've stumbled into a spider nest, webs thick as curtains. Get out the other side before the nest "
                "closes around you."],
          tasks=[{"timed": {"seconds": 180, "goal": {"kill": "minecraft:spider", "count": 10},
                            "waves": [{"entity": "minecraft:spider", "count": 3, "every": 15}],
                            "lines": ["The webs are closing in. Cut your way out!"], "start": "Fight your way out"},
                  "title": "Cut your way through the nest"}],
          rewards=[reward_item("minecraft:string", 16),
                   reward_item("minecraft:enchanted_book", name="Spider's Bane", enchant={"minecraft:bane_of_arthropods": 3}),
                   skill("attack", 220)]),
]

chapter("discovery_sky_and_underground", "Above and Below", "Vertigo and darkness", "minecraft:feather", "explore", 2, Q)
