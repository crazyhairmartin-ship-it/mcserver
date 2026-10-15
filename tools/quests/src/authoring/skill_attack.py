"""Chapter: skill_attack, the Bounty Office path: prologue and Act I (first release).
Plan: src/plans/quests/skill_attack.json. Corvin Ash runs the office from Reece; contracts, a dead hunter's journal."""
from common import chapter, quest, talk_char, item, reward_item, skill, encounter
from common import enc, fight, boss, search, sample, talk_org, talk_villager, talk_char, item, reward_item, skill, encounter, giver_org  # noqa: F401

Q = [
    quest("the_board", "Wanted", icon="bountiful:bountyboard",
          text=["Bounty Master Corvin Ash posts the office's work on boards in the villages. Find a board and take "
                "your first contract from it."],
          tasks=[talk_char("corvin", ["You want work. Find a bounty board and take a contract.", "Don't take one you can't finish. I've buried hunters who did."]),
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
                 talk_char("corvin", ["A longsword. Honest steel. Wear it where you can draw it fast.", "Every scar on me came from a blade I reached for too late."])],
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
                 {"kill": "minecraft:zombie", "count": 8, "title": "Clear the dead out of the cellar", "spawn": {"at": {"structure": "#yungs_dungeons"}}},
                 {"kill": "minecraft:skeleton", "count": 8, "title": "Clear the bones out of the cellar", "spawn": {"at": {"structure": "#yungs_dungeons"}}}],
          rewards=[reward_item("minecraft:iron_ingot", 8), reward_item("minecraft:gold_ingot", 4),
                   reward_item("minecraft:emerald", 4), skill("attack", 200)]),

    quest("spider_queen", "Silk and Venom", icon="minecraft:spider_eye", after=["dungeon_sweep"],
          text=["A spider dungeon has been sending its brood into the fields. Clear it, and cut the poison sac "
                "from its biggest spider as proof."],
          tasks=[{"structure": "betterdungeons:spider_dungeon", "title": "Find the spider dungeon"},
                 {"kill": "minecraft:cave_spider", "count": 12, "title": "Clear out the brood", "spawn": {"at": {"structure": "betterdungeons:spider_dungeon"}}},
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
                 {"kill": "minecraft:zombie", "count": 8, "title": "Put the risen back in the ground", "spawn": {"at": {"structure": "#graveyards"}}},
                 {"kill": "minecraft:skeleton", "count": 7, "title": "Put the walking bones back in the ground", "spawn": {"at": {"structure": "#graveyards"}}}],
          rewards=[reward_item("minecraft:enchanted_book", name="Rest Easy", enchant={"minecraft:smite": 3}),
                   skill("attack", 240)]),

    quest("feral_bounty", "The Mauler", icon="artifacts:feral_claws", after=["spider_queen"],
          signature="artifacts:feral_claws",
          text=["A beast-tamer's bounty: a mauler, small, fast and all teeth, has been savaging travellers in the "
                "badlands. Find it, survive its rush, and the tamer's feral claws are your pay."],
          tasks=[encounter(["Grrrrk!"], then="kill", entity="friendsandfoes:mauler", name="The Mauler", health=40,
                           glow=True, where={"biomes": ["minecraft:badlands", "minecraft:eroded_badlands",
                                                    "minecraft:wooded_badlands"]})],
          rewards=[reward_item("artifacts:feral_claws"), skill("attack", 300)]),
]

