"""Chapter: main_story, Prologue and Act I (first release). Plan: src/plans/quests/main_story.json.
Later acts are added to this file in later releases (append only: quest ids are permanent)."""
from common import chapter, quest, talk_char, talk_org, talk_villager, item, reward_item, skill, give, encounter
from common import enc, fight, boss, search, sample, talk_org, talk_villager, talk_char, item, reward_item, skill, encounter, giver_org  # noqa: F401

PROLOGUE = [
    quest("prologue_silent_wood", "The Silent Wood", icon="minecraft:oak_sapling", after=["start:clerics_worry"],
          text=["Sister Wren wants to know what's wrong with the forest. Go to the forest's edge after dusk and wait "
                "out one night.",
                "No fairies dance. The butterflies are gone. And something has scored the bark of the oldest tree."],
          tasks=[{"biome": "minecraft:forest", "title": "Go to the forest"},
                 {"be": {"night": True, "sky": True}, "title": "Wait at the forest's edge after dark"}],
          rewards=[give('minecraft:potion{Potion:"minecraft:night_vision"}', "A night vision potion")]),

    quest("prologue_shrine", "A Shrine for the Quiet", icon="minecraft:candle", after=["prologue_silent_wood"],
          text=["Sister Wren asks for a small wayside shrine: mossy stone, candles, and wildflowers gathered from "
                "three different places.",
                "Build it wherever feels right."],
          tasks=[item("minecraft:mossy_cobblestone", 16), item("minecraft:candle", 4), item("minecraft:cornflower"),
                 item("minecraft:allium"), item("minecraft:lily_of_the_valley"),
                 {"build": {"blocks": {"#minecraft:candles": 2, "#minecraft:flowers": 3, "minecraft:mossy_cobblestone": 4},
                            "radius": 6}, "title": "Build the wayside shrine"}],
          rewards=[reward_item("minecraft:candle", 8), skill("forage", 60)]),

    quest("prologue_home", "Somewhere to Come Back To", icon="minecraft:red_bed", after=["prologue_silent_wood"],
          text=["You can't sleep in a sleeping bag forever. Build your first home near Reece, with a bed, a chest, a "
                "table and chairs."],
          tasks=[item("minecraft:red_bed"), item("minecraft:chest"), item("handcrafted:oak_table"),
                 item("handcrafted:oak_chair", 2), {"build": {"blocks": {"#minecraft:beds": 1, "minecraft:chest": 1, "#minecraft:doors": 1}, "radius": 10},
                  "title": "Build your home: a bed, a chest and a door of your own"}],
          rewards=[reward_item("another_furniture:oak_chair", 2), skill("craft", 60)]),

    quest("prologue_fallen", "The Fallen Adventurer", icon="minecraft:skeleton_skull", after=["prologue_shrine"],
          text=["Out in the wild lie the remains of adventurers who never came home, still in their rusted gear.",
                "Find one. Something in the forest's silence points that way."],
          tasks=[{"observe": "realmrpg_skeletons:hunted_skeleton", "ticks": 20, "title": "Find a fallen adventurer"}],
          rewards=[reward_item("minecraft:stone_sword"), skill("agility", 60)]),

    quest("prologue_dungeon", "What the Dark Keeps", icon="minecraft:spawner", after=["prologue_fallen"],
          text=["The adventurer's journal speaks of 'the wardens growing weak', and points to an old dungeon.",
                "Clear a dungeon, and find the second journal page on one of its guardians."],
          tasks=[{"structure": "#yungs_dungeons", "title": "Find the dungeon"},
                 {"drop": {"from": ["minecraft:zombie", "minecraft:skeleton", "minecraft:spider"], "chance": 0.2,
                           "item": {"name": "Second Journal Page", "texture": "minecraft:item/paper"}},
                  "consume": False}],
          rewards=[reward_item("minecraft:iron_ingot", 8), skill("attack", 80)]),

    quest("prologue_letter", "Word to the Neighbours", icon="fotfmail:letter", after=["prologue_dungeon"],
          text=["Sister Wren writes to the cleric of the next village along the road. Deliver her letter in person; "
                "his reply will follow you home by post."],
          tasks=[talk_villager("minecraft:cleric", ["A letter from Sister Wren? It's been too long.",
                                                    "Tell her I'll write back. The post's slow, but it gets there."],
                               title="Deliver the letter to another village's cleric")],
          rewards=[reward_item("fotfmail:letter", 4), reward_item("minecraft:emerald", 5)]),
]

