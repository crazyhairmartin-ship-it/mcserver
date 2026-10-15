"""Chapter: skill_cooking, the Tavern Keepers' path: prologue and Act I (first release). Plan: src/plans/quests/skill_cooking.json."""
from common import chapter, quest, talk_char, talk_org, item, reward_item, skill, encounter
from common import enc, fight, boss, search, sample, talk_org, talk_villager, talk_char, item, reward_item, skill, encounter, giver_org  # noqa: F401

Q = [
    quest("first_order", "First Order", icon="minecraft:cooked_beef",
          text=["Bess Copperpot runs Reece's tavern, and tonight she's a cook short."],
          tasks=[talk_char("bess", ["You. Can you cook? Good, you're hired. Probably.", "Eight steaks and eight loaves for tonight. Chop chop."]),
                 item("minecraft:cooked_beef", 8, consume=True), item("minecraft:bread", 8, consume=True)],
          rewards=[reward_item("farmersdelight:flint_knife"), reward_item("minecraft:emerald", 4), skill("cook", 60)]),

    quest("cutting_board", "Knife and Board", icon="farmersdelight:cutting_board", after=["first_order"],
          text=["A proper kitchen needs a cutting board and a sharp knife. Prep cabbage leaves, minced beef and "
                "salmon slices for the shelf."],
          tasks=[item("farmersdelight:cutting_board"), item("farmersdelight:iron_knife"),
                 item("farmersdelight:cabbage_leaf", 4), item("farmersdelight:minced_beef", 4),
                 item("farmersdelight:salmon_slice", 4)],
          rewards=[reward_item("farmersdelight:skillet"), skill("cook", 80)]),

    quest("stew_pot", "The Stew Pot", icon="farmersdelight:cooking_pot", after=["cutting_board"],
          text=["Every tavern lives on its stew pot. Cook beef stew, vegetable soup and chicken soup."],
          tasks=[item("farmersdelight:beef_stew", 2), item("farmersdelight:vegetable_soup", 2),
                 item("farmersdelight:chicken_soup", 2)],
          rewards=[reward_item("farmersdelight:cooking_pot"), skill("cook", 100)]),

    quest("regulars", "The Regulars", icon="farmersdelight:egg_sandwich", after=["stew_pot"],
          text=["Three regulars can't make it to the tavern today, so the tavern goes to them: an egg sandwich for "
                "the old miner, hot cocoa for the cleric's apprentice, and mushroom rice for the farmer."],
          tasks=[talk_org("miners", ["An egg sandwich? Bess remembered! Bless her."], title="The old miner"),
                 talk_org("herbalists", ["Hot cocoa! On a day like this. Thank you."], title="The cleric's apprentice"),
                 talk_org("growers", ["Mushroom rice. Now that's a proper lunch."], title="The farmer"),
                 item("farmersdelight:egg_sandwich", consume=True), item("farmersdelight:hot_cocoa", consume=True),
                 item("farmersdelight:mushroom_rice", consume=True)],
          rewards=[reward_item("minecraft:emerald", 6), skill("cook", 120)]),

    quest("campfire_supper", "Campfire Supper", icon="camping:grill", after=["first_order"],
          text=["Travellers camped on the road need feeding. Set up a grill and cook barbecue sticks and grilled "
                "salmon for them."],
          tasks=[{"structure": "#camps", "title": "Find a traveller's camp"}, item("camping:grill"),
                 item("farmersdelight:barbecue_stick", 4, consume=True),
                 item("farmersdelight:grilled_salmon", 2, consume=True)],
          rewards=[reward_item("camping:sleeping_bag_green"), skill("cook", 100)]),

    quest("tavern_road", "The Tavern Road", icon="minecraft:oak_sign", after=["regulars"],
          text=["Bess wants to link the taverns between villages into a network. Find a tavern out on the roads and "
                "meet its keeper, who shares their house recipe."],
          tasks=[{"structure": "#taverns", "title": "Find a tavern"},
                 talk_org("tavern", ["From Reece? Bess's lot? Any friend of hers.",
                                     "Here's our house recipe. Don't tell her I gave it up so easily."])],
          rewards=[reward_item("minecraft:map"), skill("cook", 150)]),

    quest("bakers_dozen", "A Baker's Dozen", icon="bakery:baker_station", after=["tavern_road"],
          text=["The tavern needs breakfast. Build a baker station and bake for the morning crowd."],
          tasks=[item("bakery:baker_station"), item("bakery:baguette", 2), item("bakery:croissant", 2),
                 item("bakery:braided_bread", 2), item("bakery:crusty_bread", 2), item("bakery:toast", 2),
                 item("bakery:strawberry_cake")],
          rewards=[reward_item("bakery:bread_knife"), reward_item("bakery:rolling_pin"), skill("cook", 150)]),

    quest("wandering_baker", "The Wandering Baker", icon="bakery:chocolate_gateau", after=["bakers_dozen"],
          text=["A cart that smells of cinnamon is coming up the road."],
          tasks=[encounter(["Jam! Do you have jam? I'll trade you anything.", "Take my gateau recipe. There's a bakery out west you should see."], entity="bakery:wandering_baker", name="The Wandering Baker"),
                 item("bakery:strawberry_jam", 2, consume=True)],
          rewards=[reward_item("bakery:chocolate_jam", 2), reward_item("bakery:cake_stand"), skill("cook", 150)]),

    quest("tea_time", "Morning Tea", icon="herbalbrews:green_tea", after=["tavern_road"],
          text=["The morning regulars want tea and coffee before the first bell."],
          tasks=[item("herbalbrews:green_tea", 2), item("herbalbrews:black_tea", 2), item("herbalbrews:milk_coffee", 2)],
          rewards=[reward_item("herbalbrews:jug"), reward_item("herbalbrews:tea_leaf_crate"), skill("cook", 150)]),

    quest("first_brew", "The First Brew", icon="brewery:beer_mug", after=["tavern_road"],
          text=["No tavern without beer. Build a brewing station and brew wheat beer and hops beer for the bar."],
          tasks=[item("brewery:wooden_brewingstation"), item("brewery:beer_wheat"), item("brewery:beer_hops")],
          rewards=[reward_item("brewery:bar_counter"), reward_item("brewery:hops_seeds", 8), skill("cook", 150)]),

    quest("food_critic", "The Food Critic", icon="candlelight:cloche", after=["bakers_dozen", "stew_pot"],
          text=["A famous food critic has arrived unannounced. Serve three courses, properly plated and under a "
                "cloche."],
          tasks=[encounter(["I've eaten in every tavern from here to the sea. Impress me.",
                            "A salad, a roast and something sweet. On plates. I'm not an animal."],
                           entity="minecraft:villager", name="The Food Critic"),
                 item("candlelight:salad", consume=True), item("candlelight:roastbeef_with_glazed_carrots", consume=True),
                 item("candlelight:chocolate_mousse", consume=True)],
          rewards=[reward_item("candlelight:chefs_jacket"), reward_item("candlelight:cooking_hat"), skill("cook", 200)]),
]

