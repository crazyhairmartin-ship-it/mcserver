"""Chapter: skill_foraging, the Herbalists' path: prologue and Act I (first release). Plan: src/plans/quests/skill_foraging.json."""
from common import chapter, quest, talk_char, talk_org, item, reward_item, skill, giver_org, encounter
from common import enc, fight, boss, search, sample, talk_org, talk_villager, talk_char, item, reward_item, skill, encounter, giver_org  # noqa: F401

Q = [
    quest("field_journal", "A Blank Field Journal", icon="minecraft:writable_book",
          giver=giver_org("herbalists", ["A forager's first tool isn't a knife. It's a journal.",
                                         "Make yourself a book and quill, and press your first flowers into it."],
                          "I'll start one"),
          text=["Every herbalist keeps a field journal. Start yours properly: a book and quill, and five different "
                "flowers pressed into it."],
          tasks=[item("minecraft:writable_book"), item("minecraft:dandelion"), item("minecraft:poppy"),
                 item("minecraft:oxeye_daisy"), item("minecraft:azure_bluet"), item("minecraft:cornflower")],
          rewards=[reward_item("minecraft:bundle"), skill("forage", 60)]),

    quest("hedgerows", "Hedgerow Pickings", icon="minecraft:sweet_berries", after=["field_journal"],
          text=["Walk the hedgerows around the village and fill a basket."],
          tasks=[item("minecraft:sweet_berries", 16), item("minecraft:brown_mushroom", 4),
                 item("minecraft:red_mushroom", 4), item("biomesoplenty:wildflower"), item("regions_unexplored:daisy")],
          rewards=[skill("forage", 80)]),

    quest("six_saplings", "Six Saplings", icon="minecraft:oak_sapling", after=["field_journal"],
          text=["Every forager learns the trees first. Collect six kinds of sapling."],
          tasks=[item("minecraft:oak_sapling"), item("minecraft:birch_sapling"), item("minecraft:spruce_sapling"),
                 item("minecraft:jungle_sapling"), item("minecraft:acacia_sapling"), item("minecraft:dark_oak_sapling")],
          rewards=[reward_item("minecraft:bone_meal", 16), skill("forage", 100)]),

    quest("loggers_camp", "The Loggers' Camp", icon="meadow:pine_log", after=["six_saplings"],
          text=["The loggers at a meadow logging camp are behind on their order. Chop pine for them."],
          tasks=[{"structure": "meadow:logging_camp", "title": "Find the logging camp"},
                 item("meadow:pine_log", 64, consume=True)],
          rewards=[reward_item("meadow:woodcutter"), skill("forage", 120)]),

    quest("first_tea", "The First Tea", icon="herbalbrews:tea_kettle", after=["hedgerows"],
          text=["Find wild rooibos, coffee or yerba mate, dry the leaves, and brew your first pot."],
          tasks=[item("herbalbrews:rooibos_tea")],
          rewards=[reward_item("herbalbrews:copper_tea_kettle"), skill("forage", 100)]),

    quest("outpost_notes", "The Forager's Outpost", icon="minecraft:paper", after=["loggers_camp"],
          text=["Find a forager's outpost in the wilds and copy the notes its last keeper left on the herbs of that "
                "region."],
          tasks=[{"structure": "#forager_outposts", "title": "Find a forager's outpost"},
                 {"search": {"at": {"structure": ["structory_towers:foraging_outpost", "structory_towers:nomad_outpost",
                                                   "structory_towers:taiga_outpost"]}, "count": 1,
                             "item": {"name": "Keeper's Herb Notes", "tooltip": "Herbs of the region, in a careful hand",
                                      "texture": "minecraft:item/paper"},
                             "found": "The last keeper's notes on the herbs hereabouts."},
                  "title": "Find the keeper's notes"}],
          rewards=[skill("forage", 150)]),

    quest("lavender_sleep", "Lavender for the Sleepless", icon="herbalbrews:lavender_tea", after=["first_tea"],
          text=["A villager hasn't slept in a week. Gather lavender, brew lavender tea, and take it to them warm."],
          tasks=[item("herbalbrews:lavender_blossom", 4), item("herbalbrews:lavender_tea", consume=True),
                 talk_org("growers", ["Lavender tea? Oh... I might actually sleep tonight. Thank you."],
                          title="Give it to the sleepless farmer")],
          rewards=[reward_item("minecraft:white_bed"), skill("forage", 150)]),

    quest("bloom_catalogue", "The Bloom Catalogue", icon="bloomingnature:bluebell", after=["outpost_notes"],
          text=["Catalogue the wildflowers of the temperate lands, one of each pressed in your journal."],
          tasks=[item("bloomingnature:bluebell"), item("regions_unexplored:blue_lupine"), item("bloomingnature:gladiolus"),
                 item("bloomingnature:white_orchid")],
          rewards=[reward_item("meadow:big_flower_pot"), skill("forage", 150)]),

    quest("wandering_gardener", "The Wandering Gardener", icon="bloomingnature:chestnut_sapling",
          after=["bloom_catalogue"],
          text=["A gardener is coming down the road with a cart full of seeds you've never seen."],
          tasks=[encounter(["Pressed flowers! You're one of us.", "Take saplings for them. Plant them where they'll be loved."], entity="bloomingnature:wandering_gardener", name="The Wandering Gardener")],
          rewards=[reward_item("bloomingnature:chestnut_sapling"), reward_item("bloomingnature:larch_sapling"),
                   reward_item("bloomingnature:ebony_sapling"), skill("forage", 150)]),

    quest("swamp_hermit", "The Swamp Hermit", icon="herbalbrews:hibiscus_tea", after=["lavender_sleep"],
          text=["An old hermit herbalist lives in a swamp hut. Bring her cattails, reeds and a hibiscus, and she'll "
                "teach you her tea."],
          tasks=[{"structure": "#witch_huts", "title": "Find the swamp hut"}, item("bloomingnature:cattail", 4),
                 item("bloomingnature:reed", 4), item("herbalbrews:hibiscus"), item("herbalbrews:hibiscus_tea")],
          rewards=[reward_item("herbalbrews:witch_hat"), skill("forage", 200)]),

    quest("wild_herbs", "Wild Herbs", icon="farm_and_charm:wild_nettle", after=["first_tea"],
          text=["The Herbalists' oldest remedies come from weeds. Find wild nettle and ribwort and brew their teas."],
          tasks=[item("farm_and_charm:wild_nettle"), item("farm_and_charm:wild_ribwort"),
                 item("farm_and_charm:nettle_tea"), item("farm_and_charm:ribwort_tea")],
          rewards=[skill("forage", 150)]),

    quest("alpine_flora", "Alpine Flora", icon="meadow:enzian", after=["bloom_catalogue"],
          text=["Climb to the high meadows of the tallest peaks and press the alpine flowers that grow nowhere else."],
          tasks=[item("meadow:enzian"), item("meadow:saxifrage"), item("meadow:delphinium"), item("meadow:alpine_poppy")],
          rewards=[reward_item("meadow:fur_boots"), skill("forage", 200)]),

    quest("truffles", "Truffle Season", icon="wildernature:truffle", after=["wild_herbs"],
          text=["Herbalists prize truffles and hazelnuts. Follow the boars and squirrels through the woods."],
          tasks=[item("wildernature:truffle", 4), item("wildernature:hazelnut", 16)],
          rewards=[reward_item("wildernature:fur_cloak"), skill("forage", 200)]),
]

