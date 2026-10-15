"""Chapter: skill_farming, the Growers' Co-op path: prologue and Act I (first release). Plan: src/plans/quests/skill_farming.json."""
from common import chapter, quest, talk_villager, item, reward_item, skill, giver_org
from common import enc, fight, boss, search, sample, talk_org, talk_villager, talk_char, item, reward_item, skill, encounter, giver_org  # noqa: F401

Q = [
    quest("coop_share", "A Share in the Co-op", icon="minecraft:wheat",
          giver=giver_org("growers", ["Fancy a share in the Growers' Co-op? Everyone pulls their weight.", "Till a plot, plant wheat, bring in a first harvest for the festival."], "Count me in"),
          text=["The Growers' Co-op means to hold a proper Harvest Festival again. It starts with wheat."],
          tasks=[item("minecraft:wheat", 64)],
          rewards=[reward_item("minecraft:stone_hoe"), reward_item("minecraft:wheat_seeds", 16), skill("farm", 60)]),

    quest("scarecrow", "Scarecrow and Compost", icon="farm_and_charm:scarecrow", after=["coop_share"],
          text=["Protect the plot: build a scarecrow, fill a composter, and make fertilizer for the next planting."],
          tasks=[item("farm_and_charm:scarecrow"), item("minecraft:composter"), item("farm_and_charm:fertilizer", 4)],
          rewards=[reward_item("farm_and_charm:pitchfork"), skill("farm", 80)]),

    quest("wild_seeds", "Seeds from the Wild", icon="farm_and_charm:wild_tomatoes", after=["coop_share"],
          text=["The co-op wants new crops for the festival. Find wild tomatoes, lettuce, onions and oats, and wild "
                "cabbages, and gather their seeds."],
          tasks=[item("farm_and_charm:tomato_seeds"), item("farm_and_charm:lettuce_seeds"),
                 item("farm_and_charm:onion"), item("farm_and_charm:oat_seeds"), item("farmersdelight:cabbage_seeds")],
          rewards=[reward_item("farm_and_charm:crafting_bowl"), skill("farm", 100)]),

    quest("smarter_farmers", "A Farmer Who Thinks", icon="minecraft:carrot", after=["wild_seeds"],
          text=["Village farmers replant with whatever seeds they're given. Fence and water a new field in a village, "
                "hand a farmer carrots, potatoes and beetroot, and watch him keep it planted."],
          tasks=[talk_villager("minecraft:farmer", ["A new field? I'll keep it planted for the co-op.",
                                                    "Just give me something to sow."]),
                 item("minecraft:carrot", 16, consume=True), item("minecraft:potato", 16, consume=True),
                 item("minecraft:beetroot_seeds", 16, consume=True)],
          rewards=[reward_item("minecraft:iron_hoe"), skill("farm", 100)]),

    quest("spring_planting", "Spring Planting", icon="farm_and_charm:strawberry", after=["scarecrow", "wild_seeds"],
          text=["The festival is announced for the autumn, and the co-op's spring planting begins."],
          tasks=[item("farm_and_charm:tomato", 8), item("farm_and_charm:lettuce", 8),
                 item("farm_and_charm:strawberry", 8), item("farm_and_charm:onion", 8)],
          rewards=[reward_item("minecraft:yellow_banner"), skill("farm", 150)]),

    quest("barn_raising", "Barn Raising", icon="farm_and_charm:feeding_trough", after=["spring_planting"],
          text=["See how a farmstead is laid out, then raise a barn of your own with a feeding trough, a chicken coop "
                "and a loft of straw bales."],
          tasks=[{"structure": "#farmsteads", "title": "Visit a farmstead"}, item("farm_and_charm:feeding_trough"),
                 item("farm_and_charm:chicken_coop"), item("farmersdelight:straw_bale", 8)],
          rewards=[reward_item("farm_and_charm:supply_cart"), skill("farm", 150)]),

    quest("rich_soil", "Rich Soil", icon="farmersdelight:rich_soil", after=["barn_raising"],
          text=["Make organic compost and let it turn to rich soil, then grow mushroom colonies on it for the "
                "co-op's kitchen garden."],
          tasks=[item("farmersdelight:organic_compost", 4), item("farmersdelight:brown_mushroom_colony"),
                 item("farmersdelight:red_mushroom_colony")],
          rewards=[reward_item("farm_and_charm:water_sprinkler"), skill("farm", 150)]),

    quest("rice_paddies", "Rice Paddies", icon="farmersdelight:rice_bale", after=["rich_soil"],
          text=["The festival needs rice. Find wild rice by a river and grow a paddy of it in shallow water."],
          tasks=[item("farmersdelight:rice_bale")],
          rewards=[reward_item("farmersdelight:canvas_rug", 2), skill("farm", 150)]),

    quest("cheese_wheel", "The Cheese Wheel", icon="meadow:cheese_block", after=["barn_raising"],
          text=["The co-op's cheesemaker wants milk from the meadow's animals, turned into a cheese block in a "
                "cheese form."],
          tasks=[item("meadow:cheese_form"), item("meadow:cheese_block")],
          rewards=[reward_item("meadow:cheese_rack"), skill("farm", 150)]),

    quest("corn_rows", "Corn Rows", icon="farm_and_charm:corn", after=["spring_planting"],
          text=["Plant long rows of corn, harvest them, and turn the kernels into popcorn for the festival stall."],
          tasks=[item("farm_and_charm:corn", 32), item("cornexpansion:popcorn", 8)],
          rewards=[reward_item("cornexpansion:popcorn_tin", 2), skill("farm", 150)]),

    quest("vineyard", "The Vineyard", icon="vinery:red_grape", after=["spring_planting"],
          text=["Start the co-op's vineyard: red and white grapes, and one of the wilder varieties from the savanna, "
                "the taiga or the jungle, grown on lattices."],
          tasks=[item("vinery:red_grape", 8), item("vinery:white_grape", 8), item("vinery:oak_lattice", 8),
                 item("vinery:savanna_grapes_red")],
          rewards=[skill("farm", 150)]),

    quest("wine_press", "The Festival Toast", icon="vinery:red_wine", after=["vineyard"],
          text=["Press grapes and apples and ferment them, so there's red wine and cider for the festival toast."],
          tasks=[item("vinery:apple_press"), item("vinery:fermentation_barrel"), item("vinery:red_wine"),
                 item("vinery:apple_cider")],
          rewards=[skill("farm", 200)]),

    quest("shearing", "Shearing Day", icon="minecraft:shears", after=["cheese_wheel"],
          text=["Shearing day at the co-op: shear the meadow's wooly and horned sheep for the festival's bunting."],
          tasks=[item("meadow:highland_wool", 16), item("meadow:flecked_wool", 16)],
          rewards=[reward_item("minecraft:shears"), skill("farm", 150)]),
]

