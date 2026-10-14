"""Chapter: main_story, Prologue and Act I (first release). Plan: src/plans/quests/main_story.json.
Later acts are added to this file in later releases (append only: quest ids are permanent)."""
from common import chapter, quest, talk_char, talk_org, talk_villager, item, reward_item, skill, give

PROLOGUE = [
    quest("prologue_silent_wood", "The Silent Wood", icon="minecraft:oak_sapling", after=["start:clerics_worry"],
          text=["Sister Wren wants to know what's wrong with the forest. Go to the forest's edge after dusk and wait "
                "out one night.",
                "No fairies dance. The butterflies are gone. And something has scored the bark of the oldest tree."],
          tasks=[{"biome": "minecraft:forest", "title": "Go to the forest"},
                 {"checkmark": "I waited out the night"}],
          rewards=[give('minecraft:potion{Potion:"minecraft:night_vision"}', "A night vision potion")]),

    quest("prologue_shrine", "A Shrine for the Quiet", icon="minecraft:candle", after=["prologue_silent_wood"],
          text=["Sister Wren asks for a small wayside shrine: mossy stone, candles, and wildflowers gathered from "
                "three different places.",
                "Build it wherever feels right."],
          tasks=[item("minecraft:mossy_cobblestone", 16), item("minecraft:candle", 4), item("minecraft:cornflower"),
                 item("minecraft:allium"), item("minecraft:lily_of_the_valley"),
                 {"checkmark": "I built the shrine"}],
          rewards=[reward_item("minecraft:candle", 8), skill("forage", 60)]),

    quest("prologue_home", "Somewhere to Come Back To", icon="minecraft:red_bed", after=["prologue_silent_wood"],
          text=["You can't sleep in a sleeping bag forever. Build your first home near Reece, with a bed, a chest, a "
                "table and chairs."],
          tasks=[item("minecraft:red_bed"), item("minecraft:chest"), item("handcrafted:oak_table"),
                 item("handcrafted:oak_chair", 2), {"checkmark": "My home is built"}],
          rewards=[reward_item("another_furniture:oak_chair", 2), skill("craft", 60)]),

    quest("prologue_fallen", "The Fallen Adventurer", icon="minecraft:skeleton_skull", after=["prologue_shrine"],
          text=["Out in the wild lie the remains of adventurers who never came home, still in their rusted gear.",
                "Find one. Something in the forest's silence points that way."],
          tasks=[{"checkmark": "I found a fallen adventurer"}],
          rewards=[reward_item("minecraft:stone_sword"), skill("agility", 60)]),

    quest("prologue_dungeon", "What the Dark Keeps", icon="minecraft:spawner", after=["prologue_fallen"],
          text=["The adventurer's journal speaks of 'the wardens growing weak', and points to an old dungeon.",
                "Clear a dungeon, and find the second journal page on one of its guardians."],
          tasks=[{"structure": "#yungs_dungeons", "title": "Find the dungeon"},
                 {"drop": {"from": ["minecraft:zombie", "minecraft:skeleton", "minecraft:spider"], "chance": 0.2,
                           "item": {"name": "Second Journal Page", "texture": "minecraft:item/paper"}},
                  "consume": False}],
          rewards=[reward_item("minecraft:iron_ingot", 8), skill("attack", 80)]),

    quest("prologue_letter", "Word to the Neighbours", icon="fotfmail:letter", after=["prologue_dungeon"],
          text=["Sister Wren writes to the cleric of the next village along the road. Deliver her letter in person; "
                "his reply will follow you home by post."],
          tasks=[talk_villager("minecraft:cleric", ["A letter from Sister Wren? It's been too long.",
                                                    "Tell her I'll write back. The post's slow, but it gets there."],
                               title="Deliver the letter to another village's cleric")],
          rewards=[reward_item("fotfmail:letter", 4), reward_item("minecraft:emerald", 5)]),
]

