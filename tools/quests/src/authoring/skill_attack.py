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
          rewards=[reward_item("bountiful:decree"), skill("attack", 50)]),

    quest("dummy_drills", "Drills on the Dummy", icon="dummmmmmy:target_dummy", after=["the_board"],
          text=["No hunter goes out untrained. Make a target dummy, then hit it hard and fast for a minute."],
          tasks=[item("dummmmmmy:target_dummy", crafted=True),
                 {"timed": {"seconds": 60, "goal": {"stat": "minecraft:damage_dealt", "count": 600},
                            "lines": ["Sixty seconds. Hit the dummy.", "Combos, not flailing. Go."],
                            "start": "Start the drill"}, "title": "Deal the damage in a minute"}],
          rewards=[reward_item("minecraft:enchanted_book", enchant={'minecraft:sharpness': 2}), skill("attack", 80)]),

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
                               lore=["A dead hunter's notes. The last page is unfinished."]), reward_item("minecraft:enchanted_book", enchant={'minecraft:smite': 3}), skill("attack", 150)]),

    quest("dungeon_sweep", "Clearing the Cellar", icon="minecraft:spawner", after=["fallen_adventurer"],
          text=["The journal points to a dungeon below a village. Go down and clear it."],
          tasks=[{"structure": "#yungs_dungeons", "title": "Find the dungeon"},
                 {"kill": "minecraft:zombie", "count": 8, "title": "Clear the dead out of the cellar", "spawn": {"at": {"structure": "#yungs_dungeons"}}},
                 {"mine": "minecraft:spawner", "title": "Break the dungeon's spawner so it stays clear"},
                 {"kill": "minecraft:skeleton", "count": 8, "title": "Clear the bones out of the cellar", "spawn": {"at": {"structure": "#yungs_dungeons"}}}],
          rewards=[reward_item("minecraft:enchanted_book", enchant={'minecraft:smite': 3}), reward_item("minecraft:emerald", 4), skill("attack", 200)]),

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
    quest("bandit_towers", "Bandit Country", icon="bountiful:bounty",
          after=["graveyard_shift", "main_story:act2_start"],
          text=["An uncommon bounty: illager bandits have built towers over a trade road. Take them down and claim "
                "their banner as proof."],
          tasks=[fight("minecraft:pillager", 8, "dungeons_arise:bandit_towers", "Tower Bandits",
                       "Take the bandits down for the trade road's merchants"),
                 search("dungeons_arise:bandit_towers", 1, "Bandit Banner", "A bandit banner, torn from a tower wall.",
                        texture="alexsmobs:item/end_pirate_flag", title="Claim a banner as proof for the bounty")],
          rewards=[reward_item("minecraft:emerald", 12), skill("attack", 250)]),

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
          rewards=[reward_item("irons_spellbooks:greater_healing_potion", 2), skill("attack", 280)]),

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
                        texture="minecraft:block/piston_side", title="Search the top for the piston-spring trinket")],
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
                 {"killwith": "minecraft:zombie", "with": "spartanweaponry:iron_halberd", "count": 3, "title": "Make a kill with the halberd"},
                 {"killwith": "minecraft:zombie", "with": "spartanweaponry:iron_rapier", "count": 3, "title": "Make a kill with the rapier"},
                 {"killwith": "minecraft:zombie", "with": "spartanweaponry:iron_warhammer", "count": 3, "title": "Make a kill with the warhammer"},
                 {"killwith": "minecraft:zombie", "with": ["spartanweaponry:iron_javelin", "spartanweaponry:javelin"], "count": 3, "title": "Make a kill with the javelin"}],
          rewards=[reward_item("spartanweaponry:diamond_halberd"), skill("attack", 380)]),

    quest("hunter_trail", "The Hunter's Trail", icon="minecraft:writable_book", after=["weapon_master"],
          text=["The dead hunter's journal names three more of their old haunts. Find other fallen adventurers along "
                "the trail, and piece together who they were hunting."],
          tasks=[{"observe": "realmrpg_skeletons:explorer_skeleton", "ticks": 20, "title": "Find the explorer's remains"},
                 {"observe": "realmrpg_skeletons:slain_skeleton", "ticks": 20, "title": "Find the slain hunter's remains"},
                 {"observe": "realmrpg_skeletons:shot_skeleton", "ticks": 20, "title": "Find the hunter shot down on the trail"}],
          rewards=[reward_item("minecraft:writable_book", name="A Hunter's Compass Page",
                               lore=["Torn from a dead hunter's journal."]), reward_item("minecraft:enchanted_book", enchant={'minecraft:looting': 2}), skill("attack", 400)]),
]