ACT2 = [
    quest("brewfest_night", "Brewfest Night", icon="artifacts:novelty_drinking_hat",
          after=["first_brew", "main_story:act2_start"], signature="artifacts:novelty_drinking_hat",
          text=["The brewers hold their festival night in a brewfest tent out in the world. Bring barley, oat and "
                "nettle beers and pretzels, keep the mugs full all night, and win the drinking-song contest."],
          tasks=[{"structure": "brewery:brewfest_tent", "title": "Find the brewfest tent"},
                 item("brewery:beer_barley", consume=True, title="Bring barley beer for the tent"),
                 item("brewery:beer_oat", consume=True, title="Bring oat beer for the tent"),
                 item("brewery:beer_nettle", consume=True, title="Bring nettle beer for the tent"),
                 item("brewery:pretzel", 4, consume=True, title="Bring pretzels to keep the crowd fed"),
                 enc(["The mugs are full! Sing, friend! You win the song!", "Wear this hat. It's ridiculous."],
                     entity="minecraft:villager", name="Brewmaster", title="Win the brewmaster's drinking-song contest")],
          rewards=[reward_item("artifacts:novelty_drinking_hat"), skill("cook", 300)]),

    quest("candlelit_dinner", "A Candlelit Dinner", icon="candlelight:dinner_bell", after=["food_critic"],
          text=["The village elder wants a proper dinner for a wedding party. Furnish a dining room with a table, "
                "chairs and a dinner bell, and serve lasagne and fillet steak to the guests."],
          tasks=[{"structure": "#villages", "title": "Go to the elder's dining hall"},
                 {"build": {"blocks": {"candlelight:oak_table": 1, "candlelight:oak_chair": 4, "candlelight:dinner_bell": 1},
                            "radius": 10}, "title": "Furnish the dining room for the wedding party"},
                 item("candlelight:lasagne", 4, consume=True, title="Serve lasagne to the guests"),
                 item("candlelight:fillet_steak", 4, consume=True, title="Serve fillet steak to the guests")],
          rewards=[reward_item("minecraft:gold_ingot", 6), skill("cook", 280)]),

    quest("wine_pairing", "Wine Pairing", icon="vinery:red_wine", after=["candlelit_dinner"],
          text=["The wedding wants every dish paired with its wine: salmon on white wine, beef with mushroom in "
                "wine and potatoes, and a glass of red with the cheese."],
          tasks=[item("candlelight:salmon_on_white_wine", consume=True, title="Cook salmon on white wine"),
                 item("vinery:chenet_wine", consume=True, title="Pour the white wine for the salmon"),
                 item("candlelight:beef_with_mushroom_in_wine_and_potatoes", consume=True, title="Cook beef in wine with potatoes"),
                 item("vinery:red_wine", consume=True, title="Pour the red wine for the beef and cheese")],
          rewards=[reward_item("vinery:acacia_wine_rack_mid"), skill("cook", 300)]),

    quest("cheese_board", "The Cheese Board", icon="meadow:cheese_tart", after=["wine_pairing"],
          text=["The tavern wants a cheese board from Meadow's cheeses: goat, sheep, buffalo and grain cheese, with "
                "cheese tart and fondue on the side."],
          tasks=[item("meadow:piece_of_goat_cheese", consume=True, title="Cut goat cheese for the board"),
                 item("meadow:piece_of_sheep_cheese", consume=True, title="Cut sheep cheese for the board"),
                 item("meadow:piece_of_buffalo_cheese", consume=True, title="Cut buffalo cheese for the board"),
                 item("meadow:piece_of_grain_cheese", consume=True, title="Cut grain cheese for the board"),
                 item("meadow:cheese_tart", title="Bake a cheese tart for the side"),
                 item("meadow:fondue", title="Make a fondue for the side")],
          rewards=[reward_item("meadow:cheese_form"), skill("cook", 320)]),

    quest("popcorn_night", "Popcorn Night", icon="cornexpansion:popcorn_tin", after=["tea_time"],
          text=["Music night at the tavern needs snacks. Make buttery, cheesy and candied popcorn in tins, with "
                "grandma's cornbread for the band."],
          tasks=[item("cornexpansion:buttery_popcorn_tin", title="Make buttery popcorn in a tin"),
                 item("cornexpansion:cheesy_popcorn_tin", title="Make cheesy popcorn in a tin"),
                 item("cornexpansion:candied_popcorn_tin", title="Make candied popcorn in a tin"),
                 item("cornexpansion:grandmas_cornbread", title="Bake cornbread for the band")],
          rewards=[reward_item("immersive_melodies:handpan"), skill("cook", 300)]),

    quest("hot_delivery", "Still Hot", icon="farmersdelight:shepherds_pie_block", after=["tavern_road"],
          text=["A tavern two villages away has run out of stew mid-feast. Carry a shepherd's pie and eight bowls of "
                "beef stew there before the hour is up."],
          tasks=[item("farmersdelight:shepherds_pie_block", consume=True, title="Take a shepherd's pie for the feast"),
                 item("farmersdelight:beef_stew", 8, consume=True, title="Take eight bowls of beef stew"),
                 {"timed": {"seconds": 480, "goal": {"structure": "#taverns", "label": "the feasting tavern", "away": 150},
                            "lines": ["The feast is running dry. Hurry!"], "start": "Carry the food", "no": ["teleport"]},
                  "title": "Reach the tavern before the food goes cold"}],
          rewards=[reward_item("camping:small_backpack"), skill("cook", 300)]),

    quest("greenwood_pub", "The Greenwood Pub", icon="brewery:small_barrel", after=["hot_delivery"],
          text=["The greenwood pub in the deep forest is the last tavern on the network map. Bring its keeper a "
                "barrel of your best beer and find out why no one has heard from them."],
          tasks=[item("brewery:small_barrel", consume=True, title="Bring a barrel of your best beer"),
                 {"structure": "dungeons_arise:greenwood_pub", "title": "Find the greenwood pub in the deep forest"},
                 search("dungeons_arise:greenwood_pub", 1, "the Pub's Secret Ale Recipe", "A stained recipe, tucked in a barrel.",
                        title="Search the pub for why it went silent")],
          rewards=[reward_item("minecraft:writable_book", name="The Greenwood Ale Recipe", lore=["The pub's secret."]),
                   skill("cook", 350)]),

    quest("campfire_feast", "Feast Under the Stars", icon="camping:grill", after=["campfire_supper", "greenwood_pub"],
          text=["Lead a caravan of travellers between taverns and feed them every night on the road: three camps, "
                "three meals cooked on your camp grill."],
          tasks=[{"structure": "mvs:campsite", "title": "Make camp for the first night"},
                 item("farmersdelight:mutton_chops", 4, consume=True, title="Feed the first camp roasted mutton chops"),
                 {"structure": "mvs:fire_camp", "title": "Make camp for the second night"},
                 item("farmersdelight:fish_stew", 4, consume=True, title="Feed the second camp fish stew"),
                 {"structure": "structory:abandoned_camp", "title": "Make camp for the third night"},
                 item("farmersdelight:honey_glazed_ham", 2, consume=True, title="Feed the third camp honey-glazed ham"),
                 {"build": {"blocks": {"camping:grill": 1}, "radius": 8}, "title": "Set your camp grill"}],
          rewards=[reward_item("camping:large_backpack"), skill("cook", 400)]),
]

