"""Chapter: skill_mining, the Miners' Guild path: prologue and Act I (first release). Plan: src/plans/quests/skill_mining.json."""
from common import chapter, quest, talk_char, item, reward_item, skill, giver_org, encounter

Q = [
    quest("guild_card", "The Guild Card", icon="minecraft:stone_pickaxe",
          giver=giver_org("miners", ["Want to join the Miners' Guild? Prove you'll swing a pick.",
                                     "Bring me cobblestone, coal and a pickaxe you made yourself."], "Sign me up"),
          text=["The Miners' Guild signs up anyone who can prove they'll swing a pick."],
          tasks=[item("minecraft:cobblestone", 32, consume=True), item("minecraft:coal", 16, consume=True),
                 item("minecraft:stone_pickaxe", crafted=True)],
          rewards=[reward_item("minecraft:lantern"), skill("mining", 60)]),

    quest("first_shift", "First Shift", icon="minecraft:raw_copper", after=["guild_card"],
          text=["Your first paid shift: the shallow seams the guild leases near the village."],
          tasks=[item("minecraft:raw_copper", 24), item("minecraft:coal", 16)],
          rewards=[reward_item("minecraft:torch", 64), skill("mining", 80)]),

    quest("canary_call", "The Canary Stopped Singing", icon="minecraft:gravel", after=["first_shift"],
          text=["A small collapse has trapped an apprentice in a tunnel. Dig through the gravel without bringing the "
                "rest down, and get him out."],
          tasks=[encounter(["I thought nobody was coming!", "The whole roof just... went. Thank you. I'll follow you "
                                                            "out."],
                           entity="minecraft:villager", name="Trapped Apprentice", where={"below_y": 50})],
          rewards=[reward_item("minecraft:iron_pickaxe"), skill("mining", 100)]),

    quest("shoring_up", "Shoring Up", icon="minecraft:scaffolding", after=["canary_call"],
          text=["After the scare the guild drills its crews in safety: ladders, scaffolding, and plenty of light."],
          tasks=[item("minecraft:ladder", 16), item("minecraft:scaffolding", 16), item("minecraft:torch", 64)],
          rewards=[reward_item("supplementaries:rope", 32), skill("mining", 80)]),

    quest("old_workings", "The Old Workings", icon="minecraft:rail", after=["shoring_up"],
          text=["The guild is mapping every abandoned mineshaft before someone falls into one. Find one and recover "
                "a lantern and a rail from its deepest gallery."],
          tasks=[{"structure": "#mines", "title": "Find an old mineshaft"}, item("minecraft:lantern"),
                 item("minecraft:rail")],
          rewards=[reward_item("minecraft:map"), skill("mining", 100)]),

    quest("iron_seam", "The Iron Seam", icon="minecraft:iron_pickaxe", after=["old_workings"],
          text=["The guild's smiths need metal: mine raw iron, smelt it, and forge a full set of iron tools for the "
                "next rescue crew."],
          tasks=[item("minecraft:raw_iron", 48), item("minecraft:iron_pickaxe"), item("minecraft:iron_shovel"),
                 item("minecraft:iron_axe")],
          rewards=[reward_item("minecraft:blast_furnace"), skill("mining", 150)]),

    quest("lights_out", "Lights Out", icon="artifacts:night_vision_goggles", after=["iron_seam"],
          signature="artifacts:night_vision_goggles",
          text=["Every torch in an old mineshaft has gone out, and a guild surveyor is somewhere inside. Follow his "
                "tapping and the glow lichen he scraped on the walls."],
          tasks=[{"structure": "#mines", "title": "Go into the dark"},
                 encounter(["You found me! I scraped lichen on every wall.", "Take my spare goggles. I'm never coming down without two pairs again."],
                           entity="minecraft:villager", name="Lost Surveyor", where={"below_y": 40})],
          rewards=[reward_item("artifacts:night_vision_goggles"), skill("mining", 200)]),

    quest("vein_breaker", "Vein Breaker", icon="minecraft:iron_ore", after=["iron_seam"],
          text=["The guild's best miners break a whole vein in one swing. Hold the Ultimine key and try it."],
          tasks=[item("minecraft:coal", 64), item("minecraft:raw_iron", 32)],
          rewards=[reward_item("minecraft:cooked_beef", 16), skill("mining", 150)]),

    quest("alpine_prospect", "Alpine Prospect", icon="meadow:alpine_iron_ore", after=["vein_breaker"],
          text=["A prospector's letter speaks of ore in the high peaks. Climb the tallest mountains and mine alpine "
                "ore and salt."],
          tasks=[item("meadow:alpine_iron_ore"), item("meadow:alpine_copper_ore"), item("meadow:alpine_salt")],
          rewards=[reward_item("supplementaries:rope", 32), skill("mining", 200)]),

    quest("supply_run", "Supplies for the Camp", icon="minecraft:bread", after=["vein_breaker"],
          text=["A mining camp out in the wilds is short of everything. Take them food, light and tools."],
          tasks=[{"structure": "#mining_camps", "title": "Find the mining camp"},
                 item("minecraft:bread", 32, consume=True), item("minecraft:torch", 64, consume=True),
                 item("minecraft:iron_pickaxe", 4, consume=True)],
          rewards=[reward_item("minecraft:lantern", 2), skill("mining", 200)]),

    quest("depth_chart", "The Depth Chart", icon="minecraft:lapis_lazuli", after=["alpine_prospect"],
          text=["Fill in the guild's depth chart: what lies at every level of the world."],
          tasks=[item("minecraft:redstone", 16), item("minecraft:lapis_lazuli", 16), item("minecraft:raw_gold", 8),
                 item("minecraft:pointed_dripstone", 4)],
          rewards=[reward_item("minecraft:compass"), skill("mining", 250)]),

    quest("underminer", "The Underminer", icon="minecraft:iron_pickaxe", after=["depth_chart"],
          text=["Miners talk of a ghostly figure that digs beside you in the deep and then vanishes. Find the "
                "Underminer and watch where it goes."],
          tasks=[{"observe": "alexsmobs:underminer", "ticks": 60, "title": "Watch the Underminer"}],
          rewards=[reward_item("minecraft:raw_gold", 16), skill("mining", 300)]),
]

chapter("skill_mining", "The Miners' Guild", "Mining path", "minecraft:iron_pickaxe", "skills", 0, Q)
