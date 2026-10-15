"""Chapter: discovery_sea, the sea and the shore: wrecks, sunken ruins and coasts, found by sailing out and diving down.
Plan: src/plans/quests/discovery_sea.json. Quests with a "discover" stay hidden until the player reaches the place."""
from common import chapter, quest, talk_org, talk_villager, item, reward_item, skill, encounter


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
    quest("bones_of_the_deep", "Bones of the Deep", icon="minecraft:bone_block",
          discover={"structure": "#sea_dragon_bones"},
          text=["A dragon's skeleton lies on the sea floor, its ribs rising like a reef. The Anglers' Society swear "
                "it was a sea serpent, and want proof: one of its bones."],
          tasks=[{"be": {"in_water": True, "below_y": 45}, "title": "Dive down to the skeleton's skull"},
                 item("minecraft:bone_block", 2, title="Take bone from the skeleton as proof")],
          rewards=[reward_item("minecraft:bone_block", 8), reward_item("minecraft:nautilus_shell"),
                   skill("fish", 150)]),

    quest("the_tribune_of_atlantis", "The Tribune of Atlantis", icon="minecraft:sea_lantern",
          discover={"structure": "mos:atlantis_tribune"},
          text=["A tribune of white stone stands on the deep sea floor beside drowned Atlantean ruins. Its sockets are "
                "empty. Light them with sea lanterns, and the vault sealed beneath it should open."],
          tasks=[item("minecraft:sea_lantern", 4, consume=True, title="Bring four sea lanterns down to the tribune"),
                 {"build": {"blocks": {"minecraft:sea_lantern": 4}, "radius": 12}, "title": "Set the lanterns in the tribune"},
                 search("mos:atlantis_tribune", 1, "Vault Hoard", "The vault swings open on a drowned hoard.",
                        title="Open the tribune's sealed vault")],
          rewards=[reward_item("minecraft:prismarine", 32), reward_item("minecraft:trident"), skill("fish", 200)]),

    quest("the_conduit_arch", "The Conduit Arch", icon="minecraft:conduit",
          discover={"structure": "mos:conduit_arch"},
          text=["An arch of prismarine stands on the sea floor with an empty socket. A conduit set in it should "
                "light the waters around."],
          tasks=[item("minecraft:conduit", crafted=True, title="Craft a conduit from a heart of the sea and nautilus shells"),
                 {"build": {"blocks": {"minecraft:conduit": 1}, "radius": 6}, "title": "Set the conduit in the arch"}],
          rewards=[reward_item("minecraft:nautilus_shell", 2), reward_item("minecraft:prismarine", 16), skill("fish", 300)]),

    quest("x_marks_the_spot", "X Marks the Spot", icon="minecraft:filled_map",
          discover={"item": "minecraft:filled_map"},
          text=["A map you found marks a spot on the coast with an X. Dig where it points and bring home what a "
                "pirate buried."],
          tasks=[{"structure": "mos:buried_treasure", "title": "Follow the map to the X"},
                 item("minecraft:heart_of_the_sea", title="Dig out the chest and take the heart of the sea")],
          rewards=[reward_item("minecraft:gold_ingot", 12), skill("fish", 200)]),

    quest("wreck_diver", "Wreck Diver", icon="minecraft:oak_boat",
          discover={"structure": "#shipwrecks"},
          text=["Every wreck has a captain's chest, and every captain kept a log. Search the wrecks for the pages of "
                "their logs and piece together their last voyage."],
          tasks=[search("#shipwrecks", 2, "Captain's Log", "A waterlogged log, its last page still legible.",
                        title="Find two pages of the captain's logs")],
          rewards=[reward_item("minecraft:map"), reward_item("minecraft:emerald", 6), skill("fish", 150)]),

    quest("drowned_temple", "Drowned Halls", icon="minecraft:trident",
          discover={"structure": "#sunken_ruins"},
          text=["Sunken ruins are thick with drowned. One of them wears a medallion, and a cleric on shore would "
                "like to know whose."],
          tasks=[fight("minecraft:drowned", 8, "#sunken_ruins", "Ruin Drowned", "Clear the drowned from around the ruins"),
                 sample("the Drowned Priest's Medallion", ["minecraft:drowned"], 0.5, texture="minecraft:item/gold_nugget",
                        tooltip="Show it to a cleric"),
                 talk_villager("minecraft:cleric", ["A priest's medallion. He went down with his flock.", "We'll say a prayer tonight."],
                               title="Show the medallion to a cleric")],
          rewards=[reward_item("minecraft:trident"),
                   reward_item("minecraft:enchanted_book", name="Sea Spear", enchant={"minecraft:impaling": 3}),
                   skill("attack", 250)]),

    quest("typhon", "The Typhon", icon="minecraft:crossbow", after=["main_story:act2_finale"],
          discover={"structure": "dungeons_arise:typhon"},
          text=["The sea fortress Typhon rises from the ocean, its guns still manned. Board her, fight up the decks "
                "and hold her bridge until her crew breaks."],
          tasks=[fight("minecraft:pillager", 10, "dungeons_arise:typhon", "Typhon Crew", "Fight up the decks", wave=5),
                 {"timed": {"seconds": 180, "goal": {"hold": {"radius": 14}},
                            "waves": [{"entity": "minecraft:pillager", "count": 3, "every": 30}],
                            "lines": ["The crew's rallying on the bridge. Hold it!"], "start": "Hold the bridge"},
                  "title": "Hold the bridge until the crew breaks"}],
          rewards=[reward_item("minecraft:crossbow", name="Typhon's Gun", lore=["Pried from a manned gun."],
                               enchant={"minecraft:quick_charge": 2, "minecraft:piercing": 2}),
                   reward_item("smallships:oak_cog"), skill("defense", 450)]),

    quest("golden_hind", "The Golden Hind", icon="minecraft:gold_block",
          discover={"structure": "dungeons_arise:ceryneian_hind"},
          text=["The sunken ship Ceryneian Hind carried a golden figurehead of a deer. Its three pieces are scattered "
                "through the flooded holds."],
          tasks=[fight("minecraft:drowned", 6, "dungeons_arise:ceryneian_hind", "Hold Drowned",
                       "Clear the drowned from the flooded holds"),
                 search("dungeons_arise:ceryneian_hind", 1, "Figurehead Piece", "A curve of gold, shaped like an antler."),
                 sample("a Figurehead Piece", ["minecraft:drowned"], 0.4, count=2, texture="minecraft:item/gold_ingot",
                        tooltip="Part of the golden deer"),
                 {"build": {"blocks": {"minecraft:gold_block": 3}, "radius": 12}, "title": "Rebuild the figurehead on deck"}],
          rewards=[reward_item("minecraft:gold_block", 4),
                   reward_item("minecraft:enchanted_book", name="Depths Strider", enchant={"minecraft:depth_strider": 3}),
                   skill("fish", 300)]),

    quest("salvage_rights", "Salvage Rights", icon="smallships:oak_cog",
          discover={"structure": "towns_and_towers:wreckage_ocean"},
          text=["Sunken wreckage lies in the shallows, still good timber. Salvage planks, rope and cloth from it and "
                "build your own cog."],
          tasks=[item("minecraft:oak_planks", 16, title="Salvage planks from the wreckage"),
                 item("supplementaries:rope", 4, title="Salvage rope from the wreckage"),
                 item("minecraft:white_wool", 6, title="Salvage sailcloth"),
                 item("smallships:oak_cog", crafted=True, title="Build your own cog")],
          rewards=[reward_item("supplementaries:rope", 16), skill("craft", 200)]),

    quest("drowned_keeper", "The Drowned Keeper", icon="minecraft:sea_lantern",
          discover={"structure": "mvs:ocean_tower"},
          text=["An ocean tower's light has gone out, and its keeper walks the shallows as a drowned. Put him to rest "
                "and relight the lamp at the top."],
          tasks=[enc(["Grrr... the light... I must tend the light..."], then="kill", entity="minecraft:drowned",
                     name="The Drowned Keeper", health=30, title="Put the drowned keeper to rest"),
                 item("minecraft:sea_lantern", consume=True, title="Bring a lantern for the tower's lamp"),
                 {"build": {"blocks": {"minecraft:sea_lantern": 1}, "radius": 12}, "title": "Relight the lamp at the top"}],
          rewards=[reward_item("minecraft:lantern", 2), reward_item("minecraft:glowstone", 4), skill("fish", 150)]),

    quest("last_orders", "Last Orders at the Beach Bar", icon="artifacts:plastic_drinking_hat",
          signature="artifacts:plastic_drinking_hat",
          discover={"structure": "mvs:beach_bar"},
          text=["The beach bar's bartender is swamped, and his customers are thirsty and impatient. Mix four cocktails "
                "and serve them before the customers give up."],
          tasks=[item("beachparty:coconut_cocktail", consume=True, title="Mix a coconut cocktail"),
                 item("beachparty:honey_cocktail", consume=True, title="Mix a honey cocktail"),
                 item("beachparty:melon_cocktail", consume=True, title="Mix a melon cocktail"),
                 item("beachparty:pumpkin_cocktail", consume=True, title="Mix a pumpkin cocktail"),
                 {"timed": {"seconds": 150, "goal": {"hold": {"radius": 12}},
                            "lines": ["The customers are queuing. Keep them served!"], "start": "Serve the rush"},
                  "title": "Serve the beach rush before they give up"}],
          rewards=[reward_item("artifacts:plastic_drinking_hat"), reward_item("beachparty:coconut_cocktail", 3),
                   skill("cook", 220)]),

    quest("the_ritual_circle", "The Ritual Circle", icon="beachparty:radio",
          discover={"structure": "beachparty:ritual_circle"},
          text=["A circle of torches and shells on the beach. The old fishers say that if you place a seashell on "
                "each stone at sunset and play a beach disc on a radio, the sea gives something back."],
          tasks=[{"build": {"blocks": {"beachparty:radio": 1}, "radius": 8}, "title": "Set a radio in the circle"},
                 {"use": "beachparty:radio", "count": 1, "holding": "beachparty:music_disc_beachparty",
                  "title": "Play a beach disc on the radio"},
                 search("beachparty:ritual_circle", 1, "The Sea's Gift", "The sea gives a pearl-white shell back.",
                        texture="minecraft:item/nautilus_shell")],
          rewards=[reward_item("beachparty:music_disc_pridelands"), reward_item("beachparty:beach_hat"), skill("magic", 150)]),

    quest("the_faithful_hound", "The Faithful Hound", icon="domesticationinnovation:collar_tag",
          discover={"structure": "mos:prismarine_dog_statue"},
          text=["A prismarine statue of a dog still waits for its master on the sea floor. Tame a wolf, bring it to the "
                "statue and give it the statue's collar."],
          tasks=[{"tame": "minecraft:wolf", "title": "Tame a wolf to keep the statue company"},
                 search("mos:prismarine_dog_statue", 1, "the Statue's Collar", "A collar, green with age, in the statue's chest.",
                        texture="minecraft:item/lead"),
                 {"checkmark": "I gave the wolf the statue's collar"}],
          rewards=[reward_item("domesticationinnovation:collar_tag"), skill("taming", 150)]),

    quest("underwater_garden", "The Underwater Garden", icon="minecraft:brain_coral",
          discover={"structure": "mos:underwater_garden"},
          text=["A garden of coral and kelp grows inside sunken walls. Gather five kinds of coral, then plant a reef "
                "of your own."],
          tasks=[item("minecraft:tube_coral", title="Gather tube coral"),
                 item("minecraft:brain_coral", title="Gather brain coral"),
                 item("minecraft:bubble_coral", title="Gather bubble coral"),
                 item("minecraft:fire_coral", title="Gather fire coral"),
                 item("minecraft:horn_coral", title="Gather horn coral"),
                 {"build": {"blocks": {"minecraft:sea_pickle": 2, "minecraft:kelp": 4}, "radius": 10},
                  "title": "Plant a reef of your own"}],
          rewards=[reward_item("minecraft:sea_pickle", 4), reward_item("minecraft:tube_coral", 4), skill("forage", 150)]),

    quest("drowned_village", "The Drowned Village", icon="minecraft:bell",
          discover={"structure": "mos:ruined_church"},
          text=["A castle, a church and houses lie under the waves where a village once stood. Its church bell and "
                "the castle's crest would tell you its name."],
          tasks=[search("mos:ruined_church", 1, "Church Bell Clapper", "An iron clapper, green with age."),
                 search("mos:ruined_castle", 1, "Castle Crest", "A crest in cracked stone, shaped like a boat."),
                 {"checkmark": "I learned the drowned village's name"}],
          rewards=[reward_item("minecraft:bell"), reward_item("minecraft:gold_ingot", 8), skill("fish", 150)]),

    quest("beach_discs", "Songs of the Beach", icon="beachparty:radio",
          discover={"structure": "beachparty:excavated_treasure"},
          text=["An overgrown disc on the beach is the first of a set. Collect the others and play them on a radio."],
          tasks=[item("beachparty:overgrown_disc", title="Find the overgrown disc"),
                 item("beachparty:music_disc_beachparty", title="Collect the Beachparty disc"),
                 item("beachparty:music_disc_caribbean_beach", title="Collect the Caribbean Beach disc"),
                 item("beachparty:music_disc_vocalista", title="Collect the Vocalista disc"),
                 item("beachparty:music_disc_wild_veins", title="Collect the Wild Veins disc"),
                 {"use": "beachparty:radio", "count": 1, "title": "Play them on a radio"}],
          rewards=[reward_item("beachparty:radio"), reward_item("beachparty:palm_bar"), skill("fish", 150)]),

    quest("coral_reef", "The Coral Reef", icon="minecraft:tropical_fish_bucket",
          discover={"biome": "minecraft:warm_ocean"},
          text=["A warm ocean, full of colour. The Anglers' Society want reef fish in buckets to stock a tank."],
          tasks=[item("minecraft:tropical_fish_bucket", 3, title="Catch three reef fish in buckets")],
          rewards=[reward_item("minecraft:bucket", 2), skill("fish", 120)]),

    quest("frozen_ocean", "The Frozen Sea", icon="minecraft:blue_ice",
          discover={"biome": "minecraft:deep_frozen_ocean"},
          text=["A deep frozen ocean of icebergs and polar bears. Cross it, and fish through a hole in the ice, as "
                "the old Anglers do."],
          tasks=[{"be": {"biomes": ["minecraft:deep_frozen_ocean"], "in_water": False}, "title": "Cross the ice"},
                 item("minecraft:cod", 2, title="Fish through a hole in the ice")],
          rewards=[reward_item("minecraft:blue_ice", 4), skill("fish", 150)]),

    quest("tropic_islands", "Island Life", icon="beachparty:coconut",
          discover={"biome": "biomesoplenty:tropics"},
          text=["A tropical island with palms and sand. The Crafters' guild would love a coconut, and a hammock "
                "strung between two palms is the best way to rest."],
          tasks=[item("beachparty:coconut", title="Crack open a coconut"),
                 item("comforts:hammock_red", crafted=True, title="Make a hammock to rest in"),
                 {"build": {"blocks": {"comforts:hammock_red": 1}, "radius": 10}, "title": "Hang it between palms"}],
          rewards=[reward_item("beachparty:coconut", 4), reward_item("comforts:hammock_green"), skill("forage", 120)]),

    quest("rocky_reef", "The Rocky Reef", icon="regions_unexplored:hyacinth_flowers",
          discover={"biome": "regions_unexplored:rocky_reef"},
          text=["A rocky reef, with glowing plants clinging to the stones. The Herbalists would pay for hyacinth "
                "flowers from it."],
          tasks=[{"be": {"biomes": ["regions_unexplored:rocky_reef"], "in_water": True}, "title": "Dive among the reef's stones"},
                 item("regions_unexplored:hyacinth_flowers", 4, title="Bring back glowing hyacinth flowers")],
          rewards=[reward_item("regions_unexplored:hyacinth_flowers", 4), skill("fish", 120)]),

    quest("dune_beach", "The Dunes", icon="minecraft:sand",
          discover={"biome": "biomesoplenty:dune_beach"},
          text=["The dune beach has seashells and sea stars along the tide line. The Anglers collect them for their "
                "trophy cases."],
          tasks=[item("biomesoplenty:dune_grass", 4, title="Gather dune grass from the tide line"),
                 item("minecraft:nautilus_shell", title="Find a shell washed up on the beach")],
          rewards=[reward_item("minecraft:sea_pickle", 4), skill("fish", 120)]),

    quest("mangrove_maze", "The Mangrove Maze", icon="smallships:oak_rowboat",
          discover={"biome": "minecraft:mangrove_swamp"},
          text=["A mangrove swamp, its roots forming a maze. The Couriers want to know if a boat can get through "
                "without touching the bank."],
          tasks=[item("smallships:oak_rowboat", crafted=True, title="Build a rowboat for the maze"),
                 {"be": {"biomes": ["minecraft:mangrove_swamp"], "in_water": True}, "title": "Row into the mangrove roots"},
                 item("minecraft:mangrove_propagule", 2, title="Gather propagules on the far side")],
          rewards=[reward_item("minecraft:mangrove_propagule", 4), reward_item("minecraft:mangrove_boat"),
                   skill("agility", 150)]),
]

chapter("discovery_sea", "Out at Sea", "Salt, wrecks and drowned things", "minecraft:nautilus_shell", "explore", 1, Q)
