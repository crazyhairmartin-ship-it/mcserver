"""Chapter: skill_taming, the Sanctuary Keepers path: prologue and Act I (first release).
Plan: src/plans/quests/skill_taming.json. Keeper Fern Thistlewood runs the sanctuary at the edge of Reece."""
from common import chapter, quest, talk_char, item, reward_item, skill, giver_org, encounter
from common import enc, fight, boss, search, sample, talk_org, talk_villager, talk_char, item, reward_item, skill, encounter, giver_org  # noqa: F401

Q = [
    quest("stray_wolf", "The Stray", icon="minecraft:bone",
          giver=giver_org("sanctuary", ["A half-starved wolf follows my flock at a distance.", "Win its trust, and Keeper Fern in Reece will take it in."], "I'll try"),
          text=["A shepherd says a half-starved wolf follows the flock at a distance. Tame it, give it a collar "
                "tag and bring it to Fern's pen at the edge of Reece."],
          tasks=[{"tame": "minecraft:wolf", "title": "Tame the wolf"},
                 item("domesticationinnovation:collar_tag"), {"place": "reece"},
                 talk_char("fern", ["Thin as a rake. Come in. You waited, most people shout.", "There's more to do here, if you'd help."])],
          rewards=[reward_item("domesticationinnovation:collar_tag"), skill("taming", 50)]),

    quest("first_pens", "Pens and Pet Beds", icon="domesticationinnovation:pet_bed_brown", after=["stray_wolf"],
          text=["The sanctuary is a single fence. Build proper pens and pet beds so rescued animals have a place "
                "to rest."],
          tasks=[{"place": "reece"}, item("domesticationinnovation:pet_bed_brown", crafted=True),
                 {"build": {"blocks": {"#minecraft:fences": 12, "#minecraft:fence_gates": 1,
                                       "minecraft:hay_block": 2}, "radius": 10}, "title": "Build a pen"}],
          rewards=[reward_item("domesticationinnovation:pet_bed_blue"),
                   reward_item("domesticationinnovation:pet_bed_red"), skill("taming", 90)]),

    quest("lame_horse", "The Lame Horse", icon="minecraft:saddle", after=["stray_wolf"],
          text=["Travellers abandoned a lame horse at their horse campsite. Find the camp, feed the horse back to "
                "health with apples and hay, tame it and ride it home slowly."],
          tasks=[{"structure": "mvs:horse_campsite", "title": "Find the horse campsite"},
                 item("minecraft:apple", 3, consume=True), item("minecraft:hay_block", 1, consume=True),
                 {"tame": "minecraft:horse", "title": "Tame the horse"}, {"place": "reece", "title": "Ride the horse home"}],
          rewards=[reward_item("minecraft:saddle"), skill("taming", 100)]),

    quest("fox_kits", "Kits at the Hut", icon="minecraft:sweet_berries", after=["first_pens"],
          text=["A hunter's fox hut has orphaned kits nearby. Win the wary foxes' trust by breeding a pair with "
                "sweet berries."],
          tasks=[{"structure": "mvs:fox_hut", "title": "Find the fox hut"},
                 item("minecraft:sweet_berries", 4, consume=True),
                 {"breed": "minecraft:fox", "title": "Breed a pair of foxes"}],
          rewards=[reward_item("minecraft:glow_berries", 16), skill("taming", 110)]),

    quest("critter_census", "The Critter Census", icon="crittersandcompanions:ferret_spawn_egg",
          after=["stray_wolf"],
          text=["Fern keeps a census of the small animals around Reece. Find an otter, a red panda, a ferret and "
                "a shima enaga, and tame a ferret to help with the count."],
          tasks=[{"observe": "crittersandcompanions:otter", "ticks": 20, "title": "Find an otter"},
                 {"observe": "crittersandcompanions:red_panda", "ticks": 20, "title": "Find a red panda"},
                 {"observe": "crittersandcompanions:ferret", "ticks": 20, "title": "Find a ferret"},
                 {"observe": "crittersandcompanions:shima_enaga", "ticks": 20, "title": "Find a shima enaga"},
                 {"tame": "crittersandcompanions:ferret", "title": "Tame a ferret"}],
          rewards=[reward_item("crittersandcompanions:silk_lead"), skill("taming", 100)]),

    quest("butterfly_net", "Wings in a Bottle", icon="butterflies:butterfly_net", after=["critter_census"],
          text=["Start the sanctuary's butterfly collection. Bottle five different butterflies across meadows and "
                "forests, without harming a single one."],
          tasks=[item("butterflies:butterfly_net", crafted=True),
                 item("butterflies:bottled_butterfly_cabbage"), item("butterflies:bottled_butterfly_common"),
                 item("butterflies:bottled_butterfly_monarch"), item("butterflies:bottled_butterfly_admiral"),
                 item("butterflies:bottled_butterfly_morpho")],
          rewards=[reward_item("butterflies:banner_pattern_butterfly"), skill("taming", 120)]),

    quest("cat_colony", "The Cats of the Ruin", icon="artifacts:kitty_slippers", after=["fox_kits"],
          signature="artifacts:kitty_slippers",
          text=["A colony of stray cats lives in a crumbling ruin that creepers have overrun. Clear the creepers, "
                "coax every cat out with fish, and the old cat-lady of the ruin will leave you her slippers."],
          tasks=[{"structure": "#ruins", "title": "Find the overrun ruin"},
                 {"kill": "minecraft:creeper", "count": 5, "title": "Clear the creepers away from the cats", "spawn": {"at": {"structure": "#ruins"}}},
                 item("minecraft:cod", 4, consume=True, title="Coax the cats out with fish"),
                 encounter(["My darlings, all safe! Forty winters among these ruins.", "Take my slippers, dear. The cats insist."],
                           entity="minecraft:villager", name="The Cat-Lady of the Ruin")],
          rewards=[reward_item("artifacts:kitty_slippers"), skill("taming", 250)]),

    quest("sled_dogs", "Lost in the Blizzard", icon="domesticationinnovation:feather_on_a_stick",
          after=["stray_wolf"],
          text=["The snowy dog hut's sled team ran off in a blizzard. Track the wolves across the snow and tame "
                "each one back."],
          tasks=[{"structure": "mvs:snowy_dog_hut", "title": "Find the snowy dog hut"},
                 item("minecraft:bone", 8, consume=True), {"tame": "minecraft:wolf", "count": 3, "title": "Tame the sled team back"}],
          rewards=[reward_item("domesticationinnovation:feather_on_a_stick"), skill("taming", 180)]),

    quest("butterfly_house", "The Butterfly House", icon="butterflies:bottled_caterpillar_common",
          after=["butterfly_net"],
          text=["Build a glass butterfly house, raise caterpillars in jars through chrysalis to butterfly, and "
                "release them inside among the flowers."],
          tasks=[{"place": "reece"},
                 {"build": {"blocks": {"minecraft:glass": 30, "#minecraft:flowers": 8}, "radius": 12},
                  "title": "Build a glass butterfly house"},
                 item("butterflies:bottled_caterpillar_common"), {"checkmark": "I released the butterflies"}],
          rewards=[reward_item("butterflies:admiral_egg", 2), reward_item("butterflies:atlas_egg", 2),
                   skill("taming", 200)]),

    quest("koi_pond", "The Koi Pond", icon="crittersandcompanions:koi_fish_bucket", after=["first_pens"],
          text=["A merchant's koi are dying in a stagnant pool. Bucket them, dig a proper pond at the sanctuary "
                "with lily pads and clams, and add a dumbo octopus for the visitors."],
          tasks=[item("crittersandcompanions:koi_fish_bucket", 2),
                 item("crittersandcompanions:dumbo_octopus_bucket"), {"place": "reece"},
                 {"build": {"blocks": {"minecraft:lily_pad": 4, "crittersandcompanions:clam": 2}, "radius": 10},
                  "title": "Dig a pond with lily pads and clams"}],
          rewards=[reward_item("crittersandcompanions:pearl_necklace_1"), skill("taming", 220)]),

    quest("pet_enchanting", "A Collar Worth Wearing", icon="domesticationinnovation:collar_tag",
          after=["sled_dogs"],
          text=["Fern shows you how to enchant a collar tag: Health Boost and a creeper-sniffing Defusal, so your "
                "wolf can guard the sanctuary."],
          tasks=[talk_char("fern", ["A collar tag is paper and string until someone believes in it.", "Health Boost, and Defusal so your wolf sniffs out creepers."]),
                 item("domesticationinnovation:collar_tag", crafted=True),
                 {"interact": "minecraft:wolf", "holding": "domesticationinnovation:collar_tag", "consume": True, "title": "Fit the enchanted tag to a wolf's collar"}],
          rewards=[reward_item("minecraft:enchanted_book", name="Hale and Hearty",
                               enchant={"domesticationinnovation:health_boost": 1}),
                   reward_item("minecraft:enchanted_book", name="Nose for Trouble",
                               enchant={"domesticationinnovation:defusal": 1}),
                   skill("taming", 160)]),

    quest("eggs_to_hatch", "Eggs to Hatch", icon="naturalist:duck_egg", after=["koi_pond"],
          text=["A storm flooded the riverbank nests. Collect duck, tortoise and snail eggs before they're lost, "
                "hatch them at the sanctuary and keep the young safe until they're grown."],
          tasks=[item("naturalist:duck_egg", 2), item("naturalist:tortoise_egg"), item("naturalist:snail_eggs"),
                 {"place": "reece"}, {"checkmark": "The young have grown"}],
          rewards=[reward_item("naturalist:bug_net"), skill("taming", 240)]),

    quest("dragonfly_rider", "Shimmering Wings", icon="crittersandcompanions:iron_dragonfly_armor",
          after=["critter_census"],
          text=["Tame a dragonfly by the marsh and make it iron armour so it can patrol the sanctuary's pond for "
                "pests."],
          tasks=[{"observe": "crittersandcompanions:dragonfly", "ticks": 20, "title": "Find a dragonfly"},
                 item("crittersandcompanions:iron_dragonfly_armor", crafted=True),
                 {"tame": "crittersandcompanions:dragonfly", "title": "Tame a dragonfly"}],
          rewards=[reward_item("crittersandcompanions:dragonfly_wing", 4), skill("taming", 220)]),
]