ACT1 = [
    quest("act1_start", "The First Wardens", icon="minecraft:written_book", shape="diamond", size=1.5,
          after=["prologue_letter", "prologue_home"],
          text=["Both journal pages together tell of guardians: the wardens, who hold the old places shut.",
                "Sister Wren has read them twice."],
          tasks=[talk_char("wren", ["The wardens hold the old places shut, and something is draining them.", "The first sleeps in iron under the hills. Take this blessed armour."])],
          rewards=[reward_item("minecraft:iron_chestplate")]),

    quest("act1_iron_kit", "Iron and Edge", icon="spartanweaponry:iron_longsword", after=["act1_start"],
          text=["Arm yourself for what's ahead: a proper weapon, a shield and full iron armour.",
                "Any Spartan Weaponry iron weapon will do; the quest asks for a longsword, but the choice is yours."],
          tasks=[item("spartanweaponry:iron_longsword"), item("spartanshields:iron_basic_shield"),
                 item("minecraft:iron_helmet"), item("minecraft:iron_leggings"), item("minecraft:iron_boots")],
          rewards=[{"item": "minecraft:enchanted_book", "enchant": {"minecraft:sharpness": 2}}, skill("attack", 80)]),

    quest("act1_temple", "Sand and Vine", icon="minecraft:chiseled_sandstone", after=["act1_start"],
          text=["Search a desert or jungle temple. Get past its traps to the inner chamber, where a mural shows a "
                "hooded iron giant."],
          tasks=[{"structure": "#temples", "title": "Reach a temple's inner chamber"},
                 {"search": {"at": {"structure": "#temples"}, "count": 1,
                             "item": {"name": "Temple Tablet", "tooltip": "A carved tablet: a hooded iron giant",
                                      "texture": "minecraft:item/brick"},
                             "found": "Among the offerings lies a carved tablet: a hooded giant of iron."},
                  "title": "Find what the temple remembers of the iron giant"}],
          rewards=[reward_item("minecraft:gold_ingot", 6), skill("agility", 80)]),

    quest("act1_mineshaft", "The Echo in the Shaft", icon="minecraft:rail", after=["act1_start"],
          text=["Miners in an old mineshaft heard metal footsteps below them. Explore it, mine 16 iron, and look for "
                "scrape marks leading down."],
          tasks=[{"structure": "#mines", "title": "Explore a mineshaft"}, item("minecraft:raw_iron", 16)],
          rewards=[reward_item("minecraft:lantern"), skill("mining", 80)]),

    quest("act1_wrought_practice", "Strike From Behind", icon="dummmmmmy:target_dummy",
          after=["act1_temple", "act1_mineshaft"],
          text=["Armour that breathes, in a sealed chamber. Captain Hale of the Village watch knows what that means, "
                "and wants you ready before you go anywhere near it."],
          tasks=[talk_char("hale", ["Iron giants turn slowly. Get behind it and strike.", "Practise on a dummy. Look first, fight later. And come back."]),
                 item("dummmmmmy:target_dummy")],
          rewards=[skill("defense", 80)]),

    quest("act1_wrought_scout", "The Iron Door", icon="minecraft:iron_door", after=["act1_wrought_practice"],
          text=["Follow the scrape marks to a Wrought Chamber and look at its sealed door. The armour inside is "
                "breathing."],
          tasks=[{"structure": "mowziesmobs:wrought_chamber", "title": "Find a Wrought Chamber"}],
          rewards=[reward_item("minecraft:spyglass")]),

    quest("act1_wroughtnaut", "The Ferrous Wroughtnaut", icon="minecraft:iron_axe", shape="diamond", size=1.5,
          after=["act1_wrought_scout", "act1_iron_kit"],
          text=["Wake the Ferrous Wroughtnaut and beat it. Dodge its axe and strike its exposed back, like Hale "
                "taught you."],
          tasks=[{"kill": "mowziesmobs:ferrous_wroughtnaut", "title": "Put the iron giant back to sleep",
                  "spawn": {"at": {"structure": "mowziesmobs:wrought_chamber"}, "wave": 1, "ensure": True}}],
          rewards=[reward_item("minecraft:golden_apple", 2), skill("attack", 200)]),

    quest("act1_wrought_report", "Rust on the Seal", icon="minecraft:iron_nugget", after=["act1_wroughtnaut"],
          text=["Take what you learned back to Sister Wren."],
          tasks=[talk_char("wren", ["You're alive. It wasn't evil. It was starving.", "Something fed on it for years. It's all of the wardens."])],
          rewards=[reward_item("minecraft:emerald", 8)]),

    quest("act1_magic_branch", "A Priest on the Road", icon="irons_spellbooks:scroll", after=["act1_wrought_report"],
          text=["On the road, a travelling priest of the Arcane order stops you. He's been following the same trail."],
          tasks=[{"encounter": {"entity": "minecraft:villager", "name": "Travelling Priest", "then": "talk",
                                "lines": ["The drain smells of old magic. Try the Pyromancer Tower.", "Its keepers know more than they say."]}}],
          rewards=[reward_item("irons_spellbooks:scroll"), reward_item("irons_spellbooks:common_ink")]),

    quest("act1_outpost", "Banners on the Hill", icon="minecraft:white_banner", after=["act1_wrought_report"],
          text=["Pillagers have raised an outpost near the trade road. Clear it and take down its captain."],
          tasks=[{"structure": "#illager_hideouts", "title": "Find the outpost"},
                 {"kill": "minecraft:pillager", "count": 6, "title": "Clear the outpost off the trade road",
                  "spawn": {"at": {"structure": "#illager_hideouts"}, "wave": 3}}],
          rewards=[reward_item("minecraft:crossbow"), reward_item("minecraft:arrow", 32)]),

    quest("act1_iceologer", "Frost on the Wind", icon="minecraft:packed_ice", after=["act1_outpost"],
          text=["A frightened trader comes looking for help: something froze his caravan in the snowy taiga."],
          tasks=[{"encounter": {"entity": "minecraft:wandering_trader", "name": "Frightened Trader", "then": "talk",
                                "lines": ["Ice, in a heartbeat. My caravan is frozen in the taiga.", "Stop it before it finds a village."]}},
                 {"encounter": {"entity": "friendsandfoes:iceologer", "name": "The Iceologer", "then": "kill",
                                "glow": True, "where": {"biomes": ["minecraft:snowy_taiga", "minecraft:taiga",
                                                                   "minecraft:grove", "minecraft:snowy_plains"]}}}],
          rewards=[reward_item("minecraft:leather_chestplate"), skill("attack", 120)]),

    quest("act1_illusioner", "Four of Him", icon="minecraft:bow", after=["act1_iceologer"],
          text=["An Illusioner haunts the woods. Find the real one among its copies and defeat it."],
          tasks=[{"encounter": {"entity": "minecraft:illusioner", "name": "The Trickster", "then": "kill",
                                "where": {"biomes": ["minecraft:forest", "minecraft:dark_forest",
                                                     "minecraft:birch_forest"]}}}],
          rewards=[{"item": "minecraft:bow", "name": "Trickster's Bow", "enchant": {"minecraft:power": 2}},
                   skill("range", 120)]),

    quest("act1_raid", "The Long Night", icon="minecraft:totem_of_undying", after=["act1_illusioner"],
          text=["Captain Hale has a plan: draw the raiders out on your terms. Carry the Bad Omen into a village and "
                "hold it through a full raid."],
          tasks=[talk_char("hale", ["We fight at the village edge. Nobody gets near the fields.", "...Marta's fields. All the farms, equally. Bring the omen."]),
                 {"advancement": "minecraft:adventure/hero_of_the_village"}],
          rewards=[reward_item("minecraft:totem_of_undying"), skill("defense", 200)]),

    quest("act1_umvuthana_scout", "Masks in the Grass", icon="minecraft:acacia_sapling", after=["act1_raid"],
          text=["Travel to the savanna and find the Umvuthana Grove. Watch the Umvuthana from cover and count their "
                "masks."],
          tasks=[{"structure": "mowziesmobs:umvuthana_grove", "title": "Find the grove"},
                 {"observe": "mowziesmobs:umvuthana", "ticks": 60, "title": "Watch an Umvuthana"}],
          rewards=[skill("agility", 120)]),

    quest("act1_umvuthi", "Umvuthi, the Sunbird", icon="minecraft:sunflower", shape="diamond", size=1.5,
          after=["act1_umvuthana_scout"],
          text=["Face Umvuthi and its followers in the heart of the grove. Break the circle of masks before the sun "
                "spell lands."],
          tasks=[{"kill": "mowziesmobs:umvuthi", "title": "Break the circle of masks",
                  "spawn": {"at": {"structure": "mowziesmobs:umvuthana_grove"}, "wave": 1, "ensure": True}}],
          rewards=[reward_item("minecraft:diamond", 3), skill("attack", 250)]),

    quest("act1_finale", "A Door in the Flowers", icon="minecraft:diamond", shape="diamond", size=1.75,
          after=["act1_umvuthi", "act1_wroughtnaut"],
          text=["With two wardens freed, Sister Wren remembers the spirits' own realm.",
                "Dig a pool, ring it with flowers and drop a diamond in. The way into the Twilight Forest opens."],
          tasks=[{"dimension": "twilightforest:twilight_forest", "title": "Enter the Twilight Forest"}],
          rewards=[reward_item("minecraft:diamond"), skill("magic", 150)]),
]


