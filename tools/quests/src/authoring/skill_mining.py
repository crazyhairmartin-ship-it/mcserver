"""Chapter: skill_mining, the Miners' Guild path: prologue and Act I (first release). Plan: src/plans/quests/skill_mining.json."""
from common import chapter, quest, talk_char, item, reward_item, skill, giver_org, encounter
from common import enc, fight, boss, search, sample, talk_org, talk_villager, talk_char, item, reward_item, skill, encounter, giver_org  # noqa: F401

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
          rewards=[reward_item("minecraft:enchanted_book", enchant={'minecraft:efficiency': 2}), skill("mining", 100)]),

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
          rewards=[reward_item("minecraft:enchanted_book", enchant={'minecraft:fortune': 2}), skill("mining", 150)]),

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
          rewards=[reward_item("minecraft:compass"), reward_item("minecraft:enchanted_book", enchant={'minecraft:efficiency': 2}), skill("mining", 250)]),

    quest("underminer", "The Underminer", icon="minecraft:iron_pickaxe", after=["depth_chart"],
          text=["Miners talk of a ghostly figure that digs beside you in the deep and then vanishes. Find the "
                "Underminer and watch where it goes."],
          tasks=[{"observe": "alexsmobs:underminer", "ticks": 60, "title": "Watch the Underminer"}],
          rewards=[reward_item("minecraft:raw_gold", 16), skill("mining", 300)]),
]

