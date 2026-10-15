"""Chapter: skill_range, the Hunters' Lodge path: prologue and Act I (first release).
Plan: src/plans/quests/skill_range.json. Huntmistress Orla Vance and Old Tobiah keep the lodge on the hill west of Reece."""
from common import chapter, quest, talk_char, talk_org, item, reward_item, skill, encounter
from common import enc, fight, boss, search, sample, talk_org, talk_villager, talk_char, item, reward_item, skill, encounter, giver_org  # noqa: F401

Q = [
    quest("lodge_oath", "Bow and Oath", icon="minecraft:bow",
          text=["Huntmistress Vance won't take a hunter who can't make their own gear. Craft a bow and a quiver's "
                "worth of arrows, then swear the lodge oath at the hunters' lodge on the hill west of Reece."],
          tasks=[item("minecraft:bow", crafted=True), item("minecraft:arrow", 32),
                 talk_char("orla", ["A bow you made yourself. Good. The lodge has one oath.", "Never waste a kill. Say it, and you're one of us."])],
          rewards=[reward_item("minecraft:lead", name="Lodge Armband", lore=["Worn by hunters of the lodge."]),
                   reward_item("minecraft:arrow", 16), skill("range", 50)]),

    quest("first_tracks", "First Tracks", icon="naturalist:antler", after=["lodge_oath"],
          text=["A fletcher shows you how to follow hoof prints through the woods. Track a deer, and take venison "
                "and an antler."],
          tasks=[talk_org("hunters", ["Deep at the front: walking, not running. Follow quietly, downwind.", "Bring back the venison. The antler's for the lodge wall."]),
                 item("naturalist:venison", 2),
                 {"drop": {"from": ["naturalist:deer"], "chance": 0.4, "item": "naturalist:antler"}}],
          rewards=[reward_item("minecraft:leather", 8), skill("range", 80)]),

    quest("target_practice", "Bullseye", icon="minecraft:target", after=["lodge_oath"],
          text=["At the lodge's range, put ten arrows into target blocks at longer and longer distances."],
          tasks=[item("minecraft:target", 3, crafted=True, title="Make three target blocks"),
                 {"checkmark": "I put ten arrows into the targets"}],
          rewards=[reward_item("minecraft:arrow", 32), reward_item("minecraft:iron_ingot", 4), skill("range", 80)]),

    quest("boar_trouble", "Tusks in the Turnips", icon="naturalist:bushmeat", after=["first_tracks"],
          text=["Wild boars are tearing up a village's fields. Hunt down the sounder before it ruins the harvest, "
                "and keep the bushmeat."],
          tasks=[{"structure": "#villages", "title": "Reach the troubled village"},
                 {"kill": "naturalist:boar", "count": 4, "title": "Drive the sounder off the fields", "spawn": {"at": {"structure": "#villages"}}}, item("naturalist:bushmeat", 3)],
          rewards=[reward_item("naturalist:cooked_bushmeat", 8), skill("range", 120)]),

    quest("throwing_steel", "Thrown Steel", icon="spartanweaponry:iron_throwing_knife", after=["target_practice"],
          text=["Old Tobiah swears by thrown weapons, and by never whistling in a forest. Craft iron throwing "
                "knives, a tomahawk and javelins, and put them to use."],
          tasks=[item("spartanweaponry:iron_throwing_knife", crafted=True),
                 item("spartanweaponry:iron_tomahawk", crafted=True),
                 item("spartanweaponry:iron_javelin", crafted=True),
                 {"kill": "minecraft:zombie", "count": 6, "title": "Make kills with your thrown steel"}],
          rewards=[reward_item("spartanweaponry:copper_boomerang"), skill("range", 150)]),

    quest("firewatch", "The Lookout", icon="minecraft:spyglass", after=["boar_trouble"],
          text=["The lodge keeps a lookout in a firewatch tower deep in the forest. Climb it, meet the watcher and "
                "mark three game trails from the top."],
          tasks=[{"structure": "#firewatch_towers", "title": "Climb the firewatch tower"},
                 encounter(["Welcome up! Deer east, boar by the stream, something big north.", "Mark them. The lodge wants the map."],
                           entity="minecraft:villager", name="Tower Watcher", where={"above_y": 60}),
                 {"search": {"at": {"structure": "#firewatch_towers"}, "count": 1,
                             "item": {"name": "Watcher's Trail Map", "tooltip": "Three game trails, inked from the top",
                                      "texture": "minecraft:item/map"},
                             "found": "The watcher's old trail map, three game trails inked on it."},
                  "title": "Take the watcher's trail map from the tower"}],
          rewards=[reward_item("minecraft:spyglass"), skill("range", 150)]),

    quest("longbow", "The Longbow", icon="spartanweaponry:iron_longbow", after=["firewatch"],
          text=["From the tower, the watcher points out a deer far below. Craft a longbow and drop it with one "
                "shot from the top, before it wanders off."],
          tasks=[item("spartanweaponry:iron_longbow", crafted=True), {"structure": "#firewatch_towers"},
                 {"timed": {"seconds": 180, "goal": {"kill": "naturalist:deer", "count": 1},
                            "lines": ["There. Far below. You won't get long.", "One good shot."],
                            "start": "Take the shot", "no": ["teleport"]}, "title": "Drop the deer in three minutes"}],
          rewards=[reward_item("minecraft:arrow", 32), reward_item("minecraft:spectral_arrow", 8),
                   skill("range", 180)]),

    quest("silent_camp", "The Silent Camp", icon="alexsmobs:bear_fur", after=["firewatch"],
          text=["A hunting party's camp has gone quiet. Find it, follow the claw marks and rescue the last hunter "
                "from the tree where a grizzly bear has kept him for two days."],
          tasks=[{"structure": "#camps", "title": "Find the silent camp"},
                 encounter(["Grrrrr!"], then="kill", entity="alexsmobs:grizzly_bear", name="Camp Grizzly",
                           health=60, glow=True),
                 encounter(["Is it gone? Two days up this tree! Thank you, friend.", "Tell the lodge I'm alive."],
                           entity="minecraft:villager", name="Stranded Hunter")],
          rewards=[reward_item("alexsmobs:bear_fur", 2), skill("range", 220)]),

    quest("odd_coats", "Odd Coats", icon="minecraft:spider_eye", after=["throwing_steel"],
          text=["The lodge collects strange pelts and bones. Bring down odd-looking zombies, spiders and skeletons "
                "with arrows, and bring proof of each."],
          tasks=[{"drop": {"from": ["minecraft:zombie"], "chance": 0.15,
                           "item": {"name": "Odd Hide", "tooltip": "Proof for the lodge",
                                    "texture": "minecraft:item/rotten_flesh"}}, "consume": False},
                 {"drop": {"from": ["minecraft:spider"], "chance": 0.15,
                           "item": {"name": "Odd Fang", "tooltip": "Proof for the lodge",
                                    "texture": "minecraft:item/spider_eye"}}, "consume": False},
                 {"drop": {"from": ["minecraft:skeleton"], "chance": 0.15,
                           "item": {"name": "Odd Bone", "tooltip": "Proof for the lodge",
                                    "texture": "minecraft:item/bone"}}, "consume": False}],
          rewards=[reward_item("minecraft:spectral_arrow", 16), reward_item("minecraft:arrow", 32),
                   skill("range", 200)]),

    quest("heavy_crossbow", "Bolts at Night", icon="spartanweaponry:iron_heavy_crossbow",
          after=["odd_coats", "main_story:act1_start"],
          text=["Some nights call for a heavier weapon. Craft a heavy crossbow and bolts and drop twenty skeletons "
                "before dawn."],
          tasks=[item("spartanweaponry:iron_heavy_crossbow", crafted=True), item("spartanweaponry:bolt", 32),
                 {"kill": "minecraft:skeleton", "count": 20, "title": "Hold the night: drop twenty skeletons"}],
          rewards=[reward_item("spartanweaponry:bolt", 32), skill("range", 280)]),
]