ACT2 = [
    quest("wandering_winemaker", "The Wandering Winemaker", icon="vinery:cherry_wine",
          after=["wine_press", "main_story:act2_start"],
          text=["A wandering winemaker passes through the co-op's fields and wants to taste your wine. Trade him for "
                "cherry saplings and his advice on ageing."],
          tasks=[item("vinery:cherry_wine", consume=True, title="Pour your wine for the winemaker to taste"),
                 enc(["Good body. A touch young. Age it in the dark.", "Take these saplings. Plant an orchard."],
                     entity="minecraft:villager", name="Wandering Winemaker", title="Trade with the winemaker")],
          rewards=[reward_item("minecraft:cherry_sapling", 4), reward_item("vinery:apple_tree_sapling", 2), skill("farm", 250)]),

    quest("orchard", "The Orchard", icon="vinery:apple_bag", after=["wandering_winemaker"],
          text=["The co-op wants an orchard. Plant apple and cherry saplings, harvest a bag of apples and press apple "
                "juice."],
          tasks=[{"build": {"blocks": {"vinery:apple_tree_sapling": 2, "minecraft:cherry_sapling": 2}, "radius": 12},
                  "title": "Plant the co-op's orchard"},
                 item("minecraft:apple", 8, title="Harvest apples from the orchard"),
                 item("vinery:apple_juice", crafted=True, title="Press apple juice for the co-op")],
          rewards=[reward_item("vinery:apple_bag"), reward_item("vinery:applesauce", 4), skill("farm", 280)]),

    quest("field_wont_grow", "The Field That Won't Grow", icon="artifacts:rooted_boots",
          after=["rich_soil", "main_story:act2_start"], signature="artifacts:rooted_boots",
          text=["Old Farmer Hobb's field has stood bare for years. Find out why, then restore it: lay rich soil, "
                "bone meal the rows and replant until it bears again. He gives you his old boots."],
          tasks=[enc(["Nothing grows. Not for years. The water pools in that corner."], entity="minecraft:villager",
                     name="Old Farmer Hobb", title="Hear why Hobb's field stands bare"),
                 {"build": {"blocks": {"farmersdelight:rich_soil": 12, "minecraft:wheat": 8}, "radius": 10},
                  "title": "Lay rich soil and replant the field"},
                 item("minecraft:bone_meal", 8, consume=True, title="Bone meal the rows until they bear")],
          rewards=[reward_item("artifacts:rooted_boots"), skill("farm", 350)]),

    quest("silo", "The Silo", icon="farm_and_charm:silo_wood", after=["corn_rows"],
          text=["The co-op needs a silo to dry barley and oats for the winter and for the brewers."],
          tasks=[{"build": {"blocks": {"farm_and_charm:silo_wood": 1}, "radius": 10}, "title": "Build a silo for the co-op"},
                 item("farm_and_charm:barley", 32, consume=True, title="Fill it with barley to dry for the brewers"),
                 item("farm_and_charm:oat", 32, consume=True, title="Fill it with oats for the winter")],
          rewards=[reward_item("farm_and_charm:flour", 16), skill("farm", 300)]),

    quest("outpost_crows", "Crows at the Outpost", icon="farm_and_charm:scarecrow", after=["silo"],
          text=["A farmer outpost far from the village is losing its crop. Deliver seed corn and a scarecrow, and "
                "defend the field through the night from the mobs trampling it."],
          tasks=[item("farm_and_charm:kernels", 8, consume=True, title="Bring seed corn for the outpost's field"),
                 item("farm_and_charm:scarecrow", consume=True, title="Bring a scarecrow for the field"),
                 {"structure": "structory_towers:farmer_outpost", "title": "Reach the farmer outpost"},
                 {"timed": {"seconds": 240, "goal": {"hold": {"radius": 20}},
                            "waves": [{"entity": "minecraft:zombie", "count": 3, "every": 30}],
                            "lines": ["Night falls. Defend the field."], "start": "Defend the field"},
                  "title": "Defend the field through the night"}],
          rewards=[reward_item("farm_and_charm:chicken_nest"), reward_item("minecraft:chicken_spawn_egg", 3), skill("farm", 330)]),

    quest("livestock_fair", "The Livestock Fair", icon="farm_and_charm:feeding_trough", after=["cheese_wheel"],
          text=["The festival's livestock fair judges the best pairs. Breed cows, sheep, pigs, chickens and a water "
                "buffalo to show."],
          tasks=[{"breed": "minecraft:cow", "title": "Breed a pair of cows for the fair"},
                 {"breed": "minecraft:sheep", "title": "Breed a pair of sheep for the fair"},
                 {"breed": "minecraft:pig", "title": "Breed a pair of pigs for the fair"},
                 {"breed": "minecraft:chicken", "title": "Breed a pair of chickens for the fair"},
                 {"breed": "meadow:water_buffalo", "title": "Breed a pair of water buffalo for the fair"}],
          rewards=[reward_item("farm_and_charm:feeding_trough"), skill("farm", 330)]),

    quest("giant_pumpkin", "The Giant Pumpkin", icon="minecraft:pumpkin", after=["livestock_fair"],
          text=["The pumpkin contest: grow pumpkins in a patch or your own field and bring the co-op a full stack in "
                "one harvest."],
          tasks=[{"mine": "minecraft:pumpkin", "count": 64, "title": "Harvest a full stack of pumpkins in one go for the co-op"}],
          rewards=[reward_item("minecraft:pumpkin_pie", 8), skill("farm", 340)]),

    quest("mead", "Bees and Mead", icon="vinery:mead", after=["wine_press"],
          text=["The festival needs mead. Keep a hive near the flower fields, harvest honey bottles and honeycomb "
                "with a campfire beneath, and ferment it."],
          tasks=[{"build": {"blocks": {"minecraft:beehive": 1, "minecraft:campfire": 1}, "radius": 8},
                  "title": "Set a hive over a campfire near the flowers"},
                 item("minecraft:honey_bottle", 4, title="Harvest honey for the mead"),
                 item("minecraft:honeycomb", 4, title="Harvest honeycomb for the mead"),
                 item("vinery:mead", crafted=True, title="Ferment mead for the festival")],
          rewards=[reward_item("minecraft:beehive"), reward_item("vinery:mead", 2), skill("farm", 320)]),

    quest("hard_winter", "The Hard Winter", icon="minecraft:bread", after=["silo"],
          text=["A snowy village's harvest failed and they won't see spring without help. Deliver bread, potato soup "
                "and barley soup, and seed for next year, before winter closes in."],
          tasks=[item("minecraft:bread", 64, consume=True, title="Gather bread to feed the snowed-in village"),
                 item("farm_and_charm:potato_soup", 16, consume=True, title="Gather potato soup for the village"),
                 item("farm_and_charm:barley_soup", 16, consume=True, title="Gather barley soup for the village"),
                 item("minecraft:wheat_seeds", 32, consume=True, title="Gather seed for next year's fields"),
                 {"timed": {"seconds": 900, "goal": {"structure": "minecraft:village_snowy", "label": "the snowy village", "away": 200},
                            "lines": ["Winter closes in. Get the food through."], "start": "Set out", "no": ["teleport"]},
                  "title": "Get the food to the snowy village before winter closes in"}],
          rewards=[reward_item("minecraft:writable_book", name="The Snowy Village's Pledge",
                               lore=["A festival pledge, signed by every household."]), skill("farm", 400)]),
]

