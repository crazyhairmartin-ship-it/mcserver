"""Chapter: small_favours, One Small Favour-style chains. First release: the Reece chain (Bram's loaf).
Plan: src/plans/quests/small_favours.json. Later chains are appended in later releases."""
from common import chapter, quest, talk_char, item, reward_item, skill, encounter
from common import enc, fight, boss, search, sample, talk_org, talk_villager, talk_char, item, reward_item, skill, encounter, giver_org  # noqa: F401

REECE = [
    quest("sf_out_of_flour", "Just a Loaf", icon="bakery:crusty_bread", after=["start:welcome"],
          text=["Bram the baker would gladly give you a loaf for the road, if he had any flour."],
          tasks=[talk_char("bram", ["A loaf for the road? There's no flour! It's a catastrophe!", "The windmill's stopped. Ask Hesk what's wrong? You're a hero!"])],
          rewards=[reward_item("bakery:bread_with_jam")]),

    quest("sf_torn_sails", "Torn Sails", icon="minecraft:white_wool", after=["sf_out_of_flour"],
          text=["Miller Hesk is standing under his windmill, looking at it."],
          tasks=[talk_char("hesk", ["Sorry. The storm tore the sails. I can't grind a thing.", "New sails need canvas. Canvas means Nell. Would you ask her? Sorry."])],
          rewards=[skill("farm", 30)]),

    quest("sf_broken_shuttle", "The Broken Shuttle", icon="farmersdelight:straw", after=["sf_torn_sails"],
          text=["Nell the weaver would weave canvas this minute, if her loom worked."],
          tasks=[talk_char("nell", ["Wipe your feet. Canvas? My shuttle snapped at seven past six.", "Olsen can carve a new one. And sixteen bundles of straw. Not fifteen."]),
                 item("farmersdelight:straw", 16, consume=True)],
          rewards=[skill("forage", 30)]),

    quest("sf_old_birch", "Only the Old Birch Will Do", icon="minecraft:birch_log", after=["sf_broken_shuttle"],
          text=["Olsen the carpenter will carve a shuttle. Eventually. He has standards."],
          tasks=[talk_char("olsen", ["A shuttle from ordinary birch? Absolutely not. It'll warp.", "Only old birch past the woods, felled with an axe. Eight logs, no stings."]),
                 item("minecraft:birch_log", 8, consume=True)],
          rewards=[reward_item("minecraft:honeycomb", 3), skill("forage", 50)]),

    quest("sf_unwinding", "Shuttle, Canvas, Sails", icon="farmersdelight:canvas", after=["sf_old_birch"],
          text=["Now everything can happen in the right order. Take the shuttle to Nell, and the canvas to Hesk."],
          tasks=[talk_char("nell", ["Exactly right, to the hair. Infuriating. Canvas, folded in eight.", "Take it to Hesk."],
                           title="Bring Nell the shuttle"),
                 talk_char("hesk", ["Canvas? Oh, thank you. Give me an hour.", "There. Sails on, mill turning. One bag of flour. Sorry if it isn't enough."],
                           title="Bring Hesk the canvas")],
          rewards=[skill("craft", 60)]),

    quest("sf_fox_and_flour", "The Fox and the Flour", icon="minecraft:sweet_berries", after=["sf_unwinding"],
          text=["On the road back to Reece, something small and orange snatches the flour bag and bolts."],
          tasks=[encounter(["*The fox drops the flour bag, eyeing your berries.*",
                            "*It takes the berries and trots off, very pleased with itself.*"],
                           entity="minecraft:fox", name="Flour Thief"),
                 item("minecraft:sweet_berries", 8, consume=True)],
          rewards=[skill("taming", 50)]),

    quest("sf_the_loaf", "The Loaf", icon="bakery:breadbox", shape="diamond", size=1.25,
          after=["sf_fox_and_flour"],
          text=["Bram has been waiting."],
          tasks=[talk_char("bram", ["Real flour! I'm crying. You're a legend! Three loaves and a breadbox.", "Next favour, you have my permission to run."])],
          rewards=[reward_item("bakery:crusty_bread", 3), reward_item("bakery:breadbox"), skill("cook", 80)]),
]