ACT2 = [
    quest("fairy_meadow", "Lights in the Meadow", icon="fays_fairies:fairy_bottle", after=["butterfly_house"],
          text=["Fairies caught by a greedy collector are wilting in jars in his shed. Free them, and catch a blue, a "
                "pink and a gold fairy of your own to release into the sanctuary garden."],
          tasks=[enc(["Take your jars and go. I never wanted fairies. I wanted light."],
                     entity="minecraft:villager", name="Greedy Collector", title="Face the collector in his shed"),
                 item("fays_fairies:fairy_bottle", 3, title="Recover the wilting fairies' bottles"),
                 {"observe": "fays_fairies:blue_fairy", "ticks": 20, "title": "Find a blue fairy to catch"},
                 {"observe": "fays_fairies:pink_fairy", "ticks": 20, "title": "Find a pink fairy to catch"},
                 {"observe": "fays_fairies:gold_fairy", "ticks": 20, "title": "Find a gold fairy to catch"}],
          rewards=[reward_item("fays_fairies:fairy_bottle"), skill("taming", 250)]),

    quest("monkey_business", "Monkey Business", icon="alexsmobs:banana", after=["pet_enchanting"],
          text=["A capuchin monkey, a raccoon and a crow have been stealing from the market. Catch them, tame them "
                "and turn the thieves into the sanctuary's most popular residents."],
          tasks=[enc(["*A flash of fur, and a stall is bare.*"], entity="alexsmobs:capuchin_monkey", name="Market Thief",
                     title="Spot the thief at the market"),
                 {"tame": "alexsmobs:capuchin_monkey", "title": "Tame the capuchin that robs the stalls"},
                 {"tame": "alexsmobs:raccoon", "title": "Tame the raccoon that raids the bins"},
                 {"tame": "alexsmobs:crow", "title": "Tame the crow that steals shiny things"}],
          rewards=[reward_item("alexsmobs:banana", 16), skill("taming", 270)]),

    quest("falconry", "The Falconer's Glove", icon="alexsmobs:falconry_hood", after=["monkey_business"],
          text=["The sanctuary has pests, and a falcon is the clean answer. Tame a bald eagle, hood it and fly it from "
                "a falconry glove."],
          tasks=[{"tame": "alexsmobs:bald_eagle", "title": "Tame a bald eagle"},
                 item("alexsmobs:falconry_glove", crafted=True, title="Make a falconry glove to fly it from"),
                 item("alexsmobs:falconry_hood", crafted=True, title="Make a hood to calm it")],
          rewards=[reward_item("alexsmobs:falconry_hood"), skill("taming", 300)]),

    quest("elephant_caravan", "The Elephant Caravan", icon="naturalist:elephant_spawn_egg", after=["monkey_business"],
          text=["An old trader's elephant is too old to work. Escort the trader's elephant from the savanna to the "
                "sanctuary, where it can retire, at its slow pace."],
          tasks=[{"structure": "ctov:large/village_savanna", "title": "Find the old trader in the savanna village"},
                 enc(["She is slow now. Give her time, and she will walk to rest."], then="escort",
                     entity="alexsmobs:elephant", name="Retiring Elephant", to={"place": "reece"},
                     title="Lead the old elephant to the sanctuary")],
          rewards=[reward_item("minecraft:emerald", 8), reward_item("minecraft:wheat", 32), skill("taming", 330)]),

    quest("horse_roundup", "Round Them Up", icon="artifacts:cowboy_hat", after=["lame_horse"],
          signature="artifacts:cowboy_hat",
          text=["Lightning spooked the sanctuary's horses and they scattered across the plain. Ride out and lead every "
                "one back to the horse pen. The old wrangler gives you his hat."],
          tasks=[enc(["*A frightened whinny across the plain.*"], then="escort", entity="minecraft:horse",
                     name="Scattered Horse", to={"structure": "mvs:horse_pen", "label": "the horse pen"},
                     title="Lead the first scattered horse back to the pen"),
                 enc(["*Another whinny, further off.*"], then="escort", entity="minecraft:horse",
                     name="Scattered Horse", to={"structure": "mvs:horse_pen", "label": "the horse pen"},
                     title="Lead the second scattered horse back"),
                 enc(["*The last horse, shaking, hides in the trees.*"], then="escort", entity="minecraft:horse",
                     name="Scattered Horse", to={"structure": "mvs:horse_pen", "label": "the horse pen"},
                     title="Lead the last scattered horse back")],
          rewards=[reward_item("artifacts:cowboy_hat"), skill("taming", 300)]),

    quest("horse_gear", "Barding", icon="ultimate_unicorn_mod:iron_horse_armor", after=["horse_roundup"],
          text=["The sanctuary's horses were spooked, and armour will help. Make proper barding: a horse helm and "
                "armour, and test a foal's bloodline with the DNA tester."],
          tasks=[item("ultimate_unicorn_mod:leather_horse_armor", crafted=True, title="Stitch padded leather barding"),
                 item("ultimate_unicorn_mod:iron_horse_armor", crafted=True, title="Forge horse armour"),
                 item("ultimate_unicorn_mod:dna_tester", crafted=True, title="Build a DNA tester for the foals")],
          rewards=[reward_item("ultimate_unicorn_mod:diamond_horse_armor"), skill("taming", 320)]),

    quest("unicorn_tracks", "Silver Hoofprints", icon="ultimate_unicorn_mod:unicorn_spawn_egg", after=["horse_gear"],
          text=["A shepherd swears she saw a white horse with a horn at dawn. Follow the tracks, gain the unicorn's "
                "trust and bring it to the sanctuary."],
          tasks=[{"observe": "ultimate_unicorn_mod:unicorn", "ticks": 40, "title": "Follow the silver tracks to the unicorn"},
                 {"tame": "ultimate_unicorn_mod:unicorn", "title": "Win the unicorn's trust"}],
          rewards=[reward_item("ultimate_unicorn_mod:golden_horse_armor"), skill("taming", 400)]),
]