ACT3 = [
    quest("nether_grapes", "Grapes in the Nether", icon="nethervinery:crimson_grape_seeds", after=["main_story:act3_start", "wandering_winemaker"],
          text=["The winemaker swears grapes grow in the Nether. Find crimson and warped grape seeds and grow them, "
                "then visit the old nether wart plantation for its wart."],
          tasks=[item("nethervinery:crimson_grape_seeds", 2, title="Find crimson grape seeds"),
                 item("nethervinery:warped_grape_seeds", 2, title="Find warped grape seeds"),
                 {"build": {"blocks": {"nethervinery:crimson_grapevine_pot": 1, "nethervinery:warped_grapevine_pot": 1}, "radius": 10},
                  "title": "Grow the Nether grapes"},
                 {"structure": "mns:nether_wart_farm", "title": "Visit the old nether wart plantation for its wart"}],
          rewards=[reward_item("nethervinery:crimson_fermentation_barrel"), skill("farm", 400)]),

    quest("eiswein", "Ice Wine", icon="vinery:red_wine", after=["nether_grapes"],
          text=["Make the rarest wine for the festival's top table. Grow taiga grapes in the cold, and age eiswein "
                "and a cherry wine in the cellar."],
          tasks=[{"biome": "minecraft:snowy_taiga", "title": "Go to the cold where taiga grapes ripen"},
                 item("vinery:taiga_grape_seeds_white", 2, title="Take taiga grape seeds"),
                 item("vinery:cherry_wine", consume=True, title="Age a cherry wine in the cellar"),
                 item("vinery:big_bottle", title="Age the eiswein in a big bottle")],
          rewards=[reward_item("vinery:big_bottle"), skill("farm", 430)]),
]