ACT3 = [
    quest("fortress_contract", "Epic Contract: the Fortress", icon="bountiful:bounty",
          after=["hunter_trail", "main_story:act3_start"],
          text=["An epic bounty from the board: wither skeletons have overrun a Nether fortress. Kill twenty and "
                "bring three skulls as proof."],
          tasks=[{"structure": "betterfortresses:fortress", "title": "Find the overrun Nether fortress"},
                 fight("minecraft:wither_skeleton", 20, "betterfortresses:fortress", "Overrunning Skeletons", "Cull the fortress's wither skeletons", wave=5),
                 item("minecraft:wither_skeleton_skull", 3, title="Bring three skulls as proof")],
          rewards=[reward_item("minecraft:enchanted_book", enchant={"minecraft:looting": 3}), skill("attack", 450)]),

    quest("brute_force", "Brute Force", icon="minecraft:piglin_brute_spawn_egg", after=["fortress_contract"],
          text=["Piglin brutes guard a bastion's treasure room. A rare bounty wants five of them dead, without golden "
                "armour to hide behind."],
          tasks=[fight("minecraft:piglin_brute", 5, "minecraft:bastion_remnant", "Treasure-Room Brutes", "Put down five brutes guarding the treasure room")],
          rewards=[reward_item("minecraft:enchanted_book", enchant={"minecraft:sharpness": 4}), skill("attack", 480)]),

    quest("fire_bounty", "The Burning Revenant", icon="artifacts:fire_gauntlet", after=["fortress_contract"],
          signature="artifacts:fire_gauntlet",
          text=["A fire-wreathed revenant guards the soul blacksmith's forge in the Nether. Defeat the ignited "
                "revenant and take the smith's fire gauntlet it was protecting."],
          tasks=[{"structure": "cataclysm:soul_black_smith", "title": "Find the soul blacksmith's forge"},
                 boss("cataclysm:ignited_revenant", "cataclysm:soul_black_smith", "The Ignited Revenant", "Defeat the ignited revenant at the forge")],
          rewards=[reward_item("artifacts:fire_gauntlet"), skill("attack", 520)]),

    quest("vampire_crypt", "The Pale Count", icon="artifacts:vampiric_glove", after=["hunter_trail"],
          signature="artifacts:vampiric_glove",
          text=["The trail ends at an undead crypt: the dead hunter was after a vampire noble. Go in at night, "
                "defeat the Pale Count, and take the hunter's own glove, which drinks life from every blow."],
          tasks=[{"structure": "nova_structures:undead_crypt", "title": "Find the crypt the hunter's trail ends at"},
                 boss("minecraft:vindicator", "nova_structures:undead_crypt", "The Pale Count", "Defeat the Pale Count at night", health=80),
                 search("nova_structures:undead_crypt", 1, "the Hunter's Glove", "A glove, stiff with old blood.",
                        texture="minecraft:item/leather", title="Take the hunter's glove from the crypt")],
          rewards=[reward_item("artifacts:vampiric_glove"), skill("attack", 540)]),

    quest("laid_to_rest", "Laid to Rest", icon="minecraft:writable_book", after=["vampire_crypt"],
          text=["Bring the dead hunter's journal back to Corvin Ash. He knew them, and finally tells you why he "
                "stopped hunting."],
          tasks=[talk_char("corvin", ["That's their hand. They were my partner. I stopped when they didn't come back.",
                                      "Take my old badge. Hunt better than I did."],
                           title="Bring the dead hunter's journal to Corvin Ash")],
          rewards=[reward_item("minecraft:iron_ingot", name="Ash's Old Badge", lore=["Worn through forty contracts."]), skill("attack", 550)]),
]

