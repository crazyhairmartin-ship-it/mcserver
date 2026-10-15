"""Chapter: skill_crafting, the Crafters' Guild path: prologue and Act I (first release).
Plan: src/plans/quests/skill_crafting.json. Master Joiner Odile Brask keeps the guild workshop in Reece."""
from common import chapter, quest, talk_char, item, reward_item, skill, giver_org, encounter
from common import enc, fight, boss, search, sample, talk_org, talk_villager, talk_char, item, reward_item, skill, encounter, giver_org  # noqa: F401

Q = [
    quest("apprentice_papers", "Apprentice Papers", icon="handcrafted:oak_table",
          giver=giver_org("crafters", ["The guild workshop in Reece is an empty barn.", "Make a table and two chairs, and Master Joiner Brask will sign you on."], "I'll sign on"),
          text=["The guild's workshop in Reece is an empty barn. Show you can join wood by making a table and two "
                "chairs for the bare hall."],
          tasks=[item("handcrafted:oak_table", crafted=True), item("handcrafted:oak_chair", 2, crafted=True),
                 talk_char("odile", ["Turn them over. A joint you can't see still has to be true.", "They'll do. More than do. Welcome, apprentice."])],
          rewards=[reward_item("handcrafted:hammer"), reward_item("minecraft:oak_planks", 64),
                   skill("craft", 60)]),

    quest("workshop_walls", "Benches and Boards", icon="supplementaries:notice_board", after=["apprentice_papers"],
          text=["Fit out the workshop: workbenches, item shelves for tools and a notice board where commissions "
                "will be pinned."],
          tasks=[{"place": "reece"},
                 {"build": {"blocks": {"minecraft:crafting_table": 2, "supplementaries:item_shelf": 2,
                                       "supplementaries:notice_board": 1}, "radius": 12},
                  "title": "Fit out the workshop"}],
          rewards=[reward_item("supplementaries:notice_board"), skill("craft", 90)]),

    quest("widows_cottage", "A Home Again", icon="handcrafted:oak_fancy_bed", after=["workshop_walls"],
          text=["A widow's cottage was stripped bare by thieves. Make her a fancy bed, a cupboard, a nightstand and "
                "cushions, and set them in place."],
          tasks=[{"structure": "#villages", "title": "Find the widow's cottage"},
                 {"build": {"blocks": {"handcrafted:oak_fancy_bed": 1, "handcrafted:oak_cupboard": 1,
                                       "handcrafted:oak_nightstand": 1, "handcrafted:blue_cushion": 2},
                            "radius": 10}, "title": "Furnish the cottage"},
                 encounter(["It feels like home again. Thank you, dear.", "Take my husband's tools. He'd want a joiner to have them."],
                           entity="minecraft:villager", name="The Widow")],
          rewards=[reward_item("handcrafted:berry_jam_jar"), reward_item("minecraft:iron_axe"),
                   reward_item("minecraft:iron_pickaxe"), skill("craft", 130)]),

    quest("sacks_and_jars", "A Place for Everything", icon="supplementaries:sack", after=["workshop_walls"],
          text=["The workshop floor is a mess of loose materials. Make sacks, jars and a safe and sort the guild's "
                "stock into them."],
          tasks=[item("supplementaries:sack", 2, crafted=True), item("supplementaries:jar", 3, crafted=True),
                 item("supplementaries:safe", crafted=True)],
          rewards=[reward_item("supplementaries:key"), reward_item("supplementaries:safe"), skill("craft", 100)]),

    quest("road_comforts", "Sleeping Rough, Sleeping Well", icon="comforts:hammock_red", after=["apprentice_papers"],
          text=["Guild members travelling to far commissions sleep on the ground. Sew sleeping bags and hammocks "
                "and hand them out at the guild camp."],
          tasks=[item("comforts:rope_and_nail", 2, crafted=True), item("comforts:sleeping_bag_blue", crafted=True),
                 item("comforts:hammock_red", crafted=True), {"structure": "#camps", "title": "Find a camp"},
                 {"checkmark": "I handed out the bedding"}],
          rewards=[reward_item("comforts:hammock_green"), skill("craft", 100)]),

    quest("megatorch", "Light the Square", icon="torchmaster:megatorch", after=["widows_cottage"],
          text=["Zombies keep wandering into the village square at night. Build a megatorch at its centre and hold "
                "the square through the night."],
          tasks=[{"structure": "#villages", "title": "Reach the village square"},
                 item("torchmaster:megatorch", crafted=True),
                 {"build": {"blocks": {"torchmaster:megatorch": 1}, "radius": 8}, "title": "Set the megatorch"},
                 {"timed": {"seconds": 240, "goal": {"hold": {"radius": 24}},
                            "lines": ["Night's coming. Let's see if the megatorch holds."],
                            "start": "Hold the square"}, "title": "Hold the square for the night"}],
          rewards=[reward_item("minecraft:lantern", 8), skill("craft", 160)]),

    quest("tavern_refit", "Last Orders", icon="furniture:oak_grandfather_clock", after=["widows_cottage"],
          text=["A tavern keeper wants her old tavern refitted before the travelling season: a grandfather clock, a "
                "cash register, benches, curtains and a fish tank."],
          tasks=[{"structure": "#taverns", "title": "Find the tavern"},
                 {"build": {"blocks": {"furniture:oak_grandfather_clock": 1, "furniture:cash_register": 1,
                                       "furniture:oak_bench": 2, "furniture:curtain_red": 2,
                                       "furniture:copper_fish_tank": 1}, "radius": 12},
                  "title": "Refit the tavern"}],
          rewards=[reward_item("furniture:boat_in_a_jar"), reward_item("minecraft:cooked_beef", 8),
                   reward_item("minecraft:bread", 8), skill("craft", 170)]),

    quest("village_square", "Somewhere to Sit", icon="another_furniture:oak_bench", after=["megatorch"],
          text=["With the square lit, the elders want somewhere to sit and talk. Furnish it with benches, flower "
                "boxes, awnings and lamps."],
          tasks=[{"structure": "#villages", "title": "Reach the square"},
                 {"build": {"blocks": {"another_furniture:oak_bench": 2, "another_furniture:oak_flower_box": 2,
                                       "another_furniture:red_awning": 2, "another_furniture:red_lamp": 2},
                            "radius": 12}, "title": "Furnish the square"}],
          rewards=[reward_item("minecraft:poppy", 6), reward_item("minecraft:dandelion", 6),
                   skill("craft", 190)]),

    quest("washed_out_bridge", "The Washed-Out Bridge", icon="mcwbridges:oak_log_bridge_middle",
          after=["village_square"],
          text=["Spring floods took the bridge over the stream that feeds Reece's lake, and farmers are wading "
                "across. Rebuild it with piers, rails and bridge lanterns."],
          tasks=[{"place": "reece"},
                 {"build": {"blocks": {"mcwbridges:oak_bridge_pier": 2, "mcwbridges:oak_log_bridge_middle": 4,
                                       "mcwbridges:bridge_lantern": 2}, "radius": 12},
                  "title": "Rebuild the bridge"}],
          rewards=[reward_item("minecraft:stone_bricks", 64), reward_item("minecraft:wheat", 32),
                   skill("craft", 210)]),

    quest("joiners_pack", "The Travelling Joiner", icon="sophisticatedbackpacks:backpack", after=["road_comforts"],
          text=["Odile gives you her old backpack pattern. Make a Sophisticated Backpack and fit it with a crafting "
                "upgrade so you can build on site."],
          tasks=[item("sophisticatedbackpacks:backpack", crafted=True),
                 item("sophisticatedbackpacks:crafting_upgrade", crafted=True)],
          rewards=[reward_item("sophisticatedbackpacks:stack_upgrade_tier_1"), skill("craft", 180)]),

    quest("painted_signs", "Fresh Paint", icon="amendments:dye_bottle", after=["village_square"],
          text=["The shop signs have faded to nothing, and nobody can find the baker. Mix dye bottles, repaint the "
                "signs and hang the right wares on each shopfront."],
          tasks=[{"structure": "#villages", "title": "Reach the faded shopfronts"},
                 item("amendments:dye_bottle", 4, crafted=True), item("minecraft:oak_sign", 4),
                 {"checkmark": "I repainted the signs and hung the right wares"}],
          rewards=[reward_item("amendments:dye_bottle", 8), skill("craft", 210)]),

    quest("engineers_blueprints", "The Engineer's Blueprints", icon="furniture:blueprints",
          after=["washed_out_bridge"],
          text=["The guild's founder lived in an engineer's tower out in the wilds and left plans for a better "
                "workshop. Climb the tower and find his blueprints."],
          tasks=[{"structure": "structory_towers:engineer_tower", "title": "Find the engineer's tower"},
                 item("furniture:blueprints", title="Find the blueprints")],
          rewards=[reward_item("minecraft:writable_book", name="The Founder's Journal",
                               lore=["Notes from the guild's founder, in a careful hand."]),
                   skill("craft", 280)]),
]