ACT1 = [
    quest("act1_start", "The First Wardens", icon="minecraft:written_book", shape="diamond", size=1.5,
          after=["prologue_letter", "prologue_home"],
          text=["Both journal pages together tell of guardians: the wardens, who hold the old places shut.",
                "Sister Wren has read them twice."],
          tasks=[talk_char("wren", ["I've read them twice. Notch forgive me, I almost wish I hadn't.",
                                    "The wardens hold the old places shut. And someone thinks they're being drained.",
                                    "The first of them sleeps in iron, under the hills.",
                                    "Take this armour. It was blessed at the shrine, for what that's worth.",
                                    "Be careful. Whatever's draining them is still out there. Notch keep you."])],
          rewards=[reward_item("minecraft:iron_chestplate")]),

    quest("act1_iron_kit", "Iron and Edge", icon="spartanweaponry:iron_longsword", after=["act1_start"],
          text=["Arm yourself for what's ahead: a proper weapon, a shield and full iron armour.",
                "Any Spartan Weaponry iron weapon will do; the quest asks for a longsword, but the choice is yours."],
          tasks=[item("spartanweaponry:iron_longsword"), item("spartanshields:iron_basic_shield"),
                 item("minecraft:iron_helmet"), item("minecraft:iron_leggings"), item("minecraft:iron_boots")],
          rewards=[{"item": "minecraft:enchanted_book", "enchant": {"minecraft:sharpness": 2}}, skill("attack", 80)]),

    quest("act1_temple", "Sand and Vine", icon="minecraft:chiseled_sandstone", after=["act1_start"],
          text=["Search a desert or jungle temple. Get past its traps to the inner chamber, where a mural shows a "
                "hooded iron giant."],
          tasks=[{"structure": "#temples", "title": "Reach a temple's inner chamber"},
                 {"checkmark": "I saw the mural"}],
          rewards=[reward_item("minecraft:gold_ingot", 6), skill("agility", 80)]),

    quest("act1_mineshaft", "The Echo in the Shaft", icon="minecraft:rail", after=["act1_start"],
          text=["Miners in an old mineshaft heard metal footsteps below them. Explore it, mine 16 iron, and look for "
                "scrape marks leading down."],
          tasks=[{"structure": "#mines", "title": "Explore a mineshaft"}, item("minecraft:raw_iron", 16)],
          rewards=[reward_item("minecraft:lantern"), skill("mining", 80)]),

    quest("act1_wrought_practice", "Strike From Behind", icon="dummmmmmy:target_dummy",
          after=["act1_temple", "act1_mineshaft"],
          text=["Armour that breathes, in a sealed chamber. Captain Hale of the Village watch knows what that means, "
                "and wants you ready before you go anywhere near it."],
          tasks=[talk_char("hale", ["Armour that breathes. I've seen it once. Lost good people that day.",
                                    "Iron giants are slow to turn. Get behind it and strike.",
                                    "Build yourself a target dummy and practise until it's habit.",
                                    "Then go and look. Look. Don't fight it until you're ready.",
                                    "...And come back. That's an order. People here would miss you."]),
                 item("dummmmmmy:target_dummy")],
          rewards=[skill("defense", 80)]),

    quest("act1_wrought_scout", "The Iron Door", icon="minecraft:iron_door", after=["act1_wrought_practice"],
          text=["Follow the scrape marks to a Wrought Chamber and look at its sealed door. The armour inside is "
                "breathing."],
          tasks=[{"structure": "mowziesmobs:wrought_chamber", "title": "Find a Wrought Chamber"}],
          rewards=[reward_item("minecraft:spyglass")]),

    quest("act1_wroughtnaut", "The Ferrous Wroughtnaut", icon="minecraft:iron_axe", shape="diamond", size=1.5,
          after=["act1_wrought_scout", "act1_iron_kit"],
          text=["Wake the Ferrous Wroughtnaut and beat it. Dodge its axe and strike its exposed back, like Hale "
                "taught you."],
          tasks=[{"kill": "mowziesmobs:ferrous_wroughtnaut", "title": "Put the iron giant back to sleep"}],
          rewards=[reward_item("minecraft:golden_apple", 2), skill("attack", 200)]),

    quest("act1_wrought_report", "Rust on the Seal", icon="minecraft:iron_nugget", after=["act1_wroughtnaut"],
          text=["Take what you learned back to Sister Wren."],
          tasks=[talk_char("wren", ["You're alive. Thank Notch. Tell me everything.",
                                    "...It wasn't evil. It was starving.",
                                    "Something had been feeding on it, a little at a time, for years.",
                                    "Notch made the wardens to guard His world. Who would dare drain them?",
                                    "Then it's not just this one. It's all of them."])],
          rewards=[reward_item("minecraft:emerald", 8)]),

    quest("act1_magic_branch", "A Priest on the Road", icon="irons_spellbooks:scroll", after=["act1_wrought_report"],
          text=["On the road, a travelling priest of the Arcane order stops you. He's been following the same trail."],
          tasks=[{"encounter": {"entity": "minecraft:villager", "name": "Travelling Priest", "then": "talk",
                                "lines": ["The drain smells of old magic. Very old.",
                                          "There's a Pyromancer Tower not far from here. Its keepers know more than "
                                          "they say.",
                                          "If you've a head for magic, start there."]}}],
          rewards=[reward_item("irons_spellbooks:scroll"), reward_item("irons_spellbooks:common_ink")]),

    quest("act1_outpost", "Banners on the Hill", icon="minecraft:white_banner", after=["act1_wrought_report"],
          text=["Pillagers have raised an outpost near the trade road. Clear it and take down its captain."],
          tasks=[{"structure": "#illager_hideouts", "title": "Find the outpost"},
                 {"kill": "minecraft:pillager", "count": 6, "title": "Clear the outpost off the trade road"}],
          rewards=[reward_item("minecraft:crossbow"), reward_item("minecraft:arrow", 32)]),

    quest("act1_iceologer", "Frost on the Wind", icon="minecraft:packed_ice", after=["act1_outpost"],
          text=["A frightened trader comes looking for help: something froze his caravan in the snowy taiga."],
          tasks=[{"encounter": {"entity": "minecraft:wandering_trader", "name": "Frightened Trader", "then": "talk",
                                "lines": ["It came out of the snow. Ice everywhere, in a heartbeat.",
                                          "My caravan's frozen solid in the taiga. Please, stop it before it finds "
                                          "a village."]}},
                 {"encounter": {"entity": "friendsandfoes:iceologer", "name": "The Iceologer", "then": "kill",
                                "glow": True, "where": {"biomes": ["minecraft:snowy_taiga", "minecraft:taiga",
                                                                   "minecraft:grove", "minecraft:snowy_plains"]}}}],
          rewards=[reward_item("minecraft:leather_chestplate"), skill("attack", 120)]),

    quest("act1_illusioner", "Four of Him", icon="minecraft:bow", after=["act1_iceologer"],
          text=["An Illusioner haunts the woods. Find the real one among its copies and defeat it."],
          tasks=[{"encounter": {"entity": "minecraft:illusioner", "name": "The Trickster", "then": "kill",
                                "where": {"biomes": ["minecraft:forest", "minecraft:dark_forest",
                                                     "minecraft:birch_forest"]}}}],
          rewards=[{"item": "minecraft:bow", "name": "Trickster's Bow", "enchant": {"minecraft:power": 2}},
                   skill("range", 120)]),

    quest("act1_raid", "The Long Night", icon="minecraft:totem_of_undying", after=["act1_illusioner"],
          text=["Captain Hale has a plan: draw the raiders out on your terms. Carry the Bad Omen into a village and "
                "hold it through a full raid."],
          tasks=[talk_char("hale", ["Raiders come when they smell weakness. We'll show them none.",
                                    "We fight at the village edge. Nobody gets near the fields. Nobody.",
                                    "...Marta's fields, I mean. The farms. All the farms. Equally.",
                                    "Bring the omen in when you're ready. My guards will stand with you."]),
                 {"advancement": "minecraft:adventure/hero_of_the_village"}],
          rewards=[reward_item("minecraft:totem_of_undying"), skill("defense", 200)]),

    quest("act1_umvuthana_scout", "Masks in the Grass", icon="minecraft:acacia_sapling", after=["act1_raid"],
          text=["Travel to the savanna and find the Umvuthana Grove. Watch the Umvuthana from cover and count their "
                "masks."],
          tasks=[{"structure": "mowziesmobs:umvuthana_grove", "title": "Find the grove"},
                 {"observe": "mowziesmobs:umvuthana", "ticks": 60, "title": "Watch an Umvuthana"}],
          rewards=[skill("agility", 120)]),

    quest("act1_umvuthi", "Umvuthi, the Sunbird", icon="minecraft:sunflower", shape="diamond", size=1.5,
          after=["act1_umvuthana_scout"],
          text=["Face Umvuthi and its followers in the heart of the grove. Break the circle of masks before the sun "
                "spell lands."],
          tasks=[{"kill": "mowziesmobs:umvuthi", "title": "Break the circle of masks"}],
          rewards=[reward_item("minecraft:diamond", 3), skill("attack", 250)]),

    quest("act1_finale", "A Door in the Flowers", icon="minecraft:diamond", shape="diamond", size=1.75,
          after=["act1_umvuthi", "act1_wroughtnaut"],
          text=["With two wardens freed, Sister Wren remembers the spirits' own realm.",
                "Dig a pool, ring it with flowers and drop a diamond in. The way into the Twilight Forest opens."],
          tasks=[{"dimension": "twilightforest:twilight_forest", "title": "Enter the Twilight Forest"}],
          rewards=[reward_item("minecraft:diamond"), skill("magic", 150)]),
]

chapter("main_story", "The Silent Forest", "The main story", "minecraft:written_book", "story", 0,
        PROLOGUE + ACT1)
