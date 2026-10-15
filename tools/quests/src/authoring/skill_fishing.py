"""Chapter: skill_fishing, the Anglers' Society season: prologue and Act I (first release).
Plan: src/plans/quests/skill_fishing.json. Competitions aren't timed: you fish until the prize quest item bites."""
from common import chapter, quest, talk_char, item, reward_item, skill, encounter
from common import enc, fight, boss, search, sample, talk_org, talk_villager, talk_char, item, reward_item, skill, encounter, giver_org  # noqa: F401


def prize(name, chance=0.15, texture="minecraft:item/cod"):
    """A prize fish that can only be caught while its quest is open."""
    return {"drop": {"from": ["fishing"], "chance": chance, "item": {"name": name, "texture": texture,
                                                                      "tooltip": "A prize catch"}},
            "consume": False}


Q = [
    quest("sign_up", "Entry Form", icon="minecraft:fishing_rod",
          text=["Commodore Halloway runs the Anglers' Society from Reece. She'll sign you up for the season if you "
                "can land five fish with a plain rod."],
          tasks=[talk_char("halloway", ["Another hopeful! Land five fish with a plain rod and you're in.", "The season's a long line. Bring patience, and tie good knots."]),
                 {"timed": {"seconds": 1200, "goal": {"stat": "minecraft:fish_caught", "count": 5},
                            "lines": ["Five fish before the evening bell, plain rod. Off you go."],
                            "start": "Cast off"}, "title": "Land five fish before the evening bell"}],
          rewards=[reward_item("aquaculture:worm", 16), skill("fish", 60)]),

    quest("bait_and_tackle", "Bait and Tackle", icon="aquaculture:tackle_box", after=["sign_up"],
          text=["Every member keeps a worm farm for bait and a tackle box for hooks and bobbers."],
          tasks=[item("aquaculture:worm_farm"), item("aquaculture:tackle_box")],
          rewards=[reward_item("aquaculture:bobber"), reward_item("aquaculture:fishing_line"), skill("fish", 80)]),

    quest("a_rival_appears", "A Rival on the Bank", icon="minecraft:cod", after=["bait_and_tackle"],
          text=["Someone is coming along the bank, and he looks very pleased with himself."],
          tasks=[encounter(["Silas Pike. Champion angler. You've heard of me. Everyone has.", "Bet you can't hook Grandfather, the old carp. I just throw him back."],
                           character="silas"),
                 prize("Grandfather, the Old Carp", 0.12)],
          rewards=[skill("fish", 100)]),

    quest("opening_cup", "The Opening Cup", icon="artifacts:anglers_hat", after=["a_rival_appears"],
          signature="artifacts:anglers_hat",
          text=["The first competition of the season, at the nearest fishing hut. The cup goes to whoever lands the "
                "society's ribboned trout. The winner wears the lucky angler's hat until next year, or for good, "
                "says the Commodore."],
          tasks=[{"structure": "#fishing_huts", "title": "Go to a fishing hut"}, prize("The Ribboned Trout", 0.1)],
          rewards=[reward_item("artifacts:anglers_hat"), skill("fish", 150)]),

    quest("hundred_fish", "Tally Book", icon="minecraft:writable_book", after=["opening_cup"],
          text=["The society keeps a lifetime tally for every member. A hundred fish ranks you for the summer heats."],
          tasks=[{"stats": ["minecraft:fish_caught"], "count": 100, "title": "Bring your lifetime tally to a hundred"}],
          rewards=[reward_item("aquaculture:iron_hook"), skill("fish", 150)]),

    quest("river_heat", "The River Heat", icon="aquaculture:brown_trout", after=["opening_cup"],
          text=["Heat one runs along a river: a brown trout, a smallmouth bass, a bluegill and a perch, and then the "
                "heat's marked fish."],
          tasks=[item("aquaculture:brown_trout"), item("aquaculture:smallmouth_bass"), item("aquaculture:bluegill"),
                 item("aquaculture:perch"), prize("The Heat's Marked Fish", 0.1)],
          rewards=[reward_item("aquaculture:iron_fishing_rod"), skill("fish", 150)]),

    quest("hooks_and_lines", "Hooked", icon="aquaculture:double_hook", after=["river_heat"],
          text=["Silas won the heat on a technicality and won't stop bragging about his hooks. Make your own, so the "
                "next heat is fair."],
          tasks=[item("aquaculture:light_hook"), item("aquaculture:heavy_hook"), item("aquaculture:double_hook")],
          rewards=[reward_item("aquaculture:gold_hook"), skill("fish", 120)]),

    quest("trap_and_net", "Traps and Nets", icon="lilis_lucky_lures:fish_trap", after=["river_heat"],
          text=["Not every angler sits with a rod. Build a fish trap and a fishing net and set them overnight."],
          tasks=[item("lilis_lucky_lures:fish_trap"), item("lilis_lucky_lures:fishing_net")],
          rewards=[reward_item("lilis_lucky_lures:fish_bag"), skill("fish", 120)]),

    quest("lighthouse_ledger", "The Keeper's Ledger", icon="minecraft:lantern", after=["hooks_and_lines"],
          text=["The season's record book is kept at a lighthouse on the coast. Take the keeper a fresh cod meal and "
                "read the records, including one of Silas's that looks forged."],
          tasks=[{"structure": "#lighthouses", "title": "Find a lighthouse"},
                 item("lilis_lucky_lures:cooked_cod_meal", consume=True), {"search": {"at": {"structure": "#lighthouses"}, "count": 1,
                             "item": {"name": "Season's Record Book", "tooltip": "One of Silas's entries looks forged",
                                      "texture": "minecraft:item/book"},
                             "found": "The keeper's record book, the season's catches in neat columns."},
                  "title": "Find the record book"}],
          rewards=[skill("fish", 150)]),

    quest("beach_weigh_in", "Beach Weigh-in", icon="lilis_lucky_lures:grilled_tropical_fish",
          after=["lighthouse_ledger"],
          text=["The coastal heat ends with a party at a beach hut: catch three tropical fish, grill them, and serve "
                "the judges."],
          tasks=[{"structure": "beachparty:beach_hut", "title": "Find the beach hut"},
                 item("lilis_lucky_lures:grilled_tropical_fish", 3, consume=True)],
          rewards=[reward_item("lilis_lucky_lures:fish_trophy_frame"), skill("fish", 150)]),

    quest("dropped_rod", "The Rod at the Bottom", icon="artifacts:snorkel", after=["beach_weigh_in"],
          signature="artifacts:snorkel",
          text=["The society's heirloom rod went over the side of a boat in the deepest lake around. Silas swears it "
                "wasn't him. Dive down and get it back; the old diver's snorkel is yours afterwards."],
          tasks=[{"be": {"in_water": True, "below_y": 45}, "title": "Dive to the bottom of the deepest lake"}],
          rewards=[reward_item("artifacts:snorkel"), skill("fish", 200)]),
]