ACT2 = [
    quest("bandit_towers", "Bandit Country", icon="bountiful:bounty-uncommon",
          after=["graveyard_shift", "main_story:act2_start"],
          text=["An uncommon bounty: illager bandits have built towers over a trade road. Take them down and claim "
                "their banner as proof."],
          tasks=[fight("minecraft:pillager", 8, "dungeons_arise:bandit_towers", "Tower Bandits",
                       "Take the bandits down for the trade road's merchants"),
                 search("dungeons_arise:bandit_towers", 1, "Bandit Banner", "A bandit banner, torn from a tower wall.",
                        texture="minecraft:item/white_banner", title="Claim a banner as proof for the bounty")],
          rewards=[reward_item("bountiful:bounty-uncommon"), skill("attack", 250)]),

    quest("skelewag", "Wanted: the Skelewag", icon="alexsmobs:skelewag_sword", after=["feral_bounty"],
          text=["Sailors want a skelewag dead, a skeletal pirate fish that rams boats over shipwrecks. Hunt it in "
                "the water and take its sword as proof."],
          tasks=[{"structure": "#shipwrecks", "title": "Find the wreck the skelewag rams boats over"},
                 fight("alexsmobs:skelewag", 1, "#shipwrecks", "The Skelewag", "Kill the skelewag that sinks the sailors' boats",
                       wave=1),
                 item("alexsmobs:skelewag_sword", title="Take its sword as proof")],
          rewards=[reward_item("alexsmobs:skelewag_sword"), skill("attack", 280)]),

    quest("witch_hunt", "Witch Hunt", icon="minecraft:witch_spawn_egg", after=["bandit_towers"],
          text=["A village blames a witch for its sick cattle. Track her to her swamp hut, defeat her and bring "
                "back her hat as proof."],
          tasks=[{"structure": "#witch_huts", "title": "Track the witch to her hut"},
                 fight("minecraft:witch", 1, "#witch_huts", "The Cattle Witch", "Defeat the witch blamed for the sick cattle",
                       wave=1),
                 sample("the Witch's Hat", ["minecraft:witch"], 0.7, texture="minecraft:item/leather_helmet",
                        tooltip="Proof for the village")],
          rewards=[reward_item("minecraft:splash_potion", 3), skill("attack", 280)]),

    quest("arena_ladder", "The Arena Ladder", icon="artifacts:power_glove", after=["bandit_towers"],
          signature="artifacts:power_glove",
          text=["An arena's master runs a ladder: win three fights in a row against rising waves, without leaving "
                "the sand. The champion's power glove goes to whoever finishes."],
          tasks=[fight("minecraft:skeleton", 6, "#arenas", "Arena Challengers", "Win the first bout on the sand"),
                 fight("minecraft:vindicator", 4, "#arenas", "Arena Champions", "Win the second bout against tougher fighters"),
                 fight("minecraft:ravager", 1, "#arenas", "The Arena Beast", "Win the final bout against the beast", wave=1)],
          rewards=[reward_item("artifacts:power_glove"), skill("attack", 350)]),

    quest("cliff_nest", "Knock Them Down", icon="artifacts:pocket_piston", after=["skelewag"],
          signature="artifacts:pocket_piston",
          text=["Something nests high in an aviary, swooping on anyone below. Climb up and clear it the quick way: "
                "knock its occupants off the edge. A piston-spring trinket waits at the top."],
          tasks=[fight("minecraft:vex", 6, "dungeons_arise:aviary", "Aviary Nesters", "Clear the nesters off the aviary's tiers"),
                 search("dungeons_arise:aviary", 1, "the Aviary Trinket", "A spring-loaded trinket, left at the top.",
                        texture="minecraft:item/piston", title="Search the top for the piston-spring trinket")],
          rewards=[reward_item("artifacts:pocket_piston"), skill("attack", 300)]),

    quest("weapon_master", "Master of Arms", icon="spartanweaponry:diamond_halberd", after=["arena_ladder"],
          text=["Ash says a hunter should master more than one weapon. Make a halberd, a rapier, a warhammer and a "
                "javelin, then put them through their paces on the dead."],
          tasks=[talk_char("corvin", ["Four weapons, four lessons. A hunter who knows one is a hunter who dies.",
                                      "Make them. Use them. Then I'll believe you."],
                           title="Hear Ash's drill"),
                 item("spartanweaponry:iron_halberd", crafted=True, title="Forge a halberd"),
                 item("spartanweaponry:iron_rapier", crafted=True, title="Forge a rapier"),
                 item("spartanweaponry:iron_warhammer", crafted=True, title="Forge a warhammer"),
                 item("spartanweaponry:iron_javelin", crafted=True, title="Forge a javelin"),
                 {"kill": "minecraft:zombie", "count": 12, "title": "Put each weapon through its paces on the dead"}],
          rewards=[reward_item("spartanweaponry:diamond_halberd"), skill("attack", 380)]),

    quest("hunter_trail", "The Hunter's Trail", icon="minecraft:writable_book", after=["weapon_master"],
          text=["The dead hunter's journal names three more of their old haunts. Find other fallen adventurers along "
                "the trail, and piece together who they were hunting."],
          tasks=[{"observe": "realmrpg_skeletons:explorer_skeleton", "ticks": 20, "title": "Find the explorer's remains"},
                 {"observe": "realmrpg_skeletons:slain_skeleton", "ticks": 20, "title": "Find the slain hunter's remains"},
                 {"observe": "realmrpg_skeletons:shot_skeleton", "ticks": 20, "title": "Find the hunter shot down on the trail"}],
          rewards=[reward_item("minecraft:writable_book", name="A Hunter's Compass Page",
                               lore=["Torn from a dead hunter's journal."]), skill("attack", 400)]),
]

chapter("skill_attack", "The Bounty Office", "Attack path", "minecraft:iron_sword", "skills", 6, Q + ACT2)
