"""Chapter: end, the End questline: Act IV (first release; the Act V quests are in the plan's act5 tier and included).
Plan: src/plans/quests/end.json. Ilse Varr, a stargazer in Reece who has mapped every sky but this one, sends the player
out; the voices met in the void (a ship's ghost, a stranded astronomer, an Enderman scribe) fill in the rest."""
from common import chapter, quest, talk_char, item, reward_item, skill, enc, fight, boss, search, sample

END = {"dimension": "minecraft:the_end"}


def visit(structure, title):
    return {"structure": structure, "title": title}


ACT4 = [
    quest("the_island_of_stone", "The Island of Stone", icon="minecraft:end_stone", after=["main_story:act4_start"],
          text=["Ilse begs for one thing before you jump: notes on the central island. Walk the rebuilt End island, "
                "count its towers and sketch the ruined arches before the dragon notices you."],
          tasks=[talk_char("ilse", ["One thing before you jump. Notes on the island. Count the towers.", "Sketch the arches. Quickly."],
                           title="Take Ilse's request for notes on the central island"),
                 {"dimension": "minecraft:the_end", "title": "Walk the central island, counting its towers"}],
          rewards=[reward_item("minecraft:potion", 2), skill("agility", 600)]),

    quest("safe_landing", "A Safe Landing", icon="minecraft:ender_chest", after=["the_island_of_stone"],
          text=["The void forgives nothing. Build a walled platform with a shelter, a waystone and an ender chest at "
                "the island's edge, out of the dragon's flight path."],
          tasks=[{"build": {"blocks": {"minecraft:obsidian": 12, "minecraft:ender_chest": 1, "waystones:waystone": 1}, "radius": 10},
                  "title": "Build a walled platform with an ender chest and a waystone out of the dragon's path"},
                 {"waystones": 1, "title": "Light the waystone"}],
          rewards=[reward_item("minecraft:ender_chest"), reward_item("waystones:warp_scroll", 4), skill("craft", 600)]),

    quest("breath_in_a_bottle", "Breath in a Bottle", icon="minecraft:dragon_breath", after=["safe_landing"],
          text=["Ilse wants the dragon's breath for her ink. While the breath cloud hangs, fill bottles in under a "
                "minute, then brew a lingering potion."],
          tasks=[item("minecraft:glass_bottle", 5, title="Bring bottles to catch the dragon's breath"),
                 {"timed": {"seconds": 60, "goal": {"hold": {"radius": 12}}, "lines": ["The breath cloud hangs. Fill the bottles!"],
                            "start": "Catch the breath"}, "title": "Fill the bottles while the cloud hangs"},
                 item("minecraft:dragon_breath", 5, title="Hold five bottles of dragon's breath"),
                 item("minecraft:lingering_potion", crafted=True, title="Brew a lingering potion for Ilse's ink")],
          rewards=[reward_item("minecraft:glass_bottle", 8), skill("magic", 600)]),

    quest("beyond_the_gateway", "Beyond the Gateway", icon="minecraft:ender_pearl", after=["safe_landing", "main_story:act4_finale"],
          text=["With the dragon gone, the gateway portals open. Throw a pearl through one and reach the outer "
                "islands, then walk a good way across them."],
          tasks=[item("minecraft:ender_pearl", consume=True, title="Throw a pearl through a gateway portal"),
                 {"biome": "minecraft:end_midlands", "title": "Reach the outer islands"},
                 {"timed": {"seconds": 600, "goal": {"structure": "minecraft:end_city", "label": "an End city", "away": 400},
                            "lines": ["The outer islands stretch on. Walk them."], "start": "Set out", "no": ["teleport"]},
                  "title": "Walk a long way across the outer islands"}],
          rewards=[reward_item("minecraft:ender_pearl", 8), skill("agility", 650)]),

    quest("purple_towers", "The Purple Towers", icon="minecraft:purpur_block", after=["beyond_the_gateway"],
          text=["Find an End city and climb it to the top, clearing the shulkers that guard each floor."],
          tasks=[visit("minecraft:end_city", "Find an End city"),
                 fight("minecraft:shulker", 6, "minecraft:end_city", "City Shulkers", "Clear the shulkers guarding each floor", wave=3)],
          rewards=[reward_item("minecraft:purpur_block", 32), skill("defense", 650)]),

    quest("shells_for_boxes", "Shells for Boxes", icon="minecraft:shulker_shell", after=["purple_towers"],
          text=["Collect twelve shulker shells and craft two shulker boxes. Keep the rest, because some eyes need "
                "them later."],
          tasks=[item("minecraft:shulker_shell", 12, title="Collect twelve shulker shells"),
                 item("minecraft:shulker_box", 2, crafted=True, title="Craft two shulker boxes")],
          rewards=[reward_item("minecraft:purple_dye", 4), reward_item("sophisticatedbackpacks:stack_upgrade_tier_1"), skill("craft", 650)]),

    quest("the_wings", "The Wings on the Wall", icon="minecraft:elytra", after=["purple_towers"],
          text=["An End ship hangs off a city's edge with wings in its hold. Take the elytra and wear it in your "
                "elytra slot, so your chestplate stays on."],
          tasks=[item("minecraft:elytra", title="Take the elytra from the ship's hold")],
          rewards=[reward_item("minecraft:phantom_membrane", 4), reward_item("minecraft:enchanted_book", enchant={'minecraft:unbreaking': 3}), skill("agility", 700)]),

    quest("first_flight", "First Flight", icon="minecraft:firework_rocket", after=["the_wings"],
          text=["Fly with the elytra. Ilse asks for a sketch from the highest point you reach."],
          tasks=[{"timed": {"seconds": 900, "goal": {"structure": "minecraft:end_city", "label": "a far End city", "away": 800},
                            "lines": ["Fly far. Sketch from the highest point."], "start": "Take off", "no": ["teleport"]},
                  "title": "Fly far across the islands and sketch from the highest point"}],
          rewards=[reward_item("minecraft:firework_rocket", 32), skill("agility", 700)]),

    quest("chorus_garden", "The Chorus Garden", icon="minecraft:chorus_fruit", after=["beyond_the_gateway"],
          text=["Harvest chorus fruit, replant flowers on end stone at your landing, and build a purpur lookout from "
                "popped chorus."],
          tasks=[item("minecraft:chorus_fruit", 8, title="Harvest chorus fruit"),
                 {"build": {"blocks": {"minecraft:chorus_flower": 2, "minecraft:purpur_block": 16}, "radius": 10},
                  "title": "Replant flowers and raise a purpur lookout at your landing"}],
          rewards=[reward_item("minecraft:end_rod", 8), skill("forage", 600)]),

    quest("the_wrecked_fleet", "The Wrecked Fleet", icon="minecraft:spyglass", after=["the_wings"],
          text=["Huge ships, far bigger than any End ship, lie crashed across the islands. Find one of the mega ships "
                "and reach its bridge."],
          tasks=[visit("#end_mega_ships", "Find a crashed mega ship and reach its bridge"),
                 search("mes:mega_ship", 1, "the Ship's Loot", "The bridge locker, still sealed.", title="Open the bridge locker")],
          rewards=[reward_item("minecraft:spyglass", name="Captain's Spyglass"), skill("agility", 650)]),

    quest("ships_ghost", "The Ship's Ghost", icon="minecraft:written_book", after=["the_wrecked_fleet"],
          text=["The wreck's captain lingers on the bridge and wants his logbook pages, scattered through the other "
                "crashed ships, so he can learn why the fleet fell."],
          tasks=[enc(["My logbook pages. Scattered through the other ships. Why did we fall?"], entity="minecraft:allay", name="The Captain's Ghost",
                     title="Hear the ghost captain on the bridge"),
                 search("#end_mega_ships", 2, "a Logbook Page", "A page of the captain's log, brittle with age.", title="Collect logbook pages from the mega ships")],
          rewards=[reward_item("irons_spellbooks:cultist_chestplate", name="The Captain's Coat", lore=['Still smells of salt, and of void.']), skill("magic", 650)]),

    quest("starlight_voyager", "The Starlight Voyager", icon="minecraft:compass", after=["ships_ghost"],
          text=["The logbook names the fleet's flagship, the Starlight Voyager. Find it intact and bring its "
                "navigation star back to the ghost to let him rest."],
          tasks=[visit("mes:starlight_voyager", "Find the flagship intact"),
                 search("mes:starlight_voyager", 1, "the Navigation Star", "The flagship's navigation star, still bright.",
                        texture="minecraft:item/nether_star", title="Take the navigation star from the flagship")],
          rewards=[reward_item("minecraft:shulker_shell", 4), reward_item("minecraft:compass", name="Navigator's Compass"), skill("magic", 700)]),

    quest("phantom_citadel", "The Phantom Citadel", icon="minecraft:phantom_membrane", after=["purple_towers"],
          text=["A citadel that phantoms nest in, even here. Fight up its spires and clear the nests."],
          tasks=[visit("mes:phantom_citadel", "Find the phantom-haunted citadel"),
                 fight("minecraft:phantom", 6, "mes:phantom_citadel", "Citadel Phantoms", "Fight up the spires and clear the phantoms' nests")],
          rewards=[reward_item("minecraft:phantom_membrane", 8), skill("attack", 650)]),

    quest("enderkeep_siege", "The Enderkeep Courtyard", icon="minecraft:ender_pearl", after=["phantom_citadel"],
          text=["Hold the Enderkeep courtyard against waves of endermen and endermites for four minutes while its "
                "gate mechanism winds open."],
          tasks=[visit("mes:enderkeep_courtyard", "Reach the Enderkeep courtyard"),
                 {"timed": {"seconds": 240, "goal": {"hold": {"radius": 14}},
                            "waves": [{"entity": "minecraft:enderman", "count": 2, "every": 30},
                                      {"entity": "minecraft:endermite", "count": 4, "every": 30}],
                            "lines": ["The gate is winding open. Hold the courtyard!"], "start": "Hold the courtyard"},
                  "title": "Hold the courtyard until the gate winds open"}],
          rewards=[reward_item("irons_spellbooks:ender_upgrade_orb"), skill("defense", 700)]),

    quest("enderwatch", "The Enderwatch", icon="camerapture:camera", after=["beyond_the_gateway"],
          text=["Climb an Enderwatch tower and, from the top, spot three more of the End's structures for Ilse's "
                "map."],
          tasks=[visit("mes:enderwatch_tower", "Climb an Enderwatch tower"),
                 item("camerapture:camera", title="Bring a camera to mark what you see"),
                 {"photo": {"structure": "minecraft:end_city"}, "title": "Photograph an End city from the tower's top"}],
          rewards=[reward_item("minecraft:map"), reward_item("minecraft:spyglass"), skill("agility", 650)]),

    quest("manuscript_shrine", "The Manuscript Shrine", icon="minecraft:lectern", after=["enderwatch"],
          text=["An Enderman keeps a shrine of manuscripts and won't be looked at. Read the shrine's texts without "
                "meeting its gaze, and answer the scribe's question to earn a page."],
          tasks=[visit("mes:manuscript_shrine", "Find the Enderman scribe's shrine"),
                 {"timed": {"seconds": 120, "goal": {"hold": {"radius": 8}}, "lines": ["Don't meet its gaze. Read."],
                            "start": "Read the manuscripts", "no": ["hurt"]}, "title": "Read the shrine's texts without meeting the scribe's gaze"},
                 search("mes:manuscript_shrine", 1, "an Eldritch Manuscript", "A page, handed over in silence.",
                        texture="minecraft:item/writable_book", title="Answer the scribe's question and take a page")],
          rewards=[reward_item("minecraft:writable_book", name="An Eldritch Manuscript"), skill("magic", 700)]),

    quest("mythic_garden", "The Mythic Garden", icon="minecraft:flowering_azalea", after=["enderwatch"],
          text=["A walled garden of impossible plants grows on a far island. Bring back cuttings from the Mythic "
                "Garden and the Enderbloom Grove."],
          tasks=[visit("mes:mythic_garden", "Find the walled garden of impossible plants"),
                 visit("mes:enderbloom_grove", "Find the Enderbloom Grove"),
                 search("mes:mythic_garden", 1, "a Mythic Cutting", "A cutting that glows faintly.", texture="minecraft:block/oak_sapling",
                        title="Take a cutting from the garden")],
          rewards=[reward_item("minecraft:flowering_azalea", 4), skill("forage", 650)]),

    quest("fallen_star", "The Fallen Star", icon="minecraft:amethyst_shard", after=["enderwatch"],
          discover={"structure": "mes:astral_meteorite"},
          text=["A meteorite has struck an island, and a stranded astronomer camps in a hideaway nearby. Hear what "
                "fell."],
          tasks=[visit("mes:astral_hideaway", "Find the astronomer's hideaway nearby"),
                 enc(["It fell at dusk. I felt it hum. Take a fragment."], entity="minecraft:villager", name="Stranded Astronomer",
                     title="Hear what the stranded astronomer saw fall")],
          rewards=[reward_item("irons_spellbooks:arcane_ingot", 2), skill("magic", 650)]),

    quest("spire_climb", "The Ender Spire", icon="minecraft:purpur_pillar", after=["fallen_star"],
          text=["The astronomer needs a reading from the top of the Ender Spire before the next star-fall. Climb it "
                "in under three minutes, no elytra."],
          tasks=[visit("mes:ender_spire", "Find the Ender Spire"),
                 {"timed": {"seconds": 180, "goal": {"structure": "mes:ender_spire", "label": "the spire's top", "away": 30},
                            "lines": ["Three minutes. No wings."], "start": "Climb", "no": ["elytra", "teleport"]},
                  "title": "Climb the spire in under three minutes"}],
          rewards=[reward_item("minecraft:enchanted_book", name="Light Landing", enchant={"minecraft:feather_falling": 4}), skill("agility", 700)]),

    quest("the_monolith", "The Monolith", icon="minecraft:obsidian", after=["spire_climb"],
          discover={"structure": "mes:monolith"},
          text=["A black monolith hums on a barren island. Align it with the astronomer's reading and the star that "
                "fell starts to make sense."],
          tasks=[search("mes:monolith", 1, "a Lore Page", "A page, fixed to the stone with wax.", title="Read the monolith's inscriptions")],
          rewards=[reward_item("minecraft:writable_book", name="A Page of the Monolith"), skill("magic", 700)]),

    quest("quiet_meadows", "Quiet Meadows", icon="minecraft:chorus_flower", after=["chorus_garden"],
          text=["Find a placid prairie and an enderskog in the outer End, peaceful places where nothing tries to kill "
                "you, and rest there a full minute each."],
          tasks=[visit("mes:placid_prairie", "Find a placid prairie"),
                 {"timed": {"seconds": 70, "goal": {"hold": {"radius": 10}}, "lines": ["Rest. Nothing will hurt you here."],
                            "start": "Rest a minute"}, "title": "Rest a full minute in the prairie"},
                 visit("mes:enderskog", "Find an enderskog")],
          rewards=[reward_item("irons_spellbooks:oakskin_elixir", 2), skill("forage", 650)]),

    quest("void_wildlife", "Void Wildlife", icon="alexsmobs:cosmic_cod_bucket", after=["quiet_meadows"],
          text=["Ilse wants proof there's life here: bucket a cosmic cod, feed an endergrade chorus until it follows "
                "you, and bring back ender residue from an enderiophage."],
          tasks=[item("alexsmobs:cosmic_cod_bucket", title="Bucket a cosmic cod"),
                 {"interact": "alexsmobs:endergrade", "holding": "minecraft:chorus_fruit", "consume": True, "title": "Feed an endergrade chorus fruit until it follows you"},
                 item("alexsmobs:ender_residue", title="Bring back ender residue from an enderiophage")],
          rewards=[reward_item("alexsmobs:cosmic_cod_bucket"), skill("taming", 700)]),

    quest("salvage_the_scraps", "Salvage the Scraps", icon="minecraft:iron_ingot", after=["beyond_the_gateway"],
          text=["Broken pillars, spikes and scrap heaps litter the islands. Sift three of them for the void's "
                "leftovers."],
          tasks=[search("mes:endscraps", 1, "a Void Leftover", "Something the void left behind.", title="Sift a scrap heap for the void's leftovers")],
          rewards=[reward_item("irons_spellbooks:arcane_salvage", 4), skill("craft", 300)]),

    quest("null_space", "Null Space", icon="minecraft:amethyst_block", after=["first_flight"],
          text=["Beyond the cities the End gets stranger. Fly over the crystal peaks, the shadowlands and the void "
                "barrens."],
          tasks=[{"biome": "nullscape:crystal_peaks", "title": "Fly over the crystal peaks"},
                 {"biome": "nullscape:shadowlands", "title": "Fly over the shadowlands"},
                 {"biome": "nullscape:void_barrens", "title": "Fly over the void barrens"}],
          rewards=[reward_item("minecraft:amethyst_block", 8), skill("agility", 700)]),

    quest("bones_in_the_dark", "Bones in the Dark", icon="minecraft:bone_block", after=["null_space"],
          discover={"structure": "nullscape:dragon_skeleton"},
          text=["In the shadowlands lie the bones of a dragon far older than the one you killed. Count its ribs: "
                "Ilse thinks there were many dragons once."],
          tasks=[item("minecraft:bone_block", 4, title="Take bone from the old dragon")],
          rewards=[reward_item("minecraft:bone", name="An Elder Dragon's Bone", lore=["Older than the one you killed."]), skill("magic", 700)]),

    quest("strange_shores", "Strange Shores", icon="naturescompass:naturescompass", after=["null_space"],
          text=["Some islands are overgrown or rotten. Stand in the End wilds, the End reef and the End corruption."],
          tasks=[{"biome": "biomesoplenty:end_wilds", "title": "Stand in the End wilds"},
                 {"biome": "biomesoplenty:end_reef", "title": "Stand in the End reef"},
                 {"biome": "biomesoplenty:end_corruption", "title": "Stand in the End corruption"}],
          rewards=[reward_item("naturescompass:naturescompass"), skill("forage", 700)]),

    quest("the_end_tower", "The Lonely Tower", icon="minecraft:ender_chest", after=["first_flight"],
          text=["A tower stands alone on an outer island. Climb it and bring Ilse the star map kept at its top."],
          tasks=[visit("structory_towers:end/end_tower", "Find the lonely tower on the outer island"),
                 search("structory_towers:end/end_tower", 1, "the Star Map", "A star map, kept in the tower's top chest.",
                        texture="minecraft:item/map", title="Take the star map from the tower's top")],
          rewards=[reward_item("minecraft:end_crystal", 2), reward_item("minecraft:ender_pearl", 4), skill("agility", 700)]),

    quest("the_aviary", "The Aviary", icon="minecraft:bow", after=["first_flight"],
          text=["A colossal bird-cage of a dungeon floats in the End. Clear the aviary and its keepers."],
          tasks=[visit("dungeons_arise:aviary", "Find the floating aviary"),
                 fight("minecraft:vex", 8, "dungeons_arise:aviary", "Aviary Keepers", "Clear the aviary and its keepers", wave=4)],
          rewards=[reward_item("minecraft:diamond", 2), reward_item("minecraft:enchanted_book", enchant={'minecraft:feather_falling': 4}), skill("attack", 700)]),

    quest("the_sealed_citadel", "The Sealed Citadel", icon="minecraft:golden_apple", after=["null_space"],
          text=["In the highlands stands a ruined citadel with a door that will not open while its guardian sleeps. "
                "Find the Ruined Citadel and note its Ender Golems. This one is for later."],
          tasks=[visit("cataclysm:ruined_citadel", "Find the ruined citadel in the highlands"),
                 {"observe": "cataclysm:ender_golem", "ticks": 40, "title": "Note the Ender Golems at its door"}],
          rewards=[reward_item("cataclysm:void_shard"), skill("agility", 700)]),
]

