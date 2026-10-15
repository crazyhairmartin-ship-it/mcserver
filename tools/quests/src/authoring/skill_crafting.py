"""Chapter: skill_crafting, the Crafters' Guild path: prologue and Act I (first release).
Plan: src/plans/quests/skill_crafting.json. Master Joiner Odile Brask keeps the guild workshop in Reece."""
from common import chapter, quest, talk_char, item, reward_item, skill, giver_org, encounter

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

chapter("skill_crafting", "The Crafters' Guild", "Crafting path", "minecraft:crafting_table", "skills", 5, Q)
