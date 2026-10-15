"""Chapter: skill_agility, the Couriers' path: prologue and Act I (first release).
Plan: src/plans/quests/skill_agility.json. Postmistress Juniper Quill runs the post office in Reece; Ender Mail carriers
take the everyday post, the Couriers take what the endermen can't or won't."""
from common import chapter, quest, talk_char, talk_villager, item, reward_item, skill, giver_org, encounter
from common import enc, fight, boss, search, sample, talk_org, talk_villager, talk_char, item, reward_item, skill, encounter, giver_org  # noqa: F401

NO_SHORTCUTS = ["teleport", "mounts"]

Q = [
    quest("sign_the_roster", "Sign the Roster", icon="fotfmail:letter_signed",
          giver=giver_org("couriers", ["Runners wanted! Somebody has to carry the awkward jobs.", "Sign on with Postmistress Quill in Reece."], "I'll sign on"),
          text=["A cartographer has pinned a Couriers' notice: runners wanted. Sign on at the Reece post office and "
                "carry your first signed letter to a cartographer in another village."],
          tasks=[talk_char("juniper", ["New runner? Name, signature, go. We take what the carriers won't.", "Sign this letter. Take it to the next village's cartographer. Don't dawdle."]),
                 item("fotfmail:letter_signed", consume=True, title="Sign a letter for delivery"),
                 talk_villager("minecraft:cartographer", ["A letter from Quill? About time. You'll do, runner."],
                               title="Hand it to a cartographer in another village")],
          rewards=[reward_item("minecraft:bundle", name="Courier's Satchel"), reward_item("fotfmail:letter", 8),
                   skill("agility", 60)]),

    quest("first_timed_run", "Beat the Bell", icon="artifacts:running_shoes", after=["sign_the_roster"],
          signature="artifacts:running_shoes",
          text=["Juniper's runner has twisted an ankle, and the morning post must reach the next village before the "
                "noon bell. Make the run on the clock, and the runner will give you their shoes for good."],
          tasks=[item("fotfmail:letter_signed", title="Take the morning post"),
                 {"timed": {"seconds": 240, "goal": {"structure": "#villages", "label": "the next village", "away": 150},
                            "lines": ["The noon bell rings in a few minutes. Run!", "No short cuts, no mounts."],
                            "start": "Start the run", "no": NO_SHORTCUTS}, "title": "Reach the next village by noon"}],
          rewards=[reward_item("artifacts:running_shoes"), skill("agility", 100)]),

    quest("rooftop_basics", "Over, Not Around", icon="parcool:traceur_gloves", after=["sign_the_roster"],
          text=["Couriers don't take the street. Learn ParCool's vault, roll and wall-run on a rooftop line "
                "across Reece, and finish it under the time on the chalk board."],
          tasks=[{"place": "reece"},
                 {"timed": {"seconds": 45, "goal": {"stat": "minecraft:jump", "count": 25},
                            "lines": ["Up and over. Roofs, not roads.", "Keep moving."],
                            "start": "Start the rooftop line", "no": NO_SHORTCUTS},
                  "title": "Run the rooftop line"}],
          rewards=[reward_item("parcool:parcool_guide"), reward_item("parcool:traceur_gloves"),
                   skill("agility", 90)]),

    quest("carry_the_chest", "Don't Unpack It", icon="minecraft:chest", after=["sign_the_roster"],
          text=["A family is moving house, and their strongbox can't be emptied on the way. Pick up the whole chest "
                "with Carry On and walk it to the new cottage, then carry their sleeping cat across too."],
          tasks=[{"structure": "#villages", "title": "Find the family's village"},
                 {"checkmark": "I carried the chest to the new cottage"},
                 {"checkmark": "I carried the sleeping cat across"}],
          rewards=[reward_item("supplementaries:lunch_basket"), skill("agility", 80)]),

    quest("storm_cliff_parcel", "Under a Grey Sky", icon="artifacts:umbrella", after=["first_timed_run"],
          signature="artifacts:umbrella",
          text=["A courier stranded on a cliff path by a thunderstorm begs you to finish their run. Take the parcel "
                "down the wet cliff route to the cove below without falling. Their umbrella is the thanks."],
          tasks=[encounter(["Thank goodness! The path's like glass. Take the parcel down to the cove.", "Take my umbrella too."],
                           entity="minecraft:villager", name="Stranded Courier", where={"above_y": 62}),
                 {"checkmark": "I delivered the parcel to the cove"}],
          rewards=[reward_item("artifacts:umbrella"), skill("agility", 140)]),

    quest("post_office", "Stamps and Tape", icon="endermail:stamp", after=["first_timed_run"],
          text=["Juniper wants a real post office. Craft an Ender Mail package, stamps and a package controller, "
                "set up a locker at the Reece post office and send your first stamped package."],
          tasks=[item("endermail:package", crafted=True), item("endermail:stamp", crafted=True),
                 item("endermail:package_controller", crafted=True), {"place": "reece"},
                 {"build": {"blocks": {"endermail:locker": 1}, "radius": 12}, "title": "Set up a locker"},
                 {"checkmark": "I sent a stamped package"}],
          rewards=[reward_item("endermail:stamp", 8), skill("agility", 150)]),

    quest("waystone_route", "Marking the Route", icon="waystones:waystone", after=["post_office"],
          text=["Old couriers left waystones along the roads. Find and attune three wild waystones between Reece "
                "and the neighbouring villages, so later runs can start halfway."],
          tasks=[{"waystones": 3, "wild": True, "total": True, "title": "Attune three wild waystones"}],
          rewards=[reward_item("waystones:warp_scroll", 4), skill("agility", 140)]),

    quest("great_bridge_run", "Before the Light Goes", icon="minecraft:stone_bricks", after=["waystone_route"],
          text=["A parcel of medicine must cross a great ravine bridge to a village on the far side before dusk. "
                "Find the old stone bridge and make the crossing on the clock."],
          tasks=[{"timed": {"seconds": 180, "goal": {"structure": "#villages", "label": "the village across the bridge",
                                                     "away": 100},
                            "lines": ["The light is going. Run for the far side!"],
                            "start": "Cross the bridge", "no": NO_SHORTCUTS}, "title": "Reach the far village before dusk"}],
          rewards=[reward_item("minecraft:sugar", 16), reward_item("minecraft:golden_carrot", 8),
                   skill("agility", 180)]),

    quest("rooftop_route", "The Long Drop Line", icon="artifacts:bunny_hoppers", after=["rooftop_basics"],
          signature="artifacts:bunny_hoppers",
          text=["A large village's couriers race a rooftop route with drops that would break legs. Run the whole "
                "line under the record, and the record holder hands over their bouncy boots."],
          tasks=[{"structure": "#villages", "title": "Find the village's rooftop route"},
                 {"timed": {"seconds": 90, "goal": {"stat": "minecraft:jump", "count": 50},
                            "lines": ["The line runs the whole village. Gaps, drops, all of it.", "Beat the record."],
                            "start": "Run the line", "no": NO_SHORTCUTS + ["pearls"]},
                  "title": "Run the line under the record"}],
          rewards=[reward_item("artifacts:bunny_hoppers"), skill("agility", 220)]),

    quest("night_post", "The Night Post", icon="artifacts:panic_necklace", after=["great_bridge_run"],
          signature="artifacts:panic_necklace",
          text=["An urgent letter must go out after dark across open country. Monsters ambush the road, so take "
                "the hits and keep running. Stopping to fight loses the deadline."],
          tasks=[item("fotfmail:letter_signed", title="Take the urgent letter"),
                 {"timed": {"seconds": 300, "goal": {"structure": "#villages", "label": "the next village", "away": 200},
                            "waves": [{"entity": "minecraft:zombie", "count": 2, "every": 25},
                                      {"entity": "minecraft:skeleton", "count": 1, "every": 40}],
                            "lines": ["Night run. They'll come at you. Don't stop!"],
                            "start": "Start the night run", "no": NO_SHORTCUTS}, "title": "Run the night post"},
                 talk_char("juniper", ["You made it. Night runs are the worst. Everything bites.", "Take this. I wore it on mine."])],
          rewards=[reward_item("artifacts:panic_necklace"), skill("agility", 260)]),

    quest("tower_zipline", "Line from the Tower", icon="parcool:iron_zipline_hook", after=["waystone_route"],
          text=["The Couriers' lookout is an old cartographer tower. Climb it, and rig a zipline from its top to "
                "the road below so runners can drop letters down in seconds."],
          tasks=[{"structure": "mvs:cartographer_tower", "title": "Climb the cartographer tower"},
                 item("parcool:iron_zipline_hook", 2),
                 {"build": {"blocks": {"parcool:iron_zipline_hook": 2}, "radius": 12},
                  "title": "Rig a zipline"}],
          rewards=[reward_item("parcool:iron_zipline_hook", 2), skill("agility", 160)]),

    quest("first_grapple", "Hook and Swing", icon="grapplemod:grapplinghook", after=["tower_zipline"],
          text=["Craft a grappling hook and swing across a canyon course the Couriers marked with flags, faster "
                "than the long way round on foot."],
          tasks=[item("grapplemod:grapplinghook", crafted=True),
                 {"timed": {"seconds": 60, "goal": {"stat": "minecraft:sprint_one_cm", "count": 20000},
                            "lines": ["Flags along the canyon. Swing, don't walk."],
                            "start": "Start the course", "no": ["teleport", "mounts"]},
                  "title": "Swing the canyon course"}],
          rewards=[reward_item("minecraft:string", 16), reward_item("supplementaries:rope", 16), skill("agility", 200)]),

    quest("ledge_rescue", "Stuck on the Ledge", icon="minecraft:ladder",
          after=["first_grapple"],
          text=["A young courier who took a shortcut is stuck on a cliff ledge with a broken leg. Grapple down, "
                "pick them up with Carry On and bring them and their satchel safely back."],
          tasks=[encounter(["Down here! I can't move my leg. Please don't tell Juniper.", "My satchel has sealed letters. Can you finish them?"],
                           entity="minecraft:villager", name="Injured Courier", where={"above_y": 70},
                           then="escort", to={"structure": "#villages", "label": "the nearest village"},
                           thanks=["We made it. You're better at this than me.",
                                   "Take the satchel. The letters inside are yours to finish now."])],
          rewards=[reward_item("fotfmail:letter", 4), reward_item("minecraft:golden_apple"), skill("agility", 220)]),

    quest("first_ferry", "Across the Bay", icon="smallships:oak_cog", after=["post_office"],
          text=["A beach village's post piles up across the water. Build a rowboat, then a cog, and ferry three "
                "crates of mail over the bay."],
          tasks=[item("smallships:oak_rowboat", crafted=True), item("smallships:oak_cog", crafted=True),
                 item("endermail:package", 3, consume=True, title="Load three crates of mail"),
                 {"structure": "ctov:medium/village_beach", "title": "Reach the beach village"}],
          rewards=[reward_item("minecraft:white_wool", 4), reward_item("minecraft:string", 8),
                   skill("agility", 240)]),
]

