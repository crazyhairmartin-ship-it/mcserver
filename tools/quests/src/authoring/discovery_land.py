"""Chapter: discovery_land, stumbling on strange places across the land (every tier except any).
Plan: src/plans/quests/discovery_land.json. Quests with a "discover" stay hidden until the player reaches the place; a
toast announces them. The tier-"any" quests are appended later (T08)."""
from common import chapter, quest, talk_org, item, reward_item, skill, encounter


def enc(lines, title=None, **spec):
    t = encounter(lines, **spec)
    if title:
        t["title"] = title
    return t


def fight(entity, count, at, name, title, wave=4, **extra):
    """Kill steps whose enemies come to the fight when the player is at the place."""
    spawn = {"at": {"structure": at}, "wave": wave, "name": name}
    spawn.update(extra)
    return {"kill": entity, "count": count, "spawn": spawn, "title": title}


def sample(name, from_mobs, chance, count=1, texture="minecraft:item/paper", tooltip="Needed for the job"):
    return {"drop": {"from": from_mobs, "chance": chance,
                     "item": {"name": name, "texture": texture, "tooltip": tooltip}},
            "count": count, "consume": False, "title": "Take " + name}


Q = [
    quest("bandit_toll_road", "The Toll Road", icon="spartanweaponry:iron_halberd",
          discover={"structure": "dungeons_arise:bandit_village"},
          text=["A bandit village sits on the road, and a merchant is held at its gate for a toll he cannot pay. "
                "Clear out the bandits and their leader, then walk him to safety."],
          tasks=[fight("minecraft:pillager", 8, "dungeons_arise:bandit_village", "Toll Bandits",
                       "Drive off the bandits holding the merchant"),
                 fight("minecraft:vindicator", 1, "dungeons_arise:bandit_village", "Bandit Leader",
                       "Defeat the bandit leader", wave=1),
                 enc(["They let me go? You actually... Thank you! Take me to a proper village, please."],
                     then="escort", entity="minecraft:villager", name="Freed Merchant",
                     to={"structure": "#villages", "label": "the nearest village"},
                     title="Walk the freed merchant to the nearest village")],
          rewards=[reward_item("spartanweaponry:iron_halberd"), reward_item("minecraft:emerald", 8),
                   skill("attack", 200)]),

    quest("bells_of_the_bandit_towers", "The Bandits' Ledger", icon="minecraft:writable_book",
          discover={"structure": "dungeons_arise:bandit_towers"},
          text=["The bandits who hold these towers keep a ledger of every caravan they've robbed, torn into pages and "
                "hidden among their stores so no one man can sell them out. Fight off the archers and find the "
                "pages: the villages they robbed will want to know."],
          tasks=[fight("minecraft:pillager", 6, "dungeons_arise:bandit_towers", "Tower Archers",
                       "Fight off the archers on the walkways"),
                 {"search": {"at": {"structure": "dungeons_arise:bandit_towers"}, "count": 3,
                             "item": {"name": "Ledger Page", "tooltip": "A page of the bandits' accounts",
                                      "texture": "minecraft:item/paper"},
                             "found": "Under the sacks you find a torn ledger page."},
                  "title": "Find the three ledger pages in the bandits' stores"}],
          rewards=[reward_item("minecraft:arrow", 48), reward_item("minecraft:emerald", 4), skill("range", 200)]),

    quest("the_great_cage", "The Great Cage", icon="minecraft:parrot_spawn_egg",
          discover={"structure": "dungeons_arise:aviary"},
          text=["A giant aviary stands open on the mountainside with its keepers long gone. Birds are still caged "
                "inside, and they will starve."],
          tasks=[fight("minecraft:vex", 5, "dungeons_arise:aviary", "Aviary Nesters",
                       "Clear the nesters off the upper tiers"),
                 {"tame": "minecraft:parrot", "count": 3, "title": "Free and befriend three caged birds"}],
          rewards=[reward_item("domesticationinnovation:collar_tag"), reward_item("minecraft:feather", 16),
                   skill("taming", 260)]),

    quest("steam_and_shadows", "Steam and Shadows", icon="supplementaries:soap",
          discover={"structure": "dungeons_arise:bathhouse"},
          text=["The bathhouse's pools still steam, and something lurks under the water. Someone drowned here, and "
                "the bath master's ledger says who and why."],
          tasks=[fight("minecraft:drowned", 6, "dungeons_arise:bathhouse", "Bathhouse Drowned",
                       "Clear the drowned from the pools"),
                 sample("the Bath Master's Ledger", ["minecraft:drowned"], 0.5, texture="minecraft:item/book")],
          rewards=[reward_item("supplementaries:soap", 2), reward_item("minecraft:bread", 8), skill("defense", 180)]),

    quest("the_cold_forge", "The Foundry's Last Blueprint", icon="spartanshields:iron_tower_shield",
          discover={"structure": "dungeons_arise:foundry"},
          text=["The foundry's furnaces have gone cold but its guardians still walk the floor, keeping the master "
                "smith's plans. Take the plans, and forge what they describe."],
          tasks=[fight("minecraft:iron_golem", 4, "dungeons_arise:foundry", "Foundry Guardians",
                       "Fight past the foundry's guardians", wave=2),
                 sample("the Master Smith's Plans", ["minecraft:iron_golem"], 0.6, texture="minecraft:item/map"),
                 item("spartanshields:iron_tower_shield", crafted=True, title="Forge the shield the plans describe")],
          rewards=[reward_item("minecraft:iron_block", 4), reward_item("spartanshields:iron_tower_shield"),
                   skill("craft", 300)]),

    quest("siege_of_keep_kayra", "The Siege of Keep Kayra", icon="spartanweaponry:diamond_longsword",
          discover={"structure": "dungeons_arise:keep_kayra"},
          text=["Keep Kayra's garrison went mad and still holds its walls. Fight up through the gatehouse to the "
                "lord of the keep, then hold his throne room against the last of his men."],
          tasks=[fight("minecraft:vindicator", 10, "dungeons_arise:keep_kayra", "Mad Garrison",
                       "Fight up through the gatehouse and towers", wave=5),
                 fight("minecraft:vindicator", 1, "dungeons_arise:keep_kayra", "Lord of the Keep",
                       "Defeat the keep's mad lord", wave=1, ensure=True),
                 {"timed": {"seconds": 180, "goal": {"hold": {"radius": 16}},
                            "waves": [{"entity": "minecraft:vindicator", "count": 3, "every": 30}],
                            "lines": ["His last men are coming. Hold the throne room!"], "start": "Hold the throne room"},
                  "title": "Hold the throne room against his last wave"}],
          rewards=[reward_item("spartanweaponry:diamond_longsword", name="Kayra's Edge",
                               lore=["Taken from the mad lord's hand."], enchant={"minecraft:sharpness": 3}),
                   reward_item("minecraft:white_banner", name="Banner of Keep Kayra"), skill("defense", 500)]),

    quest("clockwork_hive", "The Clockwork Hive", icon="minecraft:redstone_block",
          discover={"structure": "dungeons_arise:mechanical_nest"},
          text=["The mechanical nest hums with things that aren't quite alive. Its guardians carry a mainspring: "
                "the heart of the hive. A Crafters' guild mason would very much like to study it."],
          tasks=[fight("minecraft:iron_golem", 4, "dungeons_arise:mechanical_nest", "Hive Guardians",
                       "Hunt the hive's guardians", wave=2),
                 sample("a Mainspring", ["minecraft:iron_golem"], 0.5, texture="minecraft:item/clock_00",
                        tooltip="The heart of the hive"),
                 talk_org("crafters", ["A mainspring? From the hive itself? Let me see.",
                                       "Beautiful. Dreadful. Whoever made this had patience.",
                                       "The guild will pay you for the loan, and I'll write up what it does."],
                          title="Show the mainspring to a Crafters' guild mason")],
          rewards=[reward_item("minecraft:redstone_block", 4), reward_item("minecraft:copper_block", 8),
                   skill("craft", 300)]),

    quest("asylum_samples", "Samples from the Asylum", icon="herbalbrews:lavender_tea",
          discover={"structure": "dungeons_arise:plague_asylum"},
          text=["The plague asylum's wards still hold the sick and what feeds on them. The Herbalists want samples "
                "from its apothecary, and a cure brewed from the notes."],
          tasks=[sample("an Asylum Sample", ["minecraft:zombie_villager"], 0.4, count=3,
                        texture="minecraft:item/glass_bottle", tooltip="Taken from the apothecary's wards"),
                 {"checkmark": "I brewed the cure from the apothecary's notes"}],
          rewards=[reward_item("herbalbrews:lavender_tea", 2), reward_item("irons_spellbooks:greater_healing_potion", 2),
                   skill("forage", 300)]),

    quest("palace_of_shiraz", "The Palace Treasury", icon="minecraft:gold_block",
          discover={"structure": "dungeons_arise:shiraz_palace"},
          text=["Shiraz Palace kept a fire burning in every court, and the old scholars wrote that the treasury "
                "answers only to a palace whose fires are lit. Relight the dead court fires and search for the "
                "treasury's seal among the palace stores."],
          tasks=[{"use": "#minecraft:campfires", "count": 3, "holding": "minecraft:flint_and_steel",
                  "at": {"structure": "dungeons_arise:shiraz_palace"}, "title": "Relight three of the court fires"},
                 {"search": {"at": {"structure": "dungeons_arise:shiraz_palace"}, "count": 1,
                             "item": {"name": "Treasury Seal", "tooltip": "The palace treasury's brass seal",
                                      "texture": "minecraft:item/gold_nugget"},
                             "found": "With the fires lit, you notice a brass seal glinting at the bottom of the chest."},
                  "title": "Find the treasury seal"}],
          rewards=[reward_item("minecraft:gold_block", 4), reward_item("minecraft:enchanted_golden_apple"),
                   skill("attack", 500)]),

    quest("thornborn_ascent", "The Thornborn Ascent", icon="minecraft:vine",
          discover={"structure": "dungeons_arise:thornborn_towers"},
          text=["Thorns have swallowed the Thornborn Towers from the roots up, and the vines fight back. Climb to the "
                "top and bring down a cutting of the first thorn."],
          tasks=[fight("minecraft:spider", 8, "dungeons_arise:thornborn_towers", "Thorn Guardians",
                       "Fight the thorns' guardians on the climb"),
                 item("minecraft:vine", 4, title="Cut a piece of the first thorn from the summit")],
          rewards=[reward_item("minecraft:iron_axe", name="Thornbreaker", lore=["Cut from the Thornborn Towers."],
                               enchant={"minecraft:sharpness": 3}), reward_item("minecraft:cherry_sapling", 4),
                   skill("forage", 280)]),

    quest("the_infested_temple", "Swarming Stones", icon="minecraft:infested_stone",
          discover={"structure": "dungeons_arise:infested_temple"},
          text=["Every wall of the infested temple hides silverfish. Reach the inner sanctum and smash its brood "
                "stones before the swarm closes the way out."],
          tasks=[{"timed": {"seconds": 300, "goal": {"kill": "minecraft:silverfish", "count": 15},
                            "waves": [{"entity": "minecraft:silverfish", "count": 4, "every": 20}],
                            "lines": ["The walls are moving. Break the brood stones!"], "start": "Smash the brood stones"},
                  "title": "Smash the brood stones before the swarm closes in"}],
          rewards=[reward_item("minecraft:enchanted_book", name="Quarry Hands", enchant={"minecraft:efficiency": 3}),
                   reward_item("minecraft:torch", 32), skill("mining", 250)]),

    quest("temple_of_the_old_order", "The Old Order's Temple", icon="minecraft:lapis_block",
          discover={"structure": "dungeons_arise:abandoned_temple"},
          text=["An abandoned temple of the old order still keeps its sacred fire pit. The inscriptions name four "
                "offerings to be burned there before the reliquary will open."],
          tasks=[item("minecraft:lapis_lazuli", 4, consume=True, title="Gather the offering of lapis"),
                 item("minecraft:candle", consume=True, title="Gather the offering of light"),
                 item("minecraft:emerald", consume=True, title="Gather the offering of wealth"),
                 item("minecraft:book", consume=True, title="Gather the offering of words"),
                 {"use": "#minecraft:campfires", "at": {"structure": "dungeons_arise:abandoned_temple"},
                  "title": "Burn the offerings at the temple's fire"}],
          rewards=[reward_item("minecraft:lapis_lazuli", 16),
                   reward_item("minecraft:enchanted_book", name="The Old Order's Gift", enchant={"minecraft:protection": 2}),
                   skill("magic", 200)]),

    quest("spore_folk", "The Spore Folk", icon="minecraft:red_mushroom_block",
          discover={"structure": "dungeons_arise:mushroom_village"},
          text=["A village built inside giant mushrooms trades in caps and spores. Their people will teach you to "
                "grow the mushrooms, if you bring back a full set of blocks."],
          tasks=[enc(["Visitors from above! We trade caps and spores for kindness.",
                      "Grow them in the dark, damp and quiet. Never hurry a mushroom."],
                     entity="minecraft:villager", name="Spore Elder", title="Trade with the spore folk"),
                 item("minecraft:red_mushroom_block", title="Gather a red mushroom block"),
                 item("minecraft:brown_mushroom_block", title="Gather a brown mushroom block"),
                 item("minecraft:mushroom_stem", title="Gather a mushroom stem")],
          rewards=[reward_item("farmersdelight:red_mushroom_colony", 2),
                   reward_item("farmersdelight:brown_mushroom_colony", 2), reward_item("minecraft:mushroom_stew", 4),
                   skill("farm", 100)]),

    quest("the_scorched_mines", "Fire in the Hole", icon="minecraft:magma_block",
          discover={"structure": "dungeons_arise:scorched_mines"},
          text=["The scorched mines burn, and the last shift never came up. Find the trapped miners through the heat "
                "and get them out before the next collapse."],
          tasks=[enc(["Here! Behind the rubble! The roof came down hours ago!"], then="escort",
                     entity="minecraft:villager", name="Trapped Miner",
                     to={"structure": "#villages", "label": "a village, out of the heat"},
                     title="Lead the trapped miners out of the fire")],
          rewards=[reward_item("minecraft:magma_cream", 4), reward_item("minecraft:raw_gold", 8), skill("mining", 280)]),

    quest("empty_stands", "Empty Stands", icon="minecraft:iron_sword",
          discover={"structure": "dungeons_arise:coliseum"},
          text=["The coliseum's stands are empty, but its gates still open for a challenger. A note pinned to the gate "
                "sends you to the Bounty Office, who know who runs the fights now."],
          tasks=[talk_org("bounty", ["The coliseum? Still open? Hm.",
                                     "A hunter named Dray ran the fights, until he stopped coming to the office.",
                                     "Take a decree. If you fight there, fight for coin."],
                          title="Ask the Bounty Office who runs the fights now")],
          rewards=[reward_item("bountiful:decree"), skill("attack", 150)]),

    quest("witch_villa_tea_party", "Tea at the Witch Villa", icon="minecraft:cauldron",
          discover={"structure": "nova_structures:witch_villa"},
          text=["The witches of the swamp villa are holding a tea party, and their recipe book lies open on the "
                "table. Copy it unseen, and brew their strangest potion yourself."],
          tasks=[{"checkmark": "I copied the witches' recipe book unseen"},
                 item("minecraft:splash_potion", title="Brew the witches' strangest potion")],
          rewards=[reward_item("minecraft:splash_potion", 3), reward_item("minecraft:cauldron"), skill("magic", 220)]),

    quest("old_manor_ghost", "The Old Manor", icon="supplementaries:key",
          discover={"structure": "structory:old_manor"},
          text=["The old manor's doors lock behind you. The family who lived here hid four keys among the house's "
                "stores before they fled, and the last of them opens the study where their final letter waits."],
          tasks=[{"search": {"at": {"structure": "structory:old_manor"}, "count": 4,
                             "item": {"name": "Manor Key", "tooltip": "One of the family's four keys",
                                      "texture": "minecraft:item/tripwire_hook"},
                             "found": "Wrapped in an old cloth, a heavy iron key."},
                  "title": "Find the family's four keys"}],
          rewards=[reward_item("supplementaries:key"), reward_item("supplementaries:safe"),
                   reward_item("minecraft:gold_ingot", 8), skill("magic", 220)]),

    quest("temple_on_the_peak", "The Temple on the Peak", icon="grapplemod:grapplinghook",
          discover={"structure": "structory_towers:ancient_temple"},
          text=["An ancient temple sits on a mountain peak above the clouds. The shepherds below say that once, four "
                "fires burned at its corners and the whole valley could see it. Bring fire back to the peak."],
          tasks=[{"build": {"blocks": {"minecraft:campfire": 4}, "radius": 12},
                  "title": "Set four fires burning at the temple"}],
          rewards=[reward_item("grapplemod:grapplinghook"), reward_item("minecraft:golden_carrot", 8),
                   skill("agility", 250)]),

    quest("sacred_relic", "The Sacred Relic", icon="minecraft:lapis_block",
          discover={"structure": "structory_towers:sacred_relic_temple"},
          text=["The relic temple's altar is empty. Jungle thieves took the relic, and their trail leads to a nearby "
                "ruin."],
          tasks=[{"structure": "#ruins", "title": "Follow the thieves' trail to a ruin"},
                 fight("minecraft:pillager", 4, "#ruins", "Relic Thieves", "Take the relic back from the thieves"),
                 sample("the Sacred Relic", ["minecraft:pillager"], 0.6, texture="minecraft:item/lapis_lazuli"),
                 {"structure": "structory_towers:sacred_relic_temple", "title": "Return the relic to its altar"}],
          rewards=[reward_item("minecraft:emerald", 8), reward_item("minecraft:lapis_block"), skill("magic", 240)]),

    quest("warped_greatsword", "The Sword in the Hill", icon="spartanweaponry:diamond_greatsword",
          discover={"structure": "structory_towers:warped_greatsword"},
          text=["A giant warped sword is driven into the shattered hills, as if dropped from the Nether. The forger's "
                "mark on its hilt names who made it."],
          tasks=[{"search": {"at": {"structure": "structory_towers:warped_greatsword"}, "count": 1,
                             "item": {"name": "Forger's Token", "tooltip": "Stamped with a smith's mark",
                                      "texture": "minecraft:item/iron_nugget"},
                             "found": "In the hilt's hollow lies a smith's token, stamped with a mark you don't know."},
                  "title": "Climb to the hilt and find the forger's mark"}],
          rewards=[reward_item("spartanweaponry:diamond_greatsword"), reward_item("minecraft:warped_fungus", 8),
                   skill("attack", 300)]),

    quest("the_cathedral", "The Cathedral", icon="minecraft:bell",
          discover={"structure": "mvs:cathedral"},
          text=["A cathedral stands alone in the wilds, its bell tower cracked. Climb the tower and ring the bell; a "
                "cleric will arrive to say why the town around it never got built."],
          tasks=[{"use": "minecraft:bell", "at": {"structure": "mvs:cathedral"},
                  "title": "Climb the tower and ring the bell"},
                 enc(["I heard the bell! Nobody's rung it in years.",
                      "The town was never built because the builders found something under the foundations, "
                      "and left in the night. Nobody will say what."],
                     entity="minecraft:villager", name="Wandering Cleric", title="Meet the cleric who answers the bell")],
          rewards=[reward_item("immersive_melodies:piano"), reward_item("minecraft:golden_apple", 2),
                   skill("magic", 220)]),

    quest("warped_in_the_overworld", "Wrong Side of the Portal", icon="minecraft:warped_planks",
          discover={"structure": "mvs:warped_house"},
          text=["Warped wood houses and towers stand in the Overworld where nothing warped should grow. The Arcane "
                "Order suspect a leak from the Nether, and want a sample."],
          tasks=[item("minecraft:warped_planks", 4, consume=True, title="Take a sample of the warped wood"),
                 talk_org("arcane", ["Warped planks, in the Overworld? That shouldn't be possible.",
                                     "A leak from the Nether, then. The Order will look into it.",
                                     "Well done. Keep away from the portal until we know more."],
                          title="Show the sample to the Arcane Order")],
          rewards=[reward_item("minecraft:warped_planks", 16), reward_item("minecraft:ender_pearl"),
                   skill("magic", 200)]),

    quest("beacon_gone_dark", "A Beacon Gone Dark", icon="minecraft:beacon",
          discover={"structure": "mvs:ruined_beacon"},
          text=["A ruined beacon still has its pyramid, half-robbed by looters. Replace the missing blocks and light "
                "it again, so the beam can be seen from miles away."],
          tasks=[item("minecraft:iron_block", 9, consume=True, title="Gather iron blocks to rebuild the pyramid"),
                 {"build": {"blocks": {"minecraft:iron_block": 9}, "radius": 8}, "title": "Rebuild the beacon's pyramid"}],
          rewards=[reward_item("minecraft:iron_block", 4), skill("mining", 300)]),

    quest("desert_mimic", "Too Good to Be True", icon="artifacts:mimic_spawn_egg",
          discover={"structure": "towns_and_towers:mimic_desert"},
          text=["A desert ruin has a chest sitting out in the open, unguarded. The chest bites. Beat the mimic, and "
                "the real loot is under the sand where it sat."],
          tasks=[fight("artifacts:mimic", 1, "towns_and_towers:mimic_desert", "Hungry Chest",
                       "Beat the mimic guarding the loot", wave=1, ensure=True)],
          rewards=[reward_item("minecraft:gold_ingot", 12), reward_item("minecraft:golden_horse_armor"),
                   skill("attack", 220)]),

    quest("pharaohs_vault", "The Pharaoh's Vault", icon="minecraft:gold_block",
          discover={"structure": "betterdeserttemples:desert_temple"},
          text=["The desert temple's tomb is sealed, and its corridors are trapped. The builders left hidden switches "
                "for their own way in. Press them, mind the plates, and find what the pharaoh was buried with."],
          tasks=[{"use": "#minecraft:buttons", "count": 3, "at": {"structure": "betterdeserttemples:desert_temple"},
                  "title": "Find and press three hidden switches"},
                 {"search": {"at": {"structure": "betterdeserttemples:desert_temple"}, "count": 1,
                             "item": {"name": "Pharaoh's Ankh", "tooltip": "Gold, and warm to the touch",
                                      "texture": "minecraft:item/gold_ingot"},
                             "found": "Among the grave goods lies a golden ankh, warm to the touch."},
                  "title": "Find what the pharaoh was buried with"}],
          rewards=[reward_item("minecraft:gold_ingot", 10),
                   reward_item("minecraft:enchanted_book", name="Pharaoh's Blessing", enchant={"minecraft:fire_aspect": 1}),
                   skill("attack", 220)]),

    quest("jungle_temple_traps", "Traps of the Jungle Temple", icon="minecraft:tripwire_hook",
          discover={"structure": "betterjungletemples:jungle_temple"},
          text=["A jungle temple's halls are full of dart traps and crushing floors. A carving at the entrance gives "
                "a warning and a deadline: be at the treasure room before the floors close."],
          tasks=[{"timed": {"seconds": 180, "goal": {"structure": "betterjungletemples:jungle_temple",
                                                     "label": "the treasure room"},
                            "lines": ["The carving's warning echoes in your head: before the floors close."],
                            "start": "Enter the temple", "no": ["teleport", "pearls"]},
                  "title": "Get inside before the floors close"},
                 {"search": {"at": {"structure": "betterjungletemples:jungle_temple"}, "count": 1,
                             "item": {"name": "Idol of the Deep Jungle", "tooltip": "Jade, cold as river water",
                                      "texture": "minecraft:item/emerald"},
                             "found": "Behind the treasure, a small jade idol."},
                  "title": "Claim the idol"}],
          rewards=[reward_item("minecraft:emerald", 6),
                   reward_item("minecraft:enchanted_book", name="Light Landing", enchant={"minecraft:feather_falling": 3}),
                   skill("agility", 220)]),

    quest("the_bridge_builder", "The Bridge Builder", icon="mcwbridges:oak_log_bridge_middle",
          discover={"stat": "minecraft:walk_one_cm", "count": 200000},
          text=["On one of the old river bridges you find the builder's plaque: it asks that someone build one more. "
                "Cross another river with a bridge of your own."],
          tasks=[{"build": {"blocks": {"mcwbridges:oak_log_bridge_middle": 6, "mcwbridges:oak_bridge_pier": 2},
                            "radius": 12}, "title": "Build a bridge across a river"}],
          rewards=[reward_item("mcwbridges:oak_log_bridge_middle", 8), reward_item("minecraft:oak_log", 32),
                   skill("craft", 120)]),

    quest("the_broken_gate", "The Broken Gate", icon="minecraft:crying_obsidian",
          discover={"structure": "#ruined_portals"},
          text=["A ruined portal stands half-collapsed with crying obsidian in its frame. Rebuild the frame, but "
                "don't light it yet: the Arcane Order want a word first."],
          tasks=[item("minecraft:obsidian", 10, title="Gather obsidian to mend the frame"),
                 {"build": {"blocks": {"minecraft:obsidian": 10}, "radius": 8}, "title": "Rebuild the portal's frame"},
                 talk_org("arcane", ["You rebuilt a portal? Unlit, I hope.",
                                     "Portals are doors, and doors can be opened from either side.",
                                     "Leave it cold until we've looked at it. Please."],
                          title="Tell the Arcane Order before you light it")],
          rewards=[reward_item("minecraft:flint_and_steel"), reward_item("minecraft:gold_ingot", 4),
                   skill("mining", 100)]),

    quest("igloo_basement", "The Igloo's Basement", icon="minecraft:golden_apple",
          discover={"structure": "minecraft:igloo"},
          text=["Under an igloo's carpet, a ladder leads to a cell holding a zombie villager. Cure him with weakness "
                "and a golden apple, and he will tell you whose igloo it was."],
          tasks=[{"advancement": "minecraft:story/cure_zombie_villager", "title": "Cure the prisoner in the cell"}],
          rewards=[reward_item("minecraft:brewing_stand"), reward_item("minecraft:golden_apple"), skill("magic", 200)]),

    quest("waystone_network", "Stones That Remember", icon="waystones:waystone",
          discover={"stat": "minecraft:walk_one_cm", "count": 100000},
          text=["Activating a wild waystone starts something. The Couriers say there's a whole network of them, "
                "each one remembers the others."],
          tasks=[{"waystones": 5, "wild": True, "title": "Attune five waystones in the wild"},
                 item("waystones:warp_scroll", crafted=True, title="Make a warp scroll"),
                 {"checkmark": "I used the warp scroll"}],
          rewards=[reward_item("waystones:warp_scroll", 4), reward_item("waystones:return_scroll"),
                   skill("agility", 120)]),

    quest("frostbitten_ruins", "Frostbitten Ruins", icon="minecraft:blue_ice",
          discover={"structure": "cataclysm:abandoned_spire"},
          text=["Frozen spires and an abandoned village in the snow, built by no people anyone knows. Something very "
                "large sleeps far below. Note it, copy the writing, and leave it alone for now."],
          tasks=[{"checkmark": "I copied the ruins' writing and left whatever sleeps below"}],
          rewards=[reward_item("minecraft:writable_book", name="Page of the Old Ruins' Writing",
                               lore=["Copied in the snow, in a shaking hand."]), skill("magic", 200)]),

    quest("occupied_dunes", "Occupied Dunes", icon="minecraft:gold_ingot",
          discover={"structure": "cataclysm:desert_occupied_village"},
          text=["A desert village has been occupied by scouts of something that digs, and a dig site nearby goes "
                "deeper than it should. Drive the scouts off, read the foreman's notes, and leave the pit alone."],
          tasks=[fight("cataclysm:koboleton", 6, "cataclysm:desert_occupied_village", "Dune Scouts",
                       "Drive the scouts out of the village"),
                 sample("the Foreman's Notes", ["cataclysm:koboleton"], 0.5, texture="minecraft:item/paper")],
          rewards=[reward_item("minecraft:gold_ingot", 12), skill("attack", 400)]),

    quest("return_to_the_ruins", "Back to the Ruins", icon="minecraft:writable_book",
          after=["frostbitten_ruins", "occupied_dunes"],
          text=["Now the old ruins' writing makes sense: the snow ruins and the desert dig site point to the "
                "prisons of something buried. Revisit one of each and read the inscriptions that name it."],
          tasks=[{"structure": "cataclysm:abandoned_temple", "title": "Return to the snow ruins to read the inscriptions"},
                 {"structure": "cataclysm:desert_site", "title": "Return to the dig site to read its inscriptions"},
                 {"checkmark": "I read the inscriptions that name what is buried here"}],
          rewards=[reward_item("minecraft:writable_book", name="Names of the Buried",
                               lore=["The inscriptions point toward the strongholds."]), skill("magic", 700)]),

    quest("biome_ominous_woods", "The Ominous Woods", icon="minecraft:dark_oak_log",
          discover={"biome": "biomesoplenty:ominous_woods"},
          text=["Entering the ominous woods at night, you hear something hunting through the trees. Survive until "
                "dawn without leaving the woods."],
          tasks=[{"timed": {"seconds": 600, "goal": {"hold": {"radius": 30}},
                            "waves": [{"entity": "minecraft:zombie", "count": 3, "every": 25},
                                      {"entity": "minecraft:skeleton", "count": 2, "every": 45}],
                            "lines": ["Something is hunting you through the trees. Hold until dawn."],
                            "start": "Stand until dawn"}, "title": "Survive the night in the ominous woods"}],
          rewards=[reward_item("minecraft:shield"), reward_item("minecraft:torch", 32), skill("defense", 220)]),

    quest("biome_volcano", "The Mountain That Smokes", icon="minecraft:lava_bucket",
          discover={"biome": "biomesoplenty:volcano"},
          text=["You've found a volcano, smoking and black. The Miners' Guild would pay for lava, black sand and "
                "magma from its crater."],
          tasks=[item("minecraft:lava_bucket", title="Scoop a bucket of lava from the crater"),
                 item("biomesoplenty:black_sand", 8, title="Take black sand from the slopes"),
                 item("minecraft:magma_block", 4, title="Chip magma from the crater's rim")],
          rewards=[reward_item("minecraft:obsidian", 8), reward_item("minecraft:magma_cream", 4), skill("mining", 220)]),
]

chapter("discovery_land", "Out in the Land", "Strange places on the road", "minecraft:compass", "explore", 0, Q)
