"""Chapter: magic, the Arcane Order path: Act I (first release).
Plan: src/plans/quests/magic.json. Archmage Orrin Vael runs the Order from Reece's library tower; Pip is his runaway
apprentice and Sister Agathe hunts the undead."""
from common import chapter, quest, talk_char, item, reward_item, skill, giver_org, encounter
from common import enc, fight, boss, search, sample, talk_org, talk_villager, talk_char, item, reward_item, skill, encounter, giver_org  # noqa: F401

Q = [
    quest("the_order_calls", "The Order Calls", icon="minecraft:book", after=["main_story:act1_start"],
          giver=giver_org("arcane", ["The Arcane Order is recruiting. Discreetly.", "Bring ten books and a quill to Archmage Orrin in Reece."], "I'm interested"),
          text=["A village librarian slips you a note: the Arcane Order is recruiting, and the entrance fee is ten "
                "books and a quill. Bring them to Archmage Orrin Vael in Reece."],
          tasks=[item("minecraft:book", 10, consume=True), item("minecraft:feather", consume=True),
                 item("minecraft:ink_sac", consume=True),
                 talk_char("orrin", ["Ten books and a quill! Marvellous! Where are my spectacles?", "Ah. On my head. Welcome, apprentice."])],
          rewards=[reward_item("minecraft:book", name="Guide to the Schools",
                               lore=["Eight schools. Orrin has underlined the dangerous ones."]),
                   skill("magic", 80)]),

    quest("an_honest_table", "An Honest Table", icon="minecraft:enchanting_table", after=["the_order_calls"],
          text=["Orrin despises guesswork. Build an enchanting table ringed by fifteen bookshelves, and enchant your "
                "first tool."],
          tasks=[{"place": "reece"},
                 {"build": {"blocks": {"minecraft:enchanting_table": 1, "minecraft:bookshelf": 15}, "radius": 8},
                  "title": "Build an enchanting table ringed with bookshelves"},
                 {"use": "minecraft:enchanting_table", "title": "Enchant your first tool at the table"}],
          rewards=[reward_item("minecraft:lapis_lazuli", 16), skill("magic", 100)]),

    quest("reroll_the_fates", "Reroll the Fates", icon="minecraft:enchanted_book", after=["an_honest_table"],
          text=["Orrin's test: produce a book with two enchantments he names, using the table's re-roll, without "
                "wasting more than ten levels."],
          tasks=[talk_char("orrin", ["Two enchantments on one book, wasting no more than ten levels.", "Fortune favours the frugal."]),
                 item("minecraft:enchanted_book"), {"checkmark": "I made the book without wasting ten levels"}],
          rewards=[reward_item("minecraft:enchanted_book", name="A Careful Hand",
                               enchant={"minecraft:unbreaking": 3}), skill("magic", 120)]),

    quest("the_priest", "The Priest's Blessing", icon="irons_spellbooks:priest_spawn_egg", after=["the_order_calls"],
          text=["Priests of the Order wander between villages. Find one, trade with him for a healing potion and "
                "hear about the undead stirring beneath old graves."],
          tasks=[{"structure": "#villages", "title": "Find a village priest"},
                 {"talk": "entity", "entity": "irons_spellbooks:priest",
                  "lines": ["Something stirs beneath the old graves. Sister Agathe hunts it.", "Take a healing draught. Notch's blessing."]}],
          rewards=[reward_item("irons_spellbooks:greater_healing_potion"), skill("magic", 100)]),

    quest("first_ink", "Ink and Parchment", icon="irons_spellbooks:inscription_table", after=["the_order_calls"],
          text=["Craft an inscription table, mix common ink, and copy a scroll for the library's records."],
          tasks=[item("irons_spellbooks:inscription_table", crafted=True),
                 item("irons_spellbooks:common_ink", crafted=True), item("irons_spellbooks:scroll")],
          rewards=[reward_item("minecraft:paper", 16), reward_item("irons_spellbooks:common_ink", 4),
                   skill("magic", 110)]),

    quest("arcane_essence", "Essence of the Arcane", icon="irons_spellbooks:arcane_essence", after=["first_ink"],
          text=["Break down unwanted scrolls and enchanted gear into arcane essence, and gather twenty: the Order's "
                "currency."],
          tasks=[item("irons_spellbooks:arcane_essence", 20)],
          rewards=[reward_item("irons_spellbooks:blank_rune"), skill("magic", 130)]),

    quest("first_spellbook", "A Book of One's Own", icon="irons_spellbooks:copper_spell_book",
          after=["arcane_essence"],
          text=["Orrin won't let an untested caster anywhere near the library's rare books. Bind a copper spellbook, "
                "inscribe your first spell, and prove your control on a target dummy until it comes cleanly."],
          tasks=[item("irons_spellbooks:copper_spell_book", crafted=True), item("dummmmmmy:target_dummy"),
                 {"cast": "any", "count": 10, "title": "Practise on the dummy until it comes cleanly"}],
          rewards=[reward_item("irons_spellbooks:mana_ring"), skill("magic", 160)]),

    quest("the_study", "The Study", icon="irons_spellbooks:wisewood_bookshelf", after=["first_spellbook"],
          text=["Every mage needs a study. Build one with wisewood bookshelves, a brazier, a pedestal for your book "
                "and a scroll rack."],
          tasks=[{"build": {"blocks": {"irons_spellbooks:wisewood_bookshelf": 4, "irons_spellbooks:brazier": 1,
                                       "supplementaries:pedestal": 1, "handcrafted:oak_shelf": 1}, "radius": 8},
                  "title": "Build a study"}],
          rewards=[reward_item("irons_spellbooks:wisewood_planks", 32), reward_item("minecraft:book", 8),
                   skill("magic", 150)]),

    quest("pyromancer_tower", "The Pyromancer's Tower", icon="irons_spellbooks:pyromancer_spawn_egg",
          after=["first_spellbook"],
          text=["Orrin's old rival keeps a tower near the badlands. Find the Pyromancer Tower and ask its "
                "pyromancer to teach you, politely."],
          tasks=[{"structure": "irons_spellbooks:pyromancer_tower", "title": "Find the Pyromancer Tower"},
                 {"talk": "entity", "entity": "irons_spellbooks:pyromancer",
                  "lines": ["Orrin sent you? Politely? Hm. I teach those who can take a fireball."]}],
          rewards=[reward_item("irons_spellbooks:scroll_fire"), skill("magic", 160)]),

    quest("pyromancers_duel", "Trial by Fire", icon="irons_spellbooks:pyromancer_helmet",
          after=["pyromancer_tower"],
          text=["The pyromancer only teaches those who can take a fireball. Duel him with spells until he yields."],
          tasks=[encounter(["Ha! Let's see what the old windbag taught you!", "Enough! You've earned it."],
                           then="kill", entity="irons_spellbooks:pyromancer", name="The Pyromancer", health=60)],
          rewards=[reward_item("irons_spellbooks:pyromancer_helmet"), reward_item("irons_spellbooks:fire_rune"),
                   skill("magic", 220)]),

    quest("school_of_fire", "School of Fire", icon="irons_spellbooks:fire_rune", after=["pyromancer_tower"],
          text=["The pyromancer will teach you, once you've earned it. The dead keep clawing out of the old graves "
                "around her tower, and only fire lays them to rest for good.",
                "Craft a fire rune, scribe a fire spell, and cleanse twenty of the restless dead with flame."],
          tasks=[item("irons_spellbooks:fire_rune", crafted=True), item("irons_spellbooks:scroll_fire"),
                 {"spellkill": ["minecraft:zombie", "minecraft:husk", "minecraft:skeleton", "minecraft:stray",
                                "minecraft:zombie_villager", "minecraft:drowned"], "school": "fire", "count": 20,
                  "title": "Lay twenty of the dead to rest with fire"}],
          rewards=[reward_item("irons_spellbooks:fireward_ring"), skill("magic", 200)]),

    quest("mangrove_hut", "The Apothecarist", icon="irons_spellbooks:apothecarist_spawn_egg", after=["the_priest"],
          text=["Deep in the mangroves lives the Apothecarist, who trades potions for odd ingredients. Find the hut "
                "and trade her a stack of mangrove roots and spider eyes."],
          tasks=[{"structure": "irons_spellbooks:mangrove_hut", "title": "Find the Apothecarist's hut"},
                 item("minecraft:mangrove_roots", 32, consume=True), item("minecraft:spider_eye", 8, consume=True),
                 {"talk": "entity", "entity": "irons_spellbooks:apothecarist",
                  "lines": ["Roots and eyes. You've done your reading.", "Take this elixir. It toughens the skin."]}],
          rewards=[reward_item("irons_spellbooks:oakskin_elixir"), skill("magic", 180)]),

    quest("the_poisoned_traveller", "The Poisoned Traveller", icon="artifacts:antidote_vessel",
          after=["mangrove_hut"], signature="artifacts:antidote_vessel",
          text=["A courier staggers out of the swamp, poisoned, withered and slowing by the minute. Keep him alive "
                "with what the Apothecarist taught you: brew a cure for each ailment in turn, before the next one "
                "sets in."],
          tasks=[item("irons_spellbooks:alchemist_cauldron"),
                 encounter(["Poison... then withering... I can't feel my legs.", "You cured me? Thank you."],
                           entity="minecraft:villager", name="Poisoned Courier",
                           where={"biomes": ["minecraft:swamp", "minecraft:mangrove_swamp"]}),
                 {"checkmark": "I brewed a cure for each ailment"}],
          rewards=[reward_item("artifacts:antidote_vessel"), skill("magic", 260)]),

    quest("witch_ingredients", "Hags' Pantry", icon="minecraft:glowstone_dust", after=["mangrove_hut"],
          text=["The Apothecarist won't go near the witches, but she wants their stock. Visit a witch hut and "
                "bring back a witch's redstone, glowstone and a bottle of her brew."],
          tasks=[{"structure": "#witch_huts", "title": "Find a witch's hut"},
                 {"drop": {"from": ["minecraft:witch"], "chance": 0.4, "item": "minecraft:redstone"}},
                 {"drop": {"from": ["minecraft:witch"], "chance": 0.4, "item": "minecraft:glowstone_dust"}},
                 {"drop": {"from": ["minecraft:witch"], "chance": 0.3,
                           "item": {"name": "Witch's Brew", "tooltip": "A bottle of her own stock",
                                    "texture": "minecraft:item/potion"}}, "consume": False}],
          rewards=[reward_item("irons_spellbooks:poisonward_ring"), skill("magic", 200)]),

    quest("wizard_tower", "The Lost Apprentice", icon="irons_spellbooks:wizard_hat", after=["first_spellbook"],
          text=["Pip, Orrin's apprentice, ran off with three of his books. Track her to a wizard tower in the old "
                "forests, solve the warded door, and talk her into coming home."],
          tasks=[{"structure": "structory_towers:wizard_tower", "title": "Find the wizard tower"},
                 {"checkmark": "I solved the warded door"},
                 encounter(["Orrin sent you? I only borrowed the books.", "Fine, I'll go home. I'm keeping the hat."],
                           character="pip")],
          rewards=[reward_item("irons_spellbooks:wizard_hat"),
                   reward_item("minecraft:enchanted_book", name="Orrin's Borrowed Book",
                               enchant={"minecraft:mending": 1}),
                   skill("magic", 240)]),

    quest("mana_milestone", "A Hundred Sparks", icon="irons_spellbooks:mana_upgrade_orb", after=["school_of_fire"],
          text=["Orrin is raising a ward of runes around Reece against whatever is draining the old places. Every "
                "spell cast by a sworn member of the Order feeds a spark of its echo into the ring.",
                "A hundred sparks will wake it. Cast them anywhere; the ward hears."],
          tasks=[{"cast": "any", "count": 100, "title": "Feed the ward a hundred spells"}],
          rewards=[reward_item("irons_spellbooks:mana_upgrade_orb"), skill("magic", 280)]),
]