ACT4 = [
    quest("prize_crops", "Prize Crops", icon="farmersdelight:cabbage_crate", after=["main_story:act4_start", "giant_pumpkin", "eiswein"],
          text=["The festival's prize table: a crate of every crop the co-op grows, from cabbages and rice to "
                "barley, strawberries, corn, grapes and Nether grapes."],
          tasks=[item("farmersdelight:cabbage_crate", title="Fill a crate of cabbages"),
                 item("farmersdelight:rice_bag", title="Fill a bag of rice"),
                 item("farm_and_charm:corn_bag", title="Fill a bag of corn"),
                 item("vinery:red_grape_bag", title="Fill a bag of grapes"),
                 item("nethervinery:crimson_grape_crate", title="Fill a crate of Nether grapes")],
          rewards=[reward_item("farm_and_charm:silo_wood"), skill("farm", 650)]),

    quest("market_stall", "The Market Stall", icon="artifacts:villager_hat", after=["prize_crops"],
          signature="artifacts:villager_hat",
          text=["Festival market day: run the co-op's stall against the other villages' farmers, selling your best "
                "produce to villagers for emeralds. Outsell them all and win the market master's hat."],
          tasks=[{"structure": "#moog_stalls_and_carts", "title": "Find the market stalls"},
                 {"trade": "any", "item": "minecraft:emerald", "count": 8, "title": "Sell your best produce to villagers for emeralds"},
                 enc(["Best stall at the fair. Take the hat."], entity="minecraft:villager", name="Market Master",
                     title="Be named the market master's champion")],
          rewards=[reward_item("artifacts:villager_hat"), skill("farm", 720)]),
]

