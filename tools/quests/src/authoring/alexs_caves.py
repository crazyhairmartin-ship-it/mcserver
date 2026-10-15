"""Chapter: alexs_caves, the Underworld questline (Alex's Caves): Act II (first release).
Plan: src/plans/quests/alexs_caves.json. A cartographer sells cave maps and the cave tablets point the way; four strange
worlds lie under the stone, each with its own creatures and climax. Magnetic and Toxic Caves are disabled in this pack.
Act III and later quests are appended in later tasks."""
from common import chapter, quest, talk_villager, item, reward_item, skill, enc, fight, boss, search, sample
from common import enc, fight, boss, search, sample, talk_org, talk_villager, talk_char, item, reward_item, skill, encounter, giver_org  # noqa: F401

ACT2 = [
    quest("rumours_below", "Rumours from Below", icon="alexscaves:cave_map", after=["main_story:act2_start"],
          text=["A village cartographer speaks of whole worlds under the stone, and sells cave maps. Buy one and let "
                "it search out the nearest cave biome."],
          tasks=[talk_villager("minecraft:cartographer", ["Whole worlds under the stone. I sell maps to them.",
                                                          "Take one. Mind the dark."], title="Ask a cartographer about the worlds below"),
                 item("alexscaves:cave_map", title="Buy a cave map to search out the nearest cave biome")],
          rewards=[reward_item("minecraft:emerald", 8), skill("agility", 100)]),

    quest("cave_book", "The Spelunker's Notes", icon="alexscaves:cave_codex", after=["rumours_below"],
          text=["Every cave biome is its own world. Craft a Cave Book to keep notes on each, and a Cave Codex as your "
                "journal of the underworld."],
          tasks=[item("alexscaves:cave_book", crafted=True, title="Craft a Cave Book to keep notes in"),
                 item("alexscaves:cave_codex", crafted=True, title="Craft a Cave Codex as your journal")],
          rewards=[reward_item("alexscaves:cave_codex"), skill("craft", 150)]),

    quest("primordial_caves", "Lost World", icon="minecraft:spyglass", after=["rumours_below"],
          discover={"biome": "alexscaves:primordial_caves"},
          text=["Under the forest roof lies a land of ferns and cycads: the Primordial Caves, home of the dinosaurs."],
          tasks=[{"be": {"biomes": ["alexscaves:primordial_caves"], "below_y": 60}, "title": "Walk under the forest roof into the lost world"}],
          rewards=[reward_item("minecraft:spyglass"), reward_item("alexscaves:amber", 4), skill("agility", 150)]),

    quest("cave_paintings", "Painted Walls", icon="alexscaves:cave_painting_relicheirus", after=["primordial_caves"],
          text=["The cave people left paintings on the primordial walls: hunts, friendships, and a mystery told across "
                "panels. Collect the panels and hang them to see what they show."],
          tasks=[item("alexscaves:cave_painting_ambersol", title="Find the amber-sun panel"),
                 item("alexscaves:cave_painting_relicheirus", title="Find the relicheirus panel"),
                 item("alexscaves:cave_painting_relicheirus_slash", title="Find the slashing panel"),
                 {"build": {"blocks": {"minecraft:painting": 3}, "radius": 8}, "unchecked": True,
                  "title": "Hang the panels to read the mystery"}],
          rewards=[reward_item("alexscaves:dinosaur_pottery_sherd"), skill("agility", 180)]),

    quest("ancient_groves", "Ancient Groves", icon="alexscaves:pewen_sapling", after=["primordial_caves"],
          text=["The ancient trees will not last forever. Gather pine nuts and a tree star, then grow a pewen sapling "
                "and an ancient sapling of your own."],
          tasks=[item("alexscaves:pine_nuts", 4, title="Gather pine nuts from a pewen"),
                 item("alexscaves:tree_star", title="Gather a tree star from an ancient tree"),
                 item("alexscaves:pewen_sapling", title="Take a pewen sapling"),
                 item("alexscaves:ancient_sapling", title="Take an ancient sapling"),
                 {"build": {"blocks": {"alexscaves:pewen_sapling": 1, "alexscaves:ancient_sapling": 1}, "radius": 12},
                  "title": "Plant them where they can grow on"}],
          rewards=[reward_item("alexscaves:pewen_planks", 16), skill("forage", 200)]),

    quest("dino_bowl", "The Dinosaur Bowl", icon="camerapture:camera", after=["primordial_caves"],
          text=["Look down into a dino bowl and watch grottoceratops herds and relicheirus graze among the tar. The "
                "Field Guide wants pictures."],
          tasks=[{"structure": "alexscaves:dino_bowl", "title": "Find a dino bowl"},
                 item("camerapture:camera", title="Bring a camera for the Field Guide"),
                 {"photo": {"entity": "alexscaves:grottoceratops"}, "title": "Photograph a grottoceratops"},
                 {"photo": {"entity": "alexscaves:relicheirus"}, "title": "Photograph a relicheirus"}],
          rewards=[reward_item("alexscaves:cooked_dinosaur_chop", 4), skill("taming", 200)]),

    quest("relicheirus_egg", "Claws Like Scythes", icon="alexscaves:relicheirus_egg", after=["dino_bowl"],
          text=["Find a relicheirus egg in the bowl, set it down somewhere safe until it hatches, and raise the "
                "hatchling so it learns to trust you."],
          tasks=[item("alexscaves:relicheirus_egg", title="Find a relicheirus egg in the bowl"),
                 {"tame": "alexscaves:relicheirus", "title": "Raise the hatchling until it trusts you"}],
          rewards=[reward_item("alexscaves:pine_nuts", 16), skill("taming", 250)]),

    quest("dino_chop", "Primordial Supper", icon="alexscaves:cooked_dinosaur_chop", after=["dino_bowl"],
          text=["The cave people ate well. Hunt a grottoceratops for dinosaur chops and cook them into hearty "
                "meals."],
          tasks=[fight("alexscaves:grottoceratops", 2, "alexscaves:dino_bowl", "Bowl Grottoceratops",
                       "Hunt grottoceratops for their chops", wave=2),
                 item("alexscaves:dinosaur_chop", 4, title="Take dinosaur chops"),
                 item("alexscaves:cooked_dinosaur_chop", 4, crafted=True, title="Cook the chops into hearty meals")],
          rewards=[reward_item("alexscaves:dinosaur_nugget", 8), skill("cook", 250)]),

    quest("primordial_garb", "Dressed for the Hunt", icon="alexscaves:primordial_tunic", after=["dino_chop"],
          text=["The hunt is hard on cloth. Gather tough hide and craft the full primordial outfit: helmet, tunic and "
                "pants, the cave people's own."],
          tasks=[item("alexscaves:tough_hide", 6, title="Hunt for tough hide"),
                 item("alexscaves:primordial_helmet", crafted=True, title="Craft the primordial helmet"),
                 item("alexscaves:primordial_tunic", crafted=True, title="Craft the primordial tunic"),
                 item("alexscaves:primordial_pants", crafted=True, title="Craft the primordial pants")],
          rewards=[reward_item("alexscaves:cooked_dinosaur_chop", 4), skill("craft", 280)]),

    quest("subterranodon", "Wings Over the Cave", icon="minecraft:saddle", after=["dino_bowl"],
          text=["The cavern is wide, and the herds are far. Tame a subterranodon and ride it across."],
          tasks=[{"tame": "alexscaves:subterranodon", "title": "Win a subterranodon's trust and ride it across the cavern"}],
          rewards=[reward_item("minecraft:saddle"), skill("taming", 280)]),

    quest("stolen_egg", "The Stolen Egg", icon="minecraft:egg", after=["dino_bowl"],
          text=["Vallumraptors have taken an atlatitan egg. Take it back from their pack and carry it safely to "
                "hatch."],
          tasks=[fight("alexscaves:vallumraptor", 4, "alexscaves:dino_bowl", "Egg-Thief Raptors", "Drive off the raptor pack"),
                 search("alexscaves:dino_bowl", 1, "the Atlatitan Egg", "The stolen egg, warm in the raptors' nest.",
                        texture="minecraft:item/egg", title="Take the atlatitan egg back from their nest")],
          rewards=[reward_item("alexscaves:primitive_club"), skill("taming", 300)]),

    quest("amber", "Trapped in Amber", icon="alexscaves:amber", after=["primordial_caves"],
          text=["Old things sleep inside amber. Search the cave walls for amber and an amber curiosity, relics "
                "sealed in resin."],
          tasks=[item("alexscaves:amber", 4, title="Mine amber from the cave walls"),
                 item("alexscaves:amber_curiosity", title="Find an amber curiosity sealed in resin")],
          rewards=[reward_item("alexscaves:amber", 8), skill("mining", 200)]),

    quest("volcano", "The Volcano", icon="minecraft:magma_block", after=["primordial_caves"],
          text=["The primordial volcano is a mountain of magma and tephra, guarded by the Tremorsaurus. Find it."],
          tasks=[{"structure": "alexscaves:volcano", "title": "Find the primordial volcano"}],
          rewards=[reward_item("alexscaves:charred_remnant", 2), skill("agility", 220)]),

    quest("tremorsaurus", "The Tremorsaurus", icon="alexscaves:heavy_bone", after=["volcano"],
          text=["The Tremorsaurus shakes the volcano's ground. Take it down and claim a heavy bone from the giant."],
          tasks=[boss("alexscaves:tremorsaurus", "alexscaves:volcano", "The Tremorsaurus", "Take down the volcano's Tremorsaurus"),
                 item("alexscaves:heavy_bone", title="Claim a heavy bone from the giant")],
          rewards=[reward_item("alexscaves:heavy_bone", 4), skill("attack", 350)]),

    quest("diving_gear", "Down to the Depths", icon="alexscaves:diving_helmet", after=["rumours_below"],
          text=["The drowned chasm is deeper than any breath. Craft a diving helmet, suit and boots."],
          tasks=[item("alexscaves:diving_helmet", crafted=True, title="Craft a diving helmet"),
                 item("alexscaves:diving_chestplate", crafted=True, title="Craft a diving suit"),
                 item("alexscaves:diving_leggings", crafted=True, title="Craft diving leggings"),
                 item("alexscaves:diving_boots", crafted=True, title="Craft diving boots")],
          rewards=[reward_item("alexscaves:depth_charge", 4), skill("craft", 250)]),

    quest("abyssal_chasm", "Into the Abyss", icon="alexscaves:bioluminescent_torch", after=["diving_gear"],
          discover={"biome": "alexscaves:abyssal_chasm"},
          text=["Under the ocean floor lies the Abyssal Chasm, where lanternfish and tripodfish swim in the dark."],
          tasks=[{"be": {"biomes": ["alexscaves:abyssal_chasm"], "in_water": True}, "title": "Swim down into the chasm's dark"}],
          rewards=[reward_item("alexscaves:bioluminescent_torch", 16), skill("agility", 250)]),

    quest("sea_pig", "The Sea Pig", icon="alexscaves:marine_snow", after=["abyssal_chasm"],
          text=["Sea pigs graze the chasm floor. Scoop one up, and gather marine snow and tube worms from around the "
                "glowing vents."],
          tasks=[{"interact": "alexscaves:sea_pig", "holding": "minecraft:bucket", "title": "Scoop a sea pig into a bucket"},
                 item("alexscaves:marine_snow", 4, title="Gather marine snow from the chasm floor"),
                 item("alexscaves:tube_worm", 4, title="Gather tube worms from around the vents")],
          rewards=[reward_item("alexscaves:cooked_radgill", 4), skill("fish", 250)]),

    quest("abyssal_ruins", "Ruins of the Deep Ones", icon="crittersandcompanions:pearl", after=["abyssal_chasm"],
          text=["The deep ones' city lies below, guarded by mine guardians. Sneak in without stirring them."],
          tasks=[{"structure": "alexscaves:abyssal_ruins", "title": "Find the deep ones' city"},
                 {"timed": {"seconds": 300, "goal": {"structure": "alexscaves:abyssal_ruins", "label": "the city's heart", "away": 50},
                            "lines": ["Quiet. If anything touches you, the guardians wake."], "start": "Creep in", "no": ["hurt"]},
                  "title": "Creep through the ruins without stirring the guardians"}],
          rewards=[reward_item("crittersandcompanions:pearl", 4), skill("agility", 300)]),

    quest("sushi", "Deep Sea Sushi", icon="alexscaves:deep_sea_sushi_roll", after=["abyssal_chasm"],
          text=["The deep ones' catch is a delicacy. Catch lanternfish, tripodfish and mussels and roll them into "
                "deep sea sushi."],
          tasks=[item("alexscaves:lanternfish", 2, title="Catch lanternfish"),
                 item("alexscaves:tripodfish", 2, title="Catch tripodfish"),
                 item("alexscaves:mussel", 2, title="Gather mussels"),
                 item("alexscaves:deep_sea_sushi_roll", crafted=True, title="Roll deep sea sushi")],
          rewards=[reward_item("alexscaves:deep_sea_sushi_roll", 4), skill("fish", 250)]),

    quest("forlorn_hollows", "Where Light Dies", icon="minecraft:torch", after=["rumours_below"],
          discover={"biome": "alexscaves:forlorn_hollows"},
          text=["Descend into the Forlorn Hollows, a moonless world of watchers, gloomoths and corrodents."],
          tasks=[{"be": {"biomes": ["alexscaves:forlorn_hollows"], "below_y": 40}, "title": "Descend into the moonless hollows"}],
          rewards=[reward_item("minecraft:torch", 32), skill("agility", 150)]),

    quest("vesper_hunt", "Wings in the Dark", icon="alexscaves:vesper_stew", after=["forlorn_hollows"],
          text=["Vespers hang from the hollow's ceiling and dive at anything with a light. Take their wings and cook "
                "vesper stew over a fire down there."],
          tasks=[{"kill": "alexscaves:vesper", "count": 3, "title": "Bring down the vespers that dive at your light"},
                 item("alexscaves:vesper_wing", 3, title="Take their wings"),
                 item("alexscaves:vesper_stew", crafted=True, title="Cook vesper stew over a fire in the dark")],
          rewards=[reward_item("alexscaves:darkened_apple", 4), skill("cook", 280)]),

    quest("corrodent", "Teeth in the Stone", icon="alexscaves:guanostone_bricks", after=["forlorn_hollows"],
          text=["Corrodents tunnel through the guanostone faster than you can dig. Corner one in the open and take "
                "its teeth."],
          tasks=[{"kill": "alexscaves:corrodent", "title": "Corner a corrodent in the open"},
                 sample("a Corrodent's Teeth", ["alexscaves:corrodent"], 0.6, texture="minecraft:item/bone",
                        tooltip="Chewed through stone")],
          rewards=[reward_item("alexscaves:guanostone_bricks", 16), skill("mining", 250)]),

    quest("forlorn_canyon", "The Forlorn Canyon", icon="alexscaves:guanostone", after=["forlorn_hollows"],
          text=["Guano-stained cliffs hang over a deep canyon. Find the forlorn canyon."],
          tasks=[{"structure": "alexscaves:forlorn_canyon", "title": "Find the forlorn canyon and its guano-stained cliffs"}],
          rewards=[reward_item("alexscaves:gazing_pearl"), skill("agility", 250)]),

    quest("forlorn_bridge", "Cross the Bridge", icon="alexscaves:dark_tatters", after=["forlorn_canyon"],
          text=["A forlorn bridge crosses the void, and underzealots hunt in the dark. Cross without being touched."],
          tasks=[{"structure": "alexscaves:forlorn_bridge", "title": "Find a bridge over the void"},
                 {"timed": {"seconds": 240, "goal": {"structure": "alexscaves:forlorn_bridge", "label": "the far side", "away": 40},
                            "lines": ["The underzealots hunt in the dark. Don't be touched."], "start": "Cross the bridge",
                            "no": ["hurt", "teleport"]}, "title": "Cross the bridge without being touched"}],
          rewards=[reward_item("alexscaves:dark_tatters", 4), skill("agility", 320)]),

    quest("watcher", "The Watcher", icon="minecraft:spyglass", after=["forlorn_hollows"],
          text=["Watchers take your eyes. Kill one before it can switch your view."],
          tasks=[enc(["*Your sight swims. Something watches through your eyes.*"], then="kill", entity="alexscaves:watcher",
                     name="The Watcher", title="Kill the watcher before it switches your view",
                     where={"biomes": ["alexscaves:forlorn_hollows"]})],
          rewards=[reward_item("minecraft:spyglass"), reward_item("alexscaves:dark_tatters", 4), skill("attack", 300)]),

    quest("forsaken", "The Forsaken", icon="alexscaves:pure_darkness", after=["forlorn_bridge"],
          text=["Underzealots perform a ritual to summon the Forsaken, a towering blind beast. Fight it as it "
                "emerges."],
          tasks=[boss("alexscaves:forsaken", "alexscaves:forlorn_canyon", "The Forsaken", "Fight the Forsaken as it emerges from the ritual")],
          rewards=[reward_item("alexscaves:desolate_dagger"), skill("attack", 400)]),

    quest("dreadbow", "The Dreadbow", icon="alexscaves:dreadbow", after=["forsaken"],
          text=["Pure darkness and dark tatters make cruel weapons. Craft a dreadbow and a desolate dagger."],
          tasks=[item("alexscaves:pure_darkness", 4, title="Gather pure darkness"),
                 item("alexscaves:dark_tatters", 4, title="Gather dark tatters"),
                 item("alexscaves:dreadbow", crafted=True, title="Craft a dreadbow"),
                 item("alexscaves:desolate_dagger", crafted=True, title="Craft a desolate dagger")],
          rewards=[reward_item("minecraft:arrow", 32), skill("range", 350)]),

    quest("candy_cavity", "Sugar Rush", icon="alexscaves:candy_cane", after=["rumours_below"],
          discover={"biome": "alexscaves:candy_cavity"},
          text=["A cave full of sweets: the Candy Cavity, with its frosting hills and soda lakes."],
          tasks=[{"be": {"biomes": ["alexscaves:candy_cavity"], "below_y": 50}, "title": "Wander into the frosting hills"}],
          rewards=[reward_item("alexscaves:candy_cane", 8), skill("agility", 150)]),

    quest("sweetish_fish", "Soda Lake Fishing", icon="alexscaves:sweetish_fish_blue", after=["candy_cavity"],
          text=["The soda lakes teem with sweetish fish in every colour. Fish them up."],
          tasks=[item("alexscaves:sweetish_fish_blue", title="Fish up a blue sweetish fish"),
                 item("alexscaves:sweetish_fish_green", title="Fish up a green sweetish fish"),
                 item("alexscaves:sweetish_fish_pink", title="Fish up a pink sweetish fish"),
                 item("alexscaves:sweetish_fish_red", title="Fish up a red sweetish fish"),
                 item("alexscaves:sweetish_fish_yellow", title="Fish up a yellow sweetish fish")],
          rewards=[reward_item("alexscaves:purple_soda_bucket"), skill("fish", 250)]),

    quest("caniac", "Brittle Brawl", icon="alexscaves:frostmint_spear", after=["candy_cavity"],
          text=["Caniacs and gumbeepers guard the frosting hills. Beat a few, then craft a frostmint spear from "
                "what you find in the cavity."],
          tasks=[{"kill": "alexscaves:caniac", "count": 4, "title": "Beat the caniacs that guard the frosting hills"},
                 {"kill": "alexscaves:gumbeeper", "count": 2, "title": "Beat the gumbeepers that raise the alarm"},
                 item("alexscaves:frostmint_spear", crafted=True, title="Craft a frostmint spear")],
          rewards=[reward_item("alexscaves:sharpened_candy_cane", 8), skill("attack", 300)]),

    quest("gingerbread_town", "Gingerbread Town", icon="alexscaves:gingerbread_chestplate", after=["candy_cavity"],
          text=["Visit a gingerbread town and its gingerbread men. They have a trade to offer."],
          tasks=[{"structure": "alexscaves:gingerbread_town", "title": "Find the gingerbread town"},
                 {"talk": "entity", "entity": "alexscaves:gingerbread_man",
                  "lines": ["Crumbly greetings! Mind the walls, they're edible.", "Take our armour. We bake plenty."],
                  "title": "Trade with the gingerbread men"}],
          rewards=[reward_item("alexscaves:gingerbread_chestplate"), skill("cook", 250)]),

    quest("licowitch", "The Licowitch Tower", icon="alexscaves:sugar_staff", after=["candy_cavity"],
          text=["A licowitch tower rises over the candy hills. Climb it and defeat the licowitch at its top."],
          tasks=[{"structure": "alexscaves:licowitch_tower", "title": "Find the licowitch tower"},
                 boss("alexscaves:licowitch", "alexscaves:licowitch_tower", "The Licowitch", "Defeat the licowitch at the top")],
          rewards=[reward_item("alexscaves:sugar_staff"), skill("magic", 300)]),

    quest("sweet_landmarks", "A Tour of Sweets", icon="alexscaves:cake_layer", after=["candy_cavity"],
          text=["The cavity has sweet wonders. Visit a cake cave, a soda bottle and a donut arch, and collect a treat "
                "from each."],
          tasks=[{"structure": "alexscaves:cake_cave", "title": "Visit a cake cave"},
                 item("alexscaves:cake_layer", title="Take a layer of cake from the cave"),
                 {"structure": "alexscaves:soda_bottle", "title": "Visit a soda bottle"},
                 item("alexscaves:purple_soda_bottle", title="Take a bottle of purple soda"),
                 {"structure": "alexscaves:donut_arch", "title": "Visit a donut arch"},
                 item("alexscaves:sprinkles", title="Take sprinkles from the arch")],
          rewards=[reward_item("alexscaves:caramel_apple", 4), skill("cook", 260)]),

    quest("confection_oven", "The Confection Oven", icon="alexscaves:confection_oven", after=["sweet_landmarks"],
          text=["Sweets bake best in a proper oven. Craft a confection oven and bake sweets in it."],
          tasks=[item("alexscaves:confection_oven", crafted=True, title="Craft a confection oven"),
                 {"use": "alexscaves:confection_oven", "count": 1, "title": "Bake sweets in the oven"}],
          rewards=[reward_item("alexscaves:lollipop_bunch", 2), skill("cook", 280)]),

    quest("sundae", "The Grand Sundae", icon="alexscaves:sundae", after=["confection_oven"],
          text=["The cavity's finest dessert: vanilla, chocolate and sweetberry ice cream in a sundae with "
                "sprinkles."],
          tasks=[item("alexscaves:vanilla_ice_cream", title="Make vanilla ice cream"),
                 item("alexscaves:chocolate_ice_cream", title="Make chocolate ice cream"),
                 item("alexscaves:sweetberry_ice_cream", title="Make sweetberry ice cream"),
                 item("alexscaves:sundae", crafted=True, title="Build the grand sundae with sprinkles")],
          rewards=[reward_item("alexscaves:sundae", 2), skill("cook", 300)]),

    quest("gummy_bear", "Gummy Friends", icon="alexscaves:gelatin_pink", after=["candy_cavity"],
          text=["The candy hills have their own friendly beasts. Befriend a gummy bear and ride a candicorn."],
          tasks=[{"interact": "alexscaves:gummy_bear", "holding": "alexscaves:gelatin_pink", "consume": True, "title": "Feed a gummy bear until it befriends you"},
                 {"be": {"riding": "alexscaves:candicorn"}, "title": "Ride a candicorn"}],
          rewards=[reward_item("alexscaves:gelatin_pink", 4), skill("taming", 300)]),
]

