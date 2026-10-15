"""Chapter: discovery_land, stumbling on strange places across the land (every tier, including any).
Plan: src/plans/quests/discovery_land.json. Quests with a "discover" stay hidden until the player reaches the place; a
toast announces them. """
from common import chapter, quest, talk_org, talk_villager, item, reward_item, skill, encounter


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
                 enc(["Free? Thank you! Take me to a proper village, please."],
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
                 talk_org("crafters", ["A mainspring from the hive itself? Remarkable.", "The guild will pay for the loan. I'll study it."],
                          title="Show the mainspring to a Crafters' guild mason")],
          rewards=[reward_item("minecraft:redstone_block", 4), reward_item("minecraft:copper_block", 8),
                   skill("craft", 300)]),

    quest("asylum_samples", "Samples from the Asylum", icon="herbalbrews:lavender_tea",
          discover={"structure": "dungeons_arise:plague_asylum"},
          text=["The plague asylum's wards still hold the sick and what feeds on them. The Herbalists want samples "
                "from its apothecary, and a cure brewed from the notes."],
          tasks=[sample("an Asylum Sample", ["minecraft:zombie_villager"], 0.4, count=3,
                        texture="minecraft:item/glass_bottle", tooltip="Taken from the apothecary's wards"),
                 {"make": "minecraft:potion", "how": "brew", "title": "Brew a cure from the apothecary's notes"}],
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
          tasks=[talk_org("bounty", ["Still open? A hunter named Dray ran the fights once.", "Take a decree. Fight for coin."],
                          title="Ask the Bounty Office who runs the fights now")],
          rewards=[reward_item("bountiful:decree"), skill("attack", 150)]),

    quest("witch_villa_tea_party", "Tea at the Witch Villa", icon="minecraft:cauldron",
          discover={"structure": "nova_structures:witch_villa"},
          text=["The witches of the swamp villa are holding a tea party, and their recipe book lies open on the "
                "table. Copy it unseen, and brew their strangest potion yourself."],
          tasks=[{"checkmark": "I copied the witches' recipe book unseen"},
                 {"make": "minecraft:splash_potion", "how": "brew", "title": "Brew the witches' strangest potion"}],
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
                 enc(["Nobody's rung that bell in years!", "The builders found something under the foundations and left. Nobody says what."],
                     entity="minecraft:villager", name="Wandering Cleric", title="Meet the cleric who answers the bell")],
          rewards=[reward_item("immersive_melodies:piano"), reward_item("minecraft:golden_apple", 2),
                   skill("magic", 220)]),

    quest("warped_in_the_overworld", "Wrong Side of the Portal", icon="minecraft:warped_planks",
          discover={"structure": "mvs:warped_house"},
          text=["Warped wood houses and towers stand in the Overworld where nothing warped should grow. The Arcane "
                "Order suspect a leak from the Nether, and want a sample."],
          tasks=[item("minecraft:warped_planks", 4, consume=True, title="Take a sample of the warped wood"),
                 talk_org("arcane", ["Warped planks in the Overworld? A leak from the Nether.", "The Order will look into it. Stay clear of the portal."],
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
                 talk_org("arcane", ["Portals are doors, and doors open from either side.", "Leave it cold until we've looked at it."],
                          title="Tell the Arcane Order before you light it")],
          rewards=[reward_item("minecraft:flint_and_steel"), reward_item("minecraft:gold_ingot", 4),
                   skill("mining", 100)]),

    quest("igloo_basement", "The Igloo's Basement", icon="minecraft:golden_apple",
          discover={"structure": "minecraft:igloo"},
          text=["Under an igloo's carpet, a ladder leads to a cell holding a zombie villager. Cure him with weakness "
                "and a golden apple, and he will tell you whose igloo it was."],
          tasks=[{"interact": "minecraft:zombie_villager", "holding": "minecraft:golden_apple", "consume": True,
                  "title": "Weaken the prisoner in the cell and feed them a golden apple"}],
          rewards=[reward_item("minecraft:brewing_stand"), reward_item("minecraft:golden_apple"), skill("magic", 200)]),

    quest("waystone_network", "Stones That Remember", icon="waystones:waystone",
          discover={"stat": "minecraft:walk_one_cm", "count": 100000},
          text=["Activating a wild waystone starts something. The Couriers say there's a whole network of them, "
                "each one remembers the others."],
          tasks=[{"waystones": 5, "wild": True, "total": True, "title": "Attune five waystones in the wild"},
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
          after=["frostbitten_ruins", "occupied_dunes", "main_story:act5_start"],
          text=["Now the old ruins' writing makes sense: the snow ruins and the desert dig site point to the "
                "prisons of something buried. Revisit one of each and read the inscriptions that name it."],
          tasks=[{"structure": "cataclysm:abandoned_temple", "title": "Return to the snow ruins to read the inscriptions"},
                 {"structure": "cataclysm:desert_site", "title": "Return to the dig site to read its inscriptions"},
                 enc(["The old writing, now readable. It names what is buried here."], entity="minecraft:allay", name="Spirit of the Ruins",
                     title="Have the inscriptions read to you, naming what is buried here")],
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

def search(at, count, name, found, texture="minecraft:item/paper", title=None):
    """Opening containers at the place turns up the quest item."""
    return {"search": {"at": {"structure": at}, "count": count,
                       "item": {"name": name, "texture": texture}, "found": found},
            "title": title or ("Search for " + name)}


def use(block, at, title, count=1, **extra):
    t = {"use": block, "count": count, "title": title}
    if at:
        t["at"] = {"structure": at}
    t.update(extra)
    return t


def biome_step(biome, title):
    return {"biome": biome, "title": title}


ANY = [
    quest("the_lonely_cap", "The Lonely Cap", icon="minecraft:red_mushroom",
          discover={"structure": "dungeons_arise:mushroom_house"},
          text=["A single mushroom house stands far from anywhere with its door ajar and its owner missing. A trail of "
                "spores leads from the doorstep into the cave behind, where spiders have him cornered."],
          tasks=[fight("minecraft:cave_spider", 6, "dungeons_arise:mushroom_house", "Cave Spiders",
                       "Drive the spiders off the trapped hermit"),
                 enc(["Oh, thank the caps! They had me pinned for two days.",
                      "Take me home, please. The stew's gone cold."], then="escort", entity="minecraft:villager",
                     name="Mushroom Hermit", to={"structure": "dungeons_arise:mushroom_house", "label": "his house"},
                     title="Lead the hermit home")],
          rewards=[reward_item("minecraft:suspicious_stew", 3), reward_item("farmersdelight:brown_mushroom_colony", 2),
                   skill("forage", 150)]),

    quest("chapel_in_the_pines", "The Chapel in the Pines", icon="minecraft:bell",
          discover={"structure": "structory:abandoned_chapel"},
          text=["An abandoned chapel stands silent: its bell was carried off years ago and the candles have burnt "
                "out. Someone in the forest has been listening for it ever since."],
          tasks=[item("supplementaries:rope", 2, consume=True, title="Bring a new rope for the bell"),
                 item("minecraft:candle", 3, consume=True, title="Bring candles for the altar"),
                 {"build": {"blocks": {"minecraft:bell": 1}, "radius": 10}, "title": "Hang a new bell in the chapel"},
                 use("minecraft:bell", "structory:abandoned_chapel", "Ring the chapel bell"),
                 enc(["The bell! After all these years!", "I kept this chapel once. Thank you for ringing it."], entity="minecraft:villager",
                     name="Chapel Keeper", title="See who comes out of the forest")],
          rewards=[reward_item("minecraft:bell"), reward_item("minecraft:candle", 4), skill("defense", 150)]),

    quest("outcasts", "The Outcasts", icon="minecraft:emerald",
          discover={"structure": "structory:outcast_villager_grassy"},
          text=["Villagers cast out of their village live in a shack on their own. They'd like to go home, if "
                "anyone would carry their apology."],
          tasks=[enc(["Cast out for a harvest dispute, can you believe? Over a cabbage.",
                      "We'd go home tomorrow if they'd have us. Would you take our apology?"],
                     entity="minecraft:villager", name="Outcast Villager", title="Hear the outcasts' side"),
                 item("minecraft:emerald", 3, consume=True, title="Take their gift of emeralds"),
                 {"structure": "#villages", "title": "Carry their apology to the nearest village"},
                 talk_villager("minecraft:librarian", ["They apologised? Over the cabbage?",
                                                       "Well. It was a very good cabbage. Tell them they're welcome home."],
                               title="Deliver the apology to the village")],
          rewards=[reward_item("minecraft:emerald", 6), skill("defense", 150)]),

    quest("northern_runes", "Northern Runes", icon="explorerscompass:explorerscompass",
          discover={"structure": "structory:northern_ruin"},
          text=["Northern ruins carry runes on their standing stones, and the old scholars of the Arcane Order pay "
                "well for a good rubbing. Bring paper and charcoal, and take one."],
          tasks=[{"structure": "structory:northern_ruin", "title": "Find a northern ruin"},
                 item("minecraft:paper", 2, consume=True, title="Lay paper over the runes"),
                 item("minecraft:charcoal", consume=True, title="Rub the runes onto it with charcoal")],
          rewards=[reward_item("minecraft:chest"), reward_item("explorerscompass:explorerscompass"), skill("magic", 200)]),

    quest("engineers_plans", "The Engineer's Plans", icon="minecraft:sticky_piston",
          discover={"structure": "structory_towers:engineer_tower"},
          text=["The engineer left plans for a machine half-built: a working piston door. His notes list the parts."],
          tasks=[search("structory_towers:engineer_tower", 1, "Engineer's Notes", "Notes in a cramped hand, with a "
                        "parts list."),
                 item("minecraft:sticky_piston", 2, crafted=True, title="Make the sticky pistons the notes call for"),
                 {"build": {"blocks": {"minecraft:sticky_piston": 2, "minecraft:iron_door": 1}, "radius": 8},
                  "title": "Finish the piston door"}],
          rewards=[reward_item("minecraft:piston", 8), reward_item("minecraft:redstone", 16), skill("craft", 200)]),

    quest("mirage_outpost", "The Mirage", icon="minecraft:sand",
          discover={"structure": "structory_towers:mirage_outpost"},
          text=["The desert outpost keeps a water barrel and a logbook of travellers who never arrived. The next "
                "oasis is a hard walk across the dunes, and the barrel only holds so much."],
          tasks=[{"timed": {"seconds": 480, "goal": {"structure": "#villages", "label": "the next oasis", "away": 150},
                            "lines": ["The barrel's nearly dry. Cross the dunes before your water runs out."],
                            "start": "Cross the dunes", "no": ["teleport", "mounts"]},
                  "title": "Cross the dunes before the water runs out"},
                 {"checkmark": "I added my name to the logbook"}],
          rewards=[reward_item("minecraft:dried_kelp", 16), reward_item("minecraft:golden_carrot", 6),
                   skill("agility", 200)]),

    quest("gallows_hill", "Gallows Hill", icon="minecraft:oak_sign",
          discover={"structure": "mvs:gallows"},
          text=["A notice on the gallows names a thief who swore he was innocent. The real culprit dropped a coin "
                "purse nearby, and the Village Watch could clear the dead man's name."],
          tasks=[search("mvs:gallows", 1, "Dropped Coin Purse", "A coin purse, stitched with the wrong man's initials.",
                        texture="minecraft:item/gold_nugget", title="Search the gallows for the culprit's purse"),
                 talk_org("watch", ["Wrong initials? Then the hanged man was framed.", "We'll clear his name."], title="Clear the dead man's name with the Watch")],
          rewards=[reward_item("minecraft:emerald", 6), skill("defense", 150)]),

    quest("the_tree_monument", "Grove of Remembrance", icon="minecraft:oak_sapling",
          discover={"structure": "mvs:tree_monument"},
          text=["A monument to a felled forest stands on bare ground. Plant a sapling of every vanilla tree around it "
                "and bone-meal them up, and the grove will return."],
          tasks=[{"build": {"blocks": {"minecraft:oak_sapling": 1, "minecraft:spruce_sapling": 1,
                                       "minecraft:birch_sapling": 1, "minecraft:jungle_sapling": 1,
                                       "minecraft:acacia_sapling": 1, "minecraft:dark_oak_sapling": 1},
                            "radius": 12}, "title": "Plant a sapling of every tree around the monument"},
                 item("minecraft:bone_meal", 12, consume=True, title="Bone-meal the saplings up")],
          rewards=[reward_item("minecraft:bone_meal", 16), reward_item("minecraft:oak_sapling", 8), skill("forage", 150)]),

    quest("nobodys_home", "Nobody's Home", icon="minecraft:book",
          discover={"structure": "#lonely_houses"},
          text=["Lonely houses stand empty along the roads, tables still set. A diary, torn into pages, is scattered "
                "through them. Gather its pages to learn where the families went."],
          tasks=[search("#lonely_houses", 3, "Diary Page", "A page from a diary, with a date and a worried hand.",
                        title="Search three empty houses for diary pages")],
          rewards=[reward_item("handcrafted:oak_chair", 2), reward_item("minecraft:red_bed"), skill("craft", 150)]),

    quest("circle_of_stones", "The Circle of Stones", icon="minecraft:cauldron",
          discover={"structure": "betterwitchhuts:witch_circle"},
          text=["A witch's circle of stones stands in the swamp. A potion is carved into its stones, and the old "
                "tales say a witch's familiar answers when it is poured at the centre."],
          tasks=[item("minecraft:potion", title="Brew the potion carved into the stones"),
                 use("minecraft:water_cauldron", "betterwitchhuts:witch_circle", "Pour the potion into the cauldron",
                     holding="minecraft:potion", unchecked=True),
                 enc(["Meow. The witch's tongue is in my mouth, and she says you may pass."],
                     entity="minecraft:cat", name="Witch's Familiar", title="Meet the witch's familiar")],
          rewards=[reward_item("bookoffamiliars:familiar_book"), reward_item("minecraft:redstone", 16),
                   skill("magic", 200)]),

    quest("reading_the_obelisks", "Reading the Obelisks", icon="minecraft:chiseled_sandstone",
          discover={"biome": "minecraft:desert"},
          text=["Obelisks in the desert carry the same carvings in different orders. One symbol appears on every "
                "one, and the old tales say it points to a cache."],
          tasks=[{"checkmark": "I noted the carvings on the first obelisk"},
                 {"checkmark": "I noted the carvings on the second obelisk"},
                 {"checkmark": "I noted the carvings on the third obelisk, and the symbol they share"}],
          rewards=[reward_item("minecraft:sandstone", 32), reward_item("minecraft:gold_ingot", 6), skill("magic", 200)]),

    quest("shards_of_the_trail", "Shards of the Trail", icon="minecraft:decorated_pot",
          discover={"structure": "minecraft:trail_ruins"},
          text=["Trail ruins hide their past under suspicious gravel. Brush out four different pottery sherds and "
                "fit them on a decorated pot to read the story they tell."],
          tasks=[item("minecraft:brush", title="Bring a brush for the suspicious gravel"),
                 item("minecraft:angler_pottery_sherd", title="Brush out an angler sherd"),
                 item("minecraft:archer_pottery_sherd", title="Brush out an archer sherd"),
                 item("minecraft:arms_up_pottery_sherd", title="Brush out an arms-up sherd"),
                 item("minecraft:blade_pottery_sherd", title="Brush out a blade sherd"),
                 item("minecraft:decorated_pot", crafted=True, title="Fit the sherds onto a decorated pot")],
          rewards=[reward_item("minecraft:brush"), reward_item("minecraft:sniffer_egg"), skill("craft", 200)]),

    quest("the_bakery", "Fresh from the Oven", icon="bakery:strawberry_cake",
          discover={"structure": "bakery:bakery"},
          text=["The village bakery's baker is behind on orders for the festival. Bake a strawberry cake, a baguette "
                "and a tray of cupcakes and deliver them."],
          tasks=[item("bakery:strawberry_cake", consume=True, title="Bake a strawberry cake"),
                 item("bakery:baguette", consume=True, title="Bake a baguette"),
                 item("bakery:strawberry_cupcake", 3, consume=True, title="Bake a tray of cupcakes"),
                 enc(["All of it, on time? Take a rolling pin. I have three."], entity="minecraft:villager", name="Harried Baker",
                     title="Deliver the baking before the festival")],
          rewards=[reward_item("bakery:rolling_pin"), reward_item("bakery:bread", 8), skill("cook", 200)]),

    quest("brewfest", "Brewfest", icon="brewery:beer_mug",
          discover={"structure": "brewery:brewfest_tent"},
          text=["A brewfest tent stands in the plains with a contest board. Brew three beers, enter them, and beat "
                "the brewfest regulars and the Beer Elemental they keep in the cellar."],
          tasks=[item("brewery:beer_wheat", consume=True, title="Brew a wheat beer"),
                 item("brewery:beer_barley", consume=True, title="Brew a barley beer"),
                 item("brewery:beer_oat", consume=True, title="Brew an oat beer"),
                 fight("brewery:beer_elemental", 1, "brewery:brewfest_tent", "Cellar Beer Elemental",
                       "Beat the Beer Elemental in the cellar", wave=1)],
          rewards=[reward_item("brewery:brewfest_hat"), reward_item("brewery:wooden_brewingstation"),
                   skill("cook", 220)]),

    quest("the_chalet", "Fondue at the Chalet", icon="meadow:fondue",
          discover={"structure": "meadow:chalet"},
          text=["The alpine chalet's cook makes fondue for climbers, but the cheese cellar is empty. Bring cheese of "
                "three kinds from Meadow's animals and cook the fondue together."],
          tasks=[item("meadow:piece_of_cheese", consume=True, title="Bring plain cheese"),
                 item("meadow:piece_of_goat_cheese", consume=True, title="Bring goat cheese"),
                 item("meadow:piece_of_sheep_cheese", consume=True, title="Bring sheep cheese"),
                 item("meadow:fondue", title="Cook the fondue")],
          rewards=[reward_item("meadow:cheese_sandwich", 4), reward_item("meadow:fur_boots"), skill("cook", 200)]),

    quest("the_observation_post", "The Observation Post", icon="camerapture:camera",
          discover={"structure": "meadow:observation_post"},
          text=["An alpine observation post has a list of animals to sight pinned to its sill. Photograph three "
                "of them for the survey."],
          tasks=[{"photo": {"entity": "meadow:water_buffalo"}, "title": "Photograph a water buffalo"},
                 {"photo": {"entity": "meadow:horned_sheep"}, "title": "Photograph a horned sheep"},
                 {"photo": {"entity": "meadow:highland_cattle"}, "title": "Photograph a highland cow"}],
          rewards=[reward_item("camerapture:camera"), reward_item("minecraft:spyglass"), skill("range", 200)]),

    quest("the_gardeners_cottage", "The Gardener's Cottage", icon="bloomingnature:bluebell",
          discover={"structure": "bloomingnature:cottage"},
          text=["A cottage in the woods with a garden gone wild. The wandering gardener who lives there wants her "
                "beds replanted, and will give a cutting of each."],
          tasks=[enc(["Oh, a visitor! My garden's got away from me, I'm afraid.",
                      "Could you replant the beds? Anemones, bluebells, amaryllis. I'll give you cuttings."],
                     entity="minecraft:villager", name="Wandering Gardener", title="Talk to the gardener"),
                 item("bloomingnature:anemone", 2, consume=True, title="Replant the anemones"),
                 item("bloomingnature:bluebell", 2, consume=True, title="Replant the bluebells"),
                 item("bloomingnature:amaryllis", 2, consume=True, title="Replant the amaryllis")],
          rewards=[reward_item("bloomingnature:begonie", 4), reward_item("bloomingnature:bird_of_paradise", 2),
                   skill("forage", 200)]),

    quest("gingerbread_house", "The Gingerbread House", icon="snowyspirit:gingerbread_cookie",
          discover={"structure": "snowyspirit:gingerbread_house"},
          text=["A gingerbread house in the snow, and a gingerbread golem that won't let anyone eat the walls. "
                "Bake it some gingerbread cookies and eggnog to win it over."],
          tasks=[item("snowyspirit:gingerbread_cookie", 4, consume=True, title="Bake gingerbread cookies for the golem"),
                 item("snowyspirit:eggnog", 2, consume=True, title="Bring eggnog for the golem"),
                 {"talk": "entity", "entity": "snowyspirit:gingerbread_golem",
                  "lines": ["Cookies, and a drink? Fine. One gumdrop.", "Merry Midwinter."], "title": "Win over the gingerbread golem"}],
          rewards=[reward_item("snowyspirit:sled_oak"), reward_item("snowyspirit:candy_cane", 8), skill("cook", 200)]),

    quest("butterfly_lovers", "The Butterfly Lovers", icon="butterflies:butterfly_net",
          discover={"structure": "butterflies:liangshanbo_grave"},
          text=["A lonely grave where two butterflies always circle. The legend carved on it asks for two matching "
                "butterflies to be set free at the grave."],
          tasks=[{"structure": "butterflies:liangshanbo_grave", "title": "Stand at the grave"},
                 item("butterflies:bottled_butterfly_common", 2, consume=True,
                      title="Set a matching pair of butterflies free at the grave")],
          rewards=[reward_item("butterflies:butterfly_net"), reward_item("minecraft:poppy", 6), skill("taming", 150)]),

    quest("fallen_adventurer", "Bring Them Home", icon="minecraft:name_tag",
          discover={"observe": "realmrpg_skeletons:hunted_skeleton", "ticks": 20},
          text=["A skeleton in armour lies where an adventurer fell. Take the name tag and gear found on it to the "
                "nearest village and tell the family, who will want to know."],
          tasks=[item("minecraft:name_tag", title="Take the adventurer's name tag"),
                 {"structure": "#villages", "title": "Carry the news to the nearest village"},
                 talk_org("watch", ["A name tag. Oh, no. Not young Brin.", "We'll tell the family gently. His sword is yours."],
                          title="Tell the family through the Village Watch")],
          rewards=[reward_item("minecraft:iron_sword", name="The Fallen Adventurer's Blade",
                               lore=["Returned by the one who brought them home."]), skill("defense", 150)]),

    quest("biome_cherry_grove", "Petals on the Wind", icon="minecraft:pink_petals",
          discover={"biome": "minecraft:cherry_grove"},
          text=["A cherry grove in bloom, pink petals drifting through the air. The Herbalists would love a sample "
                "of its petals, its saplings and its bees' honey."],
          tasks=[item("minecraft:pink_petals", 4, title="Gather pink petals"),
                 item("minecraft:cherry_sapling", title="Take a cherry sapling"),
                 item("minecraft:honey_bottle", title="Take honey from the grove's bees")],
          rewards=[reward_item("minecraft:cherry_sapling", 4), skill("forage", 100)]),

    quest("biome_mushroom_fields", "Mooshroom Shores", icon="minecraft:mushroom_stew",
          discover={"biome": "minecraft:mushroom_fields"},
          text=["You've landed on a mushroom island. A mushroom idol stands on some of them, and the mooshrooms give "
                "stew instead of milk."],
          tasks=[{"structure": "mvs:mushroom_statue", "title": "Find the mushroom idol"},
                 item("minecraft:mushroom_stew", title="Milk a mooshroom for a bowl of stew")],
          rewards=[reward_item("minecraft:mycelium", 8), reward_item("minecraft:mushroom_stew", 2), skill("farm", 100)]),

    quest("biome_lavender_field", "Lavender Haze", icon="biomesoplenty:lavender",
          discover={"biome": "biomesoplenty:lavender_field"},
          text=["A field of lavender hums with bees. The Herbalists say a calming tea from it settles the "
                "nerves of the whole village."],
          tasks=[item("biomesoplenty:lavender", 8, title="Gather lavender"),
                 item("herbalbrews:lavender_tea", consume=True, title="Brew a calming tea")],
          rewards=[reward_item("herbalbrews:lavender_tea", 2), skill("forage", 100)]),

    quest("biome_origin_valley", "Where It All Began", icon="biomesoplenty:origin_grass_block",
          discover={"biome": "biomesoplenty:origin_valley"},
          text=["You've stumbled into the rare Origin Valley, where the world looks as it did long ago. The Field "
                "Guide would love a block of its old grass and a rose."],
          tasks=[item("biomesoplenty:origin_grass_block", title="Take a block of the old grass"),
                 item("biomesoplenty:rose", title="Pick a rose")],
          rewards=[reward_item("minecraft:painting", 2), skill("forage", 100)]),

    quest("biome_alpha_grove", "Alpha Grove", icon="regions_unexplored:alpha_sapling",
          discover={"biome": "regions_unexplored:alpha_grove"},
          text=["The alpha grove is all old-style leaves and grass, like a memory of the world before. Bring back its "
                "saplings and leaves before you forget what it looked like."],
          tasks=[item("regions_unexplored:alpha_sapling", 2, title="Take alpha saplings"),
                 item("regions_unexplored:alpha_leaves", 4, title="Take alpha leaves")],
          rewards=[reward_item("regions_unexplored:alpha_sapling", 4), skill("forage", 100)]),

    quest("biome_mystic_grove", "The Mystic Grove", icon="fays_fairies:fairy_bottle",
          discover={"biome": "biomesoplenty:mystic_grove"},
          text=["A mystic grove glows with strange flowers. A fairy shows itself among them if you wait quietly, and "
                "will lead you to its ring."],
          tasks=[enc(["Ssh. You waited. Nobody waits.", "Follow me, if you like. There's a ring of mushrooms. It is "
                      "very nice."], entity="fays_fairies:pink_fairy", name="Grove Fairy",
                     title="Wait quietly for the fairy to appear")],
          rewards=[reward_item("fays_fairies:fairy_bottle"), skill("magic", 150)]),

    quest("biome_redwoods", "Giants of the Forest", icon="biomesoplenty:redwood_log",
          discover={"biome": "biomesoplenty:redwood_forest"},
          text=["A redwood forest, with trees taller than any tower. The Crafters' guild wants wood from one of the "
                "giants, and a climb to the top is the only way to reach the good branches."],
          tasks=[item("biomesoplenty:redwood_log", 16, title="Bring down redwood logs from the giants")],
          rewards=[reward_item("biomesoplenty:redwood_log", 16), reward_item("minecraft:iron_axe"), skill("forage", 150)]),

    quest("biome_hot_springs", "Hot Springs", icon="comforts:hammock_red",
          discover={"biome": "biomesoplenty:hot_springs"},
          text=["Hot springs steam in the cold air. Soak in the thermal water until you're fully healed, and take a "
                "bottle home for a sore friend."],
          tasks=[{"be": {"biomes": ["biomesoplenty:hot_springs"], "in_water": True}, "title": "Soak in the thermal water"},
                 item("minecraft:potion", title="Bottle the spring water for a sore friend")],
          rewards=[reward_item("comforts:hammock_blue"), skill("agility", 100)]),

    quest("biome_snowblossom", "Snowblossom", icon="biomesoplenty:snowblossom_leaves",
          discover={"biome": "biomesoplenty:snowblossom_grove"},
          text=["A snowblossom grove, white petals in the snow. The Herbalists want leaves and a sapling to see "
                "if it will grow in the village."],
          tasks=[item("biomesoplenty:snowblossom_leaves", 4, title="Gather snowblossom leaves"),
                 item("biomesoplenty:snowblossom_sapling", title="Take a snowblossom sapling")],
          rewards=[reward_item("biomesoplenty:snowblossom_sapling", 3), skill("forage", 100)]),

    quest("biome_wasteland", "The Wasteland", icon="biomesoplenty:dead_log",
          discover={"biome": "biomesoplenty:wasteland"},
          text=["A dried-out wasteland, nothing living in it. A single dead tree stands at its heart, and the "
                "Couriers want to know if the way across is safe."],
          tasks=[item("biomesoplenty:dead_log", 4, title="Bring wood from the dead tree at its heart")],
          rewards=[reward_item("minecraft:water_bucket"), reward_item("biomesoplenty:dead_log", 8), skill("agility", 100)]),

    quest("biome_pumpkin_patch", "The Pumpkin Patch", icon="minecraft:jack_o_lantern",
          discover={"biome": "biomesoplenty:pumpkin_patch"},
          text=["A pumpkin patch stretches to the horizon. The Growers' co-op would love your biggest pumpkins, and "
                "the children want a jack o'lantern."],
          tasks=[item("minecraft:pumpkin", 4, title="Pick the biggest pumpkins"),
                 item("minecraft:jack_o_lantern", crafted=True, title="Carve a jack o'lantern")],
          rewards=[reward_item("minecraft:pumpkin_pie", 4), skill("farm", 100)]),

    quest("biome_baobab_savanna", "Under the Baobabs", icon="regions_unexplored:baobab_log",
          discover={"biome": "regions_unexplored:baobab_savanna"},
          text=["Baobabs rise from the savanna like upside-down trees. The Crafters' guild would love some of their "
                "wood, and the herds that pass beneath are worth a look."],
          tasks=[item("regions_unexplored:baobab_log", 8, title="Gather baobab wood")],
          rewards=[reward_item("regions_unexplored:baobab_log", 16), skill("forage", 100)]),

    quest("biome_chalk_cliffs", "White Cliffs", icon="regions_unexplored:chalk",
          discover={"biome": "regions_unexplored:chalk_cliffs"},
          text=["White chalk cliffs rise above the sea. Climb from the beach to the top without a fall, and bring "
                "chalk for the Crafters' guild."],
          tasks=[item("regions_unexplored:chalk", 8, title="Climb the cliffs and bring back chalk")],
          rewards=[reward_item("regions_unexplored:chalk", 16), skill("agility", 100)]),

    quest("biome_spires", "Among the Spires", icon="minecraft:stone",
          discover={"biome": "regions_unexplored:spires"},
          text=["Stone spires jut from the land like needles. Stand on top of the tallest you can find and look "
                "across the world."],
          tasks=[{"be": {"biomes": ["regions_unexplored:spires"], "above_y": 110, "sky": True},
                  "title": "Stand on top of a spire"}],
          rewards=[reward_item("minecraft:string", 16), reward_item("supplementaries:rope", 16), skill("agility", 100)]),

    quest("biome_magnolia", "Magnolia in Bloom", icon="minecraft:flowering_azalea",
          discover={"biome": "regions_unexplored:magnolia_woodland"},
          text=["A magnolia woodland in bloom, with a shining meadow beyond it. The Herbalists want its flowers and "
                "the meadow's glistening grass."],
          tasks=[{"biome": "regions_unexplored:glistering_meadow", "title": "Find the glistering meadow"},
                 item("minecraft:flowering_azalea", 2, title="Gather flowering blossoms")],
          rewards=[reward_item("minecraft:flowering_azalea", 4), skill("forage", 100)]),

    quest("biome_ashen_woodland", "Ashen Woods", icon="regions_unexplored:ashen_sapling",
          discover={"biome": "regions_unexplored:ashen_woodland"},
          text=["An ashen woodland, burnt long ago. Bring back some ash and a surviving sapling to see if the soil "
                "can heal."],
          tasks=[item("regions_unexplored:ashen_dirt", 4, title="Collect ashen soil"),
                 item("regions_unexplored:ashen_sapling", title="Find a surviving sapling")],
          rewards=[reward_item("minecraft:bone_meal", 16), skill("forage", 100)]),

    quest("biome_saguaro", "Land of Cacti", icon="minecraft:cactus",
          discover={"biome": "regions_unexplored:saguaro_desert"},
          text=["A desert of towering saguaro cacti. The Growers' co-op would like a cutting of each cactus and a "
                "joshua tree sapling, if you don't hug the cactus."],
          tasks=[item("minecraft:cactus", 4, title="Cut pieces of saguaro cactus"),
                 item("regions_unexplored:joshua_beard", title="Take a joshua beard")],
          rewards=[reward_item("minecraft:green_dye", 8), skill("forage", 100)]),

    quest("tectonic_peaks", "Above the Clouds", icon="minecraft:spyglass",
          discover={"biome": "minecraft:jagged_peaks"},
          text=["The mountains here climb far higher than they should. Stand above the clouds on foot and look "
                "down at the world."],
          tasks=[{"be": {"above_y": 192, "sky": True}, "title": "Stand above the clouds on foot"}],
          rewards=[reward_item("minecraft:spyglass"), reward_item("minecraft:golden_carrot", 8), skill("agility", 150)]),

    quest("tectonic_canyon", "The Deep Valley", icon="aquaculture:worm",
          discover={"biome": "minecraft:river"},
          text=["Rivers here cut deep valleys. Follow one down to where it meets the sea and fish at its mouth, "
                "where the Anglers say the biggest fish gather."],
          tasks=[{"biome": "minecraft:beach", "title": "Follow the river to the sea"},
                 item("minecraft:salmon", 2, title="Fish at the river's mouth")],
          rewards=[reward_item("aquaculture:worm", 16), skill("fish", 100)]),

    quest("biome_ice_spikes", "Ice Spikes", icon="minecraft:packed_ice",
          discover={"biome": "minecraft:ice_spikes"},
          text=["Spikes of ice rise from a frozen plain. The Miners' Guild want packed ice from the top of a spike, "
                "which only a pick with silk touch will take."],
          tasks=[item("minecraft:packed_ice", 4, title="Mine packed ice from the top of a spike")],
          rewards=[reward_item("minecraft:blue_ice", 4), skill("mining", 100)]),

    quest("biome_badlands", "The Painted Badlands", icon="minecraft:terracotta",
          discover={"biome": "minecraft:badlands"},
          text=["The badlands are banded in every colour of clay. The Crafters' guild want a sample of each "
                "colour from the canyon walls."],
          tasks=[item("minecraft:terracotta", 4, title="Collect plain terracotta"),
                 item("minecraft:orange_terracotta", 4, title="Collect orange terracotta"),
                 item("minecraft:red_terracotta", 4, title="Collect red terracotta"),
                 item("minecraft:yellow_terracotta", 4, title="Collect yellow terracotta"),
                 item("minecraft:white_terracotta", 4, title="Collect white terracotta")],
          rewards=[reward_item("minecraft:gold_ingot", 8), skill("mining", 100)]),

    quest("biome_grand_tour", "The Grand Tour", icon="naturescompass:naturescompass", after=["biome_cherry_grove"],
          text=["The Couriers keep a list of the biomes of the Overworld, and offer a prize for anyone who has "
                "visited twenty. Nature's Compass helps you find the ones you're missing."],
          tasks=[{"biomes": 20, "dimension": "minecraft:overworld", "title": "Visit twenty different biomes"}],
          rewards=[reward_item("naturescompass:naturescompass"), reward_item("sophisticatedbackpacks:stack_upgrade_tier_1"),
                   skill("agility", 300)]),

    quest("found_music_disc", "A Song from Somewhere", icon="minecraft:jukebox",
          discover={"item": "minecraft:music_disc_13"},
          text=["You've found an old music disc, and a tune is waiting in it. Build a jukebox to hear it, then learn "
                "it on an instrument."],
          tasks=[{"build": {"blocks": {"minecraft:jukebox": 1}, "radius": 8}, "title": "Set up a jukebox"},
                 {"use": "minecraft:jukebox", "holding": "minecraft:music_disc_13", "title": "Play the disc on a jukebox"},
                 item("immersive_melodies:lute", crafted=True, title="Make an instrument to learn the tune on")],
          rewards=[reward_item("immersive_melodies:lute"), skill("craft", 100)]),

    quest("antique_ink", "Antique Ink", icon="supplementaries:antique_ink",
          discover={"item": "supplementaries:antique_ink"},
          text=["A bottle of antique ink from a chest. Ink a map with it and the map should show an old landmark that "
                "isn't on newer maps."],
          tasks=[item("minecraft:map", crafted=True, title="Make a map to ink"),
                 {"checkmark": "I inked the map and followed it to the old landmark"}],
          rewards=[reward_item("supplementaries:globe"), reward_item("explorerscompass:explorerscompass"),
                   skill("craft", 150)]),

    quest("the_strange_key", "The Strange Key", icon="supplementaries:key",
          discover={"item": "supplementaries:key"},
          text=["A lone key from a dungeon chest, with a tag that names a safe. Find the safe in a ruin nearby, and "
                "open it."],
          tasks=[{"structure": "#ruins", "title": "Find a ruin that might hold the safe"},
                 use("supplementaries:safe", None, "Open the safe with the strange key", holding="supplementaries:key")],
          rewards=[reward_item("minecraft:gold_ingot", 10), reward_item("minecraft:diamond"), skill("mining", 150)]),

    quest("sniffer_egg", "An Ancient Egg", icon="minecraft:sniffer_egg",
          discover={"item": "minecraft:sniffer_egg"},
          text=["A sniffer egg, warm to the touch. Hatch it on moss, raise the sniffer, and plant the first ancient "
                "seed it digs up."],
          tasks=[{"observe": "minecraft:sniffer", "ticks": 40, "title": "Watch the sniffer hatch and grow"},
                 item("minecraft:torchflower_seeds", title="Take the first ancient seed it digs up")],
          rewards=[reward_item("minecraft:pitcher_pod", 2), reward_item("minecraft:torchflower_seeds", 2),
                   skill("taming", 150)]),
]

chapter("discovery_land", "Out in the Land", "Strange places on the road", "minecraft:compass", "explore", 0, Q + ANY)