ACT5 = [
    quest("sky_pirates", "Sky Pirates", icon="minecraft:crossbow", after=["the_aviary"],
          text=["An airship drifts through the void, crewed by illagers who think the End is empty. Board one and "
                "take its captain's chest."],
          tasks=[visit("#airships", "Find an airship drifting through the void"),
                 fight("minecraft:pillager", 8, "#airships", "Sky Pirate Crew", "Board it and fight the crew"),
                 search("#airships", 1, "the Captain's Chest", "The captain's chest, bound in brass.", title="Take the captain's chest")],
          rewards=[reward_item("minecraft:white_banner", name="The Sky Pirates' Banner"), reward_item("minecraft:emerald", 16), skill("attack", 850)]),

    quest("void_eye", "The Void Eye", icon="cataclysm:void_eye", after=["the_sealed_citadel", "shells_for_boxes", "main_story:act5_start"],
          text=["The guardian woke with the others. Craft the Void Eye from shulker shells and an eye of ender, and "
                "give Ilse the finished chart of the End."],
          tasks=[item("minecraft:shulker_shell", 4, title="Gather shulker shells for the eye"),
                 item("minecraft:ender_eye", title="Gather an eye of ender for the eye"),
                 item("cataclysm:void_eye", crafted=True, title="Craft the Void Eye"),
                 talk_char("ilse", ["The finished chart. At last. Thank you.", "Take my boots. The void forgives nothing."],
                           title="Give Ilse the finished chart of the End")],
          rewards=[{"choice": [reward_item("cataclysm:cursium_boots", name="Ilse's Voidwalker Boots", lore=['The void gave way beneath them.'], enchant={'minecraft:feather_falling': 4, 'minecraft:soul_speed': 3}, unbreakable=True), reward_item("spartanweaponry:netherite_rapier", name="The Void's Quill", lore=['Sketches the air, then cuts it.'], enchant={'minecraft:sharpness': 5, 'minecraft:looting': 3}, unbreakable=True), reward_item("irons_spellbooks:legendary_spell_book", name="Ilse's Folio", lore=['Every page was written in the dark.'])], "title": "Choose one"}, skill("agility", 900)]),
]

chapter("end", "The End", "Cold, quiet wonder", "minecraft:end_stone", "realms", 3, ACT4 + ACT5)
