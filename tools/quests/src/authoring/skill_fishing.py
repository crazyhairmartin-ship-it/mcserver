"""Chapter: skill_fishing, the Anglers' Society season: prologue and Act I (first release).
Plan: src/plans/quests/skill_fishing.json. Competitions aren't timed: you fish until the prize quest item bites."""
from common import chapter, quest, talk_char, item, reward_item, skill, encounter


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

chapter("skill_fishing", "The Anglers' Society", "Fishing path", "minecraft:fishing_rod", "skills", 2, Q)