ACT2 = [
    quest("superstition", "Tobiah's Hat", icon="artifacts:superstitious_hat", after=["silent_camp", "heavy_crossbow"],
          signature="artifacts:superstitious_hat",
          text=["Old Tobiah never hunted without his lucky hat, and only passes it to someone who brings him "
                "trophies from three different beasts. Luck, he says, follows the hat."],
          tasks=[item("alexsmobs:moose_antler", title="Bring a moose's antler"),
                 item("alexsmobs:crocodile_scute", title="Bring a crocodile's scute"),
                 item("alexsmobs:gazelle_horn", title="Bring a gazelle's horn"),
                 talk_char("tobiah", ["Three beasts, three trophies. The hat is yours.", "Left foot first. Always."],
                           title="Show Tobiah your three trophies")],
          rewards=[reward_item("artifacts:superstitious_hat"), skill("range", 300)]),

    quest("savanna_hunt", "The Long Grass", icon="naturalist:lion_spawn_egg",
          after=["superstition", "main_story:act2_start"],
          text=["In the savanna the hunter becomes the hunted. Track a lion pride and a rhino for the lodge, and take "
                "their hides without being charged."],
          tasks=[{"biome": "minecraft:savanna", "title": "Reach the savanna's long grass"},
                 {"kill": "naturalist:lion", "count": 2, "title": "Bring down two lions of the pride for the lodge"},
                 {"kill": "naturalist:rhino", "title": "Bring down a rhino for the lodge"},
                 item("naturalist:fur", 2, title="Take their hides for the lodge wall")],
          rewards=[reward_item("minecraft:spectral_arrow", 32), reward_item("minecraft:arrow", 64), skill("range", 320)]),

    quest("tiger_stalk", "Stripes in the Shade", icon="minecraft:bow", after=["superstition"],
          text=["A tiger has been stalking a jungle village. Sneak through the undergrowth without being spotted and "
                "take it before it takes you."],
          tasks=[{"biome": "minecraft:jungle", "title": "Creep into the jungle around the village"},
                 enc(["*A low growl in the undergrowth.*"], then="kill", entity="alexsmobs:tiger", name="The Village Tiger",
                     title="Take the tiger before it takes you", where={"biomes": ["minecraft:jungle", "minecraft:bamboo_jungle"]})],
          rewards=[reward_item("minecraft:arrow", 32), reward_item("minecraft:gunpowder", 16), skill("range", 340)]),

    quest("anaconda", "Coils in the Swamp", icon="alexsmobs:shed_snake_skin", after=["superstition"],
          text=["A villager's boat was dragged under by an anaconda. Hunt it in the swamp and bring back its shed "
                "skin for the lodge."],
          tasks=[{"biome": "minecraft:swamp", "title": "Go to the swamp where the boat was lost"},
                 enc(["*The water ripples. Something huge coils.*"], then="kill", entity="alexsmobs:anaconda",
                     name="The Boat-Taker", title="Hunt the anaconda that sank the boat",
                     where={"biomes": ["minecraft:swamp", "minecraft:mangrove_swamp"]}),
                 item("alexsmobs:shed_snake_skin", title="Bring back its shed skin for the lodge")],
          rewards=[reward_item("alexsmobs:shed_snake_skin"), skill("range", 320)]),

    quest("snow_leopard", "Ghost of the Peaks", icon="alexsmobs:froststalker_horn", after=["savanna_hunt"],
          text=["High in the snowy peaks, find the tracks of a snow leopard and a froststalker. The lodge wants the "
                "froststalker's horn."],
          tasks=[{"biome": "minecraft:frozen_peaks", "title": "Climb to the snowy peaks to follow the tracks"},
                 enc(["*Ice cracks. Something pale watches.*"], then="kill", entity="alexsmobs:froststalker",
                     name="The Froststalker", title="Bring down the froststalker for its horn",
                     where={"biomes": ["minecraft:frozen_peaks", "minecraft:snowy_slopes", "minecraft:jagged_peaks"]}),
                 item("alexsmobs:froststalker_horn", title="Take its horn for the lodge")],
          rewards=[reward_item("alexsmobs:froststalker_helmet"), skill("range", 360)]),

    quest("long_shot", "The Long Shot", icon="spartanweaponry:iron_longbow", after=["snow_leopard"],
          text=["Tobiah bets you can't hit a target from fifty blocks across a ravine. Prove him wrong with a longbow."],
          tasks=[talk_char("tobiah", ["Fifty blocks. Across a ravine. Bet you miss.", "Wind's from the west. Mind it."],
                           title="Take Tobiah's bet"),
                 item("spartanweaponry:iron_longbow", crafted=True, title="Make the longbow for the shot"),
                 {"build": {"blocks": {"minecraft:target": 1}, "radius": 12}, "title": "Set up a target across the gap"}],
          rewards=[reward_item("minecraft:arrow", 64), reward_item("minecraft:spectral_arrow", 16), skill("range", 380)]),

    quest("rival_lodge", "The Rival Lodge", icon="spartanweaponry:diamond_longbow", after=["long_shot", "tiger_stalk"],
          text=["A rival lodge from a far village claims the best hunters. The contest at a logging camp: most game "
                "taken with bow and thrown weapons in one day."],
          tasks=[{"structure": "meadow:logging_camp", "title": "Reach the logging camp where the contest is held"},
                 {"timed": {"seconds": 600, "goal": {"kill": "naturalist:deer", "count": 6},
                            "waves": [{"entity": "naturalist:deer", "count": 4, "every": 60}],
                            "lines": ["Most game wins the day. Bow and thrown weapons only."],
                            "start": "Begin the contest"}, "title": "Take more game than the rival lodge"}],
          rewards=[reward_item("spartanweaponry:diamond_longbow"), skill("range", 400)]),
]