ACT4 = [
    quest("coliseum", "Champion of the Coliseum", icon="minecraft:netherite_sword",
          after=["arena_ladder", "laid_to_rest", "main_story:act4_start"],
          text=["The great coliseum holds the hardest ladder of all. Fight to the top with netherite and a Spartan "
                "weapon you've mastered."],
          tasks=[{"structure": "dungeons_arise:coliseum", "title": "Enter the great coliseum"},
                 fight("minecraft:vindicator", 10, "dungeons_arise:coliseum", "Coliseum Champions", "Win the early rounds of the ladder", wave=5),
                 fight("minecraft:ravager", 2, "dungeons_arise:coliseum", "Coliseum Beasts", "Win the beast round at the top", wave=1)],
          rewards=[{"choice": [reward_item("spartanweaponry:netherite_longsword", name="Champion's Blade", lore=['Won on the sand, not given.'], enchant={'minecraft:sharpness': 4, 'minecraft:unbreaking': 3}), reward_item("spartanshields:netherite_basic_shield", name="Champion's Shield", lore=['The crowd chanted behind it.'], enchant={'minecraft:unbreaking': 3}), reward_item("spartanweaponry:netherite_battle_hammer", name="Champion's Hammer", lore=['Ended the last round in one.'], enchant={'minecraft:sharpness': 4, 'minecraft:unbreaking': 3})], "title": "Choose one"}, skill("attack", 700)]),

    quest("plague_asylum", "The Plague Asylum", icon="bountiful:bounty", after=["coliseum"],
          text=["Nobody who goes into the plague asylum comes out. A legendary bounty is posted on whatever lives "
                "there. Clear it."],
          tasks=[{"structure": "dungeons_arise:plague_asylum", "title": "Enter the plague asylum"},
                 fight("minecraft:zombie_villager", 12, "dungeons_arise:plague_asylum", "Asylum Sick", "Clear what lives in the asylum", wave=6)],
          rewards=[reward_item("minecraft:enchanted_book", enchant={"minecraft:smite": 5}), reward_item("minecraft:emerald", 24), skill("attack", 740)]),

    quest("void_contract", "Contract in the Void", icon="minecraft:shulker_shell", after=["plague_asylum"],
          text=["Even the End gets bounties. Clear an End city's towers of shulkers and endermen for a client who "
                "won't give their name."],
          tasks=[{"structure": "minecraft:end_city", "title": "Find the End city on the contract"},
                 fight("minecraft:shulker", 4, "minecraft:end_city", "Tower Shulkers", "Clear the towers of shulkers", wave=2),
                 fight("minecraft:enderman", 4, "minecraft:end_city", "City Endermen", "Clear the streets of endermen", wave=2)],
          rewards=[reward_item("minecraft:shulker_shell", 4), skill("attack", 780)]),
]

ACT5 = [
    quest("cursed_contracts", "The Cursed Contracts", icon="cataclysm:witherite_ingot", after=["void_contract", "main_story:act5_start"],
          text=["Three wanted posters in Ash's own hand: the Prowler in the Ancient Factory, the Ender Golem at the "
                "Ruined Citadel and the Coralssus in the Sunken City."],
          tasks=[fight("cataclysm:the_prowler", 1, "cataclysm:ancient_factory", "The Factory Prowler", "Take down the Prowler in the Ancient Factory", wave=1),
                 fight("cataclysm:ender_golem", 1, "cataclysm:ruined_citadel", "The Citadel Golem", "Take down the Ender Golem at the Ruined Citadel", wave=1),
                 fight("cataclysm:coralssus", 1, "cataclysm:sunken_city", "The Coralssus", "Take down the Coralssus in the Sunken City", wave=1)],
          rewards=[reward_item("cataclysm:witherite_ingot", 2), reward_item("cataclysm:coral_chunk", 4), skill("attack", 850)]),

    quest("draugr_hunt", "Draugr Season", icon="cataclysm:black_steel_ingot", after=["cursed_contracts"],
          text=["The Frosted Prison's draugr walk the snows. Hunt a royal draugr and take its crown as proof."],
          tasks=[fight("cataclysm:royal_draugr", 1, "cataclysm:frosted_prison", "A Royal Draugr", "Hunt a royal draugr in the snows", wave=1),
                 sample("the Royal Draugr's Crown", ["cataclysm:royal_draugr"], 0.8, texture="minecraft:item/gold_ingot", tooltip="Proof for Ash")],
          rewards=[reward_item("cataclysm:black_steel_ingot", 4), skill("attack", 900)]),

    quest("ash_verdict", "The Last Contract", icon="spartanweaponry:netherite_longsword", after=["draugr_hunt"],
          text=["With every poster in the office torn down, Ash gives you the last one: his own name, retired. He "
                "hands over his blade and the office with it."],
          tasks=[talk_char("corvin", ["The last contract. My name, retired.", "Take the blade, and the office. Hunt well."],
                           title="Take Ash's last contract and his blade")],
          rewards=[{"choice": [reward_item("spartanweaponry:netherite_longsword", name="Ash's Verdict", lore=['Every contract, signed.'], enchant={'minecraft:sharpness': 5, 'minecraft:looting': 3, 'minecraft:fire_aspect': 2}, unbreakable=True), reward_item("spartanweaponry:netherite_battleaxe", name="Ash's Reckoning", lore=['For the debts nobody else would collect.'], enchant={'minecraft:sharpness': 5, 'minecraft:looting': 3}, unbreakable=True), reward_item("spartanweaponry:netherite_katana", name="Ash's Quiet Work", lore=['Quick enough that you hear it afterwards.'], enchant={'minecraft:sharpness': 5, 'minecraft:sweeping': 3}, unbreakable=True)], "title": "Choose one"}, skill("attack", 1000)]),
]

chapter("skill_attack", "The Bounty Office", "Attack path", "minecraft:iron_sword", "skills", 6, Q + ACT2 + ACT3 + ACT4 + ACT5)