ACT2 = [
    quest("lost_crew", "The Lost Crew", icon="minecraft:diamond_pickaxe", after=["supply_run", "main_story:act2_start"],
          text=["The camp's survey crew went down a mining system three days ago and never came up. Fight through "
                "the infested galleries, find the three miners and get them out."],
          tasks=[fight("minecraft:cave_spider", 8, "dungeons_arise:mining_system", "Gallery Brood",
                       "Fight through the infested galleries"),
                 enc(["Here! Behind the cart! Three days in the dark!"], then="escort", entity="minecraft:villager",
                     name="Survey Miner", to={"structure": "#mining_camps", "label": "the camp"},
                     title="Lead the first miner out"),
                 enc(["I can walk. Just show me the way up."], then="escort", entity="minecraft:villager",
                     name="Survey Miner", to={"structure": "#mining_camps", "label": "the camp"},
                     title="Lead the second miner out"),
                 enc(["My lamp died. Please, the lift!"], then="escort", entity="minecraft:villager",
                     name="Survey Foreman", to={"structure": "#mining_camps", "label": "the camp"},
                     title="Lead the foreman out")],
          rewards=[reward_item("minecraft:enchanted_book", enchant={'minecraft:efficiency': 4, 'minecraft:unbreaking': 3}, name="The Foreman's Pick"), skill("mining", 250)]),

    quest("deepslate_descent", "Into the Deepslate", icon="minecraft:deepslate_diamond_ore", after=["lost_crew"],
          text=["The guild's next shaft goes below Y -32. Mine down into the deepslate for diamond ore and cobbled "
                "deepslate for the shaft walls."],
          tasks=[{"be": {"below_y": -32}, "title": "Mine down below the old workings, past Y -32"},
                 item("minecraft:deepslate_diamond_ore", 8, title="Mine deepslate diamond ore for the guild"),
                 item("minecraft:cobbled_deepslate", 64, title="Gather cobbled deepslate for the shaft walls")],
          rewards=[reward_item("minecraft:copper_ingot", name="Deepslate Guild Badge", lore=["For those who went below."]),
                   skill("mining", 300)]),

    quest("shift_meal", "The Shift Meal", icon="artifacts:onion_ring", after=["deepslate_descent"],
          signature="artifacts:onion_ring",
          text=["The guild cook feeds the rescue crews before the big descent. Forage onions, then cook onion soup "
                "and pasta with onion sauce for a crew of six."],
          tasks=[item("farm_and_charm:onion", 8, title="Grow or forage onions for the shift meal"),
                 item("farm_and_charm:onion_soup", 6, consume=True, title="Cook onion soup for the crew"),
                 item("farm_and_charm:pasta_with_onion_sauce", 6, consume=True, title="Cook pasta with onion sauce for the crew")],
          rewards=[reward_item("artifacts:onion_ring"), skill("mining", 300)]),

    quest("cave_in", "Cave-In", icon="artifacts:digging_claws", after=["shift_meal"],
          signature="artifacts:digging_claws",
          text=["The new deep shaft collapses with you and two miners behind the fall, and your pick is under the "
                "rubble. Dig the tunnel open with a shovel before the air runs out. The old miner who survives "
                "gives you his claws."],
          tasks=[enc(["The roof came down! Dig, friend, dig!"], entity="minecraft:villager", name="Trapped Miner",
                     title="Find the miners trapped behind the fall", where={"below_y": 50}),
                 item("minecraft:iron_shovel", title="Take a shovel to dig the tunnel open"),
                 {"timed": {"seconds": 150, "goal": {"hold": {"radius": 10}},
                            "lines": ["The air is running out. Dig!"], "start": "Dig the tunnel open"},
                  "title": "Dig through before the air runs out"}],
          rewards=[reward_item("artifacts:digging_claws"), skill("mining", 380)]),

    quest("three_seams", "Three Famous Seams", icon="artifacts:lucky_scarf", after=["deepslate_descent"],
          signature="artifacts:lucky_scarf",
          text=["An old prospector swears his scarf brings luck. Bet him you can bring emerald from the high peaks, "
                "gold from a mesa mineshaft and diamond from the deepslate before he finishes his pipe."],
          tasks=[enc(["Emerald, gold and diamond before my pipe's out? Ha! Go on."], entity="minecraft:villager",
                     name="Old Prospector", title="Take the old prospector's bet"),
                 item("minecraft:emerald", 4, title="Bring emerald from the high peaks"),
                 {"structure": "bettermineshafts:mineshaft_mesa", "title": "Find a mesa mineshaft for the gold"},
                 item("minecraft:raw_gold", 8, title="Bring gold from the mesa mineshaft"),
                 item("minecraft:diamond", 3, title="Bring diamond from the deepslate")],
          rewards=[reward_item("artifacts:lucky_scarf"), skill("mining", 330)]),

    quest("spore_shaft", "The Spore Shaft", icon="minecraft:red_mushroom", after=["lost_crew"],
          text=["Miners working the mushroom mines have gone strange from the spores. Escort four of them back "
                "through the overgrown tunnels, keeping them away from the glowing caps."],
          tasks=[{"structure": "dungeons_arise:mushroom_mines", "title": "Enter the mushroom mines"},
                 enc(["Pretty... lights... so pretty..."], then="escort", entity="minecraft:villager", name="Spore Miner",
                     to={"structure": "#mining_camps", "label": "the camp"}, title="Lead the first dazed miner out"),
                 enc(["Where... where are we going?"], then="escort", entity="minecraft:villager", name="Spore Miner",
                     to={"structure": "#mining_camps", "label": "the camp"}, title="Lead the second dazed miner out"),
                 enc(["I hear singing..."], then="escort", entity="minecraft:villager", name="Spore Miner",
                     to={"structure": "#mining_camps", "label": "the camp"}, title="Lead the third dazed miner out"),
                 enc(["Is it dinner time?"], then="escort", entity="minecraft:villager", name="Spore Miner",
                     to={"structure": "#mining_camps", "label": "the camp"}, title="Lead the fourth dazed miner out")],
          rewards=[reward_item("minecraft:mushroom_stew", 4), reward_item("biomesoplenty:glowshroom", 8), skill("mining", 320)]),

    quest("scorched_mines", "Fire Below", icon="minecraft:water_bucket", after=["spore_shaft"],
          text=["A fire has broken out in the scorched mines, and the trapped miners are holding a gallery against "
                "what crawled out of the burning seams. Reach them with fire resistance and water, and hold until "
                "they're out."],
          tasks=[item("minecraft:potion", 2, consume=True, title="Bring potions to survive the heat"),
                 item("minecraft:water_bucket", 2, title="Bring water to douse the seams"),
                 {"structure": "dungeons_arise:scorched_mines", "title": "Reach the trapped miners' gallery"},
                 {"timed": {"seconds": 180, "goal": {"hold": {"radius": 12}},
                            "waves": [{"entity": "minecraft:blaze", "count": 2, "every": 45}],
                            "lines": ["The seams are spitting fire. Hold the gallery!"], "start": "Hold the gallery"},
                  "title": "Hold the gallery until the miners are out"}],
          rewards=[reward_item("irons_spellbooks:cinder_essence", 2), reward_item("minecraft:magma_cream", 6), reward_item("minecraft:raw_gold", 8), skill("mining", 350)]),

    quest("surveyors_glass", "The Surveyor's Glass", icon="minecraft:spyglass", after=["deepslate_descent"],
          text=["The guild surveyor wants to read the deep rock. Crack open an amethyst geode, bring amethyst shards "
                "and copper, and craft her a spyglass and tinted glass."],
          tasks=[item("minecraft:amethyst_shard", 16, title="Crack open a geode for amethyst shards"),
                 item("minecraft:copper_ingot", 8, title="Bring copper for the lens fittings"),
                 item("minecraft:spyglass", crafted=True, title="Craft the surveyor a spyglass"),
                 item("minecraft:tinted_glass", 2, crafted=True, title="Craft tinted glass for her lamp")],
          rewards=[reward_item("minecraft:spyglass"), reward_item("minecraft:raw_gold", 8), skill("mining", 300)]),

    quest("strange_minerals", "Strange Minerals", icon="alexscaves:amber", after=["surveyors_glass"],
          text=["Rumours of strange stone deep under the world. Dig samples of amber from the Primordial Caves, guano "
                "from the Forlorn Hollows and abyssmarine from the abyss."],
          tasks=[{"structure": "alexscaves:dino_bowl", "title": "Find the Primordial Caves"},
                 item("alexscaves:amber", 4, title="Dig amber samples"),
                 {"structure": "alexscaves:forlorn_canyon", "title": "Find the Forlorn Hollows"},
                 item("alexscaves:guano_block", 4, title="Dig guano samples"),
                 item("alexscaves:abyssmarine", 4, title="Dig abyssmarine samples from the abyss")],
          rewards=[reward_item("minecraft:writable_book", name="A Note on the Caves", lore=["The caves' own questline goes deeper."]), reward_item("minecraft:amethyst_shard", 8), skill("mining", 350)]),

    quest("lost_journal", "The Lost Expedition's Journal", icon="minecraft:written_book", after=["cave_in"],
          text=["A guild expedition went too deep and found an ancient city. One survivor made it out without the "
                "journal. Creep through the sculk without waking the Warden and bring it back from beside the "
                "portal frame."],
          tasks=[{"structure": "minecraft:ancient_city", "title": "Find the ancient city the expedition found"},
                 {"timed": {"seconds": 300, "goal": {"structure": "minecraft:ancient_city", "label": "the portal frame", "away": 60},
                            "lines": ["Quiet. Anything that touches you wakes the city."], "start": "Creep in",
                            "no": ["seen"]}, "title": "Creep across the city without waking the Warden"},
                 search("minecraft:ancient_city", 1, "the Expedition Journal", "A water-stained journal, still legible.",
                        texture="minecraft:item/written_book", title="Take the journal from beside the portal frame")],
          rewards=[reward_item("minecraft:enchanted_book", name="Silent Step", enchant={"minecraft:swift_sneak": 3}),
                   reward_item("minecraft:map"), skill("mining", 400)]),
]