def boss(entity, at, name, title, **extra):
    """A boss kill: the boss is brought in when none is there."""
    spawn = {"at": {"structure": at}, "wave": 1, "ensure": True, "name": name}
    spawn.update(extra)
    return {"kill": entity, "spawn": spawn, "title": title}


def fight(entity, count, at, name, title, wave=4, **extra):
    spawn = {"at": {"structure": at}, "wave": wave, "name": name}
    spawn.update(extra)
    return {"kill": entity, "count": count, "spawn": spawn, "title": title}


def search(at, count, name, found, texture="minecraft:item/paper", title=None):
    return {"search": {"at": {"structure": at}, "count": count,
                       "item": {"name": name, "texture": texture}, "found": found},
            "title": title or ("Search for " + name)}


def enc(lines, title=None, **spec):
    t = encounter(lines, **spec)
    if title:
        t["title"] = title
    return t


ACT2 = [
    quest("act2_start", "Where the Spirits Went", icon="twilightforest:magic_map", after=["act1_finale"],
          text=["Step through into the Twilight Forest and find its quest grove. The forest spirits Notch set "
                "to guard the woods fled here, and they know what is draining the wardens."],
          tasks=[{"dimension": "twilightforest:twilight_forest", "title": "Step into the Twilight Forest"},
                 {"structure": "twilightforest:quest_grove", "title": "Find the quest grove where the spirits hide"},
                 enc(["We hid. Something rises from below, hungry.", "It drains the wardens, one by one."],
                     entity="minecraft:allay", name="Forest Spirit", title="Hear the hiding spirits")],
          rewards=[reward_item("twilightforest:magic_map"), skill("magic", 160)]),

    quest("act2_twilight_branch", "The Twilight Calls (Part 1)", icon="twilightforest:naga_trophy",
          after=["act2_start"],
          text=["The spirits ask you to lift the first curses on their forest: the Naga in its courtyard, and the "
                "Lich in its tower. The Twilight Forest questline holds the rest of this realm."],
          tasks=[boss("twilightforest:naga", "twilightforest:naga_courtyard", "The Naga",
                      "Defeat the Naga coiled in its courtyard"),
                 boss("twilightforest:lich", "twilightforest:lich_tower", "The Lich",
                      "Defeat the Lich in its tower")],
          rewards=[reward_item("twilightforest:naga_scale", 6), reward_item("twilightforest:naga_trophy"),
                   skill("attack", 350)]),

    quest("act2_frostmaw_tale", "Ice Where None Should Be", icon="minecraft:snowball", after=["act2_start"],
          text=["Reece's shepherd lost a flock to a white beast in the snowy hills. The spirits name it Frostmaw, a "
                "warden of winter woken too early."],
          tasks=[talk_villager("minecraft:shepherd", ["A white beast took my flock. Tracks like pits in the snow.",
                                                      "The spirits call it Frostmaw. Find it before winter does."],
                               title="Hear the shepherd's loss")],
          rewards=[reward_item("minecraft:leather_boots", name="Winterwalkers", lore=["Frost-resistant boots."],
                               enchant={"minecraft:frost_walker": 1}), skill("defense", 160)]),

    quest("act2_frostmaw_trail", "Tracks in the Snow", icon="minecraft:campfire", after=["act2_frostmaw_tale"],
          text=["Follow broken ice and frozen carcasses across the snow to where Frostmaw sleeps, and leave a ring "
                "of lit campfires at its den so it cannot freeze you."],
          tasks=[{"biome": "minecraft:snowy_plains", "title": "Follow the frozen carcasses into the snow"},
                 {"structure": "mowziesmobs:frostmaw_spawn", "title": "Find Frostmaw's den"},
                 {"build": {"blocks": {"minecraft:campfire": 4}, "radius": 10}, "title": "Light a ring of campfires at the den"}],
          rewards=[reward_item("minecraft:fire_charge", 8), skill("range", 200)]),

    quest("act2_frostmaw", "Frostmaw", icon="mowziesmobs:frostmaw_spawn_egg", shape="diamond", size=1.5,
          after=["act2_frostmaw_trail"],
          text=["Wake Frostmaw and defeat it without letting its ice breath freeze you to the ground."],
          tasks=[boss("mowziesmobs:frostmaw", "mowziesmobs:frostmaw_spawn", "Frostmaw", "Defeat Frostmaw at its den")],
          rewards=[reward_item("minecraft:golden_apple", 3), skill("defense", 400)]),

    quest("act2_ice_crystal", "The Cold Heart", icon="mowziesmobs:ice_crystal", after=["act2_frostmaw"],
          text=["Frostmaw leaves an Ice Crystal behind, flecked with dark veins. As you pick it up, Sister Wren "
                "arrives with a letter: the veins are proof that the drain comes from deep underground."],
          tasks=[item("mowziesmobs:ice_crystal", title="Pick up the Ice Crystal Frostmaw left behind"),
                 enc(["The veins match the drain. It comes from deep underground.", "Find a way below, child."],
                     character="wren", title="Hear Sister Wren's news")],
          rewards=[reward_item("mowziesmobs:frostmaw_plushie"), skill("magic", 200)]),

    quest("act2_cave_map", "A Map of the Underworld", icon="alexscaves:cave_map", after=["act2_ice_crystal"],
          text=["A cartographer sells the way below: an Alex's Caves cave map. Follow it to your first cave biome. "
                "The Underworld questline takes over there."],
          tasks=[talk_villager("minecraft:cartographer", ["Caves below the caves. I've charted a cabin.",
                                                          "Take the map. Mind the dark."],
                               title="Buy a cave map from a cartographer"),
                 item("alexscaves:cave_map", title="Carry the cave map"),
                 {"structure": "alexscaves:underground_cabin", "title": "Follow the map to the underground cabin"}],
          rewards=[reward_item("alexscaves:bioluminescent_torch", 16), skill("mining", 250)]),

    quest("act2_caves_beat", "Roots of the Drain", icon="alexscaves:amber", after=["act2_cave_map"],
          text=["In the Primordial Caves and the Forlorn Hollows, amber and pure darkness hum with the same dark "
                "pulse as the crystal. Gather both as proof."],
          tasks=[{"structure": "alexscaves:dino_bowl", "title": "Find the Primordial Caves"},
                 {"structure": "alexscaves:forlorn_canyon", "title": "Find the Forlorn Hollows"},
                 item("alexscaves:amber", 4, title="Gather amber humming with the pulse"),
                 item("alexscaves:pure_darkness", 4, title="Gather pure darkness humming with the pulse")],
          rewards=[reward_item("minecraft:iron_pickaxe", name="Hollow Delver", lore=["For the Forlorn Hollows."],
                               enchant={"minecraft:efficiency": 3}), skill("mining", 300)]),

    quest("act2_monument_prep", "Breath of the Deep", icon="minecraft:turtle_helmet", after=["act2_ice_crystal"],
          text=["An ocean monument holds a warden, and you will need to breathe. Brew water breathing and night "
                "vision for the dive, and enchant a helmet for the depths."],
          tasks=[item("minecraft:potion", 2, consume=True, title="Brew potions to breathe and see underwater"),
                 item("minecraft:diamond_helmet", title="Bring a helmet to enchant for the depths"),
                 {"build": {"blocks": {"minecraft:enchanting_table": 1}, "radius": 8},
                  "title": "Set an enchanting table to prepare the helmet"}],
          rewards=[reward_item("minecraft:prismarine_shard", 16), reward_item("minecraft:turtle_helmet"),
                   skill("magic", 250)]),

    quest("act2_elder_guardian", "The Elder of the Sea", icon="minecraft:heart_of_the_sea",
          after=["act2_monument_prep"],
          text=["Dive into an ocean monument and defeat one of its Elder Guardians, the ocean's own warden, half "
                "drained already."],
          tasks=[{"structure": "betteroceanmonuments:ocean_monument", "title": "Dive to the ocean monument"},
                 boss("minecraft:elder_guardian", "betteroceanmonuments:ocean_monument", "The Elder Guardian",
                      "Defeat the monument's Elder Guardian")],
          rewards=[reward_item("minecraft:sponge", 4), reward_item("minecraft:heart_of_the_sea"), skill("defense", 400)]),

    quest("act2_pyramid_scout", "The Sealed Pyramid", icon="cataclysm:koboleton_bone", after=["act2_caves_beat"],
          text=["Scout a Cursed Pyramid in the desert: clear its outer halls of Koboletons and defeat a "
                "Kobolediator for Ancient Metal. Copy the runes on its sealed inner door while you are there."],
          tasks=[fight("cataclysm:koboleton", 6, "cataclysm:cursed_pyramid", "Pyramid Koboletons",
                       "Clear the pyramid's outer halls"),
                 fight("cataclysm:kobolediator", 1, "cataclysm:cursed_pyramid", "The Kobolediator",
                       "Defeat the Kobolediator for Ancient Metal", wave=1),
                 search("cataclysm:cursed_pyramid", 1, "Door Runes (Pyramid)", "Runes of the Door of Seal, copied in charcoal.",
                        title="Copy the runes on the sealed inner door")],
          rewards=[reward_item("cataclysm:ancient_metal_nugget", 8), skill("attack", 350)]),

    quest("act2_prison_scout", "The Frosted Prison", icon="cataclysm:aptrgangr_head", after=["act2_pyramid_scout"],
          text=["Scout a Frosted Prison in the snowy plains and defeat an Aptrgangr guarding its gate for Black "
                "Steel. The inner door is sealed and something vast sleeps behind it. Copy the runes on it too."],
          tasks=[boss("cataclysm:aptrgangr", "cataclysm:frosted_prison", "The Gatekeeper",
                      "Defeat the Aptrgangr guarding the gate"),
                 search("cataclysm:frosted_prison", 1, "Door Runes (Prison)", "Runes of the Door of Seal, frost-rimed.",
                        title="Copy the runes on the sealed inner door")],
          rewards=[reward_item("cataclysm:black_steel_ingot", 2), skill("attack", 380)]),

    quest("act2_sealed_doors", "Doors That Will Not Open", icon="minecraft:writable_book",
          after=["act2_prison_scout"],
          text=["Bring both copies of the Door of Seal runes to the Arcane Order's librarian: eight seals, eight "
                "sleepers, and none can be broken yet."],
          tasks=[talk_org("arcane", ["Two copies of the same seal. Eight sleepers, then.",
                                     "None can be broken yet. Keep these runes safe."],
                          title="Show the rune copies to the Arcane Order")],
          rewards=[reward_item("minecraft:writable_book", name="Runed Tablet", lore=["The Door of Seal, copied twice."]),
                   skill("magic", 300)]),

    quest("act2_scout_steel", "Steel From the Sleepers", icon="spartancataclysm:ancient_metal_greatsword",
          after=["act2_sealed_doors"],
          text=["The guardians' metal is sound, and the sleepers will be hard to hurt. Forge a Cataclysm weapon from "
                "the Ancient Metal or Black Steel you took."],
          tasks=[item("spartancataclysm:ancient_metal_greatsword", crafted=True,
                      title="Forge a weapon from the guardians' metal")],
          rewards=[reward_item("minecraft:grindstone"), skill("attack", 380)]),

    quest("act2_monastery_climb", "The Peak Above the Clouds", icon="grapplemod:grapplinghook",
          after=["act2_elder_guardian", "act2_scout_steel"],
          text=["The last Overworld warden waits at a mountaintop Monastery. Climb the peak with ParCool moves and "
                "a grappling hook before the storm closes in."],
          tasks=[{"timed": {"seconds": 600, "goal": {"structure": "mowziesmobs:monastery", "label": "the Monastery", "away": 150},
                            "lines": ["The storm is closing in. Climb!"], "start": "Begin the climb",
                            "no": ["teleport", "mounts"]}, "title": "Climb to the Monastery before the storm"}],
          rewards=[reward_item("grapplemod:grapplinghook"), skill("agility", 380)]),

    quest("act2_sculptor", "The Sculptor", icon="mowziesmobs:sculptor_spawn_egg", shape="diamond", size=1.5,
          after=["act2_monastery_climb"],
          text=["Climb the Sculptor's pillar trial while it reshapes the stone beneath you, then defeat it."],
          tasks=[boss("mowziesmobs:sculptor", "mowziesmobs:monastery", "The Sculptor",
                      "Defeat the Sculptor in its trial")],
          rewards=[reward_item("minecraft:diamond", 5), skill("agility", 400)]),

    quest("act2_finale", "The Red Glow", icon="minecraft:obsidian", shape="diamond", size=1.75,
          after=["act2_sculptor", "act2_frostmaw", "act2_twilight_branch"],
          text=["From the peak you see a red scar on the horizon: a ruined portal. Repair or build a Nether portal "
                "and step into the Nether for the first time."],
          tasks=[item("minecraft:obsidian", 10, title="Gather obsidian for the portal frame"),
                 {"build": {"blocks": {"minecraft:obsidian": 10}, "radius": 8}, "title": "Raise the portal frame"},
                 {"dimension": "minecraft:the_nether", "title": "Step into the Nether"}],
          rewards=[reward_item("minecraft:magma_cream", 4), reward_item("minecraft:golden_carrot", 8),
                   skill("agility", 300)]),
]