ACT3 = [
    quest("whiskey", "The Long Wait", icon="brewery:whiskey_highland_hearth", after=["main_story:act3_start", "brewfest_night"],
          text=["The bar wants a whiskey worth the name. Upgrade to a copper brewing station and age a Highland "
                "Hearth or a Smokey Reverie long enough to be worth pouring."],
          tasks=[item("brewery:copper_brewingstation", crafted=True, title="Upgrade to a copper brewing station"),
                 item("brewery:whiskey_highland_hearth", title="Age a Highland Hearth whiskey"),
                 item("brewery:whiskey_smokey_reverie", title="Age a Smokey Reverie whiskey")],
          rewards=[reward_item("brewery:small_barrel"), skill("cook", 400)]),

    quest("nether_kitchen", "The Nether Kitchen", icon="candlelight:fillet_steak", after=["main_story:act3_start", "hot_delivery"],
          text=["An expedition camped near a Nether fortress is living on mushrooms. Cook glowing wine, steak and "
                "potatoes for them, and get it there through the fire."],
          tasks=[item("vinery:glowing_wine", consume=True, title="Brew glowing wine for the expedition"),
                 item("candlelight:fillet_steak", 4, consume=True, title="Cook steak for the camp"),
                 item("minecraft:baked_potato", 8, consume=True, title="Bake potatoes to go with it"),
                 {"timed": {"seconds": 420, "goal": {"structure": "#nether_outposts", "label": "the expedition's camp", "away": 150},
                            "lines": ["Hot food for a cold camp. Through the fire!"], "start": "Carry the meal", "no": ["teleport"]},
                  "title": "Carry the meal through the fire to the expedition"}],
          rewards=[reward_item("minecraft:netherite_upgrade_smithing_template"), skill("cook", 420)]),

    quest("cook_off", "The Cook-Off", icon="artifacts:eternal_steak", after=["wine_pairing", "greenwood_pub"],
          signature="artifacts:eternal_steak",
          text=["The rival tavern down the road claims its steak never runs out. Challenge them to a cook-off: "
                "three judges, three rounds, fillet steak, beef wellington and pork ribs. Win, and their legendary "
                "steak is yours."],
          tasks=[{"structure": "#taverns", "title": "Go to the rival tavern and take up the challenge"},
                 item("candlelight:fillet_steak", consume=True, title="Round one: cook fillet steak for the judges"),
                 item("candlelight:beef_wellington", consume=True, title="Round two: cook beef wellington for the judges"),
                 item("candlelight:pork_ribs", consume=True, title="Round three: cook pork ribs for the judges")],
          rewards=[reward_item("artifacts:eternal_steak"), skill("cook", 480)]),

    quest("herbal_cure", "A Cup for the Sick", icon="herbalbrews:hibiscus_tea", after=["tea_time", "cook_off"],
          text=["A traveller staggers into the tavern feverish. Brew a herbal infusion and hibiscus tea, and nurse "
                "him through the night with chicken soup."],
          tasks=[item("herbalbrews:herbal_infusion", consume=True, title="Brew a herbal infusion for his fever"),
                 item("herbalbrews:hibiscus_tea", consume=True, title="Brew hibiscus tea to cool him"),
                 item("minecraft:rabbit_stew", consume=True, title="Make a hearty stew to nurse him through the night"),
                 enc(["Better... much better. Take my top hat. I'll not need it."], entity="minecraft:villager", name="Feverish Traveller",
                     title="Nurse the feverish traveller through the night")],
          rewards=[reward_item("herbalbrews:flask"), reward_item("minecraft:leather_helmet", name="The Traveller's Top Hat"), skill("cook", 440)]),
]

