"""Chapter: village_errands, small local jobs from the organisations' representatives in any village (pooled).
Plan: src/plans/quests/village_errands.json. Each org's errands share a pool ("<org>_errands"): a villager with no
storyline quest for the player offers one the player can take now. Cast and animals use the shared task types."""
from common import chapter, quest, talk_org, talk_villager, item, reward_item, skill, giver_org, encounter


def enc(lines, title=None, **spec):
    t = encounter(lines, **spec)
    if title:
        t["title"] = title
    return t


def errand(org, lines, accept="I'll do it"):
    g = giver_org(org, lines, accept)
    g["pool"] = org + "_errands"
    return g


Q = [
    # ---- Herbalists ----
    quest("water_from_three_wells", "Water from Three Wells", icon="minecraft:potion",
          giver=errand("herbalists", ["Every well has its own water, and every water brews its own tea. Or so I swear.",
                                      "Fill three bottles from three wells for me, and I'll prove it."]),
          text=["A Herbalist swears every well's water makes a different tea, and wants proof from three wells."],
          tasks=[{"structure": "#wells", "title": "Find a well to draw water from"},
                 item("minecraft:potion", 3, consume=True, title="Bring her three bottles of well water")],
          rewards=[reward_item("herbalbrews:green_tea_leaf", 8), skill("forage", 60)]),

    quest("make_a_wish", "Make a Wish", icon="minecraft:gold_nugget",
          giver=errand("herbalists", ["I dropped my lucky coin into a wishing well. I only wanted to make a wish!",
                                      "It's the one with a roof and a statue, past the old ruins. Could you "
                                      "fish it out?"]),
          text=["A young Herbalist lost her lucky coin in a wishing well and cannot bear to be without it."],
          tasks=[{"structure": "dungeons_arise:wishing_well", "title": "Find the wishing well"},
                 item("minecraft:gold_nugget", title="Fish her lucky coin from the bottom")],
          rewards=[reward_item("minecraft:rabbit_foot"), reward_item("minecraft:emerald", 3), skill("forage", 100)]),

    quest("honey_from_the_dome", "Honey from the Dome", icon="minecraft:honey_bottle",
          giver=errand("herbalists", ["Honey's the best thing for a sore throat, and mine has run out.",
                                      "The bees in the birch woods keep a great glass dome of hives. Calm them "
                                      "with a campfire first. They sting less."]),
          text=["A Herbalist is out of honey, and the bee dome in the birch woods has plenty."],
          tasks=[{"structure": "mvs:bee_dome", "title": "Find the bee dome in the birch woods"},
                 {"build": {"blocks": {"minecraft:campfire": 1}, "radius": 8}, "title": "Light a campfire to calm the bees"},
                 item("minecraft:honey_bottle", 2, title="Collect honey for her tea"),
                 item("minecraft:honeycomb", 4, title="Collect combs for her salves")],
          rewards=[reward_item("minecraft:beehive"), skill("forage", 120)]),

    # ---- Growers' co-op ----
    quest("sand_in_the_bucket", "Desert Water", icon="minecraft:cactus",
          giver=errand("growers", ["Folk say the desert wells never run dry. I'd like to know how.",
                                   "Bring me a bucket from one, and a cutting of the cactus that grows beside it."]),
          text=["The Growers' co-op wants to know how desert wells never run dry, and what grows beside them."],
          tasks=[{"structure": "mss:desert_well", "title": "Find a desert well"},
                 item("minecraft:water_bucket", consume=True, title="Draw a bucket of its water"),
                 item("minecraft:cactus", title="Cut a piece of the cactus beside it")],
          rewards=[reward_item("minecraft:bone_meal", 16), skill("farm", 100)]),

    quest("the_desert_pump", "The Pump Still Works", icon="minecraft:bucket",
          giver=errand("growers", ["My field's dry as old bread and there's no river for miles.",
                                   "I've heard there's a pump out in the dunes that still works. Fill a bucket "
                                   "there and bring it back to water my new field."]),
          text=["A desert farmer needs water for a new field and the only working pump is out in the dunes."],
          tasks=[{"structure": "mvs:desert_pump", "title": "Find the working pump in the dunes"},
                 item("minecraft:water_bucket", consume=True, title="Fill a bucket for her thirsty field"),
                 {"structure": "#villages", "title": "Carry it to the desert village"},
                 {"build": {"blocks": {"minecraft:farmland": 4}, "radius": 10}, "title": "Water her new field"}],
          rewards=[reward_item("farm_and_charm:tomato_seeds", 8), reward_item("farm_and_charm:lettuce_seeds", 8),
                   skill("farm", 120)]),

    quest("stall_of_your_own", "A Stall of Your Own", icon="another_furniture:red_awning",
          after=["the_travelling_market"],
          giver=errand("growers", ["The Co-op wants a stall at the next market, and the old trestle table won't do.",
                                   "You've seen the roadside stalls. Copy one in the village and put some "
                                   "produce on display."]),
          text=["The Growers' co-op wants a stall at the next market, built like the roadside ones, with produce on it."],
          tasks=[{"structure": "mvs:red_stall", "title": "Look over a roadside stall for ideas"},
                 {"build": {"blocks": {"another_furniture:oak_table": 1, "another_furniture:red_awning": 1,
                                       "farmersdelight:wooden_basket": 2}, "radius": 10},
                  "title": "Set up a market stall in the village"}],
          rewards=[reward_item("minecraft:bell"), reward_item("minecraft:emerald", 4), skill("farm", 150)]),

    quest("seeds_for_sky_farms", "Seeds for the Sky Farms", icon="minecraft:wheat_seeds", after=["parcel_for_the_sky"],
          giver=errand("growers", ["The sky villagers can't get seeds up to their islands. They'd be grateful for any.",
                                   "Four sorts, please. Then help them plant."]),
          text=["The sky villagers cannot get seeds up to their floating fields, so they are going hungry."],
          tasks=[{"structure": "skyvillages:skyvillage", "title": "Climb to the sky village"},
                 item("minecraft:wheat_seeds", 8, consume=True, title="Give them wheat seeds"),
                 item("minecraft:beetroot_seeds", 8, consume=True, title="Give them beetroot seeds"),
                 item("minecraft:melon_seeds", 4, consume=True, title="Give them melon seeds"),
                 item("minecraft:pumpkin_seeds", 4, consume=True, title="Give them pumpkin seeds"),
                 {"build": {"blocks": {"minecraft:farmland": 6}, "radius": 10}, "title": "Help plant their island fields"}],
          rewards=[reward_item("minecraft:emerald", 5), skill("farm", 200)]),

    quest("flour_run", "The Flour Run", icon="farm_and_charm:flour",
          giver=errand("growers", ["The co-op's mill has broken, and the baker is down to her last scoop of flour.",
                                   "There's a windmill out in the wild that still turns. Take it some wheat."]),
          text=["The Growers' co-op's mill has broken, and the baker needs flour before the next market day."],
          tasks=[item("minecraft:wheat", 16, consume=True, title="Gather wheat to grind"),
                 {"structure": "mvs:windmill", "title": "Find the windmill that still turns"},
                 item("farm_and_charm:flour", 8, title="Grind the wheat into flour for the baker")],
          rewards=[reward_item("farm_and_charm:flour", 16), reward_item("bakery:bread", 8), skill("farm", 130)]),

    # ---- Crafters' guild ----
    quest("restore_the_fountain", "Restore the Fountain", icon="minecraft:chiseled_stone_bricks",
          giver=errand("crafters", ["Our village square wants a proper stone fountain, and nobody remembers how "
                                    "the old ones were cut.",
                                    "There's one standing out in the wild. Look it over, then build one at home."]),
          text=["A Crafters' guild mason wants the village square to have a stone fountain like the old ones."],
          tasks=[{"structure": "mvs:stone_fountain", "title": "Study the old fountain in the wild"},
                 {"build": {"blocks": {"minecraft:stone_bricks": 16, "minecraft:stone_brick_stairs": 4,
                                       "minecraft:chiseled_stone_bricks": 1}, "radius": 10},
                  "title": "Build a fountain for the village square"}],
          rewards=[reward_item("minecraft:stone_bricks", 32), reward_item("minecraft:chiseled_stone_bricks", 4),
                   skill("craft", 130)]),

    quest("salvage_the_ruins", "Salvage", icon="minecraft:mossy_stone_bricks",
          giver=errand("crafters", ["Old stone has a character new stone lacks, and the guild wants some for the "
                                    "chapel repairs.",
                                    "Bring me blocks from two different ruins near here. Take what's loose, not "
                                    "the walls."]),
          text=["The Crafters' guild needs old stone with a history to it for the chapel repairs."],
          tasks=[{"structure": "structory:ruin_grassy", "title": "Salvage stone from a grassy ruin"},
                 {"structure": "mvs:small_ruin", "title": "Salvage stone from a second ruin"},
                 item("minecraft:mossy_stone_bricks", 8, title="Bring mossy stone for the chapel"),
                 item("minecraft:cracked_stone_bricks", 8, title="Bring weathered stone for the chapel")],
          rewards=[reward_item("minecraft:stone_bricks", 32), skill("craft", 100)]),

    # ---- Tavern keepers ----
    quest("the_travelling_market", "The Travelling Market", icon="farmersdelight:onion",
          giver=errand("tavern", ["Travellers swear the roadside stalls sell spices you can't get in town.",
                                  "Find two stalls and a cart, and bring me what their owners left behind."]),
          text=["A tavern keeper heard that the roadside stalls sell spices unavailable in town and wants a taste."],
          tasks=[{"structure": "mvs:red_stall", "title": "Find a roadside stall"},
                 {"structure": "mvs:blue_stall", "title": "Find a second stall"},
                 {"structure": "mvs:cart", "title": "Find a trader's cart"},
                 item("farmersdelight:onion", 4, title="Collect what the traders left for her kitchen"),
                 item("farmersdelight:tomato", 4, title="Collect tomatoes for her sauces")],
          rewards=[reward_item("farmersdelight:rice", 16), reward_item("farmersdelight:cabbage_seeds", 8),
                   skill("cook", 120)]),

    quest("cook_over_open_fire", "Cook over an Open Fire", icon="camping:grill",
          giver=errand("tavern", ["Food tastes better outdoors, and I'll hear no argument.",
                                  "There's a fire camp out in the wild. Cook me a proper meal there and bring "
                                  "it back while it's still warm."]),
          text=["A tavern keeper insists food tastes better cooked outdoors, and wants a meal from a wild fire camp."],
          tasks=[{"structure": "mvs:fire_camp", "title": "Find the wild fire camp"},
                 item("minecraft:cooked_beef", 2, consume=True, title="Cook a meal over the camp fire")],
          rewards=[reward_item("camping:grill"), skill("cook", 90)]),

    quest("the_prankster", "Something Smells Funny", icon="artifacts:whoopee_cushion",
          signature="artifacts:whoopee_cushion",
          giver=errand("tavern", ["Every time I sit down, there's a rude noise, and the whole village laughs.",
                                  "I know it's one of the villagers. Find out which, would you? Quietly."]),
          text=["The village butcher cannot sit without a rude noise, and the whole village laughs. Somebody is "
                "responsible."],
          tasks=[{"structure": "#villages", "title": "Follow the giggles through the village"},
                 enc(["Hee hee hee! You can't catch me!"], entity="minecraft:villager", name="The Prankster",
                           title="Spot the giggling villager"),
                 enc(["Oh, you found me again! Best of three!"], entity="minecraft:villager",
                           name="The Prankster", title="Catch him in a game of hide and seek"),
                 enc(["Fine, fine! You win! Take the cushion, and don't tell the butcher."],
                           entity="minecraft:villager", name="The Prankster",
                           title="Make the prankster give up the cushion")],
          rewards=[reward_item("artifacts:whoopee_cushion"), reward_item("minecraft:cake"), skill("agility", 150)]),

    # ---- Village Watch ----
    quest("scout_the_castle", "Scout the Castle", icon="minecraft:spyglass",
          giver=errand("watch", ["We think raiders are camping in the old castle ruins. We can't see from here.",
                                 "Go and count their fires, and don't get spotted. If you're hurt, they know "
                                 "you're there."]),
          text=["The Village Watch fear raiders are camped in the old castle ruins and need someone to look "
                "without being seen."],
          tasks=[{"timed": {"seconds": 420, "goal": {"structure": "mvs:castle_ruins", "label": "the castle ruins"},
                            "lines": ["Stay low. If anything hurts you, they've seen you."],
                            "start": "Begin scouting", "no": ["hurt"]}, "title": "Creep up to the castle unseen"},
                 {"checkmark": "I counted their fires and left unseen"}],
          rewards=[reward_item("minecraft:spyglass"), skill("defense", 80)]),

    quest("the_abandoned_camp", "Who Left the Camp?", icon="minecraft:campfire",
          giver=errand("watch", ["We found a camp, fire still warm and nobody in sight.",
                                 "Search it for clues, and find out where the campers went. They may need help."]),
          text=["The Village Watch found an abandoned camp with the fire still warm, and fear for the campers."],
          tasks=[{"structure": "structory:abandoned_camp", "title": "Search the abandoned camp for clues"},
                 {"checkmark": "I found tracks leading away from the camp"},
                 enc(["Oh! You found us! We ran when we heard wolves, and we couldn't find the way back."],
                           entity="minecraft:villager", name="Lost Camper", title="Find the missing campers")],
          rewards=[reward_item("minecraft:campfire"), reward_item("minecraft:cooked_beef", 8), skill("defense", 120)]),

    quest("fortified_village", "Behind the Walls", icon="spartanshields:iron_tower_shield",
          giver=errand("watch", ["Our captain would like to learn how a walled village holds out.",
                                 "Visit one, talk to its guards and help hold the wall for a night."]),
          text=["The Village Watch's captain wants to learn from a fortified village, and the best lesson is to "
                "help hold its wall."],
          tasks=[{"structure": "ctov:medium/village_plains_fortified", "title": "Travel to a fortified village"},
                 talk_org("watch", ["Visitor from the watch? Welcome. Mind the gate, it sticks.",
                                    "We keep two on the wall at all times, and one on the roof.",
                                    "Raiders always come at dusk. You can stand with us tonight."],
                          title="Talk to the wall's guards"),
                 {"timed": {"seconds": 300, "goal": {"hold": {"radius": 20}},
                            "waves": [{"entity": "minecraft:pillager", "count": 2, "every": 40},
                                      {"entity": "minecraft:zombie", "count": 3, "every": 30}],
                            "lines": ["Night's coming. Man the wall!"], "start": "Man the wall"},
                  "title": "Hold the wall through the night"}],
          rewards=[reward_item("spartanshields:iron_basic_shield"), skill("defense", 220)]),

    quest("a_name_on_the_gallows", "Justice", icon="minecraft:iron_sword",
          giver=errand("watch", ["A merchant was robbed on the road, and the bandit's hiding out near the old "
                                 "gallows hill.",
                                 "Bring him to justice. I'd rather he didn't get away."]),
          text=["The Village Watch want the bandit who robbed a merchant brought to justice before he vanishes."],
          tasks=[{"structure": "mvs:gallows", "title": "Track the bandit to the gallows hill"},
                 enc(["You'll never take me alive!"], then="kill", entity="minecraft:pillager",
                           name="The Bandit", health=40, glow=True, title="Bring the bandit to justice")],
          rewards=[reward_item("minecraft:emerald", 6), skill("defense", 140)]),

    # ---- Arcane order ----
    quest("statue_rubbings", "Statue Rubbings", icon="minecraft:paper",
          giver=errand("arcane", ["The carvings on the fallen statues out in the ruins are some of the oldest "
                                  "writing around.",
                                  "Make me rubbings of them with paper and charcoal. I'd go, but my knees."]),
          text=["An Arcane Order librarian wants copies of the carvings on fallen statues, which may be some of the "
                "oldest writing around."],
          tasks=[item("minecraft:paper", 4, title="Bring paper to take rubbings"),
                 item("minecraft:charcoal", 4, title="Bring charcoal to take rubbings"),
                 {"structure": "mvs:statue_ruins", "title": "Rub the carvings on a fallen statue"},
                 {"structure": "mvs:log_ruin", "title": "Rub the carvings on a log ruin"}],
          rewards=[reward_item("minecraft:book", 4), skill("magic", 100)]),

    # ---- Anglers' society ----
    quest("outcast_fisherman", "The Outcast Fisherman", icon="aquaculture:worm",
          giver=errand("anglers", ["There's a fisherman who left his village to live on a boat. They say he has "
                                   "the best bait on the water.",
                                   "Find his boat and trade for some. He'll like emeralds, I expect."]),
          text=["The Anglers' Society talk of a fisherman who left his village for a boat, and keeps the best bait."],
          tasks=[{"structure": "structory:boat", "title": "Find the outcast's boat at sea"},
                 item("minecraft:emerald", 2, consume=True, title="Pay for his best bait"),
                 enc(["Visitors? Out here? Well, sit down, sit down.",
                            "Why did I leave? The village talked too much. The sea doesn't.",
                            "Take the bait. Worms from my own bed. And take the boat when I'm done with it."],
                           entity="minecraft:villager", name="Outcast Fisherman", title="Trade with the outcast")],
          rewards=[reward_item("aquaculture:worm", 16), skill("fish", 100)]),

    quest("supplies_for_the_boat", "Supplies for the Boat", icon="minecraft:bread", after=["outcast_fisherman"],
          giver=errand("anglers", ["That fisherman on his boat is out of bread and rope.",
                                   "Take him some. If he's pleased, he'll tell you where the big fish bite."]),
          text=["The outcast fisherman is out of bread and rope, and cannot leave his boat to buy more."],
          tasks=[item("minecraft:bread", 16, consume=True, title="Gather bread for the fisherman"),
                 item("supplementaries:rope", 8, consume=True, title="Gather rope for his lines"),
                 {"structure": "structory:boat", "title": "Sail out to his boat"},
                 enc(["Bread! And rope! You're a lifesaver.",
                            "The big fish bite at dusk in the deep water off the headland. Don't tell Halloway."],
                           entity="minecraft:villager", name="Outcast Fisherman", title="Hand over the supplies")],
          rewards=[reward_item("aquaculture:gold_hook"), skill("fish", 140)]),

    quest("storm_at_sea", "Storm at Sea", icon="smallships:oak_cog", after=["supplies_for_the_boat"],
          giver=errand("anglers", ["A thunderstorm has caught a fisherman's boat far out at sea!",
                                   "Get to him before it passes, and bring him back to the harbour alive."]),
          text=["A thunderstorm has caught a fisherman's boat far out at sea, and the storm will not last."],
          tasks=[{"timed": {"seconds": 420, "goal": {"structure": "structory:boat", "label": "the stricken boat",
                                                      "away": 100},
                            "lines": ["The storm is building. Get to the boat!"], "start": "Race the storm",
                            "no": ["teleport"]}, "title": "Race out to the stricken boat"},
                 enc(["Thank the tides! The mast went an hour ago. Take me home!"], then="escort",
                           entity="minecraft:villager", name="Stranded Fisherman",
                           to={"structure": "#villages", "label": "the harbour"}, title="Bring him back to harbour")],
          rewards=[reward_item("smallships:oak_cog"),
                   reward_item("minecraft:fishing_rod", name="Storm-Tested", lore=["Pulled from a wrecked boat."],
                               enchant={"minecraft:lure": 2, "minecraft:luck_of_the_sea": 1}),
                   skill("fish", 220)]),

    # ---- Couriers ----
    quest("lost_cart", "The Lost Cart", icon="minecraft:chest",
          giver=errand("couriers", ["A courier's cart broke down in the jungle with parcels aboard.",
                                    "Find it and carry what's on it to the jungle village. Those parcels are "
                                    "overdue."]),
          text=["A courier's bamboo cart broke down in the jungle with parcels aboard, and the parcels are overdue."],
          tasks=[{"structure": "mvs:medium_bamboo_cart", "title": "Find the broken cart"},
                 {"checkmark": "I loaded the parcels from the cart"},
                 {"structure": "nova_structures:village_jungle", "title": "Carry the parcels to the jungle village"}],
          rewards=[reward_item("sophisticatedbackpacks:backpack"), skill("agility", 150)]),

    quest("ruins_on_the_map", "Ruins on the Map", icon="minecraft:map",
          giver=errand("couriers", ["I'm mapping the wild ruins so travellers don't wander into them by night.",
                                    "A desert ruin, a jungle ruin and a swamp ruin. Visit each and mark them."]),
          text=["A courier is mapping the wild ruins so that travellers do not wander into them after dark."],
          tasks=[{"structure": "nova_structures:desert_ruins", "title": "Mark the desert ruin"},
                 {"structure": "nova_structures:jungle_ruins", "title": "Mark the jungle ruin"},
                 {"structure": "structory:swamp_ruin", "title": "Mark the swamp ruin"}],
          rewards=[reward_item("minecraft:map"), reward_item("minecraft:emerald", 4), skill("agility", 160)]),

    quest("parcel_for_the_sky", "A Parcel for the Sky", icon="endermail:package",
          giver=errand("couriers", ["I've a parcel for a sky village, and the carriers won't fly that high.",
                                    "Get it up there within the day and collect the signature."]),
          text=["The Couriers have a parcel for a sky village that the Ender Mail carriers will not deliver."],
          tasks=[item("endermail:package", title="Take the parcel for the sky village"),
                 {"timed": {"seconds": 1200, "goal": {"structure": "skyvillages:skyvillage", "label": "the sky village"},
                            "lines": ["Twenty minutes to reach the sky village. No teleporting."],
                            "start": "Set off", "no": ["teleport", "elytra"]}, "title": "Reach the sky village in time"},
                 {"checkmark": "I collected the signature"}],
          rewards=[reward_item("endermail:stamp", 6), skill("agility", 200)]),

    quest("sky_village_fall", "The Long Way Down", icon="beachparty:beach_parasol", after=["parcel_for_the_sky"],
          giver=errand("couriers", ["A sky villager's child fell off the edge and floated down on a parasol!",
                                    "She'll be on the ground somewhere near their island. Get her back up there."]),
          text=["A sky villager's child fell off the edge and floated down on a parasol, and her parents are frantic."],
          tasks=[{"structure": "skyvillages:skyvillage", "title": "Reach the sky village"},
                 enc(["I fell off! It was so high! I want to go home!"], then="escort",
                           entity="minecraft:villager", name="Fallen Sky Child",
                           to={"structure": "skyvillages:skyvillage", "label": "the sky village"},
                           title="Bring the child safely home")],
          rewards=[reward_item("beachparty:beach_parasol"), reward_item("minecraft:feather", 8), skill("agility", 180)]),

    quest("map_the_region", "Map the Region", icon="supplementaries:globe",
          giver=errand("couriers", ["The cartographer's tower in the wilds keeps a master map of this whole region.",
                                    "Climb it, copy what you can and fill in the land around our village."]),
          text=["A courier needs an up-to-date map of the region, and the best one hangs in a cartographer's tower."],
          tasks=[{"structure": "mvs:cartographer_tower", "title": "Climb the cartographer's tower"},
                 item("minecraft:map", crafted=True, title="Make a map to copy from the master")],
          rewards=[reward_item("supplementaries:globe"), reward_item("explorerscompass:explorerscompass"),
                   skill("agility", 150)]),

    quest("letter_to_a_village", "Letter to Another Village", icon="fotfmail:letter",
          giver=errand("couriers", ["I've a letter for a villager in the next village along the road.",
                                    "Deliver it by hand or by mail. Either way, it needs to get there."]),
          text=["A courier has a letter for a villager in the next village along the road."],
          tasks=[item("fotfmail:letter", consume=True, title="Take the letter along the road"),
                 {"structure": "#villages", "title": "Reach the next village"},
                 talk_villager("minecraft:librarian", ["A letter? For me? Oh, how lovely.",
                                                       "I shall write a reply tonight. Tell the courier it's coming."],
                               title="Hand it to the librarian")],
          rewards=[reward_item("fotfmail:letter", 4), reward_item("endermail:stamp", 2), skill("agility", 70)]),

    quest("the_wild_waystone", "Linking the Villages", icon="waystones:warp_stone",
          giver=errand("couriers", ["It takes our runners half a day to reach the next village on foot.",
                                    "If both villages' waystones were linked, they could cross in a blink."]),
          text=["The Couriers want two villages' waystones linked, so that runners can cross between them in a blink."],
          tasks=[{"waystones": 2, "title": "Attune this village's waystone and the next one's"},
                 item("waystones:warp_stone", title="Carry a warp stone between them")],
          rewards=[reward_item("waystones:warp_stone"), skill("agility", 90)]),

    quest("village_jungle", "The Jungle Village", icon="minecraft:cocoa_beans",
          giver=errand("couriers", ["We've never reached the village in the sparse jungle. Nobody has a map.",
                                    "Find it, introduce yourself and bring back a list of what they trade."]),
          text=["The Couriers have never reached the village in the sparse jungle and would like to know what they trade."],
          tasks=[{"structure": "nova_structures:village_jungle", "title": "Find the village in the sparse jungle"},
                 talk_villager("any", ["A visitor! We get so few. Welcome.",
                                       "We trade cocoa and bamboo, mostly. Fruit in season.",
                                       "Tell your couriers the road is open."], title="Ask what they trade")],
          rewards=[reward_item("minecraft:cocoa_beans", 16), reward_item("minecraft:emerald", 4), skill("agility", 160)]),

    # ---- Sanctuary keepers ----
    quest("runaway_horse", "The Runaway Horse", icon="minecraft:saddle",
          giver=errand("sanctuary", ["My horse bolted and ran off to the wild horse pen. She's frightened, not bad.",
                                     "Find her, calm her and bring her home."]),
          text=["A Sanctuary keeper's horse ran off to a wild horse pen, and she is frightened rather than bad."],
          tasks=[{"structure": "mvs:horse_pen", "title": "Find the wild horse pen"},
                 {"tame": "minecraft:horse", "title": "Win the horse's trust and tame her"},
                 {"checkmark": "I rode her back and stabled her"}],
          rewards=[reward_item("minecraft:saddle"), reward_item("minecraft:golden_carrot", 6), skill("taming", 120)]),

    quest("fox_in_the_hut", "The Fox in the Hut", icon="minecraft:sweet_berries",
          giver=errand("sanctuary", ["Foxes have taken over a hut in the taiga, and there are kits.",
                                     "Breed a pair with sweet berries, and bring a kit back to the Sanctuary."]),
          text=["Foxes have taken over a hut in the taiga, and a Sanctuary keeper wants a kit raised safely."],
          tasks=[{"structure": "mvs:fox_hut", "title": "Find the foxes' hut"},
                 {"breed": "minecraft:fox", "title": "Breed a pair of foxes"},
                 {"tame": "minecraft:fox", "title": "Take a kit under your care"}],
          rewards=[reward_item("minecraft:sweet_berries", 16), skill("taming", 120)]),

    quest("sled_dogs", "Sled Dogs", icon="snowyspirit:sled_oak",
          giver=errand("sanctuary", ["The Sanctuary wants a sled team for winter deliveries.",
                                     "Tame wolves near the snowy dog hut, then see how a team pulls a sled."]),
          text=["The Sanctuary keepers want a sled team for winter deliveries, and need to see how wolves pull."],
          tasks=[{"structure": "mvs:snowy_dog_hut", "title": "Find the snowy dog hut"},
                 {"tame": "minecraft:wolf", "count": 2, "title": "Tame two wolves for the team"},
                 {"advancement": "snowyspirit:adventure/sled_with_wolf", "title": "Ride a sled pulled by a wolf"}],
          rewards=[reward_item("snowyspirit:sled_oak"), reward_item("minecraft:bone", 8), skill("taming", 150)]),
]

chapter("village_errands", "Village Errands", "Small jobs for the people around you", "minecraft:emerald", "side", 2, Q)
