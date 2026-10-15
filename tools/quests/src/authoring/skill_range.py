"""Chapter: skill_range, the Hunters' Lodge path: prologue and Act I (first release).
Plan: src/plans/quests/skill_range.json. Huntmistress Orla Vance and Old Tobiah keep the lodge on the hill west of Reece."""
from common import chapter, quest, talk_char, talk_org, item, reward_item, skill, encounter

Q = [
    quest("lodge_oath", "Bow and Oath", icon="minecraft:bow",
          text=["Huntmistress Vance won't take a hunter who can't make their own gear. Craft a bow and a quiver's "
                "worth of arrows, then swear the lodge oath at the hunters' lodge on the hill west of Reece."],
          tasks=[item("minecraft:bow", crafted=True), item("minecraft:arrow", 32),
                 talk_char("orla", ["A bow you made yourself. Good. The lodge has one oath.", "Never waste a kill. Say it, and you're one of us."])],
          rewards=[reward_item("minecraft:lead", name="Lodge Armband", lore=["Worn by hunters of the lodge."]),
                   reward_item("minecraft:arrow", 16), skill("range", 50)]),

    quest("first_tracks", "First Tracks", icon="naturalist:antler", after=["lodge_oath"],
          text=["A fletcher shows you how to follow hoof prints through the woods. Track a deer, and take venison "
                "and an antler."],
          tasks=[talk_org("hunters", ["Deep at the front: walking, not running. Follow quietly, downwind.", "Bring back the venison. The antler's for the lodge wall."]),
                 item("naturalist:venison", 2),
                 {"drop": {"from": ["naturalist:deer"], "chance": 0.4, "item": "naturalist:antler"}}],
          rewards=[reward_item("minecraft:leather", 8), skill("range", 80)]),

    quest("target_practice", "Bullseye", icon="minecraft:target", after=["lodge_oath"],
          text=["At the lodge's range, put ten arrows into target blocks at longer and longer distances."],
          tasks=[item("minecraft:target", 3, crafted=True, title="Make three target blocks"),
                 {"checkmark": "I put ten arrows into the targets"}],
          rewards=[reward_item("minecraft:arrow", 32), reward_item("minecraft:iron_ingot", 4), skill("range", 80)]),

    quest("boar_trouble", "Tusks in the Turnips", icon="naturalist:bushmeat", after=["first_tracks"],
          text=["Wild boars are tearing up a village's fields. Hunt down the sounder before it ruins the harvest, "
                "and keep the bushmeat."],
          tasks=[{"structure": "#villages", "title": "Reach the troubled village"},
                 {"kill": "naturalist:boar", "count": 4, "title": "Drive the sounder off the fields", "spawn": {"at": {"structure": "#villages"}}}, item("naturalist:bushmeat", 3)],
          rewards=[reward_item("naturalist:cooked_bushmeat", 8), skill("range", 120)]),

    quest("throwing_steel", "Thrown Steel", icon="spartanweaponry:iron_throwing_knife", after=["target_practice"],
          text=["Old Tobiah swears by thrown weapons, and by never whistling in a forest. Craft iron throwing "
                "knives, a tomahawk and javelins, and put them to use."],
          tasks=[item("spartanweaponry:iron_throwing_knife", crafted=True),
                 item("spartanweaponry:iron_tomahawk", crafted=True),
                 item("spartanweaponry:iron_javelin", crafted=True),
                 {"kill": "minecraft:zombie", "count": 6, "title": "Make kills with your thrown steel"}],
          rewards=[reward_item("spartanweaponry:copper_boomerang"), skill("range", 150)]),

    quest("firewatch", "The Lookout", icon="minecraft:spyglass", after=["boar_trouble"],
          text=["The lodge keeps a lookout in a firewatch tower deep in the forest. Climb it, meet the watcher and "
                "mark three game trails from the top."],
          tasks=[{"structure": "#firewatch_towers", "title": "Climb the firewatch tower"},
                 encounter(["Welcome up! Deer east, boar by the stream, something big north.", "Mark them. The lodge wants the map."],
                           entity="minecraft:villager", name="Tower Watcher", where={"above_y": 60}),
                 {"search": {"at": {"structure": "#firewatch_towers"}, "count": 1,
                             "item": {"name": "Watcher's Trail Map", "tooltip": "Three game trails, inked from the top",
                                      "texture": "minecraft:item/map"},
                             "found": "The watcher's old trail map, three game trails inked on it."},
                  "title": "Take the watcher's trail map from the tower"}],
          rewards=[reward_item("minecraft:spyglass"), skill("range", 150)]),

    quest("longbow", "The Longbow", icon="spartanweaponry:iron_longbow", after=["firewatch"],
          text=["From the tower, the watcher points out a deer far below. Craft a longbow and drop it with one "
                "shot from the top, before it wanders off."],
          tasks=[item("spartanweaponry:iron_longbow", crafted=True), {"structure": "#firewatch_towers"},
                 {"timed": {"seconds": 180, "goal": {"kill": "naturalist:deer", "count": 1},
                            "lines": ["There. Far below. You won't get long.", "One good shot."],
                            "start": "Take the shot", "no": ["teleport"]}, "title": "Drop the deer in three minutes"}],
          rewards=[reward_item("minecraft:arrow", 32), reward_item("minecraft:spectral_arrow", 8),
                   skill("range", 180)]),

    quest("silent_camp", "The Silent Camp", icon="alexsmobs:bear_fur", after=["firewatch"],
          text=["A hunting party's camp has gone quiet. Find it, follow the claw marks and rescue the last hunter "
                "from the tree where a grizzly bear has kept him for two days."],
          tasks=[{"structure": "#camps", "title": "Find the silent camp"},
                 encounter(["Grrrrr!"], then="kill", entity="alexsmobs:grizzly_bear", name="Camp Grizzly",
                           health=60, glow=True),
                 encounter(["Is it gone? Two days up this tree! Thank you, friend.", "Tell the lodge I'm alive."],
                           entity="minecraft:villager", name="Stranded Hunter")],
          rewards=[reward_item("alexsmobs:bear_fur", 2), skill("range", 220)]),

    quest("odd_coats", "Odd Coats", icon="minecraft:spider_eye", after=["throwing_steel"],
          text=["The lodge collects strange pelts and bones. Bring down odd-looking zombies, spiders and skeletons "
                "with arrows, and bring proof of each."],
          tasks=[{"drop": {"from": ["minecraft:zombie"], "chance": 0.15,
                           "item": {"name": "Odd Hide", "tooltip": "Proof for the lodge",
                                    "texture": "minecraft:item/rotten_flesh"}}, "consume": False},
                 {"drop": {"from": ["minecraft:spider"], "chance": 0.15,
                           "item": {"name": "Odd Fang", "tooltip": "Proof for the lodge",
                                    "texture": "minecraft:item/spider_eye"}}, "consume": False},
                 {"drop": {"from": ["minecraft:skeleton"], "chance": 0.15,
                           "item": {"name": "Odd Bone", "tooltip": "Proof for the lodge",
                                    "texture": "minecraft:item/bone"}}, "consume": False}],
          rewards=[reward_item("minecraft:spectral_arrow", 16), reward_item("minecraft:arrow", 32),
                   skill("range", 200)]),

    quest("heavy_crossbow", "Bolts at Night", icon="spartanweaponry:iron_heavy_crossbow",
          after=["odd_coats", "main_story:act1_start"],
          text=["Some nights call for a heavier weapon. Craft a heavy crossbow and bolts and drop twenty skeletons "
                "before dawn."],
          tasks=[item("spartanweaponry:iron_heavy_crossbow", crafted=True), item("spartanweaponry:bolt", 32),
                 {"kill": "minecraft:skeleton", "count": 20, "title": "Hold the night: drop twenty skeletons"}],
          rewards=[reward_item("spartanweaponry:bolt", 32), skill("range", 280)]),
]

chapter("skill_range", "The Hunters' Lodge", "Range path", "minecraft:bow", "skills", 7, Q)