ACT2 = [
    quest("rival_carpenter", "Two Rooms, One Judge", icon="handcrafted:oak_cupboard",
          after=["engineers_blueprints", "tavern_refit"],
          text=["A swaggering carpenter from a rival village turns up and challenges the guild. Each furnishes an "
                "identical empty room, and the villagers vote on the better one."],
          tasks=[enc(["Your guild's famous? My rooms are better. Prove otherwise."], entity="minecraft:villager",
                     name="Rival Carpenter", title="Take up the rival carpenter's challenge"),
                 {"structure": "#villages", "title": "Reach the village where the rooms are judged"},
                 {"build": {"blocks": {"handcrafted:oak_table": 1, "handcrafted:oak_chair": 2, "handcrafted:oak_shelf": 1,
                                       "handcrafted:oak_cupboard": 1, "minecraft:red_bed": 1}, "radius": 8},
                  "title": "Furnish your room for the villagers' vote"}],
          rewards=[reward_item("handcrafted:hammer"), reward_item("minecraft:iron_ingot", 8), skill("craft", 300)]),

    quest("ruined_town", "Raise the Ruin", icon="minecraft:bell", after=["engineers_blueprints"],
          text=["Refugees from a burned town want to go home. Find the ruined town, clear it, and rebuild houses and a "
                "bridge with furniture so the first families can move back in."],
          tasks=[{"structure": "nova_structures:ruin_town", "title": "Find the burned town"},
                 search("nova_structures:ruin_town", 2, "a Family Deed", "A scorched deed to a plot, its seal intact.",
                        title="Search the ruins for the families' deeds"),
                 {"build": {"blocks": {"minecraft:oak_planks": 40, "#minecraft:doors": 3, "#minecraft:beds": 3,
                                       "mcwbridges:oak_bridge_pier": 2}, "radius": 12},
                  "title": "Rebuild houses and a bridge for the returning families"}],
          rewards=[reward_item("minecraft:bell"), skill("craft", 320)]),

    quest("guild_warehouse", "The Warehouse", icon="obscuras_storage:crafting_terminal",
          after=["sacks_and_jars", "engineers_blueprints"],
          text=["The founder's blueprints show a warehouse under the workshop. Dig it out and wire it with storage "
                "cables, connectors and a crafting terminal."],
          tasks=[item("obscuras_storage:inventory_cable", 8, crafted=True, title="Make cables for the warehouse"),
                 item("obscuras_storage:inventory_connector", 2, crafted=True, title="Make connectors for the chests"),
                 item("obscuras_storage:crafting_terminal", crafted=True, title="Make the terminal the founder drew"),
                 {"place": "reece"},
                 {"build": {"blocks": {"obscuras_storage:crafting_terminal": 1, "obscuras_storage:inventory_cable": 6},
                            "radius": 12}, "title": "Wire the workshop's warehouse"}],
          rewards=[reward_item("obscuras_storage:crafting_terminal"), skill("craft", 320)]),

    quest("sorting_room", "The Sorting Room", icon="artifacts:universal_attractor", after=["guild_warehouse"],
          signature="artifacts:universal_attractor",
          text=["Odile commissions a sorting room where every delivery sorts itself: item filters and hoppers into the "
                "right crates. When it works, she gives you her prototype attractor."],
          tasks=[item("obscuras_storage:item_filter", 2, crafted=True, title="Make filters to sort the deliveries"),
                 {"build": {"blocks": {"obscuras_storage:item_filter": 2, "minecraft:hopper": 4, "minecraft:barrel": 4},
                            "radius": 10}, "title": "Build a room that sorts every delivery into its crate"}],
          rewards=[reward_item("artifacts:universal_attractor"), skill("craft", 380)]),

    quest("pack_upgrades", "Pockets Within Pockets", icon="sophisticatedbackpacks:advanced_refill_upgrade",
          after=["joiners_pack"],
          text=["Long jobs need a bigger pack. Upgrade your travelling pack with a magnet, pickup, auto-smelting and "
                "compacting upgrades, so you can work without stopping."],
          tasks=[item("sophisticatedbackpacks:magnet_upgrade", crafted=True, title="Fit a magnet to gather your work"),
                 item("sophisticatedbackpacks:pickup_upgrade", crafted=True, title="Fit a pickup upgrade"),
                 item("sophisticatedbackpacks:auto_smelting_upgrade", crafted=True, title="Fit auto-smelting for ore"),
                 item("sophisticatedbackpacks:compacting_upgrade", crafted=True, title="Fit compacting to save space")],
          rewards=[reward_item("sophisticatedbackpacks:advanced_refill_upgrade"), skill("craft", 300)]),

    quest("instrument_maker", "Strings and Skins", icon="immersive_melodies:vielle", after=["village_square"],
          text=["The village band lost its instruments in a fire. Make a lute, a flute, a tiny drum and a trumpet and "
                "deliver one to each musician."],
          tasks=[item("immersive_melodies:lute", crafted=True, title="Make a lute for the band"),
                 item("immersive_melodies:flute", crafted=True, title="Make a flute for the band"),
                 item("immersive_melodies:tiny_drum", crafted=True, title="Make a tiny drum for the band"),
                 item("immersive_melodies:trumpet", crafted=True, title="Make a trumpet for the band"),
                 {"structure": "#villages", "title": "Take the instruments to the band"},
                 enc(["You made all four? Bless you. We play tonight!"], entity="minecraft:villager", name="Band Leader",
                     title="Hand the instruments to the band's leader")],
          rewards=[reward_item("immersive_melodies:vielle"), skill("craft", 320)]),

    quest("village_concert", "The Concert", icon="supplementaries:bunting", after=["instrument_maker"],
          text=["The band needs a stage in the square. Build one with buntings and seating, then join the band so "
                "the gathered villagers can hear it play."],
          tasks=[{"structure": "#villages", "title": "Go to the village square"},
                 {"build": {"blocks": {"supplementaries:bunting": 4, "another_furniture:oak_bench": 4, "minecraft:oak_stairs": 6},
                            "radius": 12}, "title": "Build a stage with buntings and seating"}],
          rewards=[reward_item("minecraft:music_disc_cat"), reward_item("supplementaries:confetti_popper", 6),
                   skill("craft", 340)]),

    quest("guild_uniform", "Dressed for the Guild", icon="minecraft:leather_chestplate", after=["rival_carpenter"],
          text=["A guild member should look the part even in armour. Make the guild's leather apron outfit to wear "
                "over your gear when you report to Odile."],
          tasks=[item("minecraft:leather_chestplate", crafted=True, title="Make the guild apron"),
                 item("minecraft:leather_leggings", crafted=True, title="Make the guild leggings"),
                 talk_char("odile", ["Leather over armour. Good. A guild member should look the part."],
                           title="Report to Odile in your uniform")],
          rewards=[reward_item("minecraft:leather_chestplate", name="Guild Apron", lore=["Dyed in the guild's colours."]),
                   skill("craft", 300)]),

    quest("gingerbread", "Ginger in the Snow", icon="snowyspirit:gingerbread", after=["village_concert"],
          text=["Winter is coming and the children want a gingerbread house. Find wild ginger, grow it, bake "
                "gingerbread and build the house in the square."],
          tasks=[item("snowyspirit:ginger", 4, title="Find wild ginger to grow"),
                 item("snowyspirit:gingerbread", 8, crafted=True, title="Bake gingerbread for the walls"),
                 {"structure": "#villages", "title": "Go to the village square"},
                 {"build": {"blocks": {"snowyspirit:gingerbread": 16, "snowyspirit:gingerbread_door": 1},
                            "radius": 10}, "title": "Build the gingerbread house for the children"}],
          rewards=[reward_item("snowyspirit:gingerbread_cookie", 8), reward_item("snowyspirit:candy_cane", 8),
                   skill("craft", 320)]),

    quest("sled_race", "Downhill", icon="snowyspirit:sled_oak", after=["gingerbread"],
          text=["The snowy village holds a downhill race every winter. Build a sled and beat the local champion to "
                "the bottom."],
          tasks=[item("snowyspirit:sled_oak", crafted=True, title="Build a sled for the race"),
                 {"structure": "ctov:medium/village_snowy_igloo", "title": "Go to the snowy village's hill"},
                 {"advancement": "snowyspirit:adventure/ride_sled_fast", "title": "Beat the champion down the hill"}],
          rewards=[reward_item("snowyspirit:candy_cane_block", 4), skill("craft", 360)]),
]