ACT5 = [
    quest("festival_grounds", "The Festival Grounds", icon="minecraft:hay_block", after=["main_story:act5_start", "market_stall"],
          text=["Build the Harvest Festival grounds in Reece: a long table, bunting, hay bales, a stage for the band "
                "and the prize table under a barn roof."],
          tasks=[{"place": "reece"},
                 {"build": {"blocks": {"handcrafted:oak_table": 4, "supplementaries:bunting": 6, "minecraft:hay_block": 8, "minecraft:oak_stairs": 8,
                                       "minecraft:oak_planks": 40}, "radius": 12},
                  "title": "Build the festival grounds, stage and barn-roofed prize table"}],
          rewards=[reward_item("minecraft:white_banner", name="The Festival Banner"), skill("farm", 850)]),

    quest("harvest_festival", "The Harvest Festival", icon="minecraft:wheat", after=["festival_grounds"],
          text=["Festival night: bring the feast's produce, the wine and the cheese, and the co-op's leader opens "
                "the Harvest Festival in Reece with every village you fed in the hard winter."],
          tasks=[item("minecraft:bread", 32, consume=True, title="Bring the feast's bread"),
                 item("vinery:red_wine", 2, consume=True, title="Bring the festival's wine"),
                 item("meadow:piece_of_cheese", 4, consume=True, title="Bring the festival's cheese"),
                 talk_char("marta", ["The Harvest Festival! Everyone you fed is here! Have a crown!"], title="Open the Harvest Festival with Marta")],
          rewards=[reward_item("minecraft:leather_helmet", name="The Festival Crown", lore=["A straw hat for a harvest queen."]), skill("farm", 950)]),

    quest("harvest_moon", "Harvest Moon", icon="minecraft:netherite_hoe", after=["harvest_festival"],
          text=["The co-op's leader names you Master Grower and gives you the hoe that cut the first sheaf."],
          tasks=[talk_char("marta", ["Master Grower! The hoe that cut the first sheaf. Oh, I'm crying!"], title="Be named Master Grower by Marta")],
          rewards=[reward_item("minecraft:netherite_hoe", name="Harvest Moon", lore=["It cut the first sheaf."],
                               enchant={"minecraft:fortune": 3, "minecraft:efficiency": 5, "minecraft:unbreaking": 3, "minecraft:mending": 1}),
                   skill("farm", 1000)]),
]

chapter("skill_farming", "The Growers' Co-op", "Farming path", "minecraft:wheat", "skills", 1, Q + ACT2 + ACT3 + ACT4 + ACT5)