ACT2 = [
    quest("water_run", "No Boats Allowed", icon="artifacts:aqua_dashers", after=["first_ferry"],
          signature="artifacts:aqua_dashers",
          text=["A bet in the beach village: cross the lake to the far pier without a boat, before the hourglass runs "
                "out. Sprint, swim and leap. The bet's winner keeps the strange shoes that run on water."],
          tasks=[{"structure": "ctov:medium/village_beach", "title": "Take up the bet in the beach village"},
                 {"timed": {"seconds": 240, "goal": {"structure": "#fishing_huts", "label": "the far pier", "away": 80},
                            "lines": ["No boats. The hourglass is running."], "start": "Start the crossing",
                            "no": ["teleport", "mounts"]}, "title": "Reach the far pier without a boat"}],
          rewards=[reward_item("artifacts:aqua_dashers"), skill("agility", 250)]),

    quest("mountain_post", "Powder Road", icon="artifacts:snowshoes", after=["night_post"],
          signature="artifacts:snowshoes",
          text=["An alpine village is snowed in and waiting for winter supplies. Carry the parcel over the powder "
                "snow to the mountain outpost before the storm closes the pass. The outpost's courier gives you "
                "their snowshoes."],
          tasks=[item("endermail:package", consume=True, title="Take the winter supplies parcel"),
                 {"timed": {"seconds": 600, "goal": {"structure": "ctov:medium/village_mountain_alpine",
                                                       "label": "the mountain outpost", "away": 150},
                            "lines": ["The storm is closing the pass. Go!"], "start": "Start the climb",
                            "no": ["teleport", "mounts"]}, "title": "Reach the snowed-in village before the pass closes"}],
          rewards=[reward_item("artifacts:snowshoes"), skill("agility", 300)]),

    quest("monastery_climb", "Speed Climb", icon="grapplemod:grapplinghook", after=["ledge_rescue"],
          text=["A rival courier claims the peak below the monastery in record time. Get a grappling hook, "
                "wall-run boots, and beat their time."],
          tasks=[item("grapplemod:grapplinghook", title="Take your grappling hook for the climb"),
                 item("parcool:traceur_boots", crafted=True, title="Get wall-run boots"),
                 {"timed": {"seconds": 420, "goal": {"structure": "mowziesmobs:monastery", "label": "the monastery", "away": 150},
                            "lines": ["The rival's record stands. Beat it."], "start": "Start the race",
                            "no": ["teleport", "mounts"]}, "title": "Race the rival courier up the peak"}],
          rewards=[reward_item("supplementaries:rope", 16), reward_item("minecraft:string", 16), skill("agility", 300)]),

    quest("brigg_charter", "The Lighthouse Run", icon="smallships:oak_brigg", after=["first_ferry"],
          text=["The lighthouse keeper's oil comes by sea. Build a brigg with cargo room and take a full load of lamp "
                "oil and letters up the coast."],
          tasks=[item("smallships:oak_brigg", crafted=True, title="Build a brigg with room for cargo"),
                 item("minecraft:lantern", 8, consume=True, title="Load lamp lanterns for the keeper"),
                 item("fotfmail:letter", 4, consume=True, title="Load the keeper's letters"),
                 {"structure": "#lighthouses", "title": "Sail the cargo up the coast to the lighthouse"}],
          rewards=[reward_item("minecraft:spyglass"), reward_item("smallships:cannon"), skill("agility", 280)]),

    quest("ships_at_sea", "Mail for the Fleet", icon="fotfmail:letter", after=["brigg_charter"],
          text=["An outcast fisherman lives on his little boat far out at sea, and his family ashore hasn't heard from "
                "him in months. Sail out, find a boat at sea and hand him their letters."],
          tasks=[item("fotfmail:letter", 3, consume=True, title="Take the family's letters"),
                 {"structure": "#ships_at_sea", "title": "Find a boat out at sea"},
                 enc(["Letters! From home! I'll write back at once.", "Take my reply. Tell them I'm well."],
                     entity="minecraft:villager", name="Outcast Fisherman", title="Hand the fisherman his letters")],
          rewards=[reward_item("minecraft:map"), reward_item("fotfmail:letter", 2), skill("agility", 300)]),

    quest("first_flight", "Bamboo Wings", icon="immersive_aircraft:bamboo_hopper", after=["monastery_climb"],
          text=["A firewatch tower deep in the woods needs post nobody can walk to in a day. Build an Immersive "
                "Aircraft bamboo hopper and fly the first airmail to its keeper."],
          tasks=[item("immersive_aircraft:bamboo_hopper", crafted=True, title="Build a bamboo hopper"),
                 item("fotfmail:letter", consume=True, title="Load the airmail for the keeper"),
                 {"timed": {"seconds": 600, "goal": {"structure": "#firewatch_towers", "label": "the firewatch tower", "away": 150},
                            "lines": ["Fly the first airmail. The keeper's waiting."], "start": "Take off",
                            "no": ["teleport"]}, "title": "Fly the post to the firewatch tower"}],
          rewards=[reward_item("immersive_aircraft:propeller"), reward_item("minecraft:coal", 16), skill("agility", 320)]),

    quest("runaway_float", "The Float That Got Away", icon="artifacts:helium_flamingo", after=["first_flight"],
          signature="artifacts:helium_flamingo",
          text=["A child's pool float slipped its string and drifted up to an island floating in the sky. Get up there "
                "by hook, plane or pillar and bring it back. The child lets you keep it."],
          tasks=[enc(["My flamingo! It floated away! It's up there!"], entity="minecraft:villager", name="Crying Child",
                     title="Meet the child who lost their float"),
                 {"structure": "#moog_sky_islands", "title": "Get up to the floating islands by any means"},
                 search("mss:small_oak_house", 1, "the Child's Float", "A pink float, snagged on a rooftop.",
                        texture="minecraft:item/pink_dye", title="Search the islands for the child's float")],
          rewards=[reward_item("artifacts:helium_flamingo"), skill("agility", 380)]),
]