ACT3 = [
    quest("familiar_bond", "A Bond of Spirit", icon="bookoffamiliars:familiar_book", after=["fairy_meadow", "main_story:act3_start"],
          text=["A visiting hedge witch gives Fern a Book of Familiars. Read it and bond a familiar of your own, a "
                "companion bound by more than food."],
          tasks=[item("bookoffamiliars:familiar_book", title="Take the hedge witch's Book of Familiars"),
                 {"cast": "any", "count": 3, "title": "Read the book's bonding words aloud"},
                 {"tame": "minecraft:cat", "title": "Bond a familiar of your own"}],
          rewards=[reward_item("bookoffamiliars:familiar_book"), skill("taming", 450)]),

    quest("pegasus", "Wings Over the Paddock", icon="ultimate_unicorn_mod:pegasus_spawn_egg", after=["unicorn_tracks"],
          text=["Pegasus feathers keep drifting down onto the sanctuary. Find the winged horse in the mountains, "
                "tame it and fly it home."],
          tasks=[item("minecraft:feather", title="Pick up a feather drifting over the sanctuary"),
                 {"biome": "minecraft:jagged_peaks", "title": "Climb into the mountains where the feathers fall from"},
                 {"tame": "ultimate_unicorn_mod:pegasus", "title": "Win the winged horse's trust"},
                 {"place": "reece", "title": "Fly it home to the sanctuary"}],
          rewards=[reward_item("minecraft:golden_carrot", 16), skill("taming", 480)]),

    quest("hippocamp", "Horse of the Sea", icon="ultimate_unicorn_mod:hippocamp_spawn_egg", after=["pegasus"],
          text=["Fishermen speak of a horse with a fish's tail playing in their wake. Sail out past the boats at "
                "sea, find the hippocamp and ride it."],
          tasks=[{"structure": "#ships_at_sea", "title": "Sail out past the boats at sea"},
                 {"tame": "ultimate_unicorn_mod:hippocamp", "title": "Win the hippocamp's trust and ride it"}],
          rewards=[reward_item("ultimate_unicorn_mod:leather_horse_armor", name="Hippocamp Saddle Blanket", lore=["Dyed sea-blue."]),
                   skill("taming", 500)]),

    quest("nightmare", "The Nightmare", icon="ultimate_unicorn_mod:nightmare_spawn_egg", after=["pegasus", "main_story:act3_start"],
          text=["In the Nether, piglins have chained a burning nightmare horse in their camp. Free it and calm it "
                "until it lets you ride."],
          tasks=[{"structure": "nova_structures:piglin_camp", "title": "Find the camp where the nightmare is chained"},
                 {"tame": "ultimate_unicorn_mod:nightmare", "title": "Free and calm the burning nightmare"}],
          rewards=[reward_item("minecraft:netherite_scrap", 2), skill("taming", 520)]),

    quest("stolen_pet", "Wherever You Are", icon="domesticationinnovation:wayward_lantern", after=["pet_enchanting"],
          text=["A child's dog was stolen by a passing illager band. Make a wayward lantern from the dog's deed of "
                "ownership and follow its glow across the land to bring the dog home."],
          tasks=[item("domesticationinnovation:deed_of_ownership", title="Take the dog's deed of ownership from the child"),
                 item("domesticationinnovation:wayward_lantern", crafted=True, title="Make a wayward lantern from the deed"),
                 {"structure": "#illager_hideouts", "title": "Follow the lantern's glow to the illagers' hideout"},
                 enc(["*A dog barks, tied beside a tent.*"], then="escort", entity="minecraft:wolf", name="The Stolen Dog",
                     to={"place": "reece"}, title="Bring the dog home")],
          rewards=[reward_item("domesticationinnovation:deed_of_ownership"), skill("taming", 450)]),

    quest("poachers", "Poachers at the Gate", icon="minecraft:iron_bars", after=["stolen_pet", "unicorn_tracks"],
          text=["Word of a unicorn has reached the poachers' camp. They come for it at night. Defend the sanctuary "
                "with your enchanted pets, then follow them back to their campsite and free the caged animals."],
          tasks=[{"timed": {"seconds": 180, "goal": {"hold": {"radius": 20}},
                            "waves": [{"entity": "minecraft:pillager", "count": 2, "every": 40}],
                            "lines": ["Poachers at the gate! Protect the unicorn!"], "start": "Defend the sanctuary"},
                  "title": "Defend the sanctuary through the poachers' night raid"},
                 {"structure": "dungeons_arise:illager_campsite", "title": "Follow the poachers back to their campsite"},
                 search("dungeons_arise:illager_campsite", 1, "the Cage Key", "A key on the poachers' ring.",
                        texture="minecraft:block/tripwire_hook", title="Take the key and free the caged animals")],
          rewards=[reward_item("minecraft:enchanted_book", name="Herding", enchant={"minecraft:unbreaking": 3}), skill("taming", 550)]),
]