ACT3 = [
    quest("forge_cold", "The Cold Forge", icon="artifacts:pickaxe_heater", after=["main_story:act3_start", "cave_in"],
          signature="artifacts:pickaxe_heater",
          text=["The guild's deep forge below Y -50 has gone cold and no one can smelt down there. Carry coal blocks, "
                "blaze powder and magma blocks down to relight it. The smith fits your pick with a heater in thanks."],
          tasks=[item("minecraft:coal_block", 8, consume=True, title="Carry coal blocks down to the forge"),
                 item("minecraft:blaze_powder", 16, consume=True, title="Carry blaze powder to relight it"),
                 item("minecraft:magma_block", 4, consume=True, title="Carry magma blocks to heat it"),
                 {"be": {"below_y": -50}, "title": "Go down below Y -50 to the cold forge"}],
          rewards=[reward_item("artifacts:pickaxe_heater"), skill("mining", 400)]),

    quest("ancient_debris", "Ancient Debris", icon="minecraft:ancient_debris", after=["main_story:act3_start", "deepslate_descent"],
          text=["The guild has never had netherite. Find and mine ancient debris near Nether lava level, blasting "
                "or digging."],
          tasks=[{"be": {"below_y": 30, "dimension": "minecraft:the_nether"}, "title": "Go down near the Nether's lava level"},
                 item("minecraft:ancient_debris", 8, title="Mine eight ancient debris, blasting or digging")],
          rewards=[reward_item("minecraft:netherite_upgrade_smithing_template"), skill("mining", 420)]),

    quest("quartz_contract", "The Quartz Contract", icon="minecraft:quartz", after=["ancient_debris"],
          text=["A guild contract for the Nether: quartz, gold nuggets from nether gold ore and gilded blackstone, "
                "mined in one trip and sold through the guild."],
          tasks=[{"mine": "minecraft:nether_quartz_ore", "count": 24, "title": "Mine nether quartz for the contract"},
                 {"mine": "minecraft:nether_gold_ore", "count": 12, "title": "Mine nether gold ore for nuggets"},
                 item("minecraft:gilded_blackstone", 16, title="Take gilded blackstone from a bastion")],
          rewards=[reward_item("minecraft:enchanted_book", enchant={'minecraft:fortune': 3}), skill("mining", 450)]),

    quest("netherite_pick", "Netherite Pick", icon="minecraft:netherite_pickaxe", after=["ancient_debris"],
          text=["Smelt your debris to scrap, alloy an ingot, and upgrade your diamond pickaxe at a smithing table: "
                "the first netherite pick the guild has seen."],
          tasks=[item("minecraft:netherite_scrap", 4, title="Smelt your debris to netherite scrap"),
                 item("minecraft:netherite_ingot", crafted=True, title="Alloy a netherite ingot"),
                 item("minecraft:netherite_pickaxe", crafted=True, title="Upgrade your diamond pickaxe at a smithing table")],
          rewards=[reward_item("minecraft:netherite_ingot"), skill("mining", 500)]),
]