ACT2 = [
    quest("net_thieves", "Net Thieves", icon="aquaculture:oak_fish_mount", after=["dropped_rod"],
          text=["Fish keep vanishing from the society's nets at a fishing hut. Feathers and tracks lead to a seagull "
                "flock nesting nearby."],
          tasks=[{"structure": "#fishing_huts", "title": "Go to the fishing hut where the fish go missing"},
                 fight("alexsmobs:seagull", 6, "#fishing_huts", "Net-Thief Gulls", "Drive off the gulls stealing the society's fish")],
          rewards=[reward_item("aquaculture:oak_fish_mount"), skill("fish", 200)]),

    quest("buoy_race", "Between the Buoys", icon="artifacts:flippers", after=["dropped_rod"],
          signature="artifacts:flippers",
          text=["Silas challenges you to a swim, no boats: out around the buoys of the harbour and back to the jetty "
                "before him. The race-master's flippers go to the winner."],
          tasks=[enc(["Race me! No boats! I'll be at the jetty before you're wet!"], character="silas",
                     title="Take up Silas's challenge"),
                 {"timed": {"seconds": 180, "goal": {"structure": "#fishing_huts", "label": "the far jetty", "away": 60},
                            "lines": ["No boats. Around the buoys and back!"], "start": "Start the swim",
                            "no": ["teleport", "mounts"]}, "title": "Swim the harbour course before Silas"}],
          rewards=[reward_item("artifacts:flippers"), skill("fish", 280)]),

    quest("jungle_heat", "Teeth in the River", icon="aquaculture:piranha", after=["buoy_race", "main_story:act2_start"],
          text=["The jungle heat: land an arapaima, a tambaqui and a piranha from a jungle river, and the heat's "
                "marked fish, without being bitten to the bone."],
          tasks=[{"biome": "minecraft:jungle", "title": "Go to a jungle river for the heat"},
                 item("aquaculture:arapaima", title="Land an arapaima"),
                 item("aquaculture:tambaqui", title="Land a tambaqui"),
                 item("aquaculture:piranha", title="Land a piranha"),
                 {"drop": {"from": ["fishing"], "chance": 0.12,
                           "item": {"name": "The Heat's Marked Fish", "texture": "minecraft:item/cod", "tooltip": "A prize catch"}},
                  "consume": False, "title": "Land the heat's marked fish"}],
          rewards=[reward_item("aquaculture:diamond_hook"), skill("fish", 320)]),

    quest("desert_heat", "Oasis Heat", icon="aquaculture:bayad", after=["buoy_race"],
          text=["A heat on the desert rivers: bring back the society's three 'river of sand' fish, the bayad, "
                "the boulti and the capitaine."],
          tasks=[{"biome": "minecraft:desert", "title": "Go to the desert rivers for the heat"},
                 item("aquaculture:bayad", title="Land a bayad"),
                 item("aquaculture:boulti", title="Land a boulti"),
                 item("aquaculture:capitaine", title="Land a capitaine")],
          rewards=[reward_item("aquaculture:iron_fillet_knife"), skill("fish", 300)]),

    quest("reef_survey", "Colours of the Reef", icon="rainbowreef:clownfish_bucket", after=["buoy_race"],
          text=["The society wants a living display. Bucket a clownfish, a seahorse and a moorish idol from a warm "
                "reef, and the society builds an aquarium around them in Reece."],
          tasks=[{"biome": "minecraft:warm_ocean", "title": "Dive to a warm reef"},
                 item("rainbowreef:clownfish_bucket", title="Bucket a clownfish for the aquarium"),
                 item("rainbowreef:moorish_idol_bucket", title="Bucket a moorish idol for the aquarium"),
                 item("rainbowreef:raw_seahorse", title="Catch a seahorse for the aquarium")],
          rewards=[reward_item("rainbowreef:blue_puffer_lantern"), skill("fish", 300)]),

    quest("outcast_fisherman", "The Fisherman Who Left", icon="aquaculture:tuna", after=["reef_survey"],
          text=["Out at sea, an outcast fisherman lives on his little boat and knows the deep-water spots. Find him "
                "and match his catch of tuna, red grouper and halibut to earn a place in the deep-sea heat."],
          tasks=[{"structure": "structory:boat", "title": "Find the outcast fisherman's boat at sea"},
                 item("aquaculture:tuna", title="Land a tuna to match his catch"),
                 item("aquaculture:red_grouper", title="Land a red grouper to match his catch"),
                 item("aquaculture:atlantic_halibut", title="Land a halibut to match his catch")],
          rewards=[reward_item("aquaculture:leech", 16), skill("fish", 330)]),

    quest("pillager_poachers", "Poachers Afloat", icon="aquaculture:lockbox", after=["outcast_fisherman"],
          text=["A pillager ship is dragging nets through the society's fishing grounds. Sail out, board it and clear "
                "its crew."],
          tasks=[fight("minecraft:pillager", 8, "towns_and_towers:pillager_outpost_ocean", "Net Poachers",
                       "Board the poachers' ship and clear its crew", wave=4)],
          rewards=[reward_item("aquaculture:lockbox"), skill("fish", 340)]),

    quest("neptunes_bounty", "Neptune's Bounty", icon="aquaculture:neptunes_bounty", after=["outcast_fisherman"],
          text=["The outcast fisherman says the sea gives up treasure to the patient. Fish up Neptune's Bounty, "
                "open it and forge your first neptunium."],
          tasks=[item("aquaculture:neptunes_bounty", title="Fish up Neptune's Bounty"),
                 item("aquaculture:neptunium_ingot", crafted=True, title="Forge your first neptunium")],
          rewards=[reward_item("aquaculture:neptunium_nugget", 8), skill("fish", 370)]),

    quest("salvage_logbook", "The Captain's Logbook", icon="minecraft:chest", after=["pillager_poachers"],
          text=["The poachers' logbook names a wreck where they hid the society's old trophies. Find the shipwreck "
                "and salvage them."],
          tasks=[{"structure": "#shipwrecks", "title": "Find the wreck named in the logbook"},
                 search("#shipwrecks", 1, "the Society's Old Trophies", "A trophy case, green with weed.",
                        title="Salvage the society's old trophies")],
          rewards=[reward_item("minecraft:chest", 2), skill("fish", 400)]),
]

chapter("skill_fishing", "The Anglers' Society", "Fishing path", "minecraft:fishing_rod", "skills", 2, Q + ACT2)
