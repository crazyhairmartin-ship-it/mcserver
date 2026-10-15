"""Chapter: nether, the Nether questline: Act III (first release). Plan: src/plans/quests/nether.json.
A frontier expedition into a hostile realm; Vesna Ashwalker's field notes tie it together. Act IV and V quests are
appended in later tasks."""
from common import chapter, quest, talk_char, item, reward_item, skill, enc, fight, boss, search, sample
from common import enc, fight, boss, search, sample, talk_org, talk_villager, talk_char, item, reward_item, skill, encounter, giver_org  # noqa: F401

NETHER = {"dimension": "minecraft:the_nether"}


def visit(structure, title):
    return {"structure": structure, "title": title}


ACT3 = [
    quest("through_the_flames", "Through the Flames", icon="minecraft:netherrack", after=["main_story:act2_finale"],
          text=["Vesna hears you lit a portal and hands over her old field journal with one rule: never sleep down "
                "there. Step through and survive your first ten minutes in the Nether."],
          tasks=[talk_char("vesna", ["You lit a portal? Take my journal. Never sleep down there.",
                                     "Fire resistance first. Questions later."], title="Take Vesna's field journal"),
                 {"dimension": "minecraft:the_nether", "title": "Step through into the Nether"},
                 {"timed": {"seconds": 600, "goal": {"hold": {"radius": 150}},
                            "lines": ["Ten minutes. Don't sleep. Don't wander far."], "start": "Survive ten minutes"},
                  "title": "Survive your first ten minutes in the Nether"}],
          rewards=[reward_item("minecraft:magma_cream", 4),
                   reward_item("minecraft:writable_book", name="Vesna's Field Journal", lore=["Never sleep down there."]),
                   skill("agility", 300)]),

    quest("forward_camp", "Forward Camp", icon="waystones:waystone", after=["through_the_flames"],
          text=["Wall in your portal with blast-proof stone, and add a chest, a crafting table and a lit waystone so "
                "you always have a way home."],
          tasks=[{"build": {"blocks": {"minecraft:obsidian": 6, "minecraft:chest": 1, "minecraft:crafting_table": 1,
                                       "waystones:waystone": 1}, "radius": 8}, "title": "Wall in the portal and set up camp"},
                 {"waystones": 1, "title": "Light the waystone so you always have a way home"}],
          rewards=[reward_item("waystones:warp_stone"), reward_item("minecraft:cobbled_deepslate", 64), skill("craft", 300)]),

    quest("the_long_halls", "The Long Halls", icon="minecraft:nether_bricks", after=["forward_camp"],
          text=["Vesna's journal sketches a fortress nothing like the old maps. Find one of the rebuilt Nether "
                "fortresses and walk its great halls to the central keep."],
          tasks=[visit("betterfortresses:fortress", "Find a rebuilt Nether fortress and walk its great halls")],
          rewards=[reward_item("minecraft:gold_ingot", 8), skill("agility", 320)]),

    quest("rods_for_the_eyes", "Rods for the Eyes", icon="minecraft:blaze_rod", after=["the_long_halls"],
          text=["Every locator eye in the pack starts with blaze powder. Bring back blaze rods from the fortress "
                "spawners, without dying to the fireballs."],
          tasks=[fight("minecraft:blaze", 8, "betterfortresses:fortress", "Spawner Blazes", "Fight the fortress's blazes for their rods"),
                 item("minecraft:blaze_rod", 16, title="Bring back blaze rods for the eyes")],
          rewards=[reward_item("minecraft:ender_pearl", 4), reward_item("minecraft:shield"), skill("attack", 340)]),

    quest("skulls_on_the_wall", "Skulls on the Wall", icon="minecraft:wither_skeleton_skull", after=["the_long_halls"],
          text=["Wither skeletons patrol the fortress bridges. Vesna wants three of their skulls for something she "
                "won't name yet. Hunt them with a Looting blade."],
          tasks=[fight("minecraft:wither_skeleton", 6, "betterfortresses:fortress", "Bridge Wither Skeletons",
                       "Hunt the wither skeletons on the fortress bridges"),
                 item("minecraft:wither_skeleton_skull", 3, title="Bring Vesna three skulls")],
          rewards=[reward_item("minecraft:enchanted_book", name="Hunter's Greed", enchant={"minecraft:looting": 2}),
                   reward_item("minecraft:soul_lantern", 4), skill("attack", 380)]),

    quest("wart_harvest", "The Wart Garden", icon="minecraft:nether_wart", after=["the_long_halls"],
          text=["Someone tends a nether wart farm out in the wastes, and nobody knows who. Harvest from it, start "
                "your own soul-sand patch at camp, and brew three potions of fire resistance."],
          tasks=[visit("mns:nether_wart_farm", "Find the wart garden tended by nobody"),
                 item("minecraft:nether_wart", 8, title="Harvest warts from the garden"),
                 {"build": {"blocks": {"minecraft:soul_sand": 4, "minecraft:nether_wart": 4}, "radius": 8},
                  "title": "Start your own soul-sand patch at camp"},
                 item("minecraft:potion", 3, consume=True, title="Brew three potions of fire resistance")],
          rewards=[reward_item("minecraft:brewing_stand"), reward_item("minecraft:blaze_powder", 8), skill("farm", 300)]),

    quest("golden_manners", "Golden Manners", icon="minecraft:golden_helmet", after=["forward_camp"],
          text=["Wear gold and barter with piglins until they've given you an ender pearl, obsidian and string. "
                "Vesna bets you'll be robbed at least once."],
          tasks=[item("minecraft:golden_helmet", title="Wear gold so the piglins will trade"),
                 item("minecraft:ender_pearl", title="Barter for an ender pearl"),
                 item("minecraft:obsidian", 2, title="Barter for obsidian"),
                 item("minecraft:string", 4, title="Barter for string")],
          rewards=[reward_item("minecraft:golden_carrot", 8), skill("agility", 300)]),

    quest("lost_trader", "The Lost Trader", icon="minecraft:gold_ingot", after=["golden_manners"],
          text=["A piglin with a merchant's pack has strayed from his camp and the hoglins are closing in. Keep him "
                "alive back to the piglin camp, where his chief owes you a favour."],
          tasks=[enc(["Hoglins! My pack! Take me home, please!"], then="escort", entity="minecraft:piglin",
                     name="Stray Trader", to={"structure": "nova_structures:piglin_camp", "label": "the piglin camp"},
                     title="Walk the stray trader home to the piglin camp")],
          rewards=[reward_item("minecraft:ender_pearl", 4), reward_item("minecraft:fire_charge", 8),
                   reward_item("minecraft:crying_obsidian", 4), skill("agility", 320)]),

    quest("outstation_ledger", "The Outstation Ledger", icon="minecraft:writable_book", after=["lost_trader"],
          text=["The chief sends you with a sack of gold to the piglin outstation near the bastions. Deliver it, and "
                "find the ledger hidden there proving the brutes are skimming."],
          tasks=[item("minecraft:gold_ingot", 16, consume=True, title="Carry the chief's sack of gold"),
                 visit("nova_structures:piglin_outstation", "Deliver the gold to the outstation"),
                 search("nova_structures:piglin_outstation", 1, "the Skimming Ledger", "A ledger with two sets of figures.",
                        texture="minecraft:item/writable_book", title="Find the ledger proving the brutes are skimming")],
          rewards=[reward_item("minecraft:gold_block", 4), reward_item("minecraft:netherite_scrap"), skill("agility", 340)]),

    quest("bastion_quiet", "Quiet Feet in the Bastion", icon="minecraft:gilded_blackstone", after=["outstation_ledger"],
          text=["The ledger names a bastion's treasure room. Get in, lift the gilded blackstone and a banner from "
                "the vault, and get out without the brutes ever turning on you."],
          tasks=[{"timed": {"seconds": 420, "goal": {"structure": "minecraft:bastion_remnant", "label": "the treasure room", "away": 40},
                            "lines": ["Quiet feet. If a brute lands a blow, you're seen."], "start": "Creep in", "no": ["hurt"]},
                  "title": "Creep in to the treasure room without the brutes noticing"},
                 search("minecraft:bastion_remnant", 1, "the Vault's Gilded Haul", "Gilded blackstone and a snout banner.",
                        title="Lift the gilded haul from the vault")],
          rewards=[reward_item("minecraft:netherite_upgrade_smithing_template"), reward_item("minecraft:gilded_blackstone", 4),
                   skill("agility", 360)]),

    quest("lava_dock", "The Lava Dock", icon="minecraft:saddle", after=["the_long_halls"],
          discover={"structure": "nova_structures:nether_port"},
          text=["A harbour on a lava sea, with moorings and cranes and no sailors. Read the harbourmaster's last "
                "log."],
          tasks=[search("nova_structures:nether_port", 1, "the Harbourmaster's Log", "A scorched log, last entry smudged.",
                        title="Read the harbourmaster's last log")],
          rewards=[reward_item("minecraft:saddle"), reward_item("minecraft:warped_fungus_on_a_stick"), skill("agility", 320)]),

    quest("strider_crossing", "Strider Crossing", icon="minecraft:warped_fungus_on_a_stick", after=["lava_dock"],
          text=["The harbourmaster's log mentions a route across the lava ocean. Saddle a strider and cross the lava "
                "inside four minutes."],
          tasks=[item("minecraft:saddle", title="Take a saddle for a strider"),
                 item("minecraft:warped_fungus_on_a_stick", title="Take a fungus on a stick to steer it"),
                 {"timed": {"seconds": 240, "goal": {"structure": "#nether_outposts", "label": "the far shore", "away": 200},
                            "lines": ["Four minutes across the lava. Ride!"], "start": "Cross the lava ocean",
                            "no": ["teleport"]}, "title": "Cross the lava ocean on a strider in four minutes"}],
          rewards=[reward_item("minecraft:netherite_scrap"), reward_item("minecraft:magma_cream", 4), skill("agility", 380)]),

    quest("the_keep", "The Keep at the Edge", icon="minecraft:gold_block", after=["the_long_halls"],
          text=["A Nether keep sits near the fortress roads, held by blaze-guarded skeletons. Clear its walls and "
                "claim the keep's chest."],
          tasks=[fight("minecraft:wither_skeleton", 5, "nova_structures:nether_keep", "Keep Garrison", "Clear the keep's walls of its garrison"),
                 search("nova_structures:nether_keep", 1, "the Keep's Chest", "The keep's strongbox, heavy with gold.",
                        title="Claim the keep's chest")],
          rewards=[reward_item("minecraft:diamond", 3), reward_item("minecraft:golden_apple"), skill("attack", 360)]),

    quest("four_watchtowers", "Four Watchtowers", icon="minecraft:bone_block", after=["the_keep"],
          text=["Skeleton towers and camps watch over every biome. Reach a tower or camp in the crimson forest, the "
                "warped forest, the soul valleys and the wastes."],
          tasks=[visit("nova_structures:nether_skeleton_tower_crimson", "Reach a tower in the crimson forest"),
                 visit("nova_structures:nether_skeleton_tower_warped", "Reach a tower in the warped forest"),
                 visit("nova_structures:skeleton_camp_soul", "Reach a camp in the soul valley"),
                 visit("nova_structures:skeleton_camp_waste", "Reach a camp in the wastes")],
          rewards=[reward_item("minecraft:bone_block", 8), reward_item("minecraft:spyglass"), skill("range", 300)]),

    quest("fortress_tower_lookout", "From the Fortress Tower", icon="camerapture:camera", after=["four_watchtowers"],
          text=["Climb a fortress tower and look out from its top. Mark down any fortress, bastion or skull on the "
                "horizon in Vesna's journal."],
          tasks=[visit("structory_towers:nether/fortress_tower", "Climb a fortress tower"),
                 item("camerapture:camera", title="Bring a camera to mark the horizon"),
                 {"photo": {"structure": "betterfortresses:fortress"}, "title": "Photograph a fortress on the horizon"}],
          rewards=[reward_item("explorerscompass:explorerscompass"), reward_item("minecraft:paper", 16), skill("agility", 340)]),

    quest("mega_fortress", "The Mega Fortress", icon="minecraft:nether_bricks", after=["fortress_tower_lookout"],
          text=["One of the mega fortresses dwarfs even the rebuilt halls. Fight through its towers to the treasure "
                "at the top."],
          tasks=[fight("minecraft:wither_skeleton", 8, "mns:mega_fortress", "Mega-Fortress Garrison",
                       "Fight through the mega fortress's towers", wave=4),
                 search("mns:mega_fortress", 1, "the Mega Fortress's Treasure", "A treasure chest at the top, banner-hung.",
                        title="Claim the treasure at the top")],
          rewards=[reward_item("minecraft:netherite_scrap", 2), reward_item("spartanweaponry:diamond_halberd"), skill("attack", 420)]),

    quest("bridges_of_ash", "Bridges of Ash", icon="minecraft:stone_bricks", after=["fortress_tower_lookout"],
          text=["Ancient bridges span the lava lakes. Cross three of them and note who built them. The stonework "
                "doesn't match any fortress."],
          tasks=[visit("mns:bridge_1", "Cross the first lava-lake bridge"),
                 visit("mns:bridge_2", "Cross the second lava-lake bridge"),
                 visit("mns:bridge_3", "Cross the third lava-lake bridge")],
          rewards=[reward_item("minecraft:magma_cream", 8), skill("agility", 340)]),

    quest("giant_skull", "The Giant's Skull", icon="minecraft:bone", after=["bridges_of_ash"],
          discover={"structure": "mns:giant_skull"},
          text=["A skull the size of a house lies half-buried in the wastes, with a second one in the sand. Find "
                "both, then work out from the carvings which way the giant was facing when it fell."],
          tasks=[visit("mns:sandy_skull", "Find the second skull half-buried in the sand"),
                 search("mns:giant_skull", 1, "the Skull's Carved Notes", "Carvings inside the skull show a direction.",
                        title="Read the carvings inside the first skull")],
          rewards=[reward_item("minecraft:bone_meal", 16), reward_item("minecraft:bone", name="Giant's Tooth", lore=["From a skull the size of a house."]),
                   skill("agility", 340)]),

    quest("giants_sword", "The Giant's Sword", icon="spartanweaponry:diamond_greatsword", after=["giant_skull"],
          text=["The carvings point to a crimson forest where a colossal sword stands buried to the hilt. Climb it "
                "and recover what's lodged at the guard."],
          tasks=[visit("mns:sword", "Find the colossal sword in the crimson forest"),
                 sample("a Relic from the Guard", ["minecraft:magma_cube"], 0.4, texture="minecraft:item/gold_nugget",
                        tooltip="Lodged at the sword's guard")],
          rewards=[reward_item("spartanweaponry:diamond_greatsword", name="The Giant's Edge", lore=["From a sword buried to the hilt."],
                               enchant={"minecraft:sharpness": 3}), skill("attack", 420)]),

    quest("ghost_train", "The Ghost Train", icon="minecraft:rail", after=["bridges_of_ash"],
          discover={"structure": "mns:train"},
          text=["A train sits on rails to nowhere in the Nether. Its spectral conductor wants the scattered cargo "
                "back in the wagons before it can 'depart'."],
          tasks=[enc(["All aboard... cargo scattered... can't depart..."], entity="minecraft:allay", name="Spectral Conductor",
                     title="Meet the train's spectral conductor"),
                 sample("Scattered Cargo", ["minecraft:wither_skeleton"], 0.4, count=3, texture="minecraft:item/chest_minecart",
                        tooltip="Put it back in the wagons")],
          rewards=[reward_item("minecraft:gold_nugget", 64), reward_item("minecraft:soul_lantern", name="Conductor's Lantern"),
                   skill("agility", 360)]),

    quest("nether_houses", "Who Lives Here?", icon="furniture:oak_bench", after=["ghost_train"],
          text=["Small houses stand in the Nether, furnished and empty. Search two of them and piece together, from "
                "the notes left inside, what happened to the family."],
          tasks=[visit("mns:medium_house_2", "Find the second empty house, its table still set"),
                 search("mns:medium_house", 2, "a Family Note", "A note, left on a table in a hurry.",
                        title="Search the first empty house for the notes the family left")],
          rewards=[reward_item("furniture:oak_bench", 2), skill("craft", 320)]),

    quest("warped_dome", "Under the Warped Dome", icon="minecraft:shroomlight", after=["bridges_of_ash"],
          text=["A glass dome shelters a warped garden and a pool full of warped toads. Gather shroomlights and "
                "twisting vines, and catch a warped toad."],
          tasks=[visit("mns:warped_dome", "Find the warped dome"),
                 item("minecraft:shroomlight", 4, title="Gather shroomlights from the garden"),
                 item("minecraft:twisting_vines", 4, title="Gather twisting vines from the garden"),
                 {"observe": "alexsmobs:warped_toad", "ticks": 40, "title": "Catch sight of a warped toad in the pool"}],
          rewards=[reward_item("minecraft:shroomlight", 8), skill("taming", 250)]),

    quest("copper_tower", "The Copper Tower", icon="minecraft:copper_block", after=["warped_dome"],
          text=["A copper tower in a realm without rain. Restore its oxidised lightning rods at the top and the vault "
                "door at the base opens."],
          tasks=[visit("mns:copper_tower", "Find the copper tower"),
                 item("minecraft:lightning_rod", 2, title="Bring new lightning rods"),
                 {"build": {"blocks": {"minecraft:lightning_rod": 2}, "radius": 12}, "title": "Replace the oxidised rods at the top"},
                 search("mns:copper_tower", 1, "the Vault's Contents", "The vault door swings open.", title="Open the vault at the base")],
          rewards=[reward_item("minecraft:copper_block", 8), reward_item("friendsandfoes:copper_golem_head"), skill("craft", 340)]),

    quest("arena_of_ash", "Arena of Ash", icon="minecraft:blaze_powder", after=["mega_fortress"],
          text=["In one of the Nether arenas, survive three waves of blazes, wither skeletons and magma cubes for "
                "five minutes. Win in the dragon arena and Vesna buys the drinks."],
          tasks=[visit("mns:large_arena", "Enter the Nether arena"),
                 {"timed": {"seconds": 300, "goal": {"hold": {"radius": 20}},
                            "waves": [{"entity": "minecraft:blaze", "count": 2, "every": 30},
                                      {"entity": "minecraft:wither_skeleton", "count": 2, "every": 40},
                                      {"entity": "minecraft:magma_cube", "count": 2, "every": 50}],
                            "lines": ["Three waves. Five minutes. Don't leave the sand."], "start": "Fight the arena"},
                  "title": "Survive the arena's waves for five minutes"}],
          rewards=[reward_item("minecraft:golden_apple", 2), skill("attack", 480)]),

    quest("shrine_offerings", "Offerings at the Shrines", icon="minecraft:red_candle", after=["through_the_flames"],
          text=["Small shrines dot the wastes, some still smoking. Leave a gold ingot at a shrine and at a smoking "
                "shrine, and see what the realm gives back."],
          tasks=[visit("mns:shrine", "Find a small shrine"),
                 item("minecraft:gold_ingot", consume=True, title="Leave a gold ingot at the shrine"),
                 visit("mns:smoking_shrine", "Find a smoking shrine"),
                 item("minecraft:gold_ingot", consume=True, title="Leave a gold ingot at the smoking shrine")],
          rewards=[reward_item("minecraft:fire_charge", 8), reward_item("minecraft:quartz", 8), reward_item("minecraft:ghast_tear"),
                   skill("agility", 300)]),

    quest("wishing_in_fire", "Wishing in Fire", icon="minecraft:gold_nugget", after=["through_the_flames"],
          discover={"structure": "mns:medium_crimson_well"},
          text=["A well in the Nether, full of lava instead of water. Fish out the coins at its bottom with a "
                "fire-resistant hand."],
          tasks=[item("minecraft:gold_nugget", 8, title="Fish the coins out of the lava well")],
          rewards=[reward_item("minecraft:gold_nugget", 16), reward_item("minecraft:rabbit_foot"), skill("agility", 100)]),

    quest("soul_valley_graves", "The Soul Valley Graves", icon="minecraft:soul_torch", after=["four_watchtowers"],
          text=["A graveyard in the soul sand valley is circled by soul vultures. Find it, and take a soul heart from "
                "one of the vultures."],
          tasks=[visit("mns:grave_yard", "Find the soul valley's graveyard"),
                 fight("alexsmobs:soul_vulture", 2, "mns:grave_yard", "Grave Vultures", "Bring down the vultures circling the graves", wave=2),
                 sample("a Soul Heart", ["alexsmobs:soul_vulture"], 0.6, texture="minecraft:item/ghast_tear", tooltip="Taken from a vulture")],
          rewards=[reward_item("minecraft:soul_torch", 16),
                   reward_item("minecraft:enchanted_book", name="Soul Strider", enchant={"minecraft:soul_speed": 2}),
                   skill("attack", 380)]),

    quest("mosquito_season", "Mosquito Season", icon="alexsmobs:mosquito_proboscis", after=["soul_valley_graves"],
          text=["Crimson mosquitoes are draining the piglins' hoglins. Swat ten and bring a mosquito proboscis to "
                "the camp chief."],
          tasks=[fight("alexsmobs:crimson_mosquito", 10, "nova_structures:piglin_camp", "Camp Mosquitoes",
                       "Swat the mosquitoes draining the piglins' hoglins"),
                 item("alexsmobs:mosquito_proboscis", title="Bring a proboscis to the camp chief")],
          rewards=[reward_item("alexsmobs:mosquito_repellent_stew", 4), skill("range", 340)]),

    quest("realm_survey", "A Survey of Hell", icon="naturescompass:naturescompass", after=["four_watchtowers"],
          text=["Vesna's journal has blank pages for every biome she never saw. Stand in each of them and fill the "
                "survey."],
          tasks=[{"biome": "minecraft:crimson_forest", "title": "Stand in the crimson forest"},
                 {"biome": "minecraft:warped_forest", "title": "Stand in the warped forest"},
                 {"biome": "minecraft:basalt_deltas", "title": "Stand in the basalt deltas"},
                 {"biome": "minecraft:soul_sand_valley", "title": "Stand in the soul sand valley"},
                 {"biome": "biomesoplenty:visceral_heap", "title": "Stand in the visceral heap"},
                 {"biome": "biomesoplenty:withered_abyss", "title": "Stand in the withered abyss"},
                 {"biome": "biomesoplenty:crystalline_chasm", "title": "Stand in the crystalline chasm"},
                 {"biome": "biomesoplenty:undergrowth", "title": "Stand in the undergrowth"},
                 {"biome": "biomesoplenty:erupting_inferno", "title": "Stand in the erupting inferno"}],
          rewards=[reward_item("naturescompass:naturescompass"), skill("forage", 320)]),

    quest("uncharted_regions", "Uncharted Regions", icon="minecraft:shroomlight", after=["realm_survey"],
          text=["Rumours of glowing meadows and redstone pits. Visit the infernal holt, the glistering meadow, the "
                "mycotoxic undergrowth, the blackstone basin and the redstone abyss, and fill Vesna's journal."],
          tasks=[{"biome": "regions_unexplored:infernal_holt", "title": "Stand in the infernal holt"},
                 {"biome": "regions_unexplored:glistering_meadow", "title": "Stand in the glistering meadow"},
                 {"biome": "regions_unexplored:mycotoxic_undergrowth", "title": "Stand in the mycotoxic undergrowth"},
                 {"biome": "regions_unexplored:blackstone_basin", "title": "Stand in the blackstone basin"},
                 {"biome": "regions_unexplored:redstone_abyss", "title": "Stand in the redstone abyss"}],
          rewards=[reward_item("sophisticatedbackpacks:backpack"), skill("forage", 340)]),

    quest("stranded_vintner", "The Stranded Vintner", icon="nethervinery:crimson_grape_seeds", after=["realm_survey"],
          text=["A winemaker who followed a rumour through a ruined portal is stranded in the crimson forest. He'll "
                "teach you Nether winemaking if you gather crimson and warped grape seeds for him."],
          tasks=[enc(["Stranded since the rumour! Bring me crimson and warped grape seeds."], entity="minecraft:villager",
                     name="Stranded Vintner", title="Find the vintner stuck in the crimson forest",
                     where={"dimension": "minecraft:the_nether"}),
                 item("nethervinery:crimson_grape_seeds", 4, title="Gather crimson grape seeds for the vintner"),
                 item("nethervinery:warped_grape_seeds", 4, title="Gather warped grape seeds for the vintner")],
          rewards=[reward_item("nethervinery:crimson_grapevine_pot"), reward_item("nethervinery:warped_grapevine_pot"), skill("farm", 320)]),

    quest("nether_vineyard", "A Vineyard in Hell", icon="nethervinery:crimson_grape", after=["stranded_vintner"],
          text=["Plant crimson and warped grapes at your forward camp and harvest a crate of each, then build an "
                "apple press and fermentation barrel from Nether wood."],
          tasks=[{"build": {"blocks": {"nethervinery:crimson_grapevine_pot": 1, "nethervinery:warped_grapevine_pot": 1}, "radius": 10},
                  "title": "Plant crimson and warped grapes at your camp"},
                 item("nethervinery:crimson_grape_crate", title="Harvest a crate of crimson grapes"),
                 item("nethervinery:warped_grape_crate", title="Harvest a crate of warped grapes"),
                 item("nethervinery:crimson_apple_press", crafted=True, title="Build a press from Nether wood"),
                 item("nethervinery:crimson_fermentation_barrel", crafted=True, title="Build a fermentation barrel")],
          rewards=[reward_item("nethervinery:crimson_wine_rack_mid"), skill("farm", 340)]),

    quest("netherite_nectar", "Netherite Nectar", icon="nethervinery:netherite_nectar", after=["nether_vineyard"],
          text=["Ferment Ghastly Grenache, Blazewine Pinot and the vintner's prize Netherite Nectar, and deliver a "
                "bottle of each to Vesna in Reece, who has waited thirty years for a decent drink."],
          tasks=[item("nethervinery:ghastly_grenache", title="Ferment Ghastly Grenache"),
                 item("nethervinery:blazewine_pinot", title="Ferment Blazewine Pinot"),
                 item("nethervinery:netherite_nectar", title="Ferment the vintner's prize Netherite Nectar"),
                 talk_char("vesna", ["Thirty years. Finally a decent drink.", "Ghastly, blaze, netherite. You've done it."],
                           title="Deliver a bottle of each to Vesna")],
          rewards=[reward_item("nethervinery:lava_fizz", 2), reward_item("minecraft:netherite_scrap"), skill("cook", 400)]),

    quest("debris_dive", "Deep Debris", icon="minecraft:ancient_debris", after=["skulls_on_the_wall"],
          text=["Down at the bottom of the Nether, mine eight ancient debris. Vesna explains the trick with beds and "
                "tells you never to tell her how it went."],
          tasks=[{"be": {"below_y": 20, "dimension": "minecraft:the_nether"}, "title": "Dig down to the bottom of the Nether"},
                 item("minecraft:ancient_debris", 8, title="Mine eight ancient debris")],
          rewards=[reward_item("minecraft:netherite_upgrade_smithing_template"), skill("mining", 400)]),

    quest("the_burning_citadel", "The Burning Citadel", icon="minecraft:fire_charge", after=["arena_of_ash"],
          discover={"structure": "friendsandfoes:citadel"},
          text=["Fire that walks, and shields that circle it: a citadel in the wastes is held by something Vesna only "
                "calls 'the crowned flame'. Look at it from a safe distance."],
          tasks=[{"observe": "friendsandfoes:wildfire", "ticks": 40, "title": "Watch the crowned flame from a safe distance"}],
          rewards=[reward_item("minecraft:magma_cream", 4), reward_item("minecraft:snowball", 16), skill("agility", 340)]),

    quest("nether_dungeons", "Small Places, Sharp Teeth", icon="minecraft:spawner", after=["through_the_flames"],
          discover={"structure": "betterdungeons:small_nether_dungeon"},
          text=["You've stumbled on a small Nether dungeon. Clear its spawner before it floods the passage."],
          tasks=[fight("minecraft:wither_skeleton", 6, "betterdungeons:small_nether_dungeon", "Dungeon Skeletons",
                       "Clear the dungeon's spawner of its skeletons")],
          rewards=[reward_item("minecraft:quartz", 16), skill("attack", 250)]),

    quest("devils_rest", "The Devil's Rest", icon="minecraft:ghast_tear", after=["through_the_flames"],
          discover={"structure": "mvs:nether_devil"},
          text=["A horned statue squats over the lava, and people say it grants a wish to anyone who answers its "
                "riddle. The answer, the carvings hint, is an eye that sees nothing."],
          tasks=[item("minecraft:ender_eye", consume=True, title="Offer the answer to the statue's riddle")],
          rewards=[reward_item("minecraft:ghast_tear"), reward_item("minecraft:writable_book", name="The Devil's Riddle",
                                                                      lore=["An eye that sees nothing."]), skill("magic", 320)]),

    quest("the_soul_forge", "The Soul Forge", icon="minecraft:soul_lantern", after=["debris_dive"],
          discover={"structure": "cataclysm:soul_black_smith"},
          text=["An anvil the size of a hall, ringing in the soul sand valley. Look but don't knock: whatever works "
                "the forge is not for now. Vesna will remember the way."],
          tasks=[{"timed": {"seconds": 240, "goal": {"structure": "cataclysm:soul_black_smith", "label": "the forge's edge", "away": 25},
                            "lines": ["Look. Don't knock. Don't get hit."], "start": "Creep close", "no": ["hurt"]},
                  "title": "Creep close enough to look, and leave unseen"}],
          rewards=[reward_item("minecraft:soul_lantern", 4), skill("mining", 340)]),

    quest("arena_of_embers", "The Arena of Embers", icon="minecraft:blaze_rod", after=["the_soul_forge", "main_story:act5_start"],
          discover={"structure": "cataclysm:burning_arena"},
          text=["In the deepest wastes, a sealed arena burns with blue fire. Listen at its doors. Even Vesna won't go "
                "nearer."],
          tasks=[{"timed": {"seconds": 240, "goal": {"structure": "cataclysm:burning_arena", "label": "the sealed doors", "away": 25},
                            "lines": ["Listen at the doors. Don't get hit."], "start": "Creep close", "no": ["hurt"]},
                  "title": "Creep to the sealed doors and listen"}],
          rewards=[reward_item("minecraft:blaze_rod", 8), skill("agility", 340)]),
]