ACT4 = [
    quest("feast_blocks", "The Wedding Feast", icon="farmersdelight:roast_chicken_block", after=["main_story:act4_start", "candlelit_dinner"],
          text=["The couple from the candlelit dinner are marrying. Cook the feast centrepieces, a roast chicken, "
                "honey-glazed ham, shepherd's pie and stuffed pumpkin, and carry them whole to the wedding."],
          tasks=[item("farmersdelight:roast_chicken_block", consume=True, title="Cook a roast chicken centrepiece"),
                 item("farmersdelight:honey_glazed_ham_block", consume=True, title="Cook a honey-glazed ham"),
                 item("farmersdelight:shepherds_pie_block", consume=True, title="Cook a shepherd's pie"),
                 item("farmersdelight:stuffed_pumpkin_block", consume=True, title="Cook a stuffed pumpkin"),
                 {"structure": "#villages", "title": "Carry the feast whole to the wedding"}],
          rewards=[reward_item("minecraft:cake", 2), skill("cook", 650)]),

    quest("everlasting_recipe", "The Everlasting Recipe", icon="artifacts:everlasting_beef", after=["cook_off", "whiskey"],
          signature="artifacts:everlasting_beef",
          text=["The Reece tavern's own legend: a beef dish that never empties. Piece the recipe together from three "
                "taverns' keepers, then cook its chain to earn it."],
          tasks=[{"structure": "#taverns", "title": "Visit a tavern keeper for a piece of the recipe"},
                 item("farm_and_charm:minced_beef", 4, consume=True, title="Cook the chain's first link: minced beef"),
                 item("farm_and_charm:beef_patty_with_vegetables", consume=True, title="Cook the beef patty"),
                 item("candlelight:beef_wellington", consume=True, title="Cook the chain's last link: beef wellington")],
          rewards=[reward_item("artifacts:everlasting_beef"), skill("cook", 720)]),

    quest("netherite_brewery", "The Master Brewer", icon="brewery:netherite_brewingstation", after=["everlasting_recipe"],
          text=["Build a netherite brewing station and brew the whiskeys and dark brew for the banquet's toast."],
          tasks=[item("brewery:netherite_brewingstation", crafted=True, title="Build a netherite brewing station"),
                 item("brewery:whiskey_lilitusinglemalt", title="Brew a single malt for the toast"),
                 item("brewery:dark_brew", title="Brew the dark brew for the toast")],
          rewards=[reward_item("brewery:brewfest_regalia"), skill("cook", 780)]),
]

