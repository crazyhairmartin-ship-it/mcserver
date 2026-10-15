"""Chapter: milestones, small pats on the back for the long road. Plan: src/plans/quests/milestones.json.
Each one is a page Elder Maren added to the Field Guide; nobody gives them out, they open from the book."""
from common import chapter, quest, item, reward_item, skill

KM = 100000   # centimetres in a kilometre (the walk, boat, horse and flight stats count centimetres)
DAY = 24000   # ticks in an in-game day (the play_time stat counts ticks)

# distance travelled on foot: every way of moving yourself, not only walking (sprinting is its own statistic)
ON_FOOT = ["minecraft:walk_one_cm", "minecraft:sprint_one_cm", "minecraft:crouch_one_cm", "minecraft:swim_one_cm", "minecraft:walk_on_water_one_cm", "minecraft:walk_under_water_one_cm", "minecraft:climb_one_cm"]

Q = [
    quest("first_iron", "Iron Age", icon="minecraft:iron_ingot", after=["start:welcome"],
          text=["Maren has left a page in the Field Guide for the first thing every newcomer to Reece does properly: "
                "smelt iron. Tools that don't snap are the start of everything."],
          tasks=[item("minecraft:iron_ingot", title="Smelt an iron ingot")],
          rewards=[reward_item("minecraft:bucket"), skill("mining", 40)]),

    quest("first_diamond", "Hard as Diamond", icon="minecraft:diamond", after=["first_iron"],
          text=["A page in the Field Guide, in Maren's neatest hand: the day you pull up your first diamond is "
                "worth remembering. Dig deep, and watch for lava."],
          tasks=[item("minecraft:diamond", title="Mine your first diamond")],
          rewards=[reward_item("minecraft:enchanted_book", enchant={'minecraft:efficiency': 3}, name='Deep Digger'), skill("mining", 120)]),

    quest("diamond_kit", "Shining Kit", icon="minecraft:diamond_chestplate", after=["first_diamond"],
          text=["The Field Guide reminds you that one diamond tool does not make an adventurer. Armour that turns "
                "a skeleton's arrows is what keeps you alive far from home."],
          tasks=[item("minecraft:diamond_helmet", title="Forge a diamond helmet"),
                 item("minecraft:diamond_chestplate", title="Forge a diamond chestplate"),
                 item("minecraft:diamond_leggings", title="Forge diamond leggings"),
                 item("minecraft:diamond_boots", title="Forge diamond boots")],
          rewards=[reward_item("spartanshields:diamond_basic_shield"), skill("defense", 250)]),

    quest("first_netherite", "Netherite", icon="minecraft:netherite_ingot", after=["diamond_kit"],
          text=["The Field Guide has a smudged page about the Nether's rarest metal, the only thing that outlasts "
                "diamond. Smelt ancient debris and you have it."],
          tasks=[item("minecraft:netherite_ingot", title="Smelt your first netherite ingot")],
          rewards=[reward_item("minecraft:ancient_debris", 2), skill("craft", 350)]),

    quest("full_netherite", "Black as Night", icon="minecraft:netherite_chestplate", after=["first_netherite"],
          text=["One ingot is a start. The last page of Maren's armour chapter is for those who dress head to toe "
                "in netherite."],
          tasks=[item("minecraft:netherite_helmet", title="Forge a netherite helmet"),
                 item("minecraft:netherite_chestplate", title="Forge a netherite chestplate"),
                 item("minecraft:netherite_leggings", title="Forge netherite leggings"),
                 item("minecraft:netherite_boots", title="Forge netherite boots")],
          rewards=[{"choice": [reward_item("minecraft:enchanted_book", enchant={'minecraft:mending': 1}), reward_item("minecraft:enchanted_golden_apple"), reward_item("minecraft:netherite_upgrade_smithing_template", 2)], "title": "Choose one"}, skill("defense", 700)]),

    quest("easy_enchant", "Easy Magic", icon="minecraft:enchanting_table", after=["first_diamond"],
          text=["Maren swears that with Easy Magic an enchanting table forgives you: it keeps your lapis and books "
                "and lets you reroll the offers. Build a proper table, fifteen bookshelves around it, and see."],
          tasks=[{"build": {"blocks": {"minecraft:enchanting_table": 1, "minecraft:bookshelf": 15}, "radius": 8},
                  "title": "Build an enchanting table ringed with bookshelves"}],
          rewards=[reward_item("minecraft:lapis_lazuli", 16), reward_item("minecraft:bookshelf", 4),
                   skill("magic", 120)]),

    quest("enchant_30", "The Thirty Club", icon="minecraft:experience_bottle", after=["easy_enchant"],
          text=["The best enchantments cost thirty levels. Maren calls it the Thirty Club, and its only rule is "
                "that you've paid the fee at least once."],
          tasks=[{"levels": 30, "title": "Reach level thirty to afford the best enchantments"}],
          rewards=[reward_item("minecraft:experience_bottle", 8), skill("magic", 200)]),

    quest("levels_10", "Experienced", icon="minecraft:experience_bottle", after=["start:welcome"],
          text=["Maren marks your progress in the margin of the Field Guide: the first ten levels are the ones "
                "that teach you to stay alive."],
          tasks=[{"levels": 10, "title": "Reach experience level ten"}],
          rewards=[reward_item("minecraft:experience_bottle", 4), skill("craft", 50)]),

    quest("levels_50", "Seasoned", icon="minecraft:enchanted_book", after=["levels_10"],
          text=["Fifty levels is a lot of cave-diving, kills and smelting. The Field Guide has a page for those who "
                "have lived that long."],
          tasks=[{"levels": 50, "title": "Reach experience level fifty"}],
          rewards=[reward_item("minecraft:enchanted_book", name="Seasoned", enchant={"minecraft:mending": 1}),
                   skill("magic", 400)]),

    quest("skill_level_10", "A Trade Mastered", icon="fotfskills:skill_tonic", after=["start:skill_trees"],
          text=["Sister Wren noticed you spending your skill points wisely, and Maren added a page to the Guide: "
                "master one trade and the villages will treat you differently."],
          tasks=[{"skill_level": 10, "tree": "any", "title": "Reach level ten in any skill tree"}],
          rewards=[reward_item("fotfskills:skill_tonic"), skill("craft", 200)]),

    quest("walk_1km", "The First Mile", icon="minecraft:leather_boots", after=["start:welcome"],
          text=["Maren says the best way to learn the land is to walk it. A kilometre on foot gets you out of the "
                "village and into the wild."],
          tasks=[{"stats": ON_FOOT, "count": 1 * KM, "title": "Travel one kilometre on foot"}],
          rewards=[reward_item("minecraft:enchanted_book", enchant={'minecraft:feather_falling': 2}), skill("agility", 20)]),

    quest("walk_10km", "The Long Walk", icon="minecraft:leather_boots", after=["walk_1km"],
          text=["The Couriers say a runner who hasn't walked ten kilometres isn't a runner. The Field Guide agrees."],
          tasks=[{"stats": ON_FOOT, "count": 10 * KM, "title": "Travel ten kilometres on foot"}],
          rewards=[reward_item("waystones:waystone"), skill("agility", 100)]),

    quest("walk_100km", "Worn Soles", icon="minecraft:iron_boots", after=["walk_10km"],
          text=["A hundred kilometres is a long way to go on foot. Maren has pasted a page about it into the Guide, "
                "with a note: new boots."],
          tasks=[{"stats": ON_FOOT, "count": 100 * KM, "title": "Travel a hundred kilometres on foot"}],
          rewards=[reward_item("minecraft:enchanted_book", enchant={'minecraft:feather_falling': 4, 'minecraft:depth_strider': 3}, name='Well-Worn Boots'), skill("agility", 300)]),

    quest("sail_5km", "Sea Legs", icon="minecraft:oak_boat", after=["walk_1km"],
          text=["Gil the Ferryman says anyone can row across a pond, but five kilometres by boat makes a sailor. "
                "The Guide has a page for it."],
          tasks=[{"stat": "minecraft:boat_one_cm", "count": 5 * KM, "title": "Sail five kilometres"}],
          rewards=[reward_item("minecraft:white_wool", 4), skill("fish", 100)]),

    quest("ride_5km", "Saddle Sore", icon="minecraft:saddle", after=["walk_1km"],
          text=["The Sanctuary keepers say a good rider knows their mount's temper by the end of five kilometres, "
                "and will be sore by the end of it too."],
          tasks=[{"stat": "minecraft:horse_one_cm", "count": 5 * KM, "title": "Ride five kilometres on horseback"}],
          rewards=[reward_item("minecraft:iron_horse_armor"), skill("taming", 100)]),

    quest("fly_10km", "Cloud Walker", icon="minecraft:elytra", after=["walk_10km"],
          text=["Few things beat flying, and the Field Guide has a page for those who have gone ten kilometres on "
                "elytra wings."],
          tasks=[{"stat": "minecraft:aviate_one_cm", "count": 10 * KM, "title": "Fly ten kilometres"}],
          rewards=[reward_item("minecraft:firework_rocket", 16), skill("agility", 500)]),

    quest("days_7", "A Week in Reece", icon="minecraft:cake", after=["start:welcome"],
          text=["Elder Maren marks a week on her calendar for every newcomer who sticks around. Survive seven "
                "days and nights in Reece and she'll bake you something."],
          tasks=[{"stat": "minecraft:play_time", "count": 7 * DAY, "title": "Survive seven in-game days"}],
          rewards=[reward_item("minecraft:cake"), skill("defense", 40)]),

    quest("days_30", "A Month of Mornings", icon="minecraft:clock", after=["days_7"],
          text=["Thirty days: Maren's calendar has a gold star for it. The clock on the wall of her library was "
                "given to the first person to manage it."],
          tasks=[{"stat": "minecraft:play_time", "count": 30 * DAY, "title": "Survive thirty in-game days"}],
          rewards=[reward_item("minecraft:clock"), reward_item("minecraft:emerald", 6), skill("defense", 120)]),

    quest("days_100", "A Hundred Dawns", icon="minecraft:white_banner", after=["days_30"],
          text=["A hundred dawns is a long time to stay alive. Maren stitches a banner for those who reach it, with "
                "their name along the hem."],
          tasks=[{"stat": "minecraft:play_time", "count": 100 * DAY, "title": "Survive a hundred in-game days"}],
          rewards=[reward_item("minecraft:white_banner", name="A Hundred Dawns", lore=["Stitched by Elder Maren."]), reward_item("minecraft:enchanted_book", enchant={'minecraft:unbreaking': 3}), skill("defense", 300)]),

    quest("mine_1000", "Thousand Stones", icon="minecraft:cobblestone", after=["first_iron"],
          text=["Dagna Holt says a miner who hasn't shifted a thousand stones hasn't earned the title. The Field "
                "Guide has a tally page."],
          tasks=[{"mine": "any", "count": 1000, "title": "Dig a thousand blocks out of the ground"}],
          rewards=[reward_item("minecraft:enchanted_book", name="Thousand Stones", enchant={"minecraft:efficiency": 3}),
                   skill("mining", 150)]),

    quest("mobs_500", "Monster Hunter", icon="minecraft:iron_sword", after=["first_iron"],
          text=["Corvin Ash keeps a tally of the monsters killed in Reece's name, and the five hundredth earns a "
                "page in the Field Guide."],
          tasks=[{"stat": "minecraft:mob_kills", "count": 500, "title": "Defeat five hundred monsters"}],
          rewards=[reward_item("spartanweaponry:iron_katana", name='Five Hundred Notches', lore=['Every nick is a story.'], enchant={'minecraft:sharpness': 2, 'minecraft:looting': 1}), skill("attack", 250)]),

    quest("waystones_10", "Every Road Home", icon="waystones:waystone", after=["start:waystone_reece"],
          text=["Waystones are the Couriers' trade secret, and ten of them is a whole network. The Field Guide says "
                "that someone who knows ten waystones can get home from anywhere."],
          tasks=[{"waystones": 10, "total": True, "title": "Attune ten different waystones"}],
          rewards=[reward_item("waystones:warp_scroll", 4), skill("agility", 150)]),

    quest("back_from_grave", "Not Today", icon="gravestone:gravestone", after=["start:gravestone"],
          text=["Old Edda keeps a ledger of the gravestones she has seen emptied. If you ever fall, open your own "
                "and carry on, and she'll add a tick beside your name."],
          tasks=[{"mine": "gravestone:gravestone", "title": "Recover your belongings from your gravestone"}],
          rewards=[reward_item("minecraft:golden_apple"), skill("defense", 60)]),

    quest("backpack_upgrade", "Bigger on the Inside", icon="sophisticatedbackpacks:gold_backpack",
          after=["start:backpack"],
          text=["Olsen and Odile agree on one thing: a backpack that holds more is worth the gold. Upgrade yours "
                "to gold or diamond."],
          tasks=[item("sophisticatedbackpacks:gold_backpack", title="Upgrade a backpack to gold")],
          rewards=[reward_item("sophisticatedbackpacks:stack_upgrade_tier_1"), skill("craft", 250)]),
]

chapter("milestones", "Milestones", "Small pats on the back for the long road", "minecraft:experience_bottle",
        "milestones", 0, Q)