ACT3 = [
    quest("winter_festival", "The Winter Festival", icon="snowyspirit:wreath", after=["sled_race", "main_story:act3_start"],
          text=["The guild runs the winter festival in a festive village: hang wreaths and glow lights, wrap presents "
                "for every villager and set up the gingerbread stalls before the first night."],
          tasks=[{"structure": "ctov:large/village_christmas", "title": "Go to the festive village"},
                 {"build": {"blocks": {"snowyspirit:wreath": 2, "snowyspirit:glow_lights_prismatic": 4, "snowyspirit:gingerbread": 8},
                            "radius": 12}, "title": "Hang wreaths and lights and set up the gingerbread stalls"},
                 item("supplementaries:present", 4, title="Wrap presents for the villagers")],
          rewards=[reward_item("snowyspirit:glow_lights_prismatic", 8), reward_item("snowyspirit:eggnog", 4), skill("craft", 450)]),

    quest("nether_lamps", "Lamps for the Dark Side", icon="torchmaster:dreadlamp", after=["megatorch", "main_story:act3_start"],
          text=["The guild wants a safe workshop camp in the Nether. Make a dreadlamp and feral flare lanterns and "
                "light the camp so it stays free of spawns."],
          tasks=[item("torchmaster:dreadlamp", crafted=True, title="Make a dreadlamp for the camp"),
                 item("torchmaster:feral_flare_lantern", 2, crafted=True, title="Make feral flare lanterns for the camp"),
                 {"structure": "#nether_outposts", "title": "Choose a camp site near a Nether outpost"},
                 {"build": {"blocks": {"torchmaster:dreadlamp": 1, "torchmaster:feral_flare_lantern": 2}, "radius": 10},
                  "title": "Light the camp so it stays free of spawns"}],
          rewards=[reward_item("torchmaster:frozen_pearl", 2), skill("craft", 460)]),

    quest("tower_lift", "Restart the Lift", icon="supplementaries:pulley_block", after=["engineers_blueprints"],
          text=["The engineer's tower had a lift. Fix it with pulleys, cranks and cog blocks so it runs from the "
                "cellar to the roof."],
          tasks=[{"structure": "structory_towers:engineer_tower", "title": "Return to the engineer's tower"},
                 item("supplementaries:pulley_block", 2, title="Bring pulleys for the lift"),
                 item("supplementaries:crank", title="Bring a crank to turn it"),
                 item("supplementaries:cog_block", 2, title="Bring cog blocks to carry the load"),
                 {"build": {"blocks": {"supplementaries:pulley_block": 2, "supplementaries:crank": 1, "supplementaries:cog_block": 2},
                            "radius": 12}, "title": "Fit the lift's machinery from cellar to roof"}],
          rewards=[reward_item("furniture:blueprints"), skill("craft", 470)]),

    quest("wireless_workshop", "Anywhere in the Workshop", icon="obscuras_storage:wireless_terminal", after=["sorting_room"],
          text=["The warehouse has outgrown walking. Build a wireless terminal and pull items from the network from "
                "anywhere in Reece."],
          tasks=[item("obscuras_storage:wireless_terminal", crafted=True, title="Build a wireless terminal"),
                 {"place": "reece", "title": "Use it from anywhere in Reece"}],
          rewards=[reward_item("obscuras_storage:adv_wireless_terminal"), skill("craft", 480)]),

    quest("sea_bridge", "Bridge to the Island", icon="mcwbridges:balustrade_stone_bricks_bridge",
          after=["washed_out_bridge", "ruined_town"],
          text=["A fishing hamlet on an island off the coast wants a stone balustrade bridge to the mainland, long "
                "enough to need piers in deep water."],
          tasks=[{"structure": "#villages", "title": "Go to the coastal fishing village"},
                 {"build": {"blocks": {"mcwbridges:balustrade_stone_bricks_bridge": 16, "mcwbridges:andesite_bridge_pier": 4},
                            "radius": 12}, "title": "Span the water to the island with a balustrade bridge on piers"}],
          rewards=[reward_item("minecraft:prismarine", 32), reward_item("minecraft:cod", 16), skill("craft", 500)]),
]