ACT4 = [
    quest("obsidian_cut", "Cutting Obsidian", icon="minecraft:obsidian", after=["main_story:act4_start", "netherite_pick"],
          text=["For the memorial and the guild's new deep doors: obsidian and crying obsidian, cut cleanly."],
          tasks=[item("minecraft:obsidian", 64, title="Cut obsidian for the guild's deep doors"),
                 item("minecraft:crying_obsidian", 16, title="Cut crying obsidian for the memorial")],
          rewards=[reward_item("minecraft:diamond", 4), skill("mining", 700)]),

    quest("great_collapse", "The Great Collapse", icon="minecraft:diamond_block", after=["main_story:act4_start", "forge_cold", "lost_journal"],
          text=["The deepest rescue: the old mine under Reece gives way at Y -58 with seven miners below. Reach "
                "each pocket of survivors and bring them all up before the last torch burns down."],
          tasks=[{"be": {"below_y": -55}, "title": "Dig down to the collapse at Y -58"},
                 enc(["Here! A pocket of us, behind the gravel!"], then="escort", entity="minecraft:villager", name="Trapped Miner",
                     to={"place": "reece"}, title="Bring the first pocket of survivors up"),
                 enc(["Over here! The lava's close!"], then="escort", entity="minecraft:villager", name="Trapped Miner",
                     to={"place": "reece"}, title="Bring the second pocket of survivors up"),
                 enc(["The last torch! Hurry!"], then="escort", entity="minecraft:villager", name="Trapped Miner",
                     to={"place": "reece"}, title="Bring the last pocket of survivors up")],
          rewards=[reward_item("minecraft:diamond_block"), skill("mining", 780)]),

    quest("memorial", "The Miners' Memorial", icon="minecraft:polished_deepslate", after=["great_collapse", "obsidian_cut"],
          text=["Build the guild a memorial at the guildhall in Reece: polished deepslate, obsidian, lanterns and a "
                "sign for every miner lost or saved on your rescues."],
          tasks=[{"place": "reece"},
                 {"build": {"blocks": {"minecraft:polished_deepslate": 16, "minecraft:obsidian": 8, "minecraft:lantern": 4, "minecraft:oak_sign": 4},
                            "radius": 12}, "title": "Raise the memorial at the guildhall"}],
          rewards=[reward_item("minecraft:oak_sign", name="The Memorial Plaque", lore=["Named for you."]), reward_item("minecraft:candle", 6), skill("mining", 800)]),
]

