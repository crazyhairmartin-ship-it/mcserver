"""Chapter: magic, the Arcane Order path: Act I (first release).
Plan: src/plans/quests/magic.json. Archmage Orrin Vael runs the Order from Reece's library tower; Pip is his runaway
apprentice and Sister Agathe hunts the undead."""
from common import chapter, quest, talk_char, item, reward_item, skill, giver_org, encounter

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

chapter("magic", "The Arcane Order", "Magic path", "irons_spellbooks:iron_spell_book", "skills", 10, Q)