ACT4 = [
    quest("trophy_room", "The Guild's Trophies", icon="handcrafted:bear_trophy", after=["guild_uniform", "main_story:act4_start"],
          text=["Every great guild hall has trophies. Make trophies from what you've hunted (a bear, a blaze, a "
                "skeleton) and mount them in the hall."],
          tasks=[item("handcrafted:bear_trophy", crafted=True, title="Make a bear trophy"),
                 item("handcrafted:blaze_trophy", crafted=True, title="Make a blaze trophy"),
                 item("handcrafted:skeleton_trophy", crafted=True, title="Make a skeleton trophy"),
                 {"place": "reece"},
                 {"build": {"blocks": {"handcrafted:bear_trophy": 1, "handcrafted:blaze_trophy": 1, "handcrafted:skeleton_trophy": 1}, "radius": 12},
                  "title": "Mount them in the guild hall"}],
          rewards=[reward_item("minecraft:experience_bottle", 16), skill("craft", 700)]),

    quest("guild_hall", "The Guild Hall", icon="minecraft:white_banner", after=["trophy_room", "wireless_workshop", "tower_lift"],
          text=["Build the guild hall from the founder's last blueprint: furnished with all three furniture "
                "traditions, a stage, the warehouse below and the trophy wall."],
          tasks=[{"place": "reece"},
                 {"build": {"blocks": {"handcrafted:oak_table": 2, "another_furniture:oak_bench": 4, "furniture:oak_bench": 2,
                                       "supplementaries:bunting": 4, "obscuras_storage:crafting_terminal": 1, "handcrafted:bear_trophy": 1},
                            "radius": 12}, "title": "Raise the guild hall, furnished in all three traditions"}],
          rewards=[reward_item("minecraft:white_banner", name="The Guild Banner"), skill("craft", 740)]),

    quest("endless_pack", "A Pack That Never Wears Out", icon="sophisticatedbackpacks:netherite_backpack", after=["pack_upgrades"],
          text=["Finish your masterwork backpack: netherite tier with an everlasting upgrade and an inception "
                "upgrade."],
          tasks=[item("sophisticatedbackpacks:netherite_backpack", crafted=True, title="Forge a netherite backpack"),
                 item("sophisticatedbackpacks:everlasting_upgrade", crafted=True, title="Fit an everlasting upgrade"),
                 item("sophisticatedbackpacks:inception_upgrade", crafted=True, title="Fit an inception upgrade")],
          rewards=[reward_item("sophisticatedbackpacks:advanced_tool_swapper_upgrade"), skill("craft", 760)]),
]

