"""Chapter: skill_farming, the Growers' Co-op path: prologue and Act I (first release). Plan: src/plans/quests/skill_farming.json."""
from common import chapter, quest, talk_villager, item, reward_item, skill, giver_org

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

chapter("skill_farming", "The Growers' Co-op", "Farming path", "minecraft:wheat", "skills", 1, Q)
