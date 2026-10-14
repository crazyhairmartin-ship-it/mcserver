"""Chapter: small_favours, One Small Favour-style chains. First release: the Reece chain (Bram's loaf).
Plan: src/plans/quests/small_favours.json. Later chains are appended in later releases."""
from common import chapter, quest, talk_char, item, reward_item, skill, encounter

REECE = [
    quest("sf_out_of_flour", "Just a Loaf", icon="bakery:crusty_bread", after=["start:welcome"],
          text=["Bram the baker would gladly give you a loaf for the road, if he had any flour."],
          tasks=[talk_char("bram", ["A loaf? I'd love to. I'd love to. But there's no flour.",
                                    "The windmill's stopped turning. Would you go and ask Hesk what's wrong?",
                                    "It's just one small favour."])],
          rewards=[reward_item("bakery:bread_with_jam")]),

    quest("sf_torn_sails", "Torn Sails", icon="minecraft:white_wool", after=["sf_out_of_flour"],
          text=["Miller Hesk is standing under his windmill, looking at it."],
          tasks=[talk_char("hesk", ["Storm tore the sails clean through. Can't grind a thing.",
                                    "New sails need canvas. Canvas means Nell. Ask Nell, would you?",
                                    "One small favour, that's all."])],
          rewards=[skill("farm", 30)]),

    quest("sf_broken_shuttle", "The Broken Shuttle", icon="farmersdelight:straw", after=["sf_torn_sails"],
          text=["Nell the weaver would weave canvas this minute, if her loom worked."],
          tasks=[talk_char("nell", ["Canvas? Of course. Except my shuttle snapped this morning.",
                                    "Olsen could carve me a new one. And bring me straw while you're at it, I'm out.",
                                    "Just a small favour."]),
                 item("farmersdelight:straw", 16, consume=True)],
          rewards=[skill("forage", 30)]),

    quest("sf_old_birch", "Only the Old Birch Will Do", icon="minecraft:birch_log", after=["sf_broken_shuttle"],
          text=["Olsen the carpenter will carve a shuttle. Eventually. He has standards."],
          tasks=[talk_char("olsen", ["A shuttle? From ordinary birch? Absolutely not.",
                                     "Only the old birches past the woods will do. The ones with the bees.",
                                     "Eight logs, no stings. It's a very small favour, really."]),
                 item("minecraft:birch_log", 8, consume=True)],
          rewards=[reward_item("minecraft:honeycomb", 3), skill("forage", 50)]),

    quest("sf_unwinding", "Shuttle, Canvas, Sails", icon="farmersdelight:canvas", after=["sf_old_birch"],
          text=["Now everything can happen in the right order. Take the shuttle to Nell, and the canvas to Hesk."],
          tasks=[talk_char("nell", ["My shuttle! Lovely work. He's insufferable, but lovely work.",
                                    "Here's your canvas. Off you go to Hesk."], title="Bring Nell the shuttle"),
                 talk_char("hesk", ["Canvas! She did it! Give me an hour.",
                                    "...There. Sails on, mill turning. One bag of flour, as promised."],
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
          tasks=[talk_char("bram", ["Flour! Real flour! You're a marvel.",
                                    "One crusty loaf, as promised. And a breadbox, since you went to all that trouble.",
                                    "Next time I ask a small favour, you have my permission to run."])],
          rewards=[reward_item("bakery:crusty_bread", 3), reward_item("bakery:breadbox"), skill("cook", 80)]),
]

chapter("small_favours", "Small Favours", "One small favour leads to another", "bakery:crusty_bread", "side", 0,
        REECE)