ACT3 = [
    quest("soul_vultures", "Vultures of the Valley", icon="alexsmobs:soul_heart", after=["rival_lodge", "main_story:act3_start"],
          text=["The Nether has game too. Shoot soul vultures out of the sky over a soul sand valley and take a soul "
                "heart."],
          tasks=[{"biome": "minecraft:soul_sand_valley", "title": "Go to a soul sand valley's skies"},
                 {"kill": "alexsmobs:soul_vulture", "count": 2, "title": "Shoot soul vultures out of the sky for the lodge"},
                 item("alexsmobs:soul_heart", title="Take a soul heart")],
          rewards=[reward_item("alexsmobs:soul_heart"), skill("range", 450)]),

    quest("bone_serpent", "The Serpent in the Lava", icon="alexsmobs:bone_serpent_tooth", after=["soul_vultures"],
          text=["Lava lakes hide a bone serpent. Lure it out and bring it down from the shore before it pulls you "
                "in. Its tooth goes on the lodge wall."],
          tasks=[enc(["*The lava heaves, and bone breaks the surface.*"], then="kill", entity="alexsmobs:bone_serpent", name="The Lava Serpent",
                     title="Lure the bone serpent out and bring it down from the shore", where={"dimension": "minecraft:the_nether"}),
                 item("alexsmobs:bone_serpent_tooth", title="Take its tooth for the lodge wall")],
          rewards=[reward_item("alexsmobs:bone_serpent_tooth"), skill("range", 480)]),

    quest("warped_mosco", "The Warped Swarm", icon="alexsmobs:warped_muscle", after=["bone_serpent"],
          text=["A crimson mosquito fed on warped fungus and grew into a monster. Track it to its warped forest and "
                "shoot it down."],
          tasks=[{"biome": "minecraft:warped_forest", "title": "Track the monster into the warped forest"},
                 enc(["*A shrill drone, far too large.*"], then="kill", entity="alexsmobs:warped_mosco", name="The Warped Mosco",
                     title="Shoot down the monster mosquito", where={"biomes": ["minecraft:warped_forest"]})],
          rewards=[reward_item("alexsmobs:warped_muscle"), reward_item("minecraft:arrow", 32), skill("range", 500)]),

    quest("trophy_hall", "The Trophy Hall", icon="handcrafted:bear_trophy", after=["warped_mosco"],
          text=["The lodge in Reece needs a hall worthy of its hunters. Build it, and hang five trophies."],
          tasks=[{"place": "reece"},
                 item("handcrafted:bear_trophy", title="Mount a bear trophy"),
                 item("handcrafted:skeleton_trophy", title="Mount a skeleton trophy"),
                 item("handcrafted:fox_trophy", title="Mount a fox trophy"),
                 item("handcrafted:goat_trophy", title="Mount a goat trophy"),
                 {"build": {"blocks": {"handcrafted:bear_trophy": 1, "handcrafted:skeleton_trophy": 1,
                                       "handcrafted:fox_trophy": 1, "handcrafted:goat_trophy": 1}, "radius": 12},
                  "title": "Hang the trophies in the lodge's new hall"}],
          rewards=[reward_item("handcrafted:bear_trophy"), skill("range", 520)]),
]

