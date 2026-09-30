"""Generate the Friends of the Forest Field Guide as a Patchouli external book.

Patchouli only discovers books inside mod jars or in the game directory's patchouli_books/
folder, so the book ships in pack/patchouli_books/ (book id: patchouli:fotf_field_guide).
"""
import json
import os
import shutil

PACK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
BOOK = 'fotf_field_guide'
DATA = os.path.join(PACK, 'patchouli_books', BOOK)
ASSETS = os.path.join(DATA, 'en_us')
OLD_KUBEJS_COPIES = [os.path.join(PACK, 'kubejs', 'data', 'kubejs', 'patchouli_books'),
                     os.path.join(PACK, 'kubejs', 'assets', 'kubejs', 'patchouli_books')]

UNICORN_BOOK = 'patchouli:guide_book{"patchouli:book":"ultimate_unicorn_mod:unicorn_guide"}'


def text(t, title=None):
    page = {'type': 'patchouli:text', 'text': t}
    if title:
        page['title'] = title
    return page


def spot(item, t, title=None):
    page = {'type': 'patchouli:spotlight', 'item': item, 'text': t}
    if title:
        page['title'] = title
    return page


def craft(recipe, t):
    return {'type': 'patchouli:crafting', 'recipe': recipe, 'text': t}


CATEGORIES = [
    ('getting_started', 'Ways to Get Started', 'minecraft:oak_sapling',
     'New to modded Minecraft? Start here. Everything you need for your first day in the forest.'),
    ('creatures', 'Creatures & Companions', 'minecraft:lead',
     'Unicorns, critters, pets and every other friend of the forest.'),
    ('farming', 'Farming & Cooking', 'farmersdelight:cooking_pot',
     'Grow, cook, bake, brew and fish.'),
    ('building', 'Building & Decor', 'refurbished_furniture:oak_chair',
     'Furniture, decorations and cozy homes.'),
    ('magic', 'Magic', 'irons_spellbooks:copper_spell_book',
     'Two magic mods: one for battle spells, one for building your own spells and magical helpers.'),
    ('combat', 'Combat & Gear', 'minecraft:iron_sword',
     'Weapons, armor, tools and the bosses worth using them on.'),
    ('exploring', 'Exploring', 'minecraft:filled_map',
     'Villages, dungeons, caves and whole new dimensions.'),
    ('travel', 'Travel & Movement', 'paraglider:paraglider',
     'Parkour, gliders, grappling hooks, airships and boats.'),
    ('grove', 'Grove Rules & Server Info', 'minecraft:clock',
     'How this server works, and how we treat each other.'),
]