ACT2 = [
    quest("wanderers_map", "Mapping the Wild", icon="naturescompass:naturescompass",
          after=["outpost_notes", "main_story:act2_start"],
          text=["The journal's map has more blanks than lines. Set foot in twenty different biomes, and the "
                "Herbalists will craft you a Nature's Compass to keep going."],
          tasks=[{"biomes": 20, "dimension": "minecraft:overworld", "title": "Set foot in twenty different biomes to fill the journal"},
                 talk_org("herbalists", ["Twenty biomes! The journal's nearly full.", "A Nature's Compass will take you further."],
                          title="Show the filled map to a Herbalist")],
          rewards=[reward_item("naturescompass:naturescompass"), skill("forage", 250)]),

    quest("magnolia_bloom", "Magnolia and Jacaranda", icon="biomesoplenty:jacaranda_sapling", after=["wanderers_map"],
          text=["The journal has blank pages for the flowering forests: pink magnolia from a magnolia woodland and a "
                "jacaranda sapling from a jacaranda glade."],
          tasks=[{"biome": "regions_unexplored:magnolia_woodland", "title": "Find a magnolia woodland in bloom"},
                 item("regions_unexplored:magnolia_leaves", 4, title="Press pink magnolia leaves for the journal"),
                 {"biome": "biomesoplenty:jacaranda_glade", "title": "Find a jacaranda glade"},
                 item("biomesoplenty:jacaranda_sapling", title="Take a jacaranda sapling for the journal")],
          rewards=[reward_item("regions_unexplored:magnolia_sapling"), skill("forage", 260)]),

    quest("redwood_giant", "The Redwood Giant", icon="biomesoplenty:redwood_sapling", after=["wanderers_map"],
          text=["The journal wants the tallest redwood measured. Climb it, drop a rope to measure it, and bring down "
                "a redwood sapling and a branch of its leaves."],
          tasks=[{"biome": "biomesoplenty:redwood_forest", "title": "Find the tallest redwood in the forest"},
                 {"build": {"blocks": {"supplementaries:rope": 12}, "radius": 12}, "title": "Drop a rope from the crown to measure it"},
                 item("biomesoplenty:redwood_sapling", title="Bring down a redwood sapling"),
                 item("biomesoplenty:redwood_leaves", 4, title="Bring down a branch of its leaves")],
          rewards=[reward_item("minecraft:ladder", 16), reward_item("supplementaries:rope", 16), skill("forage", 280)]),

    quest("lost_botanist", "The Lost Botanist", icon="minecraft:writable_book", after=["swamp_hermit"],
          text=["A visiting botanist went into the bog and didn't come back. Follow his trail of dropped pressed "
                "flowers across a muskeg or bog and find him stuck in the mud."],
          tasks=[{"be": {"biomes": ["biomesoplenty:bog", "biomesoplenty:muskeg"]}, "title": "Follow the pressed-flower trail into the bog"},
                 enc(["Oh, thank the bog! I've been stuck since nightfall.", "Take my field journal. It's full of rare sketches."],
                     entity="minecraft:villager", name="Lost Botanist", title="Pull the botanist out of the mud",
                     where={"biomes": ["biomesoplenty:bog", "biomesoplenty:muskeg"]})],
          rewards=[reward_item("minecraft:writable_book", name="The Botanist's Field Journal",
                               lore=["Full of rare sketches."]), skill("forage", 280)]),

    quest("glowing_grotto", "The Glowing Grotto", icon="biomesoplenty:glowshroom", after=["lost_botanist"],
          text=["The botanist's journal points underground. Find a glowing grotto and collect glowshrooms, "
                "glowflowers and glowworm silk for the Herbalists."],
          tasks=[{"biome": "biomesoplenty:glowing_grotto", "title": "Find the glowing grotto the journal names"},
                 item("biomesoplenty:glowshroom", 4, title="Collect glowshrooms"),
                 item("biomesoplenty:glowflower", 4, title="Collect glowflowers"),
                 item("biomesoplenty:glowworm_silk", 4, title="Collect glowworm silk")],
          rewards=[reward_item("biomesoplenty:glowing_moss_block", 8), reward_item("minecraft:lantern", 2), skill("forage", 300)]),

    quest("bioshroom_caves", "Bioshroom Caves", icon="regions_unexplored:blue_bioshroom", after=["glowing_grotto"],
          text=["Below the grotto lies another wonder: bioshroom caves. Gather blue, green and pink bioshrooms and a "
                "sprig of cave hyssop for the Herbalists."],
          tasks=[{"biome": "regions_unexplored:bioshroom_caves", "title": "Find the bioshroom caves below the grotto"},
                 item("regions_unexplored:blue_bioshroom", 2, title="Gather blue bioshrooms"),
                 item("regions_unexplored:green_bioshroom", 2, title="Gather green bioshrooms"),
                 item("regions_unexplored:pink_bioshroom", 2, title="Gather pink bioshrooms"),
                 item("regions_unexplored:cave_hyssop", title="Gather a sprig of cave hyssop")],
          rewards=[reward_item("regions_unexplored:glowing_blue_bioshroom_block", 4), skill("forage", 320)]),

    quest("rainforest_run", "Before It Wilts", icon="bloomingnature:bird_of_paradise", after=["magnolia_bloom"],
          text=["The Herbalists need a fresh bird of paradise and a mahogany sapling from the rainforest for a cure. "
                "Bring them back to Reece before they wilt."],
          tasks=[{"biome": "biomesoplenty:rainforest", "title": "Go to the rainforest for the cure's ingredients"},
                 item("bloomingnature:bird_of_paradise", title="Pick a fresh bird of paradise"),
                 item("biomesoplenty:mahogany_sapling", title="Take a mahogany sapling"),
                 {"timed": {"seconds": 900, "goal": {"place": "reece"},
                            "lines": ["The flower wilts quickly. Get it to Reece!"], "start": "Rush the cure home",
                            "no": ["teleport"]}, "title": "Reach Reece before the flower wilts"}],
          rewards=[reward_item("irons_spellbooks:greater_healing_potion", 2), skill("forage", 330)]),

    quest("snowbelles", "Snowbelles", icon="regions_unexplored:blue_snowbelle", after=["wanderers_map"],
          text=["In the cold north grow snowbelles in many colours and snowblossom trees. Press six snowbelle colours "
                "and bring a snowblossom sapling to the Herbalists."],
          tasks=[{"be": {"biomes": ["minecraft:snowy_plains", "minecraft:snowy_taiga", "minecraft:grove", "minecraft:snowy_slopes"]},
                  "title": "Travel into the cold north"},
                 item("regions_unexplored:black_snowbelle", title="Press a black snowbelle"),
                 item("regions_unexplored:blue_snowbelle", title="Press a blue snowbelle"),
                 item("regions_unexplored:brown_snowbelle", title="Press a brown snowbelle"),
                 item("regions_unexplored:cyan_snowbelle", title="Press a cyan snowbelle"),
                 item("regions_unexplored:gray_snowbelle", title="Press a gray snowbelle"),
                 item("regions_unexplored:green_snowbelle", title="Press a green snowbelle"),
                 item("biomesoplenty:snowblossom_sapling", title="Take a snowblossom sapling")],
          rewards=[reward_item("meadow:fur_boots"), skill("forage", 300)]),

    quest("herbarium", "The Herbarium", icon="meadow:wooden_flower_pot_big", after=["bioshroom_caves", "snowbelles"],
          text=["The Herbalists want a herbarium in Reece: glass, big flower pots, and a living specimen of every "
                "plant you've pressed so far."],
          tasks=[{"place": "reece"},
                 {"build": {"blocks": {"minecraft:glass": 24, "meadow:wooden_flower_pot_big": 2, "bloomingnature:flower_pot_big": 2,
                                       "regions_unexplored:blue_snowbelle": 1, "biomesoplenty:glowshroom": 1}, "radius": 12},
                  "title": "Build the herbarium with a living specimen of every pressed plant"}],
          rewards=[reward_item("minecraft:writable_book", name="The Herbarium's Key", lore=["A seat on the Herbalists' council."]),
                   skill("forage", 400)]),
]