ACT3 = [
    quest("catch_a_cloud", "Bottle a Cloud", icon="artifacts:cloud_in_a_bottle", after=["runaway_float"],
          signature="artifacts:cloud_in_a_bottle",
          text=["The sky villagers say the best clouds gather above their highest roof. Climb the sky village to its "
                "very top and bottle one, the old way."],
          tasks=[{"structure": "skyvillages:skyvillage", "title": "Climb to the sky village"},
                 item("minecraft:glass_bottle", title="Bring an empty bottle for the cloud"),
                 search("skyvillages:skyvillage", 1, "a Bottled Cloud", "A cloud, caught in glass on the highest roof.",
                        texture="minecraft:item/glass_bottle", title="Climb to the highest roof and bottle a cloud")],
          rewards=[reward_item("artifacts:cloud_in_a_bottle"), skill("agility", 420)]),

    quest("sky_post_office", "Post Office in the Clouds", icon="endermail:locker", after=["catch_a_cloud"],
          text=["The sky village has never had a post office. Set up an Ender Mail locker there, then carry the first "
                "ground-mail up and the first sky-mail down."],
          tasks=[{"structure": "skyvillages:skyvillage", "title": "Go up to the sky village"},
                 {"build": {"blocks": {"endermail:locker": 1}, "radius": 12}, "title": "Set up a locker for the sky village's first post office"},
                 item("endermail:package", consume=True, title="Carry the first ground-mail up"),
                 enc(["A parcel! For us! And here is our first letter down."], entity="minecraft:villager", name="Sky Postmaster",
                     title="Hand over the mail and take the first sky-mail")],
          rewards=[reward_item("endermail:package_controller"), skill("agility", 440)]),

    quest("drakkar_race", "Oars Against the Wind", icon="smallships:oak_drakkar", after=["ships_at_sea", "main_story:act3_start"],
          text=["A rival harbour's couriers say their drakkar is faster than anything the Couriers sail. Build your "
                "own drakkar and beat them along the coast course, buoy to buoy."],
          tasks=[item("smallships:oak_drakkar", crafted=True, title="Build a drakkar to race"),
                 enc(["Our drakkar's faster! Race us down the coast!"], entity="minecraft:villager", name="Rival Courier",
                     title="Take up the rival harbour's challenge"),
                 {"timed": {"seconds": 420, "goal": {"structure": "#villages", "label": "the course's end", "away": 200},
                            "lines": ["Buoy to buoy. Beat their drakkar!"], "start": "Start the race", "no": ["teleport"]},
                  "title": "Sail the coast course ahead of the rival drakkar"}],
          rewards=[reward_item("minecraft:white_wool", 16), reward_item("minecraft:white_banner", name="The Rivals' Banner"),
                   skill("agility", 440)]),

    quest("galley_convoy", "Convoy to the Sea Town", icon="smallships:oak_galley", after=["drakkar_race"],
          text=["A merchant convoy must reach a beach village across the gulf through waters a pillager ship and a "
                "pirate wreck patrol. Captain a galley and keep the cargo cog afloat all the way."],
          tasks=[item("smallships:oak_galley", crafted=True, title="Build a galley to captain the convoy"),
                 item("smallships:oak_cog", crafted=True, title="Build the cargo cog to protect"),
                 fight("minecraft:pillager", 6, "towns_and_towers:pillager_outpost_ocean", "Convoy Raiders", "Beat off the pillager ship as the convoy passes"),
                 {"structure": "ctov:large/village_beach", "title": "Bring the convoy into the beach village"}],
          rewards=[reward_item("smallships:cannon_ball", 8), reward_item("minecraft:emerald", 12), skill("agility", 460)]),

    quest("airmail_day", "Three Villages, One Day", icon="immersive_aircraft:biplane", after=["first_flight"],
          text=["Build a biplane and run the airmail: three villages, three parcels, one day from sunrise to "
                "sunset."],
          tasks=[item("immersive_aircraft:biplane", crafted=True, title="Build a biplane for the airmail"),
                 item("fotfmail:letter", 3, consume=True, title="Load three parcels of airmail"),
                 {"timed": {"seconds": 1200, "goal": {"structure": "#villages", "label": "the third village", "away": 300},
                            "lines": ["Three villages before sunset. Fly!"], "start": "Take off", "no": ["teleport"]},
                  "title": "Fly the airmail to three villages before sunset"}],
          rewards=[reward_item("immersive_aircraft:enhanced_propeller"), skill("agility", 460)]),

    quest("wings_of_the_post", "Feathers Not Engines", icon="icarus:red_feathered_wings", after=["sky_post_office"],
          text=["Juniper's grandfather flew the post on homemade wings. Craft a pair of Icarus feathered wings and "
                "glide from the sky village back down to Reece without touching the ground."],
          tasks=[item("icarus:red_feathered_wings", crafted=True, title="Craft a pair of feathered wings"),
                 {"structure": "skyvillages:skyvillage", "title": "Climb back up to the sky village"},
                 {"timed": {"seconds": 900, "goal": {"place": "reece"},
                            "lines": ["Glide home. Don't touch the ground."], "start": "Launch", "no": ["teleport"]},
                  "title": "Glide from the sky village down to Reece"}],
          rewards=[reward_item("icarus:red_feathered_wings", name="The Couriers' Wings", lore=["Juniper's grandfather's colours."]),
                   skill("agility", 480)]),
]