# (category, id, name, icon, pages)
ENTRIES = [
    # ---------- Ways to Get Started ----------
    ('getting_started', 'welcome', 'Welcome, Friend!', 'minecraft:oak_sapling', [
        text('This book is your field guide to the forest.$(br2)The first chapter covers the basics. The other chapters introduce every big mod and point you to its own guide book when it has one.'),
        text('Lost this book? Type $(l)/guide$() in chat for a new copy.$(br2)Stuck on anything? Ask in chat. Someone has probably figured it out already.', 'Tip'),
    ]),
    ('getting_started', 'first_day', 'Your First Day', 'minecraft:oak_log', [
        text('A good first day:$(br)$(li)Punch trees, make tools$(li)Find a village for food and a $(l)Waystone$()$(li)Make a bed before night$(li)Claim your base (see $(l)Your Base$())'),
        text('Days here are long and sunsets are slow, so take your time.$(br2)If you die, your items wait in a $(l)gravestone$(). Nothing is lost!', 'No Rush'),
    ]),
    ('getting_started', 'jei', 'Looking Things Up', 'minecraft:knowledge_book', [
        text('$(l)JEI$() is a list of every item in the pack. It starts hidden: press $(l)Ctrl+O$() to show it next to your inventory.$(br2)Hover an item and press:$(li)$(l)R$() to see how to make it$(li)$(l)U$() to see what it is used for'),
        text('Type in the search bar at the bottom of JEI to find anything.$(br2)$(l)Jade$() shows the name and mod of whatever you look at, at the top of your screen.$(br2)Hold $(l)Shift$() over items for extra info.', 'More Tips'),
    ]),
    ('getting_started', 'death', 'When You Die', 'gravestone:gravestone', [
        spot('gravestone:gravestone', 'Dying drops a $(l)gravestone$() holding all your items.$(br2)Walk back and right-click it (or break it) to get everything back.'),
        text('Your minimap marks the spot where you died, so you can find your way back.$(br2)Some dungeons are dangerous, so bring spare gear when you go back for your grave.'),
    ]),
    ('getting_started', 'maps', 'Maps & Waypoints', 'minecraft:filled_map', [
        text('The minimap sits in the corner of your screen. It shows players and your tamed pets.$(br2)Press $(l)M$() for the big world map.$(br2)Right-click on the world map to create a $(l)waypoint$(), so you can find a place again.'),
        text('Press $(l)Y$() for minimap settings: size, what it shows and more.$(br2)Waypoints show on your minimap to point you in the right direction.', 'Settings'),
    ]),
    ('getting_started', 'claims', 'Your Base & Friends', 'minecraft:white_banner', [
        text('Claim your land so nobody else can break blocks or open chests there.$(br2)Open the world map ($(l)M$()), then right-click chunks to claim them. Or press the $(l)\'$() (apostrophe) key for the claims menu.'),
        text('In the claims menu, make a $(l)party$() and invite friends.$(br2)Party members can build in each other\'s claims and see each other on the map.', 'Parties'),
    ]),
    ('getting_started', 'waystones', 'Waystones', 'waystones:waystone', [
        spot('waystones:waystone', 'Stone pillars found in villages. Right-click one to unlock it.$(br2)Then use any waystone to teleport to every waystone you have unlocked. It is free!'),
        spot('waystones:warp_stone', 'Craft a $(l)Warp Stone$() (press $(l)R$() on it in JEI) to teleport to your waystones from anywhere. It needs a short rest between uses.'),
    ]),
    ('getting_started', 'voice', 'Voice Chat', 'minecraft:goat_horn', [
        text('Talk to players near you: hold $(l)Caps Lock$().$(br2)Press $(l)G$() to make or join a $(l)group$(), so friends can hear you anywhere in the world.$(br2)Press $(l)N$() to turn voice chat off.'),
    ]),
    ('getting_started', 'storage', 'Backpacks & Storage', 'sophisticatedbackpacks:backpack', [
        spot('sophisticatedbackpacks:backpack', 'Craft a $(l)backpack$() for extra space. Press $(l)B$() to open it while wearing it. Upgrades add auto-pickup, feeding and more.'),
        text('$(l)Tom\'s Simple Storage$() links all your chests to one terminal where you can search everything.$(br2)Right-click an animal or chest while crouching with empty hands to $(l)carry$() it (Carry On).', 'More Storage'),
    ]),
    ('getting_started', 'keys', 'Handy Keys', 'minecraft:tripwire_hook', [
        text('$(li)$(l)Ctrl+O$(): show/hide JEI$(li)$(l)B$(): backpack$(li)$(l)V$(): cast spell$(li)$(l)R$(): spell wheel$(li)$(l)Caps Lock$(): talk$(li)$(l)Alt+P$(): parkour skills$(li)$(l)Y$(): minimap settings$(li)$(l)F7$(): shaders on/off'),
        text('Change any key in $(l)Options > Controls > Key Binds$(). The search bar there helps.$(br2)$(l)Reset All$() brings back the server\'s recommended keys.', 'Changing Keys'),
    ]),

    # ---------- Creatures & Companions ----------
    ('creatures', 'unicorns', 'Unicorns & Magical Horses', 'ultimate_unicorn_mod:unicorn_horn', [
        text('Unicorns, pegasi, hippocamps, reindeer and more live in forests, plains, hills and oceans.$(br2)Tame and ride them like horses. Pegasi fly, and unicorns have magical powers!'),
        spot(UNICORN_BOOK, 'The $(l)Unicorn Guidebook$() explains everything. Get one with $(l)/guide unicorn$().', 'Official Guide'),
    ]),
    ('creatures', 'alexs_mobs', 'Alex\'s Mobs', 'alexsmobs:animal_dictionary', [
        text('Around 90 real and fantasy animals: elephants, raccoons, hummingbirds, whales, crows and many more.$(br2)Some can be tamed, and many drop useful items.'),
        craft('alexsmobs:animal_dictionary', 'The $(l)Animal Dictionary$() describes every animal and how to tame it.'),
    ]),
    ('creatures', 'critters', 'Critters & Companions', 'crittersandcompanions:dragonfly_wing', [
        text('Small friends to tame by feeding:$(li)Red panda: bamboo$(li)Ferret: raw chicken$(li)Shima enaga: seeds$(li)Snail: carrots$(li)Ladybug: mushrooms$(li)Jumping spider: dragonfly wings'),
        text('$(li)Dragonfly: spider eyes$(li)Stag beetle: sweet berries$(li)Stick bug: leaves$(li)Roly poly: dead bushes$(li)Weevil: acorns$(br2)Otters, koi and sea bunnies can\'t be tamed.', 'More Critters'),
    ]),
    ('creatures', 'wildlife', 'More Wildlife', 'minecraft:lead', [
        text('$(l)Naturalist$(): deer, bears, snails, birds and fireflies.$(br2)$(l)WilderNature$(): deer, raccoons, owls, penguins, flamingos and more.$(br2)$(l)Friends & Foes$(): mobs from the Minecraft mob votes, like the copper golem.'),
    ]),
    ('creatures', 'pets', 'Pets & Collars', 'domesticationinnovation:collar_tag', [
        text('Tame an animal by feeding it until hearts appear. Foxes, rabbits, frogs and axolotls can be tamed here too!$(br2)A $(l)name tag$() keeps any animal from despawning.'),
        spot('domesticationinnovation:collar_tag', 'Rename a $(l)Collar Tag$() at an anvil, add pet enchantments there too, then right-click your tamed pet. Pet beds let pets respawn.'),
    ]),
    ('creatures', 'bugs', 'Butterflies & Bugs', 'butterflies:butterfly_net', [
        spot('butterflies:butterfly_net', 'Swing a $(l)Butterfly Net$() to catch butterflies, moths and caterpillars. Collect every species!'),
        spot('supplementaries:jar', 'Right-click fireflies, dragonflies, snails and leaf insects with an empty $(l)jar$() to keep them. Firefly jars glow!'),
    ]),

    # ---------- Farming & Cooking ----------
    ('farming', 'farmers_delight', 'Farmer\'s Delight', 'farmersdelight:cooking_pot', [
        text('New crops (tomatoes, onions, rice, cabbage) and real meals.$(br2)Place a $(l)Cooking Pot$() over a fire or heat source, then add ingredients.'),
        spot('farmersdelight:cutting_board', 'Use a knife on a $(l)Cutting Board$() to slice ingredients. Look up any meal with $(l)R$() in JEI.'),
    ]),
    ('farming', 'lets_do', 'The Let\'s Do Mods', 'vinery:red_grape', [
        text('A whole cozy series:$(li)$(l)Farm & Charm$(): farm life$(li)$(l)Bakery$(): breads and cakes$(li)$(l)Vinery$(): grapes and wine$(li)$(l)Brewery$(): beer'),
        text('$(li)$(l)Candlelight$(): dinners$(li)$(l)HerbalBrews$(): tea and coffee$(li)$(l)Meadow$(): cheese$(li)$(l)Beachparty$(): beach fun$(li)$(l)Camping$(): tents$(li)$(l)Furniture$(): more decor', 'And More'),
    ]),
    ('farming', 'seasons', 'Seasons', 'sereneseasons:calendar', [
        spot('sereneseasons:calendar', 'The year has seasons. Crops only grow in the right seasons, and winter gets cold and snowy.$(br2)A $(l)Calendar$() shows the season. JEI shows which seasons each crop likes.'),
    ]),
    ('farming', 'fishing', 'Fishing', 'aquaculture:iron_fishing_rod', [
        spot('aquaculture:iron_fishing_rod', '$(l)Aquaculture$() adds lots of fish, better rods, hooks and bait. $(l)Lili\'s Lucky Lures$() adds fishing gear too.'),
    ]),

    # ---------- Building & Decor ----------
    ('building', 'furniture', 'Furniture', 'refurbished_furniture:oak_chair', [
        text('Four furniture mods, each with its own style:$(li)$(l)Refurbished Furniture$(): kitchens that really work$(li)$(l)Handcrafted$()$(li)$(l)Another Furniture$()$(li)$(l)Let\'s Do Furniture$()$(br2)Search JEI for "chair", "table" or "sofa".'),
    ]),
    ('building', 'decor', 'Decorations', 'supplementaries:jar', [
        text('$(l)Supplementaries$() and $(l)Amendments$(): jars, signposts, flower boxes, wall lanterns and lots of small details.$(br2)$(l)Snowy Spirit$(): sleds, gingerbread and winter decor.'),
        text('$(l)Comforts$(): sleeping bags for camping trips and hammocks for napping through the day.', 'Resting'),
    ]),

    # ---------- Magic ----------
    ('magic', 'irons_spells', 'Iron\'s Spells', 'irons_spellbooks:copper_spell_book', [
        text('Battle magic! Find spell $(l)scrolls$() in dungeons, put them in a $(l)spell book$(), then cast.$(br2)$(l)V$() casts your spell, $(l)R$() opens the spell wheel.'),
        craft('irons_spellbooks:patchouli_book', 'The official guidebook explains schools of magic, gear and bosses.'),
    ]),
    ('magic', 'ars_nouveau', 'Ars Nouveau', 'ars_nouveau:worn_notebook', [
        text('Build your own spells from pieces called glyphs, and make magical helpers that farm, carry items and craft for you.'),
        craft('ars_nouveau:worn_notebook', 'Craft the $(l)Worn Notebook$() first. It teaches everything, step by step.'),
    ]),
    ('magic', 'which_magic', 'Which Magic?', 'minecraft:enchanted_book', [
        text('$(l)Iron\'s Spells$(): easy to start, flashy fights, loot from dungeons.$(br2)$(l)Ars Nouveau$(): design your own spells, flying ritual, cute helpers for your base.$(br2)You can use both!'),
    ]),

    # ---------- Combat & Gear ----------
    ('combat', 'tinkers', 'Tinkers\' Construct', 'tconstruct:materials_and_you', [
        text('Build your own tools and weapons from parts. Every material behaves differently.'),
        craft('tconstruct:common/materials_and_you', 'Start with $(l)Materials and You$(). Each Tinkers\' book unlocks the next step.'),
    ]),
    ('combat', 'weapons', 'Weapons & Shields', 'spartanweaponry:iron_longsword', [
        text('$(l)Spartan Weaponry$(): daggers, spears, halberds, longbows and more, in every material.$(br2)$(l)Spartan Shields$(): more shields.$(br2)$(l)Simply Swords$(): katanas, glaives and rare legendary weapons from dungeons.'),
    ]),
    ('combat', 'bosses', 'Bosses', 'cataclysm:ignitium_ingot', [
        text('$(l)L_Ender\'s Cataclysm$() and $(l)Mowzie\'s Mobs$() add huge bosses in their own arenas.$(br2)They only fight you if you go to them, so the rest of the world stays normal. Bring your best gear!'),
    ]),
    ('combat', 'cosmetics', 'Looking Good', 'minecraft:leather_helmet', [
        text('$(l)Cosmetic Armor$() lets you wear any outfit over your real armor. Look for the extra slots in your inventory.$(br2)Try the funny hats from $(l)Alex\'s Mobs$()!'),
    ]),

    # ---------- Exploring ----------
    ('exploring', 'structures', 'Villages & Dungeons', 'minecraft:filled_map', [
        text('Villages come in many styles (CTOV). Guards protect them, and bounty boards give jobs for rewards.$(br2)Ruins, towers, camps and dungeons are everywhere. Their chests have separate loot for each player.'),
        text('Big dungeons (When Dungeons Arise, Cataclysm) are dangerous.$(br2)Spawners keep making mobs until you break them or light them up with torches.', 'Be Careful'),
    ]),
    ('exploring', 'compasses', 'Finding Places', 'naturescompass:naturescompass', [
        spot('naturescompass:naturescompass', 'The $(l)Nature\'s Compass$() points to any biome you pick.'),
        spot('explorerscompass:explorerscompass', 'The $(l)Explorer\'s Compass$() points to any structure you pick.'),
    ]),
    ('exploring', 'alexs_caves', 'Alex\'s Caves', 'alexscaves:cave_codex', [
        text('Six rare cave biomes deep underground: dinosaurs, candy, magnets, toxic caves and more.$(br2)They are hard to find. Look up $(l)Cave Tablet$() and $(l)Cave Codex$() in JEI to learn how to track them down.'),
    ]),
    ('exploring', 'twilight', 'The Twilight Forest', 'twilightforest:twilight_oak_sapling', [
        text('A magical forest dimension with bosses to beat in order.$(br2)To get there: dig a 2x2 pool of water, surround it with flowers and grass, then throw a $(l)diamond$() into it.'),
    ]),

    # ---------- Travel & Movement ----------
    ('travel', 'parcool', 'Parkour', 'parcool:parcool_guide', [
        text('$(l)ParCool$(): vault, wall-run, climb ledges, slide and roll.$(br2)Unlock moves in the skill tree ($(l)Alt+P$()). To slide: sprint, then press $(l)C$().'),
        craft('parcool:parcool_guide', 'The $(l)ParCool Guide$() explains every move.'),
    ]),
    ('travel', 'gliding', 'Gliders & Wings', 'paraglider:paraglider', [
        spot('paraglider:paraglider', 'Jump from high places and glide. Campfires push you up. Gliding uses stamina, and goddess statues increase it.'),
        spot('minecraft:elytra', 'Elytra go in their own slot, so you can still wear a chestplate.'),
    ]),
    ('travel', 'grappling', 'Grappling Hook', 'grapplemod:grapplinghook', [
        spot('grapplemod:grapplinghook', 'Left-click to throw, again to let go. Space jumps off. Hold Shift and W/S to climb the rope. Upgrade it at a Grappling Hook Modifier.'),
    ]),
    ('travel', 'aircraft', 'Aircraft', 'immersive_aircraft:gyrodyne', [
        spot('immersive_aircraft:gyrodyne', 'Start with a $(l)Gyrodyne$(): it needs no fuel. Later build biplanes and airships. Look them up in JEI.'),
    ]),
    ('travel', 'ships', 'Ships', 'smallships:oak_cog', [
        spot('smallships:oak_cog', '$(l)Small Ships$(): rowboats, cogs, galleys and more, with sails, storage and cannons.'),
    ]),
    ('travel', 'music', 'Music Together', 'mimi:guide', [
        text('$(l)MIMI$(): play instruments with friends. You can even plug in a real MIDI keyboard or play MIDI files.'),
        craft('mimi:guide', 'The $(l)MIMI guide$() explains the instruments.'),
    ]),

    # ---------- Grove Rules & Server Info ----------
    ('grove', 'time', 'Days & Nights', 'minecraft:clock', [
        text('Days are long here, and sunrises and sunsets last a long time, so enjoy the view!$(br2)The night is skipped when at least half of the players online are sleeping.'),
    ]),
    ('grove', 'rules', 'Grove Rules', 'minecraft:oak_sign', [
        text('$(li)Be kind$(li)No griefing or stealing$(li)Ask before building close to someone$(li)Leave the forest nicer than you found it$(li)Have fun!'),
    ]),
    ('grove', 'safety', 'Backups & Help', 'minecraft:chest', [
        text('The world is backed up regularly, so big accidents can be undone. Ask Dylan.$(br2)Something broken, or have an idea for the server? Tell Dylan!'),
    ]),
]


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