ACT3 = [
    quest("nether_botany", "Nether Botany", icon="biomesoplenty:burning_blossom", after=["main_story:act3_start", "herbarium"],
          text=["Even the Nether grows things. Collect crimson and warped fungi, a burning blossom and a hellbark "
                "sapling, and carry them home without burning."],
          tasks=[{"dimension": "minecraft:the_nether", "title": "Go down into the Nether to forage"},
                 item("minecraft:crimson_fungus", title="Gather crimson fungus"),
                 item("minecraft:warped_fungus", title="Gather warped fungus"),
                 item("biomesoplenty:burning_blossom", title="Pick a burning blossom"),
                 item("biomesoplenty:hellbark_sapling", title="Take a hellbark sapling")],
          rewards=[reward_item("minecraft:magma_cream", 4), skill("forage", 400)]),

    quest("dying_grove", "The Dying Grove", icon="biomesoplenty:flowering_oak_sapling", after=["nether_botany"],
          text=["The Herbalists' sacred grove near Reece is withering into dead forest. Clear the dead logs, cure the "
                "soil with herbal infusions and bone meal, and replant it until leaves grow back."],
          tasks=[{"place": "reece"},
                 item("herbalbrews:herbal_infusion", 2, consume=True, title="Cure the soil with herbal infusions"),
                 item("minecraft:bone_meal", 16, consume=True, title="Feed the soil with bone meal"),
                 {"build": {"blocks": {"minecraft:oak_sapling": 2, "minecraft:birch_sapling": 2, "minecraft:spruce_sapling": 2}, "radius": 12},
                  "title": "Replant the grove until leaves grow back"}],
          rewards=[reward_item("biomesoplenty:flowering_oak_sapling"), skill("forage", 430)]),

    quest("mystic_trees", "The Three Impossible Trees", icon="biomesoplenty:magic_sapling", after=["dying_grove"],
          text=["An old page lists trees no one has grown in Reece: a magic sapling from a mystic grove, a rainbow "
                "birch sapling, and a golden larch sapling."],
          tasks=[item("biomesoplenty:magic_sapling", title="Find a magic sapling in a mystic grove"),
                 item("biomesoplenty:rainbow_birch_sapling", title="Find a rainbow birch sapling"),
                 item("regions_unexplored:golden_larch_sapling", title="Find a golden larch sapling")],
          rewards=[reward_item("biomesoplenty:magic_sapling", 2), skill("forage", 460)]),
]