ACT4 = [
    quest("airship_logbook", "The Lost Couriers' Log", icon="immersive_aircraft:gyroscope", after=["wings_of_the_post", "main_story:act4_start"],
          text=["A courier crew vanished chasing a great airship through the clouds. Reach one of the airships and "
                "bring back their logbook from among the dangers aboard."],
          tasks=[{"structure": "#airships", "title": "Reach one of the airships"},
                 fight("minecraft:pillager", 6, "#airships", "Airship Guards", "Fight past the airship's guards"),
                 search("#airships", 1, "the Couriers' Logbook", "The couriers' logbook, wedged behind a locker.",
                        texture="minecraft:item/written_book", title="Find the lost couriers' logbook aboard")],
          rewards=[reward_item("immersive_aircraft:gyroscope"), skill("agility", 700)]),

    quest("cargo_airship", "Freight by Air", icon="immersive_aircraft:cargo_airship", after=["airmail_day"],
          text=["The far villages want bulk goods, not letters. Build a cargo airship and fly a full hold of building "
                "supplies to a village beyond the mountains."],
          tasks=[item("immersive_aircraft:cargo_airship", crafted=True, title="Build a cargo airship"),
                 item("minecraft:stone_bricks", 64, consume=True, title="Load building stone"),
                 item("minecraft:oak_planks", 64, consume=True, title="Load building timber"),
                 {"timed": {"seconds": 1200, "goal": {"structure": "#villages", "label": "the village beyond the mountains", "away": 400},
                            "lines": ["A full hold. Fly it over the mountains."], "start": "Take off", "no": ["teleport"]},
                  "title": "Fly the supplies to a village beyond the mountains"}],
          rewards=[reward_item("immersive_aircraft:boiler"), skill("agility", 720)]),

    quest("sharestone_network", "Every Village a Stop", icon="waystones:sharestone", after=["waystone_route", "cargo_airship"],
          text=["Make the Couriers' network permanent. Craft sharestones and warp plates and place them in the "
                "villages the Couriers serve, all linked to the Reece post office."],
          tasks=[item("waystones:sharestone", 2, crafted=True, title="Craft sharestones for the network"),
                 item("waystones:warp_plate", 2, crafted=True, title="Craft warp plates for the network"),
                 {"structure": "#villages", "title": "Take them out to a village on the route"},
                 {"build": {"blocks": {"waystones:sharestone": 1, "waystones:warp_plate": 1}, "radius": 10},
                  "title": "Place a sharestone and a warp plate in the village"}],
          rewards=[reward_item("waystones:warp_stone", 2), skill("agility", 740)]),

    quest("wings_and_armour", "Elytra on the Route", icon="minecraft:elytra", after=["main_story:act4_finale"],
          text=["Elytra from the End change everything. Wear them in the elytra slot alongside your chestplate and "
                "fly the full courier circuit without landing."],
          tasks=[item("minecraft:elytra", title="Wear the elytra from the End"),
                 {"timed": {"seconds": 1200, "goal": {"structure": "#villages", "label": "the circuit's last village", "away": 800},
                            "lines": ["The full circuit, no landing."], "start": "Start the circuit", "no": ["teleport", "mounts"]},
                  "title": "Fly the courier circuit without landing"}],
          rewards=[reward_item("minecraft:firework_rocket", 32), skill("agility", 760)]),
]