ACT3 = [
    quest("miners_cabin", "The Abandoned Cabin", icon="alexscaves:cave_tablet",
          discover={"structure": "alexscaves:underground_cabin"},
          text=["You stumble on an underground cabin deep in the rock. A cave tablet lies among its chests, and it "
                "points toward a hidden biome."],
          tasks=[search("alexscaves:underground_cabin", 1, "a Cave Tablet", "A carved tablet, pointing toward a hidden biome.",
                        texture="minecraft:item/clay_ball", title="Search the cabin's chests for the cave tablet")],
          rewards=[reward_item("alexscaves:cave_tablet"), reward_item("minecraft:torch", 16), skill("mining", 120)]),

    quest("ominous_catalyst", "Ominous Catalyst", icon="alexscaves:heavy_bone", after=["tremorsaurus", "amber"],
          text=["Heavy bones and an amber curiosity, combined, make a catalyst that can wake something at the "
                "volcano."],
          tasks=[item("alexscaves:heavy_bone", 4, title="Carry heavy bones from the giant"),
                 item("alexscaves:amber_curiosity", title="Carry an amber curiosity"),
                 item("alexscaves:ominous_catalyst", crafted=True, title="Craft the Ominous Catalyst")],
          rewards=[reward_item("alexscaves:heavy_bone"), skill("craft", 400)]),

    quest("luxtructosaurus", "The Luxtructosaurus", icon="alexscaves:spawn_egg_luxtructosaurus", shape="diamond", size=1.5,
          after=["ominous_catalyst"],
          text=["Use the Ominous Catalyst at the volcano to summon the Luxtructosaurus. Outlast its meteors and "
                "stomps."],
          tasks=[boss("alexscaves:luxtructosaurus", "alexscaves:volcano", "The Luxtructosaurus", "Outlast the Luxtructosaurus at the volcano")],
          rewards=[reward_item("alexscaves:tectonic_shard"), skill("attack", 650)]),

    quest("extinction_spear", "Extinction", icon="alexscaves:extinction_spear", after=["luxtructosaurus"],
          text=["The underworld's final weapon is made from the tectonic shard. Craft the Extinction Spear."],
          tasks=[item("alexscaves:tectonic_shard", title="Carry the tectonic shard"),
                 item("alexscaves:extinction_spear", crafted=True, title="Craft the Extinction Spear")],
          rewards=[reward_item("minecraft:enchanted_book", enchant={'minecraft:unbreaking': 3}), skill("craft", 700)]),

    quest("submarine", "The Submarine", icon="alexscaves:submarine", after=["abyssal_chasm"],
          text=["The trench's floor is too deep to swim. Build a submarine and pilot it to the bottom."],
          tasks=[item("alexscaves:submarine", crafted=True, title="Build a submarine"),
                 {"structure": "alexscaves:ocean_trench", "title": "Pilot it down to the trench's floor"}],
          rewards=[reward_item("alexscaves:scrap_metal", 16), skill("craft", 400)]),

    quest("mine_guardian", "Anchored", icon="alexscaves:depth_charge", after=["abyssal_ruins"],
          text=["Mine guardians are living sea mines chained to anchors in the ruins. Take one down from a distance "
                "without getting caught in its blast."],
          tasks=[fight("alexscaves:mine_guardian", 1, "alexscaves:abyssal_ruins", "Anchored Mine", "Take down a mine guardian from a distance", wave=1)],
          rewards=[reward_item("alexscaves:depth_charge", 4), skill("attack", 380)]),

    quest("deep_ones", "Trade with the Deep", icon="alexscaves:spawn_egg_deep_one_knight", after=["abyssal_ruins"],
          text=["Earn the deep ones' trust with offerings at an abyssal altar and trade for their gear."],
          tasks=[{"structure": "alexscaves:abyssal_ruins", "title": "Find an abyssal altar in the ruins"},
                 item("minecraft:prismarine_shard", 8, consume=True, title="Leave an offering of prismarine at the altar"),
                 enc(["*The deep one bows, and holds out a staff of the sea.*"], entity="alexscaves:deep_one", name="Deep One Elder",
                     title="Trade with the deep ones")],
          rewards=[reward_item("alexscaves:sea_staff"), skill("fish", 350)]),

    quest("magic_conch", "Call of the Conch", icon="alexscaves:magic_conch", after=["deep_ones"],
          text=["Win a magic conch from the deep ones, and blow it in the chasm. The deep ones you've befriended "
                "come to fight beside you."],
          tasks=[item("alexscaves:magic_conch", title="Win a magic conch from the deep ones"),
                 {"be": {"biomes": ["alexscaves:abyssal_chasm"], "in_water": True}, "title": "Go to the chasm to blow the conch"}],
          rewards=[reward_item("crittersandcompanions:pearl", 4), skill("fish", 380)]),

    quest("hullbreaker", "The Hullbreaker", icon="alexscaves:spawn_egg_hullbreaker", shape="diamond", size=1.5,
          after=["submarine", "deep_ones"],
          text=["The Hullbreaker, a giant bony angler that rams submarines, hunts the trench's floor. Bring it down "
                "from your sub or on foot."],
          tasks=[boss("alexscaves:hullbreaker", "alexscaves:ocean_trench", "The Hullbreaker", "Bring down the Hullbreaker on the trench's floor")],
          rewards=[reward_item("alexscaves:depth_glass", 8), skill("fish", 500)]),

    quest("cloak_of_darkness", "One With the Dark", icon="alexscaves:dark_tatters", after=["forlorn_bridge"],
          text=["Spin shadow silk from what the hollows leave behind and craft the hood and cloak of darkness, then "
                "walk past a watcher without being seen."],
          tasks=[item("alexscaves:dark_tatters", 6, title="Gather what the hollows leave behind"),
                 item("alexscaves:hood_of_darkness", crafted=True, title="Craft the hood of darkness"),
                 item("alexscaves:cloak_of_darkness", crafted=True, title="Craft the cloak of darkness"),
                 {"timed": {"seconds": 90, "goal": {"hold": {"radius": 12}}, "lines": ["Stay in the dark. Be unseen."],
                            "start": "Walk past the watcher", "no": ["hurt"]}, "title": "Pass a watcher without being seen"}],
          rewards=[reward_item("alexscaves:glow_ink_bomb", 4), skill("agility", 400)]),

    quest("beholder", "The Beholder", icon="alexscaves:beholder", after=["forsaken"],
          text=["The Forsaken's death leaves occult gems. Build a beholder and use it to watch far places."],
          tasks=[item("alexscaves:beholder", crafted=True, title="Build a beholder to watch far places")],
          rewards=[reward_item("alexscaves:radiant_essence"), skill("magic", 420)]),

    quest("gum_worm", "The Gum Worm", icon="alexscaves:candy_cane_hook", after=["candy_cavity"],
          text=["The Candy Cavity's gum worms are rideable, if you can hook one. Hook a gum worm with a candy cane "
                "hook and ride it."],
          tasks=[item("alexscaves:candy_cane_hook", crafted=True, title="Craft a candy cane hook"),
                 {"interact": "alexscaves:gum_worm", "holding": "alexscaves:candy_cane_hook", "title": "Hook a gum worm with the candy cane hook"}],
          rewards=[reward_item("alexscaves:candy_cane_hook"), skill("agility", 400)]),

    quest("four_worlds", "Four Worlds Below", icon="alexscaves:cave_codex", after=["primordial_caves", "abyssal_chasm", "forlorn_hollows", "candy_cavity"],
          text=["Visit all four cave biomes and record them in your Cave Codex."],
          tasks=[{"biome": "alexscaves:primordial_caves", "title": "Record the Primordial Caves"},
                 {"biome": "alexscaves:abyssal_chasm", "title": "Record the Abyssal Chasm"},
                 {"biome": "alexscaves:forlorn_hollows", "title": "Record the Forlorn Hollows"},
                 {"biome": "alexscaves:candy_cavity", "title": "Record the Candy Cavity"}],
          rewards=[{"choice": [reward_item("alexscaves:conversion_crucible"), reward_item("alexscaves:dreadbow", name='Four-World Bow', lore=['It drew from every cave at once.'], enchant={'minecraft:power': 5, 'minecraft:infinity': 1}, unbreakable=True), reward_item("alexscaves:galena_gauntlet", name='Four-World Gauntlet', lore=["Humming with every cave's charge."], enchant={'minecraft:unbreaking': 3}, unbreakable=True)], "title": "Choose one"}, skill("agility", 420)]),

    quest("crucible", "The Conversion Crucible", icon="alexscaves:conversion_crucible", after=["four_worlds"],
          text=["A conversion crucible can turn an area into a cave biome. Set one up and make your own corner of "
                "the underworld."],
          tasks=[item("alexscaves:conversion_crucible", crafted=True, title="Craft a conversion crucible"),
                 {"build": {"blocks": {"alexscaves:conversion_crucible": 1}, "radius": 10}, "title": "Set the crucible to convert an area"}],
          rewards=[reward_item("alexscaves:caramel_apple", 4), skill("craft", 420)]),
]

chapter("alexs_caves", "The Underworld", "Four strange worlds under the stone", "alexscaves:cave_map", "realms", 1, ACT2 + ACT3)
