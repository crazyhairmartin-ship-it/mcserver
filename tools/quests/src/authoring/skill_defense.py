"""Chapter: skill_defense, the Village Watch path: prologue and Act I (first release).
Plan: src/plans/quests/skill_defense.json. Captain Hale and Sergeant Brannock run the watch from Reece."""
from common import chapter, quest, talk_char, item, reward_item, skill
from common import enc, fight, boss, search, sample, talk_org, talk_villager, talk_char, item, reward_item, skill, encounter, giver_org  # noqa: F401

Q = [
    quest("enlist", "Enlist", icon="minecraft:shield",
          text=["Captain Hale enlists anyone who turns up with a shield. Make one and swear to the watch."],
          tasks=[item("minecraft:shield", crafted=True, title="Craft a shield"),
                 talk_char("hale", ["Another recruit. A shield, good. Stand up straight.", "The watch protects villagers. And farmers. No farmer in particular. You're in."])],
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
          tasks=[talk_char("brannock", ["Mind my knees. See that gap in the fence, that dark lane?", "Fix them before sundown. Hale will pretend he didn't ask."]),
                 {"build": {"blocks": {"#minecraft:fence_gates": 1, "#minecraft:fences": 6, "minecraft:torch": 6},
                            "radius": 10}, "title": "Fix the fence and light the lane"}],
          rewards=[reward_item("minecraft:lantern", 4), reward_item("minecraft:oak_fence_gate", 2),
                   skill("defense", 110)]),

    quest("arm_a_guard", "Arm the Watch", icon="guardvillagers:guard_spawn_egg", after=["weak_spots"],
          text=["Some villages have no guards at all. Give a willing villager a sword to make a guard, then arm a "
                "second with a crossbow and armour."],
          tasks=[{"advancement": "minecraft:adventure/recruit_guard", "title": "Make a villager a guard"},
                 item("minecraft:crossbow", crafted=True), item("minecraft:iron_chestplate")],
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
                 talk_char("brannock", ["Well held. I wore this through forty years of raids. Take it.", "Tell Hale I said so. He'll go red."])],
          rewards=[reward_item("artifacts:crystal_heart"), skill("defense", 300)]),

    quest("iceologer", "The Cold Caster", icon="friendsandfoes:totem_of_freezing", after=["first_raid"],
          text=["A snowy village is freezing under ice-chunk storms. Track the iceologer back to its cabin and end "
                "it."],
          tasks=[{"structure": "friendsandfoes:iceologer_cabin", "title": "Find the iceologer's cabin"},
                 {"kill": "friendsandfoes:iceologer", "title": "Defeat the iceologer", "spawn": {"at": {"structure": "friendsandfoes:iceologer_cabin"}, "wave": 1, "ensure": True}}],
          rewards=[reward_item("friendsandfoes:totem_of_freezing"), skill("defense", 280)]),
]