ACT4 = [
    quest("netherite_longbow", "A Bow for the End", icon="spartanweaponry:netherite_longbow", after=["trophy_hall", "main_story:act4_start"],
          text=["The hunts ahead need reach. Forge a netherite longbow and a huge quiver of arrows."],
          tasks=[item("spartanweaponry:netherite_longbow", crafted=True, title="Forge a netherite longbow"),
                 item("minecraft:arrow", 64, title="Fill a quiver for the hunts to come")],
          rewards=[reward_item("minecraft:spectral_arrow", 32), skill("range", 700)]),

    quest("void_swarm", "Swarm Out of the Void", icon="alexsmobs:ender_residue", after=["netherite_longbow"],
          text=["In the End, enderiophage swarms drift between the islands. Thin them out with arrows and keep your "
                "feet on the edge."],
          tasks=[{"dimension": "minecraft:the_end", "title": "Go to the End's drifting islands"},
                 {"kill": "alexsmobs:enderiophage", "count": 6, "title": "Thin the swarms with arrows from the island edge"},
                 item("alexsmobs:ender_residue", 2, title="Take ender residue from the swarm")],
          rewards=[reward_item("alexsmobs:ender_residue", 4), skill("range", 740)]),

    quest("ironhide", "Old Ironhide", icon="naturalist:rhino_spawn_egg", after=["netherite_longbow"],
          text=["First of the legendary beasts: a rhinoceros the size of a hut, its hide stopping ordinary arrows. "
                "Find Old Ironhide on the plains and take him."],
          tasks=[{"biome": "minecraft:savanna", "title": "Find Old Ironhide on the plains"},
                 enc(["*A thunder of hooves.*"], then="kill", entity="naturalist:rhino", name="Old Ironhide", health=120, glow=True,
                     title="Take down Old Ironhide", where={"biomes": ["minecraft:savanna", "minecraft:plains"]}),
                 sample("Ironhide's Horn", ["naturalist:rhino"], 0.7, texture="minecraft:item/bone", tooltip="For the lodge wall")],
          rewards=[reward_item("minecraft:bone", name="Ironhide's Horn", lore=["From the first legend."]), skill("range", 780)]),

    quest("grey_widow", "The Grey Widow", icon="alexsmobs:tarantula_hawk_wing", after=["ironhide"],
          text=["Second legend: a tarantula hawk that hunts travellers in the desert, faster in the air than any "
                "arrow you've fired. Take its wing."],
          tasks=[{"biome": "minecraft:desert", "title": "Go where the Grey Widow hunts"},
                 enc(["*A shrill whine, high above.*"], then="kill", entity="alexsmobs:tarantula_hawk", name="The Grey Widow", health=100, glow=True,
                     title="Shoot down the Grey Widow", where={"biomes": ["minecraft:desert"]}),
                 item("alexsmobs:tarantula_hawk_wing", title="Take its wing")],
          rewards=[reward_item("alexsmobs:tarantula_hawk_wing"), skill("range", 800)]),
]