ACT5 = [
    quest("grand_relay", "The Grand Relay", icon="minecraft:white_banner", after=["galley_convoy", "airship_logbook", "wings_and_armour", "main_story:act5_start"],
          text=["The Couriers' great race: one parcel around the whole network in a single day, on foot over "
                "rooftops, by ship across the bay and by air to the sky village, against the best runners from every "
                "village."],
          tasks=[item("endermail:package", consume=True, title="Take the relay parcel"),
                 {"timed": {"seconds": 900, "goal": {"structure": "#villages", "label": "the first leg's village", "away": 200},
                            "lines": ["The grand relay. First leg on foot!"], "start": "Start the relay", "no": ["teleport", "mounts"]},
                  "title": "Run the first leg over the rooftops"},
                 {"timed": {"seconds": 900, "goal": {"structure": "ctov:large/village_beach", "label": "the bay's far village", "away": 200},
                            "lines": ["Second leg, by ship!"], "start": "Sail the second leg", "no": ["teleport"]},
                  "title": "Sail the second leg across the bay"},
                 {"timed": {"seconds": 900, "goal": {"structure": "skyvillages:skyvillage", "label": "the sky village", "away": 200},
                            "lines": ["Last leg, by air!"], "start": "Fly the last leg", "no": ["teleport"]},
                  "title": "Fly the last leg to the sky village"}],
          rewards=[reward_item("minecraft:white_banner", name="The Relay Pennant"), skill("agility", 900)]),

    quest("courier_capstone", "Seven Leagues", icon="minecraft:netherite_boots", after=["grand_relay", "sharestone_network"],
          text=["Juniper hands you the post office keys and the Couriers' oldest treasure, reforged for you."],
          tasks=[talk_char("juniper", ["The post office keys. And the oldest treasure.", "Run well. Stamp everything."],
                           title="Take the post office keys and the oldest treasure from Juniper")],
          rewards=[reward_item("minecraft:netherite_boots", name="Juniper's Seven-League Boots", lore=["The Couriers' oldest treasure."],
                               enchant={"minecraft:feather_falling": 4, "minecraft:depth_strider": 3, "minecraft:soul_speed": 3,
                                        "minecraft:unbreaking": 3, "minecraft:mending": 1}), skill("agility", 1000)]),
]

chapter("skill_agility", "The Couriers", "Agility path", "minecraft:leather_boots", "skills", 9, Q + ACT2 + ACT3 + ACT4 + ACT5)
