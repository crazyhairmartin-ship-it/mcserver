"""Chapter: skill_agility, the Couriers' path: prologue and Act I (first release).
Plan: src/plans/quests/skill_agility.json. Postmistress Juniper Quill runs the post office in Reece; Ender Mail carriers
take the everyday post, the Couriers take what the endermen can't or won't."""
from common import chapter, quest, talk_char, talk_villager, item, reward_item, skill, giver_org, encounter

NO_SHORTCUTS = ["teleport", "mounts"]

Q = [
    quest("sign_the_roster", "Sign the Roster", icon="fotfmail:letter_signed",
          giver=giver_org("couriers", ["Runners wanted! The Ender Mail lot take the parcels, but somebody has to "
                                       "carry the awkward jobs.",
                                       "Sign on at the post office in Reece. Ask for Postmistress Quill, and be quick "
                                       "about it."], "I'll sign on"),
          text=["A cartographer has pinned a Couriers' notice: runners wanted. Sign on at the Reece post office and "
                "carry your first signed letter to a cartographer in another village."],
          tasks=[talk_char("juniper", ["New runner? Good. Name, signature, go.",
                                       "The carriers handle the parcels. We handle what they won't: anything alive, "
                                       "hot, fragile or too big for a mailbox.",
                                       "Sign this letter and take it to the cartographer in the next village. "
                                       "Don't dawdle. Don't read it. Go."]),
                 item("fotfmail:letter_signed", consume=True, title="Sign a letter for delivery"),
                 talk_villager("minecraft:cartographer", ["A letter from Quill? About time.",
                                                          "Signed and sealed. You'll do, runner.",
                                                          "Come back when you want a longer run."],
                               title="Hand it to a cartographer in another village")],
          rewards=[reward_item("minecraft:bundle", name="Courier's Satchel"), reward_item("fotfmail:letter", 8),
                   skill("agility", 60)]),

    quest("first_timed_run", "Beat the Bell", icon="artifacts:running_shoes", after=["sign_the_roster"],
          signature="artifacts:running_shoes",
          text=["Juniper's runner has twisted an ankle, and the morning post must reach the next village before the "
                "noon bell. Make the run on the clock, and the runner will give you their shoes for good."],
          tasks=[item("fotfmail:letter_signed", title="Take the morning post"),
                 {"timed": {"seconds": 150, "goal": {"stat": "minecraft:sprint_one_cm", "count": 40000},
                            "lines": ["The noon bell rings in a few minutes. Run!", "No short cuts, no mounts."],
                            "start": "Start the run", "no": NO_SHORTCUTS}, "title": "Run for the next village"},
                 {"structure": "#villages", "title": "Reach the village"}],
          rewards=[reward_item("artifacts:running_shoes"), skill("agility", 100)]),

    quest("rooftop_basics", "Over, Not Around", icon="parcool:traceur_gloves", after=["sign_the_roster"],
          text=["Couriers don't take the street. Learn ParCool's vault, roll and wall-run on a rooftop line "
                "across Reece, and finish it under the time on the chalk board."],
          tasks=[{"place": "reece"},
                 {"timed": {"seconds": 45, "goal": {"stat": "minecraft:jump", "count": 25},
                            "lines": ["Up and over. Roofs, not roads.", "Keep moving."],
                            "start": "Start the rooftop line", "no": NO_SHORTCUTS},
                  "title": "Run the rooftop line"}],
          rewards=[reward_item("parcool:parcool_guide"), reward_item("parcool:traceur_gloves"),
                   skill("agility", 90)]),

    quest("carry_the_chest", "Don't Unpack It", icon="minecraft:chest", after=["sign_the_roster"],
          text=["A family is moving house, and their strongbox can't be emptied on the way. Pick up the whole chest "
                "with Carry On and walk it to the new cottage, then carry their sleeping cat across too."],
          tasks=[{"structure": "#villages", "title": "Find the family's village"},
                 {"checkmark": "I carried the chest to the new cottage"},
                 {"checkmark": "I carried the sleeping cat across"}],
          rewards=[reward_item("supplementaries:lunch_basket"), skill("agility", 80)]),

    quest("storm_cliff_parcel", "Under a Grey Sky", icon="artifacts:umbrella", after=["first_timed_run"],
          signature="artifacts:umbrella",
          text=["A courier stranded on a cliff path by a thunderstorm begs you to finish their run. Take the parcel "
                "down the wet cliff route to the cove below without falling. Their umbrella is the thanks."],
          tasks=[encounter(["Oh, thank goodness! I can't go on. The path's like glass.",
                            "Take the parcel down to the cove. Slowly! One slip and it's a long way down.",
                            "Here, take my umbrella too. I won't need it where I'm going: back to bed."],
                           entity="minecraft:villager", name="Stranded Courier", where={"above_y": 62}),
                 {"checkmark": "I delivered the parcel to the cove"}],
          rewards=[reward_item("artifacts:umbrella"), skill("agility", 140)]),

    quest("post_office", "Stamps and Tape", icon="endermail:stamp", after=["first_timed_run"],
          text=["Juniper wants a real post office. Craft an Ender Mail package, stamps and a package controller, "
                "set up a locker at the Reece post office and send your first stamped package."],
          tasks=[item("endermail:package", crafted=True), item("endermail:stamp", crafted=True),
                 item("endermail:package_controller", crafted=True), {"place": "reece"},
                 {"build": {"blocks": {"endermail:locker": 1}, "radius": 12}, "title": "Set up a locker"},
                 {"checkmark": "I sent a stamped package"}],
          rewards=[reward_item("endermail:stamp", 8), skill("agility", 150)]),

    quest("waystone_route", "Marking the Route", icon="waystones:waystone", after=["post_office"],
          text=["Old couriers left waystones along the roads. Find and attune three wild waystones between Reece "
                "and the neighbouring villages, so later runs can start halfway."],
          tasks=[item("waystones:attuned_shard", title="Find a waystone and take a shard"),
                 {"checkmark": "I attuned three wild waystones"}],
          rewards=[reward_item("waystones:warp_scroll", 4), skill("agility", 140)]),

    quest("great_bridge_run", "Before the Light Goes", icon="minecraft:stone_bricks", after=["waystone_route"],
          text=["A parcel of medicine must cross a great ravine bridge to a village on the far side before dusk. "
                "Find the old stone bridge and make the crossing on the clock."],
          tasks=[{"checkmark": "I found the old stone bridge"},
                 {"timed": {"seconds": 90, "goal": {"stat": "minecraft:sprint_one_cm", "count": 30000},
                            "lines": ["The light is going. Run for the far side!"],
                            "start": "Cross the bridge", "no": NO_SHORTCUTS}, "title": "Cross before dusk"}],
          rewards=[reward_item("minecraft:sugar", 16), reward_item("minecraft:golden_carrot", 8),
                   skill("agility", 180)]),

    quest("rooftop_route", "The Long Drop Line", icon="artifacts:bunny_hoppers", after=["rooftop_basics"],
          signature="artifacts:bunny_hoppers",
          text=["A large village's couriers race a rooftop route with drops that would break legs. Run the whole "
                "line under the record, and the record holder hands over their bouncy boots."],
          tasks=[{"structure": "#villages", "title": "Find the village's rooftop route"},
                 {"timed": {"seconds": 90, "goal": {"stat": "minecraft:jump", "count": 50},
                            "lines": ["The line runs the whole village. Gaps, drops, all of it.", "Beat the record."],
                            "start": "Run the line", "no": NO_SHORTCUTS + ["pearls"]},
                  "title": "Run the line under the record"}],
          rewards=[reward_item("artifacts:bunny_hoppers"), skill("agility", 220)]),

    quest("night_post", "The Night Post", icon="artifacts:panic_necklace", after=["great_bridge_run"],
          signature="artifacts:panic_necklace",
          text=["An urgent letter must go out after dark across open country. Monsters ambush the road, so take "
                "the hits and keep running. Stopping to fight loses the deadline."],
          tasks=[item("fotfmail:letter_signed", title="Take the urgent letter"),
                 {"timed": {"seconds": 180, "goal": {"stat": "minecraft:sprint_one_cm", "count": 40000},
                            "waves": [{"entity": "minecraft:zombie", "count": 2, "every": 25},
                                      {"entity": "minecraft:skeleton", "count": 1, "every": 40}],
                            "lines": ["Night run. They'll come at you. Don't stop!"],
                            "start": "Start the night run", "no": NO_SHORTCUTS}, "title": "Run the night post"},
                 talk_char("juniper", ["You made it? In one piece? ...Good. Timing was fine.",
                                       "Night runs are the worst. Everything bites.",
                                       "Here. I wore this on my own night runs. It works. Mostly because it "
                                       "makes you run faster."])],
          rewards=[reward_item("artifacts:panic_necklace"), skill("agility", 260)]),

    quest("tower_zipline", "Line from the Tower", icon="parcool:iron_zipline_hook", after=["waystone_route"],
          text=["The Couriers' lookout is an old cartographer tower. Climb it, and rig a zipline from its top to "
                "the road below so runners can drop letters down in seconds."],
          tasks=[{"structure": "mvs:cartographer_tower", "title": "Climb the cartographer tower"},
                 item("parcool:iron_zipline_hook", 2),
                 {"build": {"blocks": {"parcool:iron_zipline_hook": 2}, "radius": 12},
                  "title": "Rig a zipline"}],
          rewards=[reward_item("parcool:iron_zipline_hook", 2), skill("agility", 160)]),

    quest("first_grapple", "Hook and Swing", icon="grapplemod:grapplinghook", after=["tower_zipline"],
          text=["Craft a grappling hook and swing across a canyon course the Couriers marked with flags, faster "
                "than the long way round on foot."],
          tasks=[item("grapplemod:grapplinghook", crafted=True),
                 {"timed": {"seconds": 60, "goal": {"stat": "minecraft:sprint_one_cm", "count": 20000},
                            "lines": ["Flags along the canyon. Swing, don't walk."],
                            "start": "Start the course", "no": ["teleport", "mounts"]},
                  "title": "Swing the canyon course"}],
          rewards=[reward_item("minecraft:string", 16), reward_item("supplementaries:rope", 16), skill("agility", 200)]),

    quest("ledge_rescue", "Stuck on the Ledge", icon="minecraft:ladder",
          after=["first_grapple"],
          text=["A young courier who took a shortcut is stuck on a cliff ledge with a broken leg. Grapple down, "
                "pick them up with Carry On and bring them and their satchel safely back."],
          tasks=[encounter(["Down here! I can't move my leg. I took a shortcut...",
                            "Please don't tell Juniper. She'll make me do the stairs forever.",
                            "My satchel's got sealed letters in it. Can you finish them for me?"],
                           entity="minecraft:villager", name="Injured Courier", where={"above_y": 70}),
                 {"checkmark": "I carried the courier to safety"}, {"structure": "#villages"}],
          rewards=[reward_item("fotfmail:letter", 4), reward_item("minecraft:golden_apple"), skill("agility", 220)]),

    quest("first_ferry", "Across the Bay", icon="smallships:oak_cog", after=["post_office"],
          text=["A beach village's post piles up across the water. Build a rowboat, then a cog, and ferry three "
                "crates of mail over the bay."],
          tasks=[item("smallships:oak_rowboat", crafted=True), item("smallships:oak_cog", crafted=True),
                 item("endermail:package", 3, consume=True, title="Load three crates of mail"),
                 {"structure": "ctov:medium/village_beach", "title": "Reach the beach village"}],
          rewards=[reward_item("minecraft:white_wool", 4), reward_item("minecraft:string", 8),
                   skill("agility", 240)]),
]

chapter("skill_agility", "The Couriers", "Agility path", "minecraft:leather_boots", "skills", 9, Q)