ACT4 = [
    quest("the_full_herd", "The Full Herd", icon="ultimate_unicorn_mod:diamond_horse_armor", after=["hippocamp", "nightmare", "main_story:act4_start"],
          text=["Complete the sanctuary's magical herd. Add a kirin, a destrier and a reindeer to the unicorn, "
                "pegasus, hippocamp and nightmare."],
          tasks=[{"tame": "ultimate_unicorn_mod:kirin", "title": "Win a kirin's trust"},
                 {"tame": "ultimate_unicorn_mod:destrier", "title": "Win a destrier's trust"},
                 {"tame": "ultimate_unicorn_mod:reindeer", "title": "Win a reindeer's trust"}],
          rewards=[reward_item("ultimate_unicorn_mod:diamond_horse_armor"), skill("taming", 700)]),

    quest("end_ready_pets", "Pets for the Void", icon="domesticationinnovation:collar_tag", after=["poachers", "main_story:act4_start"],
          text=["Your companions want to follow you to the End. Enchant their collars so they come back safe."],
          tasks=[item("domesticationinnovation:collar_tag", crafted=True, title="Make a collar tag for the journey"),
                 item("minecraft:enchanted_book", 3, title="Gather collar enchantments to keep pets safe in the void")],
          rewards=[reward_item("sophisticatedbackpacks:magnet_upgrade"), reward_item("minecraft:chorus_fruit", 16), skill("taming", 720)]),

    quest("pet_show", "Best in Show", icon="domesticationinnovation:pet_bed_red", after=["end_ready_pets", "falconry"],
          text=["The sanctuary hosts a pet show for every village. Enter a companion judged on its collar and bed, "
                "and beat the shepherds' champion sheepdog."],
          tasks=[{"structure": "#villages", "title": "Take your companion to the village pet show"},
                 {"build": {"blocks": {"domesticationinnovation:pet_bed_red": 1}, "radius": 10}, "title": "Set up your companion's bed for the judges"},
                 enc(["Fine collar. Fine bed. Almost as good as the shepherds' champion."], entity="minecraft:villager", name="Show Judge",
                     title="Have the judge rank your companion")],
          rewards=[reward_item("minecraft:red_wool", 2), reward_item("crittersandcompanions:acorn_hat"), skill("taming", 740)]),

    quest("butterfly_atlas", "The Complete Atlas", icon="butterflies:bottled_butterfly_ice", after=["butterfly_house"],
          text=["Finish the butterfly collection with the rarest wings: the ice butterfly from frozen peaks, the lava "
                "butterfly from the Nether and the obsidian one from the darkest places."],
          tasks=[item("butterflies:bottled_butterfly_ice", title="Catch an ice butterfly in the frozen peaks"),
                 item("butterflies:bottled_butterfly_lava", title="Catch a lava butterfly in the Nether"),
                 item("butterflies:bottled_butterfly_obsidian", title="Catch an obsidian butterfly in the darkest places")],
          rewards=[reward_item("alexscaves:gelatin_pink", 4), skill("taming", 760)]),
]

