"""Chapter: twilight, the Twilight Forest questline: Act II (first release). Plan: src/plans/quests/twilight.json.
The spirits of the forest speak through signs and the trophies of fallen guardians; each guardian lifts a curse and opens
the next land. Act III and IV quests are appended in later tasks."""
from common import chapter, quest, talk_org, item, reward_item, skill, enc, fight, boss, search, sample

WOOLS = ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", "light_gray", "cyan", "purple",
         "blue", "brown", "green", "red", "black"]

ACT2 = [
    quest("through_the_pool", "Through the Pool", icon="twilightforest:twilight_oak_sapling", after=["main_story:act1_finale"],
          text=["The pool you ringed with flowers is shimmering. Step in and wake in the Twilight Forest, the spirits' own "
                "realm, under its endless dusk."],
          tasks=[{"dimension": "twilightforest:twilight_forest", "title": "Step through the shimmering pool into the Twilight Forest"}],
          rewards=[reward_item("minecraft:torch", 16), reward_item("minecraft:bread", 8),
                   reward_item("twilightforest:twilight_oak_sapling"), skill("agility", 60)]),

    quest("fireflies_and_cicadas", "Lanterns of the Dusk", icon="twilightforest:firefly_jar", after=["through_the_pool"],
          text=["The dusk never lifts, and a camp needs light. Walk into a Firefly Forest and catch fireflies and "
                "cicadas in jars to light your first camp."],
          tasks=[{"biome": "twilightforest:firefly_forest", "title": "Walk into a Firefly Forest"},
                 item("twilightforest:firefly_jar", 2, title="Catch fireflies in jars to light your camp"),
                 item("twilightforest:cicada_jar", 2, title="Catch cicadas in jars to light your camp")],
          rewards=[reward_item("twilightforest:firefly_jar", 2), skill("forage", 150)]),

    quest("raven_feather", "The Wary Raven", icon="twilightforest:raven_feather", after=["through_the_pool"],
          text=["Forest ravens take flight at the slightest noise. Sneak up and take a raven feather, the key "
                "ingredient of the realm's maps."],
          tasks=[{"biome": "twilightforest:forest", "title": "Find the quiet forest where ravens roost"},
                 item("twilightforest:raven_feather", 2, title="Take raven feathers without startling the flock")],
          rewards=[reward_item("minecraft:arrow", 16), skill("range", 150)]),

    quest("magic_map", "A Map That Draws Itself", icon="twilightforest:magic_map", after=["raven_feather", "fireflies_and_cicadas"],
          text=["The forest hides its own roads. Bind a raven feather, torchberries and glowstone into a Magic Map "
                "Focus, then a Magic Map that charts biomes and marks every landmark around the portal."],
          tasks=[item("twilightforest:torchberries", 2, title="Pick torchberries for the focus"),
                 item("twilightforest:magic_map_focus", crafted=True, title="Bind a Magic Map Focus"),
                 item("twilightforest:magic_map", crafted=True, title="Craft a Magic Map that draws itself")],
          rewards=[reward_item("twilightforest:magic_map"), skill("craft", 180)]),

    quest("twilight_biomes", "Atlas of the Twilight", icon="twilightforest:twilight_oak_sapling", after=["magic_map"],
          text=["The map shows which lands are still veiled by curses. Set foot in the Enchanted Forest, the "
                "Mushroom Forest, the Spooky Forest and the Oak Savannah to chart them."],
          tasks=[{"biome": "twilightforest:enchanted_forest", "title": "Chart the Enchanted Forest"},
                 {"biome": "twilightforest:mushroom_forest", "title": "Chart the Mushroom Forest"},
                 {"biome": "twilightforest:spooky_forest", "title": "Chart the Spooky Forest"},
                 {"biome": "twilightforest:oak_savannah", "title": "Chart the Oak Savannah"}],
          rewards=[reward_item("twilightforest:charm_of_life_1"), skill("agility", 200)]),

    quest("hollow_hill", "Inside the Hollow Hill", icon="twilightforest:steeleaf_ingot", after=["magic_map"],
          text=["A grassy mound hides a cavern full of ores, spider spawners and redcaps. Break in, raid its chests "
                "and come out with steeleaf."],
          tasks=[{"structure": "#hollow_hills", "title": "Break into a hollow hill"},
                 item("twilightforest:steeleaf_ingot", 2, title="Raid the hill's chests for steeleaf")],
          rewards=[reward_item("twilightforest:steeleaf_ingot", 2), skill("mining", 200)]),

    quest("steeleaf_kit", "Leaf-Steel", icon="twilightforest:steeleaf_pickaxe", after=["hollow_hill"],
          text=["Steeleaf is the realm's first native metal, and gear that grows enchantments of its own. Forge "
                "a steeleaf pickaxe or chestplate."],
          tasks=[item("twilightforest:steeleaf_pickaxe", crafted=True, title="Forge steeleaf gear")],
          rewards=[reward_item("twilightforest:steeleaf_ingot", 2), skill("craft", 220)]),

    quest("naga_courtyard", "The Serpent's Court", icon="twilightforest:etched_nagastone", after=["magic_map"],
          text=["The magic map shows a walled courtyard of nagastone. Find it and scout its broken pillars before "
                "the guardian wakes."],
          tasks=[{"structure": "twilightforest:naga_courtyard", "title": "Find the Naga Courtyard on the map"},
                 {"observe": "twilightforest:naga", "ticks": 20, "title": "Watch the Naga coil among its pillars"}],
          rewards=[reward_item("minecraft:cooked_beef", 8), skill("agility", 160)]),

    quest("naga", "Coils of the Naga", icon="mowziesmobs:naga_fang", shape="diamond", size=1.5, after=["naga_courtyard"],
          text=["The Naga charges in loops through the courtyard. Dodge its rushes and strike its segments until it "
                "falls, lifting the first curse."],
          tasks=[boss("twilightforest:naga", "twilightforest:naga_courtyard", "The Naga", "Defeat the Naga to lift the first curse")],
          rewards=[reward_item("minecraft:golden_apple", 2), reward_item("irons_spellbooks:greater_healing_potion", 2),
                   skill("attack", 300)]),

    quest("naga_armor", "Scales of the Serpent", icon="twilightforest:naga_chestplate", after=["naga"],
          text=["The Naga's scales make armour that shrugs off knockback. Turn them into a chestplate and leggings."],
          tasks=[item("twilightforest:naga_chestplate", crafted=True, title="Forge a Naga Scale chestplate"),
                 item("twilightforest:naga_leggings", crafted=True, title="Forge Naga Scale leggings")],
          rewards=[reward_item("twilightforest:naga_banner_pattern"), skill("defense", 250)]),

    quest("quest_grove", "The Questing Ram", icon="twilightforest:quest_ram_banner_pattern", after=["magic_map"],
          text=["In a ring of stone in the Quest Grove grazes the Questing Ram, who wants wool of all sixteen "
                "colours. Feed it one of each and see what it leaves behind."],
          tasks=[{"structure": "twilightforest:quest_grove", "title": "Find the Questing Ram in its grove"}]
                + [item(f"minecraft:{c}_wool", consume=True, title=f"Feed the ram {c.replace('_', ' ')} wool") for c in WOOLS],
          rewards=[reward_item("twilightforest:quest_ram_banner_pattern"), reward_item("minecraft:emerald", 8), skill("farm", 250)]),

    quest("ironwood", "Living Iron", icon="twilightforest:ironwood_ingot", after=["hollow_hill"],
          text=["Ironwood grows from the forest floor. Dig liveroot, craft it with iron and gold into raw ironwood, "
                "and smelt ironwood ingots."],
          tasks=[item("twilightforest:liveroot", 4, title="Dig liveroot from the forest floor"),
                 item("twilightforest:raw_ironwood", 2, crafted=True, title="Craft raw ironwood with iron and gold"),
                 item("twilightforest:ironwood_ingot", 2, title="Smelt ironwood ingots")],
          rewards=[reward_item("twilightforest:ironwood_ingot", 4), skill("mining", 220)]),

    quest("spartan_ironwood", "Ironwood Arsenal", icon="spartantwilight:ironwood_glaive", after=["ironwood"],
          text=["A Spartan smith's pattern takes ironwood well. Craft an ironwood weapon: a glaive, katana or "
                "halberd."],
          tasks=[item("spartantwilight:ironwood_glaive", crafted=True, title="Forge an ironwood glaive")],
          rewards=[reward_item("twilightforest:ironwood_ingot", 4), skill("craft", 260)]),

    quest("mushroom_tower", "The Glowing Spire", icon="minecraft:red_mushroom_block", after=["twilight_biomes"],
          text=["A giant mushroom tower rises in the Mushroom Forest. Find the way up through its caps and stems to "
                "the loot at the top."],
          tasks=[{"structure": "twilightforest:mushroom_tower", "title": "Find the giant mushroom tower"},
                 item("twilightforest:torchberries", 4, title="Climb the caps and stems to the loot at the top")],
          rewards=[reward_item("twilightforest:torchberries", 4), skill("agility", 230)]),

    quest("hedge_maze", "Thorns in the Hedge", icon="minecraft:oak_leaves", after=["naga"],
          text=["Hedge spiders lurk in the Hedge Maze's walls. Reach the chests at its centre and get back out "
                "within ten minutes, before the spiders swarm."],
          tasks=[{"structure": "twilightforest:hedge_maze", "title": "Enter the Hedge Maze"},
                 {"timed": {"seconds": 600, "goal": {"kill": "twilightforest:hedge_spider", "count": 6},
                            "waves": [{"entity": "twilightforest:hedge_spider", "count": 3, "every": 40}],
                            "lines": ["The walls are crawling. Reach the centre quickly."], "start": "Run the maze"},
                  "title": "Fight through the hedge spiders before the swarm closes in"},
                 sample("a Centre Chest Key", ["twilightforest:hedge_spider"], 0.5, texture="minecraft:item/tripwire_hook", tooltip="Opens the chests at the maze's heart")],
          rewards=[reward_item("twilightforest:crumble_horn"), skill("agility", 250)]),

    quest("lich_tower", "The Lich's Spire", icon="twilightforest:lich_banner_pattern", after=["naga"],
          text=["With the Naga gone the Lich Tower opens. Climb its winding stairs and painting rooms, past skeleton "
                "druids and the tower's spawners."],
          tasks=[{"structure": "twilightforest:lich_tower", "title": "Find the Lich Tower"},
                 fight("twilightforest:skeleton_druid", 6, "twilightforest:lich_tower", "Tower Druids",
                       "Fight past the tower's skeleton druids")],
          rewards=[reward_item("minecraft:ender_pearl", 4), skill("agility", 250)]),

    quest("lich", "Shields of the Lich", icon="twilightforest:lich_trophy", shape="diamond", size=1.5, after=["lich_tower"],
          text=["The Lich hides behind spinning shields and clones. Break the shields with ranged blows, ignore the "
                "copies, and end it at the tower's crown."],
          tasks=[boss("twilightforest:lich", "twilightforest:lich_tower", "The Lich", "Defeat the Lich at the tower's crown")],
          rewards=[reward_item("twilightforest:charm_of_keeping_1"), reward_item("minecraft:golden_carrot", 8), skill("magic", 350)]),

    quest("scepters", "The Lich's Sceptres", icon="twilightforest:lifedrain_scepter", after=["lich"],
          text=["Among the Lich's treasures lie four sceptres. Claim one and use it in battle against the undead."],
          tasks=[item("twilightforest:lifedrain_scepter", title="Claim a sceptre from the Lich's treasures"),
                 {"kill": "minecraft:zombie", "count": 6, "title": "Test the sceptre against the dead"}],
          rewards=[reward_item("minecraft:ender_pearl", 8), reward_item("minecraft:rotten_flesh", 16), skill("magic", 330)]),

    quest("cursed_swamp", "The Choking Swamp", icon="minecraft:vine", after=["lich"],
          text=["The Lich's fall clears the fog over the Swamp, but mosquito swarms and hunger still haunt it. Cross "
                "it in search of the labyrinth."],
          tasks=[{"biome": "twilightforest:swamp", "title": "Cross the clearing swamp"},
                 enc(["*A buzzing cloud descends.*"], then="kill", entity="twilightforest:swarm_spider", name="Swamp Swarm",
                     title="Beat off the swarm that haunts the swamp", where={"biomes": ["twilightforest:swamp"]})],
          rewards=[reward_item("minecraft:cooked_beef", 16), skill("agility", 260)]),

    quest("maze_map", "Map of the Maze", icon="twilightforest:maze_map", after=["cursed_swamp", "magic_map"],
          text=["The labyrinth lies underground. Upgrade your Magic Map Focus into a Maze Map Focus and craft a Maze "
                "Map that traces corridors below."],
          tasks=[item("twilightforest:maze_map_focus", crafted=True, title="Upgrade your focus to trace corridors"),
                 item("twilightforest:maze_map", crafted=True, title="Craft a Maze Map")],
          rewards=[reward_item("twilightforest:maze_map"), skill("craft", 280)]),

    quest("labyrinth", "Halls of the Labyrinth", icon="twilightforest:mazebreaker_pickaxe", after=["maze_map"],
          text=["Below the swamp sprawls the Labyrinth, with maze slimes and trapped vaults. Map it and find the "
                "Mazebreaker Pickaxe or Ore Magnet in its vaults."],
          tasks=[{"structure": "twilightforest:labyrinth", "title": "Find the entrance to the labyrinth"},
                 fight("twilightforest:maze_slime", 6, "twilightforest:labyrinth", "Maze Slimes", "Clear the maze slimes from the halls"),
                 sample("a Vault Key", ["twilightforest:maze_slime"], 0.4, texture="minecraft:item/tripwire_hook", tooltip="Opens a trapped vault")],
          rewards=[reward_item("twilightforest:maze_map"), skill("mining", 330)]),

    quest("minotaurs", "Horns in the Dark", icon="twilightforest:diamond_minotaur_axe", after=["labyrinth"],
          text=["Minotaurs pace the labyrinth halls. Bring down five and take a Minotaur axe from them."],
          tasks=[fight("twilightforest:minotaur", 5, "twilightforest:labyrinth", "Labyrinth Minotaurs", "Bring down the labyrinth's minotaurs"),
                 sample("a Minotaur Axe", ["twilightforest:minotaur"], 0.5, texture="minecraft:item/iron_axe", tooltip="Taken from a minotaur")],
          rewards=[reward_item("minecraft:shield"), skill("attack", 340)]),

    quest("minoshroom", "The Minoshroom", icon="twilightforest:minoshroom_trophy", shape="diamond", size=1.5, after=["labyrinth"],
          text=["At the labyrinth's heart waits the Minoshroom, charging with its diamond axe. Bait its charge into "
                "walls and finish it."],
          tasks=[boss("twilightforest:minoshroom", "twilightforest:labyrinth", "The Minoshroom", "Defeat the Minoshroom at the labyrinth's heart")],
          rewards=[reward_item("twilightforest:diamond_minotaur_axe"), reward_item("irons_spellbooks:greater_healing_potion", 2),
                   skill("attack", 400)]),

    quest("meef", "Meef Stroganoff", icon="twilightforest:meef_stroganoff", after=["minoshroom"],
          text=["The Minoshroom's meef stroganoff is a Twilight classic. Taste it, then hunt raw meef from minotaurs "
                "and cook enough for your next trip."],
          tasks=[item("twilightforest:meef_stroganoff", 4, title="Cook meef stroganoff for the road")],
          rewards=[reward_item("twilightforest:meef_stroganoff", 4), skill("cook", 300)]),

    quest("uncrafting", "Unmaking Things", icon="twilightforest:uncrafting_table", after=["lich"],
          text=["Old gear can be unmade. Build an Uncrafting Table and break down an old enchanted item into its "
                "parts."],
          tasks=[item("twilightforest:uncrafting_table", crafted=True, title="Build an Uncrafting Table"),
                 {"use": "twilightforest:uncrafting_table", "count": 1, "title": "Break down an old enchanted item into its parts"}],
          rewards=[reward_item("minecraft:experience_bottle", 8), skill("craft", 280)]),

    quest("trophies_one", "Three Trophies", icon="twilightforest:naga_trophy", after=["naga", "lich", "minoshroom"],
          text=["The first part of the spirits' realm is free. Gather the Naga, Lich and Minoshroom trophies as "
                "proof."],
          tasks=[item("twilightforest:naga_trophy", title="Gather the Naga's trophy"),
                 item("twilightforest:lich_trophy", title="Gather the Lich's trophy"),
                 item("twilightforest:minoshroom_trophy", title="Gather the Minoshroom's trophy")],
          rewards=[reward_item("minecraft:chest", name="Ironwood Supply Chest", lore=["The spirits' thanks."]),
                   skill("agility", 350)]),
]

chapter("twilight", "The Twilight Forest", "The spirits' realm", "twilightforest:twilight_oak_sapling", "realms", 0, ACT2)