ACT4 = [
    quest("origin_valley", "The Origin Valley", icon="biomesoplenty:origin_sapling", after=["main_story:act4_start", "mystic_trees"],
          text=["Legend says all plants began in one valley where the grass is the old green. Find an origin valley "
                "and take an origin sapling and origin grass."],
          tasks=[{"biome": "biomesoplenty:origin_valley", "title": "Find the valley where all plants began"},
                 item("biomesoplenty:origin_sapling", title="Take an origin sapling"),
                 item("biomesoplenty:origin_grass_block", title="Take origin grass")],
          rewards=[reward_item("biomesoplenty:origin_sapling"), skill("forage", 650)]),

    quest("end_flora", "Flowers at the End", icon="minecraft:chorus_flower", after=["main_story:act4_finale", "origin_valley"],
          text=["With the Dragon gone, the Herbalists want the End's plants: chorus flowers, an endbloom and "
                "enderphyte, and an empyreal sapling, plus a look at an enderbloom grove."],
          tasks=[{"dimension": "minecraft:the_end", "title": "Go out to the End's islands"},
                 item("minecraft:chorus_flower", 2, title="Gather chorus flowers"),
                 item("biomesoplenty:empyreal_sapling", title="Take an empyreal sapling"),
                 {"structure": "mes:enderbloom_grove", "title": "Look over an enderbloom grove"}],
          rewards=[reward_item("minecraft:chorus_flower", 8), skill("forage", 720)]),
]

