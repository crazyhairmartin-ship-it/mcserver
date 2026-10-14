"""Chapter: skill_cooking, the Tavern Keepers' path: prologue and Act I (first release). Plan: src/plans/quests/skill_cooking.json."""
from common import chapter, quest, talk_char, talk_org, item, reward_item, skill, encounter

Q = [
    quest("first_order", "First Order", icon="minecraft:cooked_beef",
          text=["Bess Copperpot runs Reece's tavern, and tonight she's a cook short."],
          tasks=[talk_char("bess", ["You can cook? Wonderful. You're hired. Probably.",
                                    "Eight steaks and eight loaves for tonight's regulars. Go on, chop chop."]),
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
          tasks=[encounter(["Jam! Do you have jam? I'll trade you anything for good jam.",
                            "Strawberry? Perfect. Here: my chocolate gateau recipe. And there's a bakery out west "
                            "you should see."], entity="bakery:wandering_baker", name="The Wandering Baker"),
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

chapter("skill_cooking", "The Tavern Keepers", "Cooking path", "farmersdelight:cooking_pot", "skills", 3, Q)