LAKE = [
    quest("sf_ferry_fee", "The Ferryman's Fee", icon="lilis_lucky_lures:fishing_net",
          after=["main_story:act1_start"],
          text=["Gil the ferryman will row anyone across to the island village, for a fee."],
          tasks=[talk_char("gil", ["I'll row you, for a good fishing net. Mine's more hole than net.", "Ada, next village along the lake, makes the best. Tell her Gil sent you."])],
          rewards=[skill("fish", 60)]),

    quest("sf_out_of_rope", "Out of Rope", icon="supplementaries:rope", after=["sf_ferry_fee"],
          text=["Ada can knot a net blindfolded. She's out of rope."],
          tasks=[talk_char("ada", ["Gil owes me for the last net. I'm out of rope, though.", "Rope means flax. Farmer Tamsin, round the lake. Mind the beans."],
                          title="Ask Ada about the net")],
          rewards=[skill("agility", 80)]),

    quest("sf_scarecrow_hat", "The Scarecrow's Hat", icon="minecraft:carved_pumpkin", after=["sf_out_of_rope"],
          text=["Farmer Tamsin won't spare a stalk until her scarecrow has its hat back."],
          tasks=[talk_char("tamsin", ["Flax? Not a stalk, not till he has his hat.", "A witch's cat took it into the swamp. Go and get it."]),
                 {"structure": "#witch_huts", "title": "Find the witch's hut"}],
          rewards=[skill("agility", 90)]),

    quest("sf_witch_bargain", "A Witch's Bargain", icon="herbalbrews:copper_tea_kettle", after=["sf_scarecrow_hat"],
          text=["The witch will give the hat back, for a pot of proper black tea brewed in a copper kettle. She's "
                "very particular about the kettle."],
          tasks=[item("herbalbrews:copper_tea_kettle", crafted=True), item("herbalbrews:black_tea", consume=True),
                 {"talk": "entity", "entity": "minecraft:witch",
                  "lines": ["Tea in a copper kettle. You know the old ways. Take the hat.", "Now go away before I put the kettle back on."],
                  "title": "Trade the tea to the witch"}],
          rewards=[reward_item("minecraft:carved_pumpkin", name="The Scarecrow's Hat",
                               lore=["A faded hat, slightly chewed by a cat."]), reward_item("minecraft:pumpkin_pie", 4), skill("magic", 100)]),

    quest("sf_hat_flax_rope", "Hat, Flax, Rope", icon="supplementaries:flax", after=["sf_witch_bargain"],
          text=["Return the hat to its scarecrow, and Tamsin gives you a sheaf of flax. Twist it into rope and "
                "take it to Ada, who knots the net while you wait."],
          tasks=[talk_char("tamsin", ["His hat! Chewed, but his. Look at him glow.", "Take a sheaf of flax. Tell Ada the rope's on me."],
                           title="Return the hat to Tamsin"),
                 item("supplementaries:flax", 8), item("supplementaries:rope", 4, crafted=True),
                 talk_char("ada", ["Good, strong rope. Sit. Don't touch the mesh.", "There, knotted while you waited. Tell Gil it's the last on credit."],
                           title="Take the rope to Ada")],
          rewards=[reward_item("lilis_lucky_lures:fishing_net"), skill("craft", 120)]),

    quest("sf_the_crossing", "The Crossing", icon="minecraft:oak_boat", shape="diamond", size=1.25,
          after=["sf_hat_flax_rope"],
          text=["Gil takes the net, keeps his word and rows you out to the island village. Halfway across, the "
                "drowned come up around the boat."],
          tasks=[item("lilis_lucky_lures:fishing_net", consume=True),
                 talk_char("gil", ["Ada's net! She's forgiven me, I think. Hop in, mind the wet bit.", "The lake's gone quiet. It's never quiet."]),
                 encounter(["*A drowned lurches up beside the boat.*"], then="kill",
                           entity="minecraft:drowned", name="Drowned", health=20),
                 encounter(["*Another drowned climbs out of the water.*"], then="kill",
                           entity="minecraft:drowned", name="Drowned", health=20),
                 {"structure": "#villages", "title": "Reach the island village"}],
          rewards=[reward_item("smallships:oak_drakkar"), skill("fish", 200)]),
]