ACT5 = [
    quest("almanac", "The Complete Almanac", icon="minecraft:writable_book", after=["main_story:act5_start", "end_flora"],
          text=["Finish the field journal: plants pressed from all three dimensions, handed to the Head Herbalist "
                "in Reece to be copied for every village."],
          tasks=[item("minecraft:poppy", title="Press an Overworld flower"),
                 item("minecraft:crimson_fungus", title="Press a Nether fungus"),
                 item("minecraft:chorus_flower", title="Press an End flower"),
                 item("biomesoplenty:burning_blossom", title="Press a burning blossom"),
                 item("regions_unexplored:blue_snowbelle", title="Press a blue snowbelle"),
                 talk_char("rue", ["Pressed from all three dimensions? Oh, I'm so... oh. Oh my.", "I'll have it copied for every village. Sorry. Thank you."],
                           title="Hand the field journal to the Head Herbalist")],
          rewards=[reward_item("minecraft:writable_book", name="The Complete Almanac", lore=["Bound in leather with your name on it."]), skill("forage", 850)]),

    quest("greenwarden", "Greenwarden", icon="minecraft:netherite_axe", after=["almanac"],
          text=["The Head Herbalist names you Greenwarden of the wild lands and gives you the axe the order uses "
                "only on dead wood."],
          tasks=[talk_char("rue", ["Greenwarden of the wild lands. I worry you'll do it wonderfully.", "The axe is only for dead wood. Please."],
                           title="Be named Greenwarden by Mother Rue")],
          rewards=[reward_item("minecraft:netherite_axe", name="Greenwarden", lore=["Only for dead wood."], unbreakable=True,
                               enchant={"minecraft:efficiency": 5, "minecraft:unbreaking": 3, "minecraft:mending": 1}),
                   skill("forage", 1000)]),
]

chapter("skill_foraging", "The Herbalists", "Foraging path", "minecraft:oak_sapling", "skills", 4, Q + ACT2 + ACT3 + ACT4 + ACT5)