ACT5 = [
    quest("banquet", "The Grand Banquet", icon="minecraft:cake", after=["main_story:act5_start", "feast_blocks", "netherite_brewery"],
          text=["Every keeper on the tavern network comes to Reece for a grand banquet. Cook a dish from every "
                "kitchen you've worked, with wine and beer to match."],
          tasks=[{"place": "reece"},
                 item("farmersdelight:beef_stew", 4, consume=True, title="Serve a Farmer's Delight stew"),
                 item("bakery:strawberry_cake", consume=True, title="Serve a Bakery cake"),
                 item("candlelight:lasagne", consume=True, title="Serve a Candlelight lasagne"),
                 item("cornexpansion:grandmas_cornbread", consume=True, title="Serve Corn Expansion cornbread"),
                 item("meadow:fondue", consume=True, title="Serve a Meadow fondue"),
                 item("vinery:red_wine", consume=True, title="Pour a Vinery wine"),
                 item("brewery:beer_wheat", consume=True, title="Pour a Brewery beer")],
          rewards=[reward_item("farmersdelight:cooking_pot"), skill("cook", 850)]),

    quest("last_course", "The Last Course", icon="spartanweaponry:netherite_dagger", after=["banquet"],
          text=["The tavern keepers name you Head of the Table and give you the knife every keeper's mentor passed "
                "down."],
          tasks=[talk_char("bess", ["Head of the Table. You've earned it.", "Take the knife. Don't cut yourself, love."],
                           title="Be named Head of the Table by Bess")],
          rewards=[reward_item("spartanweaponry:netherite_dagger", name="The Last Course", lore=["Passed down from mentor to mentor."],
                               enchant={"minecraft:sharpness": 5, "minecraft:looting": 3, "minecraft:unbreaking": 3, "minecraft:mending": 1}),
                   skill("cook", 1000)]),
]

chapter("skill_cooking", "The Tavern Keepers", "Cooking path", "farmersdelight:cooking_pot", "skills", 3, Q + ACT2 + ACT3 + ACT4 + ACT5)