NETHER = [
    quest("sf_permit", "Paperwork", icon="minecraft:paper", after=["main_story:act3_start"],
          text=["The piglin camp's gatekeeper won't let a stranger barter without a permit, stamped by the chief's clerk. "
                "The clerk is in the big tent. Probably."],
          tasks=[{"structure": "nova_structures:piglin_camp", "title": "Find the piglin camp's gate"},
                 {"talk": "entity", "entity": "minecraft:piglin",
                  "lines": ["No permit, no barter. See the clerk.", "Big tent. Probably."],
                  "title": "Ask the gatekeeper how to trade"}],
          rewards=[reward_item("minecraft:gold_nugget", 8), skill("agility", 100)]),

    quest("sf_dry_ink", "The Ink Has Dried", icon="minecraft:glow_ink_sac", after=["sf_permit"],
          text=["The clerk can't write a permit: his ink has dried in the heat. The chief's permits are always "
                "written in glow ink, from glow squid in the Overworld."],
          tasks=[item("minecraft:glow_ink_sac", 4, title="Bring glow ink from the Overworld's glow squid"),
                 {"talk": "entity", "entity": "minecraft:piglin",
                  "lines": ["Glow ink? Finally. The chief demands it.", "The stamp is cracked, though."],
                  "title": "Give the clerk the glow ink"}],
          rewards=[skill("fish", 100)]),

    quest("sf_cracked_stamp", "The Cracked Stamp", icon="minecraft:gold_block", after=["sf_dry_ink"],
          text=["The clerk's stamp is cracked. A brute at the camp's forge will cast a new one from a gold block, if "
                "you survive his arm-wrestling swings for a minute."],
          tasks=[item("minecraft:gold_block", consume=True, title="Bring a gold block for the new stamp"),
                 {"timed": {"seconds": 60, "goal": {"hold": {"radius": 6}},
                            "waves": [{"entity": "minecraft:piglin_brute", "count": 1, "every": 20}],
                            "lines": ["The brute wants a wrestle. Stand your ground."], "start": "Take the brute's challenge"},
                  "title": "Survive the brute's swings for a minute"}],
          rewards=[skill("defense", 120)]),

    quest("sf_sleeping_chief", "Signed by the Chief", icon="immersive_melodies:tiny_drum", after=["sf_cracked_stamp"],
          text=["Stamped, but not signed. The chief is asleep, and waking him badly is how outsiders get eaten. "
                "Piglins dance to a drum. Play one by his bed until he wakes in a good mood."],
          tasks=[item("immersive_melodies:tiny_drum", crafted=True, title="Make a drum to wake the chief gently"),
                 enc(["*The chief stirs, stamps a foot, and signs with a grunt.*"], entity="minecraft:piglin",
                     name="The Sleeping Chief", title="Wake the chief with a drum by his bed")],
          rewards=[reward_item("minecraft:gold_ingot", 8), skill("agility", 150)]),

    quest("sf_permit_granted", "Permit Granted", icon="minecraft:item_frame", after=["sf_sleeping_chief"],
          text=["Hand the signed, stamped permit to the gatekeeper. He reads it twice, upside down, and lets you in "
                "to trade."],
          tasks=[item("minecraft:paper", consume=True, title="Carry the signed, stamped permit to the gate"),
                 {"talk": "entity", "entity": "minecraft:piglin",
                  "lines": ["Signed. Stamped. Upside down is fine. Welcome."], "title": "Hand the permit to the gatekeeper"}],
          rewards=[reward_item("minecraft:item_frame"), reward_item("minecraft:gold_nugget", 16), skill("agility", 200)]),
]

chapter("small_favours", "Small Favours", "One small favour leads to another", "bakery:crusty_bread", "side", 0,
        REECE + LAKE + NETHER)