ACT5 = [
    quest("mother_lode", "The Mother Lode", icon="minecraft:netherite_block", after=["main_story:act5_start", "memorial"],
          text=["A guildmaster's test: bring a block of every metal and gem the guild works."],
          tasks=[item("minecraft:coal_block", title="Bring a block of coal"), item("minecraft:copper_block", title="Bring a block of copper"),
                 item("minecraft:iron_block", title="Bring a block of iron"), item("minecraft:gold_block", title="Bring a block of gold"),
                 item("minecraft:redstone_block", title="Bring a block of redstone"), item("minecraft:lapis_block", title="Bring a block of lapis"),
                 item("minecraft:emerald_block", title="Bring a block of emerald"), item("minecraft:diamond_block", title="Bring a block of diamond"),
                 item("minecraft:netherite_block", title="Bring a block of netherite")],
          rewards=[reward_item("minecraft:beacon"), skill("mining", 900)]),

    quest("guildmaster", "Lifeline", icon="minecraft:netherite_pickaxe", after=["mother_lode"],
          text=["The Guildmaster in Reece names you Master of Rescues and hands over the guild's oldest pick, "
                "reforged."],
          tasks=[talk_char("dagna", ["Master of Rescues, aye. The oldest pick, reforged.", "Dinnae lose it, lass."],
                           title="Be named Master of Rescues by Dagna")],
          rewards=[{"choice": [reward_item("minecraft:netherite_pickaxe", name='Lifeline', lore=['It always finds the way back up.'], enchant={'minecraft:efficiency': 5, 'minecraft:fortune': 3, 'minecraft:unbreaking': 3}, unbreakable=True), reward_item("spartanweaponry:netherite_battle_hammer", name="Lifeline's Hammer", lore=['Breaks stone, props beams.'], enchant={'minecraft:sharpness': 4, 'minecraft:unbreaking': 3}, unbreakable=True), reward_item("alexscaves:galena_gauntlet", name="Guildmaster's Gauntlet", lore=['Hums near ore.'], unbreakable=True)], "title": "Choose one"}, skill("mining", 1000)]),
]

chapter("skill_mining", "The Miners' Guild", "Mining path", "minecraft:iron_pickaxe", "skills", 0, Q + ACT2 + ACT3 + ACT4 + ACT5)