ACT3 = [
    quest("act3_start", "The Burning Realm", icon="minecraft:netherrack", after=["act2_finale"],
          text=["In the Nether, a lost Reece courier hides in a ruin. She saw the drain's threads running toward the "
                "fortresses."],
          tasks=[{"dimension": "minecraft:the_nether", "title": "Cross into the Nether"},
                 {"structure": "#nether_outposts", "title": "Find the ruin where the lost courier hides"},
                 enc(["Thank Notch, someone from Reece! The threads all run toward the fortresses.", "Take my map."],
                     entity="minecraft:villager", name="Lost Courier", title="Find the lost Reece courier")],
          rewards=[reward_item("minecraft:golden_chestplate"), reward_item("minecraft:map"), skill("agility", 300)]),

    quest("act3_fortress", "Blaze and Bone", icon="minecraft:blaze_rod", after=["act3_start"],
          text=["The drain's threads end at the fortresses. Raid a Nether fortress for blaze rods and nether wart "
                "to brew what you will need."],
          tasks=[{"structure": "betterfortresses:fortress", "title": "Find a Nether fortress"},
                 fight("minecraft:blaze", 6, "betterfortresses:fortress", "Fortress Blazes", "Fight the fortress's blazes"),
                 item("minecraft:blaze_rod", 12, title="Take blaze rods for brewing"),
                 item("minecraft:nether_wart", 8, title="Take nether wart for brewing")],
          rewards=[reward_item("minecraft:brewing_stand"), skill("attack", 350)]),

    quest("act3_eyes", "Eyes That See", icon="minecraft:ender_eye", after=["act3_fortress"],
          text=["The wardens' homes are hidden. Craft Eyes of Ender to find the way."],
          tasks=[item("minecraft:ender_eye", 3, crafted=True, title="Craft Eyes of Ender to find the wardens' homes")],
          rewards=[reward_item("minecraft:ender_pearl", 8), skill("magic", 300)]),

    quest("act3_wildfire_scout", "The Citadel of Flame", icon="minecraft:fire_charge", after=["act3_fortress"],
          text=["Find the Nether citadel and slip past its blazes to see the Wildfire on its throne."],
          tasks=[{"structure": "friendsandfoes:citadel", "title": "Find the citadel of flame"},
                 {"timed": {"seconds": 300, "goal": {"structure": "friendsandfoes:citadel", "label": "the Wildfire's throne room", "away": 40},
                            "lines": ["Blazes watch the halls. If anything burns you, they've seen you."], "start": "Slip in",
                            "no": ["hurt"]}, "title": "Slip past the blazes to the throne room unseen"}],
          rewards=[reward_item("minecraft:magma_cream", 4), reward_item("minecraft:golden_carrot", 8), skill("agility", 320)]),

    quest("act3_wildfire", "The Wildfire", icon="friendsandfoes:wildfire_crown_fragment", shape="diamond", size=1.5,
          after=["act3_wildfire_scout"],
          text=["Defeat the Wildfire by breaking its shields and dodging its fire waves."],
          tasks=[boss("friendsandfoes:wildfire", "friendsandfoes:citadel", "The Wildfire", "Defeat the Wildfire on its throne")],
          rewards=[reward_item("friendsandfoes:wildfire_crown_fragment"), skill("attack", 500)]),

    quest("act3_debris", "Debris From Below", icon="minecraft:ancient_debris", after=["act3_start"],
          text=["The deepest metal is buried deep in the Nether. Mine ancient debris, and watch your footing."],
          tasks=[item("minecraft:ancient_debris", 8, title="Mine ancient debris deep in the Nether")],
          rewards=[reward_item("minecraft:tnt", 8), skill("mining", 400)]),

    quest("act3_netherite", "The Black Smith", icon="minecraft:netherite_upgrade_smithing_template", after=["act3_debris"],
          text=["Netherite needs a template to be worked. Loot one from a bastion and upgrade your first netherite "
                "piece."],
          tasks=[{"structure": "minecraft:bastion_remnant", "title": "Find a bastion remnant"},
                 item("minecraft:netherite_upgrade_smithing_template", title="Loot a netherite upgrade template"),
                 item("minecraft:netherite_ingot", crafted=True, title="Smelt your first netherite ingot")],
          rewards=[reward_item("minecraft:netherite_upgrade_smithing_template"), skill("craft", 450)]),

    quest("act3_twilight_branch", "The Twilight Calls (Part 2)", icon="spartantwilight:fiery_battleaxe",
          after=["act3_netherite", "act2_twilight_branch"],
          text=["The spirits' second curse: defeat the Hydra in its fiery lair, and forge a Fiery weapon from its "
                "blood. The Twilight questline continues."],
          tasks=[boss("twilightforest:hydra", "twilightforest:hydra_lair", "The Hydra", "Defeat the Hydra in its fiery lair"),
                 item("spartantwilight:fiery_battleaxe", crafted=True, title="Forge a Fiery weapon from its blood")],
          rewards=[reward_item("twilightforest:fiery_ingot", 2), skill("attack", 550)]),

    quest("act3_dead_king", "The Dead King's Crypt", icon="irons_spellbooks:furled_map", after=["act3_start"],
          text=["Optional: the Arcane Order traces the drain to Iron's Catacombs and the Dead King. Reaching the "
                "catacombs opens the magic questline's chain, which holds the fight."],
          tasks=[talk_org("arcane", ["The drain runs to the catacombs. The Dead King sleeps there.", "Take this map."],
                          title="Ask the Arcane Order where the drain leads"),
                 {"structure": "irons_spellbooks:catacombs", "title": "Reach the catacombs the Order names"}],
          rewards=[reward_item("irons_spellbooks:furled_map"), skill("magic", 350)]),

    quest("act3_skulls", "Three Black Skulls", icon="minecraft:wither_skeleton_skull", after=["act3_wildfire", "act3_netherite"],
          text=["The Wither needs three wither skeleton skulls. Hunt wither skeletons in fortresses. A fourth, cursed "
                "one only drops while this quest is open."],
          tasks=[fight("minecraft:wither_skeleton", 6, "betterfortresses:fortress", "Fortress Wither Skeletons",
                       "Hunt wither skeletons in a fortress"),
                 item("minecraft:wither_skeleton_skull", 3, title="Hold three wither skeleton skulls"),
                 sample("a Cursed Skull", ["minecraft:wither_skeleton"], 0.3, texture="minecraft:item/wither_skeleton_skull",
                        tooltip="Only drops while the quest is open")],
          rewards=[reward_item("minecraft:enchanted_book", name="Hunter's Greed", enchant={"minecraft:looting": 3}),
                   skill("attack", 450)]),

    quest("act3_wither", "The Wither", icon="minecraft:nether_star", shape="diamond", size=1.5, after=["act3_skulls"],
          text=["Summon the Wither far from Reece, in a pit you dig deep underground, and destroy it. The world's "
                "wardens are being turned. This one was made to be."],
          tasks=[item("minecraft:soul_sand", 4, title="Bring soul sand for the summoning"),
                 {"build": {"blocks": {"minecraft:soul_sand": 4, "minecraft:wither_skeleton_skull": 3}, "radius": 8},
                  "title": "Build the summoning in a pit far from Reece"},
                 {"kill": "minecraft:wither", "title": "Destroy the Wither in its pit"}],
          rewards=[reward_item("minecraft:nether_star"), skill("attack", 600)]),

    quest("act3_beacon", "A Light for Reece", icon="minecraft:beacon", after=["act3_wither"],
          text=["Build a beacon on a pyramid in Reece's square so the village has a light the drain can't reach."],
          tasks=[{"place": "reece"},
                 {"build": {"blocks": {"minecraft:beacon": 1, "minecraft:iron_block": 9}, "radius": 12},
                  "title": "Raise a beacon on a pyramid in Reece's square"}],
          rewards=[reward_item("minecraft:iron_block", 4), skill("defense", 450)]),

    quest("act3_hullbreaker", "Something Below the Chasm", icon="alexscaves:diving_helmet", after=["act3_netherite"],
          text=["Optional: a diver's logbook speaks of something huge circling a ruined submarine in the Abyssal "
                "Chasm. Finding the trench opens the Alex's Caves chain, which holds the Hullbreaker fight."],
          tasks=[{"structure": "alexscaves:ocean_trench", "title": "Find the trench the logbook names"},
                 {"structure": "alexscaves:abyssal_ruins", "title": "Find the ruined submarine below"}],
          rewards=[reward_item("minecraft:map"), skill("defense", 300)]),

    quest("act3_tremorsaurus", "Something Big Hatches", icon="alexscaves:cooked_dinosaur_chop", after=["act3_netherite"],
          text=["Optional: find a tremorsaurus egg near the primordial volcano and raise the hatchling, or fight a "
                "wild tremorsaurus."],
          tasks=[{"structure": "alexscaves:volcano", "title": "Search the volcano's slopes for an egg"},
                 {"tame": "alexscaves:tremorsaurus", "title": "Raise the hatchling until it follows you"}],
          rewards=[reward_item("alexscaves:cooked_dinosaur_chop", 8), skill("taming", 450)]),

    quest("act3_finale", "Where the Eyes Fall", icon="minecraft:ender_eye", after=["act3_beacon", "act3_twilight_branch"],
          text=["Throw Eyes of Ender across the land until they dive, then dig down into a stronghold."],
          tasks=[item("minecraft:ender_eye", 6, title="Gather Eyes of Ender to throw"),
                 {"structure": "betterstrongholds:stronghold", "title": "Follow the eyes down into a stronghold"}],
          rewards=[reward_item("minecraft:ender_eye", 8), skill("agility", 500)]),
]

chapter("main_story", "The Silent Forest", "The main story", "minecraft:written_book", "story", 0,
        PROLOGUE + ACT1 + ACT2 + ACT3)