ACT2 = [
    quest("pilgrim", "The Pilgrim's Road", icon="artifacts:cross_necklace", after=["first_raid"],
          signature="artifacts:cross_necklace",
          text=["An old priest appears on the road, set on reaching a distant chapel through bandit country. Keep him "
                "alive all the way. At the altar he gives you the necklace he prayed with."],
          tasks=[enc(["I walk to the chapel. Bandits or no.", "Stay close, and I'll pray for you."],
                     then="escort", entity="minecraft:villager", name="Old Priest",
                     to={"structure": "meadow:chapel", "label": "the chapel"}, title="Escort the old priest to the chapel")],
          rewards=[reward_item("artifacts:cross_necklace"), skill("defense", 300)]),

    quest("illusioner", "Which One Is Real?", icon="friendsandfoes:totem_of_illusion",
          after=["iceologer", "main_story:act2_start"],
          text=["At the illusioner's training grounds, a dozen copies attack at once. Find the real illusioner and "
                "break the spell."],
          tasks=[boss("minecraft:illusioner", "friendsandfoes:illusioner_training_grounds", "The Illusioner",
                      "Find the real illusioner among the copies and break the spell")],
          rewards=[reward_item("friendsandfoes:totem_of_illusion"), skill("defense", 280)]),

    quest("fortified_village", "The Walled Town", icon="minecraft:iron_ingot", after=["pilgrim"],
          text=["Captain Hale wants plans for Reece's walls. Travel to a fortified village, bring its watch captain "
                "iron, and copy how its walls are built."],
          tasks=[{"structure": "ctov:large/village_plains_fortified", "title": "Travel to a walled village"},
                 item("minecraft:iron_ingot", 16, consume=True, title="Bring the watch captain iron for the favour"),
                 talk_org("watch", ["Hale sent you? For the wall plans? Iron's welcome.", "Copy ours. Walls like this hold."],
                          title="Ask the wall's captain for the plans"),
                 search("ctov:large/village_plains_fortified", 1, "the Wall Plans", "Rolled plans of the wall, in a captain's chest.",
                        title="Copy the wall's plans")],
          rewards=[reward_item("minecraft:writable_book", name="The Wall Plans", lore=["How the walls are built."]),
                   skill("defense", 300)]),

    quest("build_walls", "Walls for Reece", icon="minecraft:stone_bricks", after=["fortified_village"],
          text=["Raise a stone wall and a gatehouse on Reece's open side from the plans, and raise two iron golems "
                "to stand at the gate."],
          tasks=[{"place": "reece"},
                 {"build": {"blocks": {"#minecraft:walls": 8, "minecraft:stone_bricks": 24, "#minecraft:fence_gates": 1},
                            "radius": 12}, "title": "Raise a wall and gatehouse on Reece's open side"},
                 item("minecraft:iron_block", 8, consume=True, title="Bring iron to raise the gate's golems"),
                 item("minecraft:carved_pumpkin", 2, consume=True, title="Bring pumpkins to crown the golems")],
          rewards=[reward_item("spartanshields:diamond_basic_shield"), skill("defense", 340)]),

    quest("stray_fort", "The Stray Fort", icon="minecraft:stray_spawn_egg", after=["illusioner"],
          text=["Strays from a fort in the snow keep shooting at travellers. Storm the stray fort and take its banner."],
          tasks=[fight("minecraft:stray", 8, "nova_structures:stray_fort", "Fort Strays", "Storm the fort and drive off the strays"),
                 search("nova_structures:stray_fort", 1, "the Stray Fort Banner", "A frosted banner, nailed up in the hall.",
                        texture="minecraft:item/white_banner", title="Take down the fort's banner")],
          rewards=[reward_item("minecraft:tipped_arrow", 16), skill("defense", 300)]),

    quest("thorn_shrine", "The Thornborn Towers", icon="artifacts:thorn_pendant", after=["stray_fort"],
          signature="artifacts:thorn_pendant",
          text=["A shrine choked by thorns has become a nest. Fight through the Thornborn Towers and clear what lives "
                "inside. A pendant of thorns lies on the altar."],
          tasks=[fight("minecraft:spider", 8, "dungeons_arise:thornborn_towers", "Thorn Nest", "Clear the nest from the thorned shrine"),
                 search("dungeons_arise:thornborn_towers", 1, "the Shrine Offering", "An offering on the altar, wound in thorns.",
                        title="Search the altar for what the thorns guard")],
          rewards=[reward_item("artifacts:thorn_pendant"), skill("defense", 340)]),

    quest("lightning_tower", "Struck Again", icon="artifacts:shock_pendant", after=["build_walls"],
          signature="artifacts:shock_pendant",
          text=["The engineers' tower that draws lightning away from a village has burnt out. Replace its copper "
                "lightning rods while bolts keep striking, with a copper golem's help."],
          tasks=[item("minecraft:lightning_rod", 2, title="Bring copper lightning rods to replace the burnt ones"),
                 enc(["Bzzt. I steady the ladder. You fit the rods."], entity="friendsandfoes:copper_golem",
                     name="Tower Copper Golem", title="Meet the copper golem that helps at the tower"),
                 {"build": {"blocks": {"minecraft:lightning_rod": 2}, "radius": 10}, "title": "Fit the new rods at the top"},
                 {"timed": {"seconds": 90, "goal": {"hold": {"radius": 10}},
                            "lines": ["Bolts are striking. Stay on the tower!"], "start": "Brave the storm"},
                  "title": "Stay on the tower while bolts keep striking"}],
          rewards=[reward_item("artifacts:shock_pendant"), skill("defense", 350)]),

    quest("sea_raiders", "Raiders from the Sea", icon="minecraft:white_banner", after=["thorn_shrine"],
          text=["Coastal villages are raided from the water. Sail out and take the pillager ship that launches the "
                "raids."],
          tasks=[fight("minecraft:pillager", 10, "towns_and_towers:pillager_outpost_ocean", "Sea Raiders",
                       "Take the raiders' ship at sea", wave=5)],
          rewards=[reward_item("minecraft:white_banner", name="Ominous Banner", lore=["Taken from the raiders' ship."]),
                   skill("defense", 400)]),
]

chapter("skill_defense", "The Village Watch", "Defense path", "minecraft:shield", "skills", 8, Q + ACT2)