ACT5 = [
    quest("rebuild_after_cataclysm", "After the Ruin", icon="handcrafted:oak_table", after=["guild_hall", "main_story:act5_start"],
          text=["With the monster in the desert gone, the occupied village it held can be rebuilt. Lead the guild "
                "there, repair its houses and furnish them for the survivors coming home."],
          tasks=[{"structure": "cataclysm:desert_occupied_village", "title": "Lead the guild to the freed desert village"},
                 {"build": {"blocks": {"minecraft:sandstone": 40, "#minecraft:doors": 3, "#minecraft:beds": 3, "handcrafted:oak_table": 2, "handcrafted:oak_chair": 4},
                            "radius": 12}, "title": "Repair its houses and furnish them for the survivors"}],
          rewards=[reward_item("minecraft:bell", name="The Survivors' Heirloom"), skill("craft", 850)]),

    quest("crafting_capstone", "Master of the Guild", icon="minecraft:netherite_pickaxe",
          after=["rebuild_after_cataclysm", "endless_pack", "winter_festival"],
          text=["Odile steps aside and names you master of the guild, handing over the founder's tools reforged for "
                "you."],
          tasks=[talk_char("odile", ["Master of the guild. About time.", "The founder's tools, reforged. Don't let them rust."],
                           title="Be named Master of the Guild by Odile")],
          rewards=[reward_item("minecraft:netherite_pickaxe", name="The Founder's Pickaxe", lore=["The founder's masterwork."],
                               enchant={"minecraft:efficiency": 5, "minecraft:unbreaking": 3, "minecraft:mending": 1, "minecraft:fortune": 3}),
                   reward_item("minecraft:netherite_axe", name="The Founder's Axe", lore=["The founder's masterwork."],
                               enchant={"minecraft:efficiency": 5, "minecraft:unbreaking": 3, "minecraft:mending": 1}),
                   skill("craft", 1000)]),
]

chapter("skill_crafting", "The Crafters' Guild", "Crafting path", "minecraft:crafting_table", "skills", 5, Q + ACT2 + ACT3 + ACT4 + ACT5)