ACT5 = [
    quest("after_the_storm", "After the Storm", icon="minecraft:lead", after=["the_full_herd", "main_story:act5_start"],
          text=["The great battles have driven animals out of their homes. Find the frightened ones wandering far "
                "from home and lead them to the sanctuary with your herd."],
          tasks=[enc(["*A terrified fawn, far from any wood.*"], then="escort", entity="naturalist:deer", name="Frightened Fawn",
                     to={"place": "reece"}, title="Lead the frightened fawn to the sanctuary"),
                 enc(["*A shivering fox kit, lost.*"], then="escort", entity="minecraft:fox", name="Lost Kit",
                     to={"place": "reece"}, title="Lead the lost kit to the sanctuary"),
                 enc(["*A singed wolf pup, limping.*"], then="escort", entity="minecraft:wolf", name="Singed Pup",
                     to={"place": "reece"}, title="Lead the singed pup to the sanctuary")],
          rewards=[reward_item("domesticationinnovation:magnet"), reward_item("minecraft:emerald", 8), skill("taming", 850)]),

    quest("taming_capstone", "Keeper of the Sanctuary", icon="minecraft:saddle",
          after=["after_the_storm", "pet_show", "butterfly_atlas", "familiar_bond"],
          text=["Fern names you Keeper and gives you the sanctuary's oldest gift, stitched for you."],
          tasks=[talk_char("fern", ["Keeper of the Sanctuary. The animals chose you.", "The oldest gift. Stitched for you."],
                           title="Be named Keeper of the Sanctuary by Fern")],
          rewards=[{"choice": [reward_item("minecraft:saddle", name='The Thistlewood Saddle', lore=['It never slips, whatever you ride.']), reward_item("domesticationinnovation:deflection_shield", name='Thistlewood Guard', lore=['The herd stood behind it.'], enchant={'minecraft:unbreaking': 3}, unbreakable=True), reward_item("ultimate_unicorn_mod:diamond_horse_armor", name='Thistlewood Barding', lore=['Fits anything with four legs and a heart.'], unbreakable=True)], "title": "Choose one"}, skill("taming", 1000)]),
]

chapter("skill_taming", "The Sanctuary", "Taming path", "minecraft:bone", "skills", 11, Q + ACT2 + ACT3 + ACT4 + ACT5)