ACT2 = [
    quest("alchemist_cauldron", "The Bubbling Cauldron", icon="irons_spellbooks:alchemist_cauldron",
          after=["the_poisoned_traveller", "main_story:act2_start"],
          text=["Orrin's long nights need better ink and a stronger brew. Mix uncommon and rare ink in an alchemist "
                "cauldron, and brew a casters' tea for him."],
          tasks=[item("irons_spellbooks:uncommon_ink", crafted=True, title="Mix uncommon ink for Orrin's scrolls"),
                 item("irons_spellbooks:rare_ink", crafted=True, title="Mix rare ink for his best work"),
                 item("herbalbrews:oolong_tea", consume=True, title="Brew a casters' tea for his long nights")],
          rewards=[reward_item("irons_spellbooks:rare_ink", 2), skill("magic", 180)]),

    quest("arcane_anvil", "The Arcane Anvil", icon="irons_spellbooks:arcane_anvil", after=["alchemist_cauldron"],
          text=["Scrolls are weak alone and strong merged. Forge an arcane anvil, merge two scrolls into a stronger "
                "one, and add an upgrade orb to your armour."],
          tasks=[item("irons_spellbooks:arcane_anvil", crafted=True, title="Forge an arcane anvil"),
                 {"use": "irons_spellbooks:arcane_anvil", "count": 1, "title": "Merge two scrolls on the anvil"}],
          rewards=[reward_item("irons_spellbooks:evocation_upgrade_orb"), skill("magic", 200)]),

    quest("mithril_vein", "The Mithril Vein", icon="irons_spellbooks:mithril_ingot", after=["arcane_anvil"],
          text=["A better spellbook needs mithril. Mine it deep in the deepslate, smelt it and weave mithril cloth "
                "for the binding."],
          tasks=[item("irons_spellbooks:mithril_scrap", 4, title="Mine mithril deep in the deepslate"),
                 item("irons_spellbooks:mithril_ingot", 2, title="Smelt the mithril"),
                 item("irons_spellbooks:mithril_weave", crafted=True, title="Weave mithril cloth for a spellbook binding")],
          rewards=[reward_item("irons_spellbooks:mithril_ingot", 2), skill("magic", 220), skill("mining", 150)]),

    quest("mountain_tower", "The Cryomancer's Tower", icon="irons_spellbooks:frostward_ring",
          after=["alchemist_cauldron"],
          text=["High in the frozen peaks stands the Cryomancer's tower. Climb to it through the snow, with the cold "
                "biting at you."],
          tasks=[{"be": {"biomes": ["minecraft:frozen_peaks", "minecraft:snowy_slopes", "minecraft:jagged_peaks"]},
                  "title": "Climb into the frozen peaks"},
                 {"structure": "irons_spellbooks:mountain_tower", "title": "Reach the Cryomancer's tower"}],
          rewards=[reward_item("irons_spellbooks:frostward_ring"), skill("magic", 220)]),

    quest("cryomancer", "Thaw the Cryomancer", icon="irons_spellbooks:cryomancer_chestplate", after=["mountain_tower"],
          text=["The Cryomancer has gone cold in every way and attacks anyone who climbs his stairs. Melt him with "
                "fire."],
          tasks=[boss("irons_spellbooks:cryomancer", "irons_spellbooks:mountain_tower", "The Cryomancer",
                      "Defeat the Cryomancer at the top of his stairs"),
                 {"cast": {"school": "irons_spellbooks:fire"}, "count": 5, "title": "Melt his ice with fire spells"}],
          rewards=[reward_item("irons_spellbooks:cryomancer_chestplate"), reward_item("irons_spellbooks:scroll_ice"),
                   skill("magic", 300)]),

    quest("school_of_ice", "School of Ice", icon="irons_spellbooks:ice_rune", after=["mountain_tower"],
          text=["The tower's frost leaves materials behind. Collect frozen bones and permafrost shards, craft an ice "
                "rune, and bind an ice spellbook."],
          tasks=[item("irons_spellbooks:frozen_bone", 4, title="Collect frozen bones from the peaks"),
                 item("irons_spellbooks:permafrost_shard", 4, title="Collect permafrost shards"),
                 item("irons_spellbooks:ice_rune", crafted=True, title="Craft an ice rune"),
                 item("irons_spellbooks:ice_spell_book", crafted=True, title="Bind an ice spellbook")],
          rewards=[reward_item("irons_spellbooks:ice_staff"), skill("magic", 260)]),

    quest("spider_den", "The Ice Spider Den", icon="irons_spellbooks:ice_spider_egg", after=["school_of_ice"],
          text=["A furled map points to the Ice Spider den. Kill its brood and take one unbroken ice spider egg."],
          tasks=[fight("irons_spellbooks:ice_spider", 8, "irons_spellbooks:ice_spider_den", "Den Brood",
                       "Kill the den's brood"),
                 search("irons_spellbooks:ice_spider_den", 1, "an Unbroken Ice Spider Egg", "An unbroken egg, cold as a stone.",
                        texture="minecraft:item/egg", title="Search the den for an unbroken egg")],
          rewards=[reward_item("irons_spellbooks:ice_venom_vial", 3), skill("magic", 280)]),

    quest("spider_egg_feast", "A Cold Delicacy", icon="irons_spellbooks:cooked_ice_spider_egg", after=["spider_den"],
          text=["Pip dares you to cook an ice spider egg and serve it to Orrin without telling him what it is."],
          tasks=[enc(["Cook an ice spider egg. Serve it to Orrin. Don't tell him."], character="pip",
                     title="Take Pip's dare"),
                 item("irons_spellbooks:cooked_ice_spider_egg", consume=True, title="Cook an ice spider egg"),
                 talk_char("orrin", ["A cold delicacy? Splendid. Is that... egg? Delicious."],
                           title="Serve the dish to Orrin")],
          rewards=[skill("magic", 240), skill("cook", 150)]),

    quest("impaled_icebreaker", "The Impaled Icebreaker", icon="irons_spellbooks:music_disc_whispers_of_ice",
          after=["school_of_ice"], discover={"structure": "irons_spellbooks:impaled_icebreaker"},
          text=["A ship is skewered on an iceberg, its crew frozen solid. Climb aboard and bring the captain's sea "
                "chest back intact."],
          tasks=[search("irons_spellbooks:impaled_icebreaker", 1, "the Captain's Sea Chest", "The captain's chest, iced shut.",
                        texture="minecraft:item/chest_minecart", title="Climb aboard and open the captain's chest")],
          rewards=[reward_item("irons_spellbooks:music_disc_whispers_of_ice"), skill("magic", 260)]),

    quest("lightning_in_a_bottle", "Lightning in a Bottle", icon="irons_spellbooks:lightning_bottle",
          after=["arcane_anvil"],
          text=["Storms hold more than rain. Catch three bottles of lightning while one rages, and craft a "
                "lightning rune from them."],
          tasks=[{"cast": {"school": "irons_spellbooks:lightning"}, "count": 5, "title": "Call the storm down with lightning spells"},
                 item("irons_spellbooks:lightning_bottle", 3, title="Catch three bottles of lightning"),
                 item("irons_spellbooks:lightning_rune", crafted=True, title="Craft a lightning rune")],
          rewards=[reward_item("irons_spellbooks:electromancer_helmet"), skill("magic", 260)]),

    quest("evoker_fort", "The Evoker Fort", icon="minecraft:spyglass", after=["arcane_anvil"],
          text=["Orrin's stolen tome, the Archevoker's logbook, is kept in the Evoker Fort. Scout it and learn the "
                "guards' rotations."],
          tasks=[{"structure": "irons_spellbooks:evoker_fort", "title": "Scout the Evoker Fort"},
                 {"observe": "minecraft:evoker", "ticks": 60, "title": "Watch the guards' rotation from cover"},
                 enc(["I came as soon as I could. What did you see?", "Good. Remember it."], character="orrin",
                     title="Report what you saw to Orrin")],
          rewards=[reward_item("minecraft:spyglass"), skill("magic", 250)]),

    quest("unseen_thief", "The Unseen Thief", icon="artifacts:scarf_of_invisibility", after=["evoker_fort"],
          signature="artifacts:scarf_of_invisibility",
          text=["Get into the fort and take the logbook without any illager seeing you. Caught once, you start again. "
                "Pip lends her trick for the first try, and the scarf she borrowed from Orrin once you're out."],
          tasks=[item("irons_spellbooks:invisibility_elixir", title="Take Pip's invisibility elixir"),
                 {"timed": {"seconds": 300, "goal": {"structure": "irons_spellbooks:evoker_fort", "label": "the logbook's vault", "away": 40},
                            "lines": ["Don't be seen. If anything hurts you, you start again."], "start": "Slip in",
                            "no": ["hurt"]}, "title": "Cross the fort unseen"},
                 search("irons_spellbooks:evoker_fort", 1, "the Archevoker's Logbook", "A cipher-written logbook, untranslated.",
                        texture="minecraft:item/written_book", title="Take the logbook from the vault")],
          rewards=[reward_item("artifacts:scarf_of_invisibility"), reward_item("irons_spellbooks:archevoker_logbook_untranslated"),
                   skill("magic", 300)]),

    quest("translate_logbook", "In the Illagers' Hand", icon="irons_spellbooks:archevoker_logbook_translated",
          after=["unseen_thief"],
          text=["The Archevoker's logbook is written in a cipher. Translate it with Orrin's help, page by page. It "
                "names the catacombs where the dead are being raised."],
          tasks=[item("irons_spellbooks:archevoker_logbook_untranslated", title="Bring the untranslated logbook"),
                 talk_char("orrin", ["A cipher, page by page. Hold the lamp.", "It names the catacombs. The dead are being raised."],
                           title="Translate the cipher with Orrin")],
          rewards=[reward_item("irons_spellbooks:archevoker_logbook_translated"), skill("magic", 300)]),

    quest("archevoker", "The Archevoker", icon="irons_spellbooks:archevoker_spawn_egg", after=["evoker_fort"],
          text=["The Archevoker summons fangs and vexes in the fort's great hall. Defeat him, if you want his robes."],
          tasks=[boss("irons_spellbooks:archevoker", "irons_spellbooks:evoker_fort", "The Archevoker",
                      "Defeat the Archevoker in the great hall")],
          rewards=[reward_item("irons_spellbooks:evoker_spell_book"), skill("magic", 380)]),

    quest("five_schools", "Five Schools", icon="irons_spellbooks:affinity_ring",
          after=["lightning_in_a_bottle", "school_of_ice"],
          text=["Orrin will not call you a mage until you can show him five schools. Cast each once in front of "
                "him: fire, ice, lightning, nature and holy."],
          tasks=[{"cast": {"school": "irons_spellbooks:fire"}, "count": 1, "title": "Cast a fire spell for Orrin"},
                 {"cast": {"school": "irons_spellbooks:ice"}, "count": 1, "title": "Cast an ice spell for Orrin"},
                 {"cast": {"school": "irons_spellbooks:lightning"}, "count": 1, "title": "Cast a lightning spell for Orrin"},
                 {"cast": {"school": "irons_spellbooks:nature"}, "count": 1, "title": "Cast a nature spell for Orrin"},
                 {"cast": {"school": "irons_spellbooks:holy"}, "count": 1, "title": "Cast a holy spell for Orrin"}],
          rewards=[reward_item("irons_spellbooks:affinity_ring"), skill("magic", 320)]),

    quest("spell_slot", "Room for More", icon="irons_spellbooks:gold_spell_book", after=["five_schools", "mithril_vein"],
          text=["Five schools need a bigger book. Bind a gold spellbook and add a spell-slot upgrade so it holds "
                "every school you know."],
          tasks=[item("irons_spellbooks:gold_spell_book", crafted=True, title="Bind a gold spellbook"),
                 item("irons_spellbooks:arcane_rune", title="Make the rune that adds a spell slot")],
          rewards=[reward_item("irons_spellbooks:epic_ink", 2), skill("magic", 400)]),
]

chapter("magic", "The Arcane Order", "Magic path", "irons_spellbooks:iron_spell_book", "skills", 10, Q + ACT2)
