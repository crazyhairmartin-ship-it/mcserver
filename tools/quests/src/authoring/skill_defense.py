"""Chapter: skill_defense, the Village Watch path: prologue and Act I (first release).
Plan: src/plans/quests/skill_defense.json. Captain Hale and Sergeant Brannock run the watch from Reece."""
from common import chapter, quest, talk_char, item, reward_item, skill

Q = [
    quest("enlist", "Enlist", icon="minecraft:shield",
          text=["Captain Hale enlists anyone who turns up with a shield. Make one and swear to the watch."],
          tasks=[item("minecraft:shield", crafted=True, title="Craft a shield"),
                 talk_char("hale", ["Another recruit. Fine. Stand up straight.",
                                    "A shield. Good. You can't hold a wall without one.",
                                    "The watch protects villages, villagers and, er, anyone who happens to be "
                                    "nearby. Farmers, say.",
                                    "I don't mean any farmer in particular. Moving on. You're in."])],
          rewards=[reward_item("minecraft:leather_chestplate", name="Watch Tabard",
                               lore=["Issued to new recruits of the Village Watch."]),
                   skill("defense", 50)]),

    quest("night_watch", "First Night on the Wall", icon="minecraft:lantern", after=["enlist"],
          text=["Stand the gate of Reece from dusk to dawn beside the guards, and don't give an inch."],
          tasks=[{"place": "reece"},
                 {"timed": {"seconds": 600, "goal": {"hold": {"radius": 20}},
                            "waves": [{"entity": "minecraft:zombie", "count": 3, "every": 40},
                                      {"entity": "minecraft:skeleton", "count": 2, "every": 60}],
                            "lines": ["Night's falling. Take your post at the gate.",
                                      "Hold it until dawn. Don't wander off."],
                            "start": "Take the watch"}, "title": "Hold the gate until dawn"}],
          rewards=[reward_item("spartanshields:copper_basic_shield"), skill("defense", 90)]),

    quest("weak_spots", "Weak Spots", icon="minecraft:oak_fence_gate", after=["night_watch"],
          text=["Walk the edge of Reece with Sergeant Brannock and fix what he points at: a gap in the fence, a "
                "dark lane without torches."],
          tasks=[talk_char("brannock", ["Ah, there you are. Mind my knees.",
                                        "Back in the Marsh Campaign we lost a whole wall to one loose gate.",
                                        "See that gap in the fence? And that lane with no light? Fix them. "
                                        "Hale will want it done by sundown, and he'll pretend he didn't ask.",
                                        "Fence, a gate, and light. Off you go."]),
                 {"build": {"blocks": {"#minecraft:fence_gates": 1, "#minecraft:fences": 6, "minecraft:torch": 6},
                            "radius": 10}, "title": "Fix the fence and light the lane"}],
          rewards=[reward_item("minecraft:lantern", 4), reward_item("minecraft:oak_fence_gate", 2),
                   skill("defense", 110)]),

    quest("arm_a_guard", "Arm the Watch", icon="guardvillagers:guard_spawn_egg", after=["weak_spots"],
          text=["Some villages have no guards at all. Give a willing villager a sword to make a guard, then arm a "
                "second with a crossbow and armour."],
          tasks=[{"advancement": "minecraft:adventure/recruit_guard", "title": "Make a villager a guard"},
                 item("minecraft:crossbow", crafted=True), item("minecraft:iron_chestplate"),
                 {"checkmark": "I armed a second guard"}],
          rewards=[reward_item("minecraft:iron_helmet"), reward_item("minecraft:iron_leggings"),
                   reward_item("minecraft:iron_boots"), skill("defense", 150)]),

    quest("tower_shield", "Behind the Wall of Iron", icon="spartanshields:iron_tower_shield",
          after=["arm_a_guard"],
          text=["Brannock fights behind a tower shield. Craft an iron one, then soak up a beating behind it."],
          tasks=[item("spartanshields:iron_tower_shield", crafted=True),
                 {"timed": {"seconds": 900, "goal": {"stat": "minecraft:damage_blocked_by_shield", "count": 500},
                            "lines": ["Shield up. Let them hit it, not you.", "Fifteen minutes. Hold it."],
                            "start": "Raise the shield"}, "title": "Block 50 hearts of damage"}],
          rewards=[reward_item("minecraft:white_banner", name="Iron Wall Banner",
                               lore=["The mark of those who held the line."]),
                   skill("defense", 200)]),

    quest("scout_outpost", "Eyes on the Outpost", icon="minecraft:spyglass",
          after=["arm_a_guard", "main_story:act1_start"],
          text=["Pillagers have been seen on the roads. Find their outpost and count the crossbows from cover, "
                "without being spotted."],
          tasks=[{"timed": {"seconds": 600, "goal": {"structure": "#illager_hideouts", "label": "the outpost"},
                            "lines": ["Stay low. Don't take a scratch, or you've been seen.",
                                      "Reach the outpost and count the crossbows."],
                            "start": "Begin the scouting", "no": ["hurt"]}, "title": "Reach the outpost unseen"}],
          rewards=[reward_item("minecraft:spyglass"), skill("defense", 220)]),

    quest("first_raid", "At the Gate", icon="artifacts:crystal_heart", after=["scout_outpost", "tower_shield"],
          signature="artifacts:crystal_heart",
          text=["The pillagers come. Stand at the village gate through the whole raid with the guards.",
                "Afterwards Brannock gives you the crystal heart he wore through forty years of raids."],
          tasks=[{"place": "reece"},
                 {"timed": {"seconds": 300, "goal": {"hold": {"radius": 20}},
                            "waves": [{"entity": "minecraft:pillager", "count": 3, "every": 30},
                                      {"entity": "minecraft:vindicator", "count": 2, "every": 45}],
                            "lines": ["Here they come! To the gate!", "Hold the line!"],
                            "start": "Hold the gate"}, "title": "Hold the gate through the raid"},
                 talk_char("brannock", ["Well held. Forty years of raids, and I haven't seen it done better "
                                        "by a new recruit.",
                                        "I wore this through every one. It never cracked. Take it.",
                                        "Tell Hale I said so. He'll go red. He always does."])],
          rewards=[reward_item("artifacts:crystal_heart"), skill("defense", 300)]),

    quest("iceologer", "The Cold Caster", icon="friendsandfoes:totem_of_freezing", after=["first_raid"],
          text=["A snowy village is freezing under ice-chunk storms. Track the iceologer back to its cabin and end "
                "it."],
          tasks=[{"structure": "friendsandfoes:iceologer_cabin", "title": "Find the iceologer's cabin"},
                 {"kill": "friendsandfoes:iceologer", "title": "Defeat the iceologer"}],
          rewards=[reward_item("friendsandfoes:totem_of_freezing"), skill("defense", 280)]),
]

chapter("skill_defense", "The Village Watch", "Defense path", "minecraft:shield", "skills", 8, Q)
