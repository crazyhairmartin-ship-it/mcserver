"""Chapter: skill_attack, the Bounty Office path: prologue and Act I (first release).
Plan: src/plans/quests/skill_attack.json. Corvin Ash runs the office from Reece; contracts, a dead hunter's journal."""
from common import chapter, quest, talk_char, item, reward_item, skill, encounter

Q = [
    quest("the_board", "Wanted", icon="bountiful:bountyboard",
          text=["Bounty Master Corvin Ash posts the office's work on boards in the villages. Find a board and take "
                "your first contract from it."],
          tasks=[talk_char("corvin", ["You want work. Good. Work pays.",
                                      "The office posts contracts on bounty boards. Every village has one.",
                                      "Find a board. Take a contract. Don't take one you can't finish.",
                                      "I've buried hunters who did."]),
                 {"structure": "#villages", "title": "Find a village's bounty board"},
                 item("bountiful:bounty", title="Take a contract from the board")],
          rewards=[reward_item("bountiful:bounty-common"), skill("attack", 50)]),

    quest("dummy_drills", "Drills on the Dummy", icon="dummmmmmy:target_dummy", after=["the_board"],
          text=["No hunter goes out untrained. Make a target dummy, then hit it hard and fast for a minute."],
          tasks=[item("dummmmmmy:target_dummy", crafted=True),
                 {"timed": {"seconds": 60, "goal": {"stat": "minecraft:damage_dealt", "count": 600},
                            "lines": ["Sixty seconds. Hit the dummy.", "Combos, not flailing. Go."],
                            "start": "Start the drill"}, "title": "Deal the damage in a minute"}],
          rewards=[reward_item("minecraft:iron_ingot", 4), skill("attack", 80)]),

    quest("first_contract", "Night Shift", icon="minecraft:zombie_head", after=["dummy_drills"],
          text=["The first proper contract: the outskirts of a village crawl with zombies of every odd variety. Put "
                "down fifteen."],
          tasks=[{"structure": "#villages", "title": "Reach a village"},
                 {"kill": "minecraft:zombie", "count": 15, "title": "Put down fifteen zombies"}],
          rewards=[reward_item("minecraft:bread", 8), reward_item("minecraft:emerald", 2), skill("attack", 120)]),

    quest("the_rascal", "The Thief in the Mine", icon="friendsandfoes:rascal_spawn_egg", after=["first_contract"],
          text=["A bounty on a 'thief' who robs miners. The thief is a rascal, and it is playing hide-and-seek in an "
                "old mineshaft. Find it three times and it will pay you off."],
          tasks=[{"structure": "#mines", "title": "Go into the mineshaft"},
                 encounter(["Hee hee! You found me!", "Again! Count to ten!"], entity="friendsandfoes:rascal",
                           name="Rascal", where={"below_y": 60}),
                 encounter(["Oh! You're good at this.", "One more. Go on, I dare you."],
                           entity="friendsandfoes:rascal", name="Rascal", where={"below_y": 60}),
                 encounter(["Found me again! Fine, fine. Take the shiny things.",
                            "I only borrowed them. Mostly."],
                           entity="friendsandfoes:rascal", name="Rascal", where={"below_y": 60})],
          rewards=[reward_item("minecraft:gold_ingot", 8), reward_item("minecraft:emerald", 6),
                   skill("attack", 160)]),

    quest("weapon_of_choice", "Weapon of Choice", icon="spartanweaponry:iron_longsword", after=["first_contract"],
          text=["Ash wants you to choose your style. Forge an iron Spartan weapon and wear it like a hunter."],
          tasks=[item("spartanweaponry:iron_longsword", crafted=True, title="Forge an iron Spartan weapon"),
                 talk_char("corvin", ["A longsword. Honest steel.",
                                      "Wear it where you can draw it fast. A weapon in your pack is a weapon you "
                                      "don't have.",
                                      "Every scar on me came from a blade I reached for too late."])],
          rewards=[reward_item("minecraft:grindstone"), reward_item("minecraft:iron_ingot", 6),
                   skill("attack", 180)]),

    quest("fallen_adventurer", "The Unfinished Contract", icon="minecraft:writable_book",
          after=["weapon_of_choice"],
          discover={"observe": "realmrpg_skeletons:hunted_skeleton", "ticks": 20},
          text=["You find the remains of a fallen bounty hunter with a contract still clutched in their bones. You "
                "read it, and you can see how it ends."],
          tasks=[{"checkmark": "I read the contract"}],
          rewards=[reward_item("minecraft:writable_book", name="The Hunter's Journal",
                               lore=["A dead hunter's notes. The last page is unfinished."]),
                   skill("attack", 150)]),

    quest("dungeon_sweep", "Clearing the Cellar", icon="minecraft:spawner", after=["fallen_adventurer"],
          text=["The journal points to a dungeon below a village. Go down and clear it."],
          tasks=[{"structure": "#yungs_dungeons", "title": "Find the dungeon"},
                 {"kill": "minecraft:zombie", "count": 8}, {"kill": "minecraft:skeleton", "count": 8}],
          rewards=[reward_item("minecraft:iron_ingot", 8), reward_item("minecraft:gold_ingot", 4),
                   reward_item("minecraft:emerald", 4), skill("attack", 200)]),

    quest("spider_queen", "Silk and Venom", icon="minecraft:spider_eye", after=["dungeon_sweep"],
          text=["A spider dungeon has been sending its brood into the fields. Clear it, and cut the poison sac "
                "from its biggest spider as proof."],
          tasks=[{"structure": "betterdungeons:spider_dungeon", "title": "Find the spider dungeon"},
                 {"kill": "minecraft:cave_spider", "count": 12},
                 {"drop": {"from": ["minecraft:spider"], "chance": 0.15,
                           "item": {"name": "Queen's Poison Sac", "tooltip": "Proof of the kill",
                                    "texture": "minecraft:item/spider_eye"}}, "consume": False}],
          rewards=[reward_item("minecraft:enchanted_book", name="Bane of the Brood",
                               enchant={"minecraft:bane_of_arthropods": 3}), skill("attack", 240)]),

    quest("graveyard_shift", "Graveyard Shift", icon="minecraft:bone",
          after=["dungeon_sweep", "main_story:act1_start"],
          text=["The dead won't stay down in an old graveyard. Spend a night there and put them back in the "
                "ground."],
          tasks=[{"structure": "#graveyards", "title": "Reach the graveyard"},
                 {"kill": "minecraft:zombie", "count": 8}, {"kill": "minecraft:skeleton", "count": 7}],
          rewards=[reward_item("minecraft:enchanted_book", name="Rest Easy", enchant={"minecraft:smite": 3}),
                   skill("attack", 240)]),

    quest("feral_bounty", "The Mauler", icon="artifacts:feral_claws", after=["spider_queen"],
          signature="artifacts:feral_claws",
          text=["A beast-tamer's bounty: a mauler, small, fast and all teeth, has been savaging travellers in the "
                "badlands. Find it, survive its rush, and the tamer's feral claws are your pay."],
          tasks=[encounter(["Grrrrk!"], then="kill", entity="friendsandfoes:mauler", name="The Mauler", health=40,
                           glow=True, where={"biomes": ["minecraft:badlands"]})],
          rewards=[reward_item("artifacts:feral_claws"), skill("attack", 300)]),
]

chapter("skill_attack", "The Bounty Office", "Attack path", "minecraft:iron_sword", "skills", 6, Q)