ACT5 = [
    quest("white_stag", "The White Stag", icon="artifacts:golden_hook", after=["grey_widow", "main_story:act5_start"],
          signature="artifacts:golden_hook",
          text=["The last legend: a white stag seen once a generation. Track it across three biomes, and when it "
                "falls, hang its antlers on the lodge's golden hook, which Vance then gives to you."],
          tasks=[{"biome": "minecraft:forest", "title": "Pick up the white stag's trail in the forest"},
                 {"biome": "minecraft:taiga", "title": "Follow it across the taiga"},
                 enc(["*Pale antlers among the snow-laden firs.*"], then="kill", entity="naturalist:deer", name="The White Stag", health=80, glow=True,
                     title="Bring down the white stag", where={"biomes": ["minecraft:snowy_taiga", "minecraft:taiga", "minecraft:grove"]}),
                 item("naturalist:antler", title="Hang its antlers on the lodge's golden hook")],
          rewards=[reward_item("artifacts:golden_hook"), skill("range", 850)]),

    quest("crystal_crabs", "Crabs of Amethyst", icon="cataclysm:amethyst_crab_shell", after=["white_stag"],
          text=["Something has been crystallising beaches. Find the amethyst nest and bring down its amethyst crab "
                "from range."],
          tasks=[{"structure": "cataclysm:amethyst_nest", "title": "Find the amethyst nest"},
                 fight("cataclysm:amethyst_crab", 2, "cataclysm:amethyst_nest", "Nest Crabs", "Bring down the amethyst crab from range", wave=1),
                 item("cataclysm:amethyst_crab_shell", title="Take an amethyst crab shell")],
          rewards=[reward_item("cataclysm:amethyst_crab_shell"), skill("range", 900)]),

    quest("huntmaster", "Huntmaster", icon="spartanweaponry:netherite_longbow", after=["crystal_crabs"],
          text=["With every legend on the wall and a thousand kills at range, Vance names you Huntmaster and gives "
                "you the lodge's own bow."],
          tasks=[talk_char("orla", ["Every legend on the wall. Huntmaster.", "Take the lodge's own bow."], title="Be named Huntmaster by Orla")],
          rewards=[reward_item("spartanweaponry:netherite_longbow", name="Vance's Whisper", lore=["The lodge's own bow."],
                               enchant={"minecraft:power": 5, "minecraft:infinity": 1, "minecraft:unbreaking": 3, "minecraft:flame": 1}),
                   skill("range", 1000)]),
]

chapter("skill_range", "The Hunters' Lodge", "Range path", "minecraft:bow", "skills", 7, Q + ACT2 + ACT3 + ACT4 + ACT5)