for d in [DATA] + OLD_KUBEJS_COPIES:
    shutil.rmtree(d, ignore_errors=True)

write(os.path.join(DATA, 'book.json'), {
    'name': 'Friends of the Forest Field Guide',
    'landing_text': 'Welcome to the forest, friend!$(br2)Start with $(l)Ways to Get Started$(), then explore the other chapters whenever you are curious.',
    'version': 1,
    'model': 'patchouli:book_green',
    'book_texture': 'patchouli:textures/gui/book_green.png',
    'show_progress': False,
    'use_resource_pack': False,
    'creative_tab': 'minecraft:tools_and_utilities',
    'i18n': False,
})

for sortnum, (cid, name, icon, desc) in enumerate(CATEGORIES):
    write(os.path.join(ASSETS, 'categories', cid + '.json'),
          {'name': name, 'description': desc, 'icon': icon, 'sortnum': sortnum})

order = {}
for cat, eid, name, icon, pages in ENTRIES:
    order[cat] = order.get(cat, -1) + 1
    write(os.path.join(ASSETS, 'entries', cat, eid + '.json'), {
        'name': name, 'icon': icon, 'category': 'patchouli:' + cat,
        'sortnum': order[cat], 'pages': pages,
    })

print(f'{len(CATEGORIES)} categories, {len(ENTRIES)} entries, {sum(len(e[4]) for e in ENTRIES)} pages')
