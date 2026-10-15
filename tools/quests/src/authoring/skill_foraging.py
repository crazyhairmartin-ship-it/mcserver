"""Chapter: skill_foraging, the Herbalists' path: prologue and Act I (first release). Plan: src/plans/quests/skill_foraging.json."""
from common import chapter, quest, talk_char, talk_org, item, reward_item, skill, giver_org, encounter

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

chapter("skill_foraging", "The Herbalists", "Foraging path", "minecraft:oak_sapling", "skills", 4, Q)
