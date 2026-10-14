"""Chapter: skill_taming, the Sanctuary Keepers path: prologue and Act I (first release).
Plan: src/plans/quests/skill_taming.json. Keeper Fern Thistlewood runs the sanctuary at the edge of Reece."""
from common import chapter, quest, talk_char, item, reward_item, skill, giver_org, encounter

Q = [
    quest("stray_wolf", "The Stray", icon="minecraft:bone",
          giver=giver_org("sanctuary", ["There's a wolf that follows my flock at a distance. Half-starved, poor thing.",
                                        "If you can win its trust, Keeper Fern at the sanctuary in Reece will "
                                        "take it in."], "I'll try"),
          text=["A shepherd says a half-starved wolf follows the flock at a distance. Tame it, give it a collar "
                "tag and bring it to Fern's pen at the edge of Reece."],
          tasks=[{"tame": "minecraft:wolf", "title": "Tame the wolf"},
                 item("domesticationinnovation:collar_tag"), {"place": "reece"},
                 talk_char("fern", ["Oh, look at you. Thin as a rake. Come in, come in.",
                                    "You did well. Most people shout at strays. You waited.",
                                    "I'll name it later. Names come when they're ready.",
                                    "There's more to do here, if you'd like to help."])],
          rewards=[reward_item("minecraft:bone", 16), skill("taming", 50)]),

    quest("first_pens", "Pens and Pet Beds", icon="domesticationinnovation:pet_bed_brown", after=["stray_wolf"],
          text=["The sanctuary is a single fence. Build proper pens and pet beds so rescued animals have a place "
                "to rest."],
          tasks=[{"place": "reece"}, item("domesticationinnovation:pet_bed_brown", crafted=True),
                 {"build": {"blocks": {"#minecraft:fences": 12, "#minecraft:fence_gates": 1,
                                       "minecraft:hay_block": 2}, "radius": 10}, "title": "Build a pen"}],
          rewards=[reward_item("domesticationinnovation:pet_bed_blue"),
                   reward_item("domesticationinnovation:pet_bed_red"), skill("taming", 90)]),

    quest("lame_horse", "The Lame Horse", icon="minecraft:saddle", after=["stray_wolf"],
          text=["Travellers abandoned a lame horse at their horse campsite. Find the camp, feed the horse back to "
                "health with apples and hay, tame it and ride it home slowly."],
          tasks=[{"structure": "mvs:horse_campsite", "title": "Find the horse campsite"},
                 item("minecraft:apple", 3, consume=True), item("minecraft:hay_block", 1, consume=True),
                 {"tame": "minecraft:horse", "title": "Tame the horse"}, {"place": "reece", "title": "Ride the horse home"}],
          rewards=[reward_item("minecraft:saddle"), skill("taming", 100)]),

    quest("fox_kits", "Kits at the Hut", icon="minecraft:sweet_berries", after=["first_pens"],
          text=["A hunter's fox hut has orphaned kits nearby. Win the wary foxes' trust by breeding a pair with "
                "sweet berries."],
          tasks=[{"structure": "mvs:fox_hut", "title": "Find the fox hut"},
                 item("minecraft:sweet_berries", 4, consume=True),
                 {"breed": "minecraft:fox", "title": "Breed a pair of foxes"}],
          rewards=[reward_item("minecraft:glow_berries", 16), skill("taming", 110)]),

    quest("critter_census", "The Critter Census", icon="crittersandcompanions:ferret_spawn_egg",
          after=["stray_wolf"],
          text=["Fern keeps a census of the small animals around Reece. Find an otter, a red panda, a ferret and "
                "a shima enaga, and tame a ferret to help with the count."],
          tasks=[{"observe": "crittersandcompanions:otter", "ticks": 20, "title": "Find an otter"},
                 {"observe": "crittersandcompanions:red_panda", "ticks": 20, "title": "Find a red panda"},
                 {"observe": "crittersandcompanions:ferret", "ticks": 20, "title": "Find a ferret"},
                 {"observe": "crittersandcompanions:shima_enaga", "ticks": 20, "title": "Find a shima enaga"},
                 {"tame": "crittersandcompanions:ferret", "title": "Tame a ferret"}],
          rewards=[reward_item("crittersandcompanions:silk_lead"), skill("taming", 100)]),

    quest("butterfly_net", "Wings in a Bottle", icon="butterflies:butterfly_net", after=["critter_census"],
          text=["Start the sanctuary's butterfly collection. Bottle five different butterflies across meadows and "
                "forests, without harming a single one."],
          tasks=[item("butterflies:butterfly_net", crafted=True),
                 item("butterflies:bottled_butterfly_cabbage"), item("butterflies:bottled_butterfly_common"),
                 item("butterflies:bottled_butterfly_monarch"), item("butterflies:bottled_butterfly_admiral"),
                 item("butterflies:bottled_butterfly_morpho")],
          rewards=[reward_item("butterflies:banner_pattern_butterfly"), skill("taming", 120)]),

    quest("cat_colony", "The Cats of the Ruin", icon="artifacts:kitty_slippers", after=["fox_kits"],
          signature="artifacts:kitty_slippers",
          text=["A colony of stray cats lives in a crumbling ruin that creepers have overrun. Clear the creepers, "
                "coax every cat out with fish, and the old cat-lady of the ruin will leave you her slippers."],
          tasks=[{"structure": "#ruins", "title": "Find the overrun ruin"},
                 {"kill": "minecraft:creeper", "count": 5, "title": "Clear the creepers away from the cats"},
                 item("minecraft:cod", 4, consume=True, title="Coax the cats out with fish"),
                 encounter(["Oh, my darlings! All of them, safe!",
                            "I've lived among these ruins forty winters, and never once had the creepers "
                            "outstay a good broom. But five at once...",
                            "Take my slippers, dear. The cats insist."],
                           entity="minecraft:villager", name="The Cat-Lady of the Ruin")],
          rewards=[reward_item("artifacts:kitty_slippers"), skill("taming", 250)]),

    quest("sled_dogs", "Lost in the Blizzard", icon="domesticationinnovation:feather_on_a_stick",
          after=["stray_wolf"],
          text=["The snowy dog hut's sled team ran off in a blizzard. Track the wolves across the snow and tame "
                "each one back."],
          tasks=[{"structure": "mvs:snowy_dog_hut", "title": "Find the snowy dog hut"},
                 item("minecraft:bone", 8, consume=True), {"tame": "minecraft:wolf", "count": 3, "title": "Tame the sled team back"}],
          rewards=[reward_item("domesticationinnovation:feather_on_a_stick"), skill("taming", 180)]),

    quest("butterfly_house", "The Butterfly House", icon="butterflies:bottled_caterpillar_common",
          after=["butterfly_net"],
          text=["Build a glass butterfly house, raise caterpillars in jars through chrysalis to butterfly, and "
                "release them inside among the flowers."],
          tasks=[{"place": "reece"},
                 {"build": {"blocks": {"minecraft:glass": 30, "#minecraft:flowers": 8}, "radius": 12},
                  "title": "Build a glass butterfly house"},
                 item("butterflies:bottled_caterpillar_common"), {"checkmark": "I released the butterflies"}],
          rewards=[reward_item("butterflies:admiral_egg", 2), reward_item("butterflies:atlas_egg", 2),
                   skill("taming", 200)]),

    quest("koi_pond", "The Koi Pond", icon="crittersandcompanions:koi_fish_bucket", after=["first_pens"],
          text=["A merchant's koi are dying in a stagnant pool. Bucket them, dig a proper pond at the sanctuary "
                "with lily pads and clams, and add a dumbo octopus for the visitors."],
          tasks=[item("crittersandcompanions:koi_fish_bucket", 2),
                 item("crittersandcompanions:dumbo_octopus_bucket"), {"place": "reece"},
                 {"build": {"blocks": {"minecraft:lily_pad": 4, "crittersandcompanions:clam": 2}, "radius": 10},
                  "title": "Dig a pond with lily pads and clams"}],
          rewards=[reward_item("crittersandcompanions:pearl_necklace_1"), skill("taming", 220)]),

    quest("pet_enchanting", "A Collar Worth Wearing", icon="domesticationinnovation:collar_tag",
          after=["sled_dogs"],
          text=["Fern shows you how to enchant a collar tag: Health Boost and a creeper-sniffing Defusal, so your "
                "wolf can guard the sanctuary."],
          tasks=[talk_char("fern", ["A collar tag is only paper and string until someone believes in it.",
                                    "Health Boost for stamina. Defusal so your wolf will sniff out a creeper "
                                    "before it makes its mind up.",
                                    "The books will teach you the rest."]),
                 item("domesticationinnovation:collar_tag", crafted=True),
                 {"checkmark": "I enchanted a collar tag"}],
          rewards=[reward_item("minecraft:enchanted_book", name="Hale and Hearty",
                               enchant={"domesticationinnovation:health_boost": 1}),
                   reward_item("minecraft:enchanted_book", name="Nose for Trouble",
                               enchant={"domesticationinnovation:defusal": 1}),
                   skill("taming", 160)]),

    quest("eggs_to_hatch", "Eggs to Hatch", icon="naturalist:duck_egg", after=["koi_pond"],
          text=["A storm flooded the riverbank nests. Collect duck, tortoise and snail eggs before they're lost, "
                "hatch them at the sanctuary and keep the young safe until they're grown."],
          tasks=[item("naturalist:duck_egg", 2), item("naturalist:tortoise_egg"), item("naturalist:snail_eggs"),
                 {"place": "reece"}, {"checkmark": "The young have grown"}],
          rewards=[reward_item("naturalist:bug_net"), skill("taming", 240)]),

    quest("dragonfly_rider", "Shimmering Wings", icon="crittersandcompanions:iron_dragonfly_armor",
          after=["critter_census"],
          text=["Tame a dragonfly by the marsh and make it iron armour so it can patrol the sanctuary's pond for "
                "pests."],
          tasks=[{"observe": "crittersandcompanions:dragonfly", "ticks": 20, "title": "Find a dragonfly"},
                 item("crittersandcompanions:iron_dragonfly_armor", crafted=True),
                 {"tame": "crittersandcompanions:dragonfly", "title": "Tame a dragonfly"}],
          rewards=[reward_item("crittersandcompanions:dragonfly_wing", 4), skill("taming", 220)]),
]

chapter("skill_taming", "The Sanctuary", "Taming path", "minecraft:bone", "skills", 11, Q)