ACT4 = [
    quest("crimson_donjon", "The Crimson Donjon", icon="spartanshields:iron_tower_shield", after=["the_keep"],
          text=["Deep in a crimson forest stands a donjon, and near the bastions a piglin hamlet. Raid the donjon's "
                "tower, then trade at the hamlet with what you took."],
          tasks=[{"structure": "nova_structures:donjon", "title": "Find the donjon deep in the crimson forest"},
                 fight("minecraft:wither_skeleton", 8, "nova_structures:donjon", "Donjon Garrison", "Raid the donjon's tower"),
                 search("nova_structures:donjon", 1, "the Donjon's Plunder", "Gold and plunder from the donjon's keep.",
                        texture="minecraft:item/gold_ingot", title="Take the donjon's plunder to trade"),
                 {"structure": "nova_structures:hamlet", "title": "Take the plunder to the piglin hamlet and trade"}],
          rewards=[reward_item("minecraft:netherite_scrap"), reward_item("spartanshields:iron_tower_shield"), skill("attack", 650)]),

    quest("monstrous_eye", "The Monstrous Eye", icon="cataclysm:monstrous_eye", after=["the_soul_forge"],
          text=["The strongholds have woken. Craft the Monstrous Eye from netherite scrap and an eye of ender, and "
                "bring it to Vesna so she can confirm it points at the forge you found."],
          tasks=[item("minecraft:netherite_scrap", 4, title="Gather netherite scrap for the eye"),
                 item("minecraft:ender_eye", title="Gather an eye of ender for the eye"),
                 item("cataclysm:monstrous_eye", crafted=True, title="Craft the Monstrous Eye"),
                 talk_char("vesna", ["That points at the forge you found. Good.", "The old fire is awake."],
                           title="Show Vesna the eye pointing at the forge")],
          rewards=[reward_item("minecraft:golden_apple", 2), reward_item("minecraft:magma_cream", 4), skill("craft", 800)]),

    quest("flame_eye", "The Flame Eye", icon="cataclysm:flame_eye", after=["arena_of_embers", "monstrous_eye"],
          text=["Craft the Flame Eye and hand Vesna her journal back, filled in. She writes the last page herself: "
                "the arena is waiting, when the story is."],
          tasks=[item("cataclysm:flame_eye", crafted=True, title="Craft the Flame Eye"),
                 talk_char("vesna", ["My journal, filled in. I'll write the last page.", "The arena waits for the story."],
                           title="Hand Vesna her journal back, filled in")],
          rewards=[reward_item("minecraft:leather_chestplate", name="Vesna's Ashwalker Cloak", lore=["The last page is hers."],
                               enchant={"minecraft:fire_protection": 4, "minecraft:unbreaking": 3}), skill("agility", 850)]),
]

chapter("nether", "The Nether", "A frontier expedition", "minecraft:netherrack", "realms", 2, ACT3 + ACT4)
