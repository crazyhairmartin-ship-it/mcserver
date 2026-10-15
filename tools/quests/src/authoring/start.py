"""Chapter: start (the first hour in Reece). Plan: src/plans/quests/start.json. Writes src/chapters/start.json."""
from common import chapter, quest, talk_char, talk_org, talk_villager, item, reward_item, skill, give, give_guide

Q = [
    quest("welcome", "Welcome to Reece", icon="minecraft:oak_sapling", shape="diamond", size=1.5,
          text=["Elder Maren is waiting by Reece's well. She meets every newcomer herself.",
                "Find her in Reece and say hello."],
          tasks=[talk_char("maren", ["A new face! Welcome to Reece, dearie. Here, the Field Guide. I wrote half.", "And bread and torches. Nobody argues with me."])],
          rewards=[give_guide(), reward_item("minecraft:bread", 4), reward_item("minecraft:torch", 16)]),

    quest("field_guide", "Read the Field Guide", icon="patchouli:guide_book", after=["welcome"],
          text=["The Field Guide explains everything the forest has to offer. Lost it? Type /guide for a new one.",
                "Somewhere in it there's a page on the quiet forest. Someone pressed a leaf between its pages and "
                "left Reece in a hurry."],
          tasks=[item("patchouli:guide_book", title="Keep the Field Guide with you")],
          rewards=[reward_item("minecraft:wooden_pickaxe"), reward_item("minecraft:wooden_axe"),
                   reward_item("minecraft:lantern")]),

    quest("reece_tour", "Old Streets, New Roofs", icon="minecraft:bell", after=["welcome"],
          text=["Reece is bigger than it looks. Walk its streets: the smithy, the farms and the market square, and "
                "meet the people who keep them going."],
          tasks=[{"place": "reece", "title": "Walk around Reece"},
                 talk_org("crafters", ["The smithy's this way. Mind the anvil."], title="Say hello at the smithy"),
                 talk_org("growers", ["Fields don't plant themselves. Nice to meet you."], title="Say hello at the farms")],
          rewards=[reward_item("minecraft:emerald", 3), reward_item("minecraft:map")]),

    quest("skill_trees", "Every Hand Learns", icon="minecraft:experience_bottle", after=["field_guide"],
          text=["Reece trains its people in skills: mining, farming, fishing, fighting and more. Almost everything "
                "you do earns skill XP.",
                "Press K to open your skill trees, earn your first point in any tree and spend it."],
          tasks=[{"skill_level": 1, "tree": "any", "spent": True, "title": "Spend your first skill point"}],
          rewards=[skill(t, 15) for t in ("mining", "forage", "farm", "fish", "cook", "craft", "attack", "range",
                                          "defense", "agility", "magic", "taming")]),

    quest("skill_tonic", "A Bitter Tonic", icon="fotfskills:skill_tonic", after=["skill_trees"],
          text=["Changed your mind about a skill? Sister Wren, Reece's cleric, brews skill tonics that let you "
                "unlearn a tree's choices.",
                "Ask her how they work, and keep one in reserve."],
          tasks=[talk_char("wren", ["Notch gave us learning, and in mercy, unlearning. A tonic undoes one tree.", "It tastes awful. That's how you know it works. Keep it."])],
          rewards=[reward_item("fotfskills:skill_tonic")]),

    quest("first_timber", "Timber!", icon="minecraft:oak_log", after=["welcome"],
          text=["Every journey starts with a tree. Hold the Ultimine key while you chop and the whole trunk comes "
                "down in one go.",
                "Reece's woodpile needs filling: gather 64 oak logs."],
          tasks=[item("minecraft:oak_log", 64)],
          rewards=[reward_item("minecraft:stone_axe"), reward_item("minecraft:apple", 4), skill("forage", 40)]),

    quest("waystone_reece", "The Stone That Remembers", icon="waystones:waystone", after=["reece_tour"],
          text=["The waystone in Reece remembers everyone who touches it. Attune to it, then find a second waystone "
                "out in the wild.",
                "Waystones let you warp between any you've found."],
          tasks=[{"place": "reece", "title": "Attune to Reece's waystone"},
                 {"waystones": 1, "wild": True, "title": "Find and attune a waystone out in the wild"}],
          rewards=[reward_item("waystones:return_scroll"), reward_item("waystones:warp_dust", 4)]),

    quest("backpack", "Room to Carry", icon="sophisticatedbackpacks:backpack", after=["first_timber"],
          text=["Your pockets won't hold a forest. Stitch a backpack, and fit it with a pickup upgrade so it fills "
                "itself as you walk."],
          tasks=[item("sophisticatedbackpacks:backpack"), item("sophisticatedbackpacks:pickup_upgrade")],
          rewards=[reward_item("minecraft:leather", 6), skill("craft", 40)]),

    quest("first_night", "The Hourglass Night", icon="minecraft:red_bed", after=["reece_tour"],
          text=["Craft a bed and sleep through your first night. The more of the server is asleep, the faster the "
                "stars wheel by."],
          tasks=[{"advancement": "minecraft:adventure/sleep_in_bed"}],
          rewards=[reward_item("minecraft:cooked_mutton", 4), reward_item("minecraft:candle", 2)]),

    quest("camp_out", "Under the Open Sky", icon="comforts:sleeping_bag_white", after=["first_night"],
          text=["Nights on the road are kinder with a sleeping bag, and afternoons are kinder with a hammock.",
                "Make both."],
          tasks=[item("comforts:sleeping_bag_white"), item("comforts:hammock_white")],
          rewards=[reward_item("comforts:rope_and_nail", 2), reward_item("minecraft:campfire")]),

    quest("gravestone", "The Sexton's Promise", icon="gravestone:gravestone", after=["reece_tour"],
          text=["Old Edda keeps Reece's graveyard. She has something to tell every newcomer."],
          tasks=[talk_char("edda", ["A gravestone holds your things where you fall. Only you can open it.", "Read this obituary. Then don't be them."])],
          rewards=[reward_item("gravestone:obituary"), reward_item("minecraft:golden_carrot")]),

    quest("cosmetic_armor", "Dressed for Reece", icon="minecraft:leather_chestplate", after=["reece_tour"],
          text=["Reece's tailor thinks armour is ugly at the harvest dance. You can wear anything over your armour "
                "in the cosmetic armour slots of your inventory and keep the protection underneath.",
                "Bring the tailor 8 white wool for a festival outfit."],
          tasks=[talk_villager("minecraft:leatherworker", ["Armour at a dance? Absolutely not.",
                                                            "Bring me wool and I'll make you something proper."]),
                 item("minecraft:white_wool", 8, consume=True)],
          rewards=[reward_item("minecraft:leather_helmet"), reward_item("minecraft:leather_chestplate"),
                   reward_item("minecraft:leather_leggings"), reward_item("minecraft:leather_boots")]),

    quest("natures_compass", "Which Way the Wind Blows", icon="minecraft:compass", after=["waystone_reece"],
          text=["A Nature's Compass points to any biome you name. Craft one and use it to find somewhere you've "
                "never been."],
          tasks=[item("naturescompass:naturescompass")],
          rewards=[reward_item("minecraft:emerald", 4), skill("agility", 40)]),

    quest("explorers_compass", "Which Way the Stones Lie", icon="explorerscompass:explorerscompass",
          after=["natures_compass"],
          text=["An Explorer's Compass points to places people built. Craft one and follow it to the nearest well."],
          tasks=[item("explorerscompass:explorerscompass"), {"structure": "#wells", "title": "Find a well"}],
          rewards=[reward_item("minecraft:iron_ingot", 4), reward_item("minecraft:bucket")]),

    quest("guilds_of_the_field", "Hands of the Field", icon="minecraft:wheat", after=["reece_tour"],
          text=["Four organisations work the land and water around Reece. Meet a member of each: the Growers' "
                "co-op (farmers), the Anglers' society (fishermen), the Herbalists (clerics) and the Tavern keepers "
                "(butchers).",
                "Sneak and right-click a villager to talk."],
          tasks=[talk_org("growers", ["The co-op's always short of hands. Come and see us."]),
                 talk_org("anglers", ["Fish bite at dawn and dusk. We'll teach you the rest."]),
                 talk_org("herbalists", ["Every weed is a medicine to someone."]),
                 talk_org("tavern", ["Nobody leaves a tavern hungry. That's the rule."])],
          rewards=[reward_item("minecraft:wheat_seeds", 16), reward_item("minecraft:fishing_rod"),
                   reward_item("minecraft:bread", 4)]),

    quest("guilds_of_the_forge", "Hands of the Forge", icon="minecraft:iron_pickaxe", after=["reece_tour"],
          text=["Four more work stone, metal and the hunt: the Miners' guild (toolsmiths), the Crafters' guild "
                "(masons), the Bounty office (weaponsmiths, by the bounty board) and the Hunters' lodge (fletchers)."],
          tasks=[talk_org("miners", ["Mind the gravel and carry torches. That's half of mining."]),
                 talk_org("crafters", ["Anything worth making is worth making twice."]),
                 talk_org("bounty", ["The board pays for monsters. Read it every morning."]),
                 talk_org("hunters", ["Walk soft and shoot straight."])],
          rewards=[reward_item("minecraft:torch", 16), reward_item("minecraft:stonecutter"),
                   reward_item("minecraft:arrow", 16)]),

    quest("guilds_of_the_road", "Hands of the Road", icon="minecraft:filled_map", after=["reece_tour"],
          text=["And four keep the roads open: the Couriers (cartographers), the Village watch (guards), the Arcane "
                "order (librarians) and the Sanctuary keepers (shepherds)."],
          tasks=[talk_org("couriers", ["If it needs to be somewhere else, we'll take it."]),
                 talk_org("watch", ["Keep your eyes open at dusk."]),
                 talk_org("arcane", ["Magic is just knowledge nobody's written down yet."]),
                 talk_org("sanctuary", ["Every animal deserves somewhere safe."])],
          rewards=[reward_item("minecraft:map"), reward_item("minecraft:shield"), reward_item("minecraft:book"),
                   reward_item("minecraft:lead")]),

    quest("clerics_worry", "The Cleric's Worry", icon="minecraft:candle", shape="diamond", size=1.25,
          after=["field_guide", "guilds_of_the_field"],
          text=["Sister Wren has been watching the forest. She'd like a word."],
          tasks=[talk_char("wren", ["The forest has gone quiet. The old spirits no longer answer my prayers.", "I don't know what's wrong. Will you help me find out?"])],
          rewards=[give('minecraft:potion{Potion:"minecraft:healing"}', "A healing potion")]),
]

chapter("start", "Welcome to Reece", "Your first day in the forest", "minecraft:oak_sapling", "start", 0, Q)
