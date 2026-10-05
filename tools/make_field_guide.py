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
    ('building', 'Building & Decor', 'handcrafted:oak_chair',
     'Furniture, decorations and cozy homes.'),
    ('magic', 'Magic', 'irons_spellbooks:copper_spell_book',
     'Two magic mods: one for battle spells, one for building your own spells and magical helpers.'),
    ('combat', 'Combat & Gear', 'minecraft:iron_sword',
     'Weapons, armor and the bosses worth using them on.'),
    ('exploring', 'Exploring', 'minecraft:filled_map',
     'Villages, dungeons, caves and whole new dimensions.'),
    ('travel', 'Travel & Movement', 'minecraft:elytra',
     'Parkour, grappling hooks, airships and boats.'),
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
    ('getting_started', 'books', 'More Guide Books', 'minecraft:bookshelf', [
        text('Big mods have their own guide books. Type a command in chat to get one:$(li)$(l)/guide unicorn$(): unicorns$(li)$(l)/guide spells$(): Iron\'s Spells$(li)$(l)/guide ars$(): Ars Nouveau$(li)$(l)/guide animals$(): Alex\'s Mobs$(li)$(l)/guide caves$(): Alex\'s Caves$(li)$(l)/guide music$(): MIMI'),
    ]),
    ('getting_started', 'first_day', 'Your First Day', 'minecraft:oak_log', [
        text('A good first day:$(br)$(li)Punch trees, make tools$(li)Find a village for food and a $(l)Waystone$()$(li)Make a bed before night$(li)Claim your base (see $(l)Your Base$())'),
        text('Days here are long and sunsets are slow, so take your time.$(br2)If you die, your items wait in a $(l)gravestone$(). Nothing is lost!', 'No Rush'),
    ]),
    ('getting_started', 'skills', 'Skills & Levels', 'minecraft:experience_bottle', [
        text('You get better at things by doing them. There are 12 skills: Mining, Foraging, Farming, Fishing, Cooking, Crafting, Attack, Range, Defense, Agility, Magic and Taming. Each level up to 50 gives a point to spend in that skill\'s tree. Press $(l)K$() to open the skill menu.'),
        text('Trees have five tiers. Spending points in a tree opens the next tier (5, 10, 15, then 25 points). Tiers marked $(l)OR$() let you pick one of two branches. Hover a node to see what it does now (white) and what the next rank adds (grey). A full tree costs exactly 50 points.', 'Skill Trees'),
        text('$(l)/fotfskills perks$() lists every perk you have. Click the $(l)star button$() beside your inventory for your character screen: health, stamina and mana, an $(l)Overview$() of every skill\'s level and your active buffs, and an icon tab per skill showing its XP and exactly what each of your nodes does (scroll for more).$(br2)Level-up messages are short: open chat and point at one to read the details.$(br2)$(l)/fotfskills levelups off$() hides them; $(l)on$() brings them back.', 'Perks'),
        text('Your $(l)total level$() (all 12 skills added up) gives extra hearts and ParCool stamina: the first at total level 8, all 15 by 256.$(br2)$(l)/fotfskills reset <tree>$() gives a tree\'s points back for 1 XP level per 2 points spent (at least 5).', 'Hearts & Resets'),
        text('Place a $(l)Pet Bed$() and let your pet walk onto it once: if it dies, it comes back at its bed the next morning (someone has to be nearby at sunrise).$(br2)Taming\'s $(l)Ferality$() gives a chance that a pet survives a killing blow and turns feral: full health, extra hearts and Strength II for 15 seconds.', 'Pets'),
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
        text('Press $(l)U$() to see and edit your waypoints. They show on your minimap to point you in the right direction.$(br2)To change the minimap\'s size and what it shows, go to $(l)Mods$() on the title screen and open $(l)Xaero\'s Minimap$() config.', 'Settings'),
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
        text('Right-click an animal or chest while crouching with empty hands to $(l)carry$() it (Carry On). Chests keep everything inside.', 'Carrying Things'),
    ]),
    ('getting_started', 'keys', 'Handy Keys', 'minecraft:tripwire_hook', [
        text('$(li)$(l)Ctrl+O$(): show/hide JEI$(li)$(l)M$(): world map$(li)$(l)U$(): waypoints$(li)$(l)B$(): backpack$(li)$(l)I$(): quiver$(li)$(l)V$(): cast spell$(li)$(l)R$(): spell wheel$(li)$(l)Caps Lock$(): talk$(li)$(l)G$(): voice chat groups'),
        text('$(li)$(l)Z$(): Alex\'s Caves ability$(li)$(l)H$(): kirin breath (while riding one)$(li)$(l)X$(): Cataclysm ability$(li)$(l)J$(): instrument in your hand$(li)$(l)F7$(): shaders on/off', 'Riding & Abilities'),
        text('Change any key in $(l)Options > Controls > Key Binds$(). The search bar there helps.$(br2)$(l)Reset All$() brings back the server\'s recommended keys. Do this after big pack updates.', 'Changing Keys'),
        text('Shaders add real shadows, sky and water. Turn them on in $(l)Options > Video Settings > Shader Packs$().$(br2)$(l)Complementary$() looks the best; $(l)MakeUp$() and $(l)Super Duper Vanilla$() are lighter for slower computers. $(l)F7$() toggles them.', 'Shaders'),
    ]),

    # ---------- Creatures & Companions ----------
    ('creatures', 'unicorns', 'Unicorns & Magical Horses', 'ultimate_unicorn_mod:unicorn_horn', [
        text('Unicorns, pegasi, hippocamps, reindeer and more live in forests, plains, hills and oceans.$(br2)Tame and ride them like horses. Pegasi fly: hold $(l)Space$() to go up and $(l)Left Ctrl$() to go down. Unicorns have magical powers!'),
        text('Nightmares fly on speed, not wing power: gallop straight to full speed on open ground, then hold $(l)Space$(). Keep turns gentle. If they slow down, they glide back to the ground.$(br2)Their hoof fire and fireballs here never hurt friends, only monsters.', 'Nightmares'),
        spot(UNICORN_BOOK, 'The $(l)Unicorn Guidebook$() explains everything. Get one with $(l)/guide unicorn$().', 'Official Guide'),
        craft('fotf:saddle', 'Saddles can be crafted here: 5 leather, 1 iron ingot and 2 string.'),
    ]),
    ('creatures', 'alexs_mobs', 'Alex\'s Mobs', 'alexsmobs:animal_dictionary', [
        text('Around 90 real and fantasy animals: elephants, raccoons, hummingbirds, whales, crows and many more.$(br2)Some can be tamed, and many drop useful items.'),
        craft('alexsmobs:animal_dictionary', 'The $(l)Animal Dictionary$() describes every animal and how to tame it. Craft one or type $(l)/guide animals$().'),
    ]),
    ('creatures', 'critters', 'Critters & Companions', 'crittersandcompanions:dragonfly_wing', [
        text('Small friends to tame by feeding:$(li)Red panda: bamboo$(li)Ferret: raw chicken$(li)Shima enaga: seeds$(li)Snail: carrots$(li)Ladybug: mushrooms$(li)Jumping spider: dragonfly wings (heal it with spider eyes or rotten flesh)'),
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
    ('farming', 'fishing', 'Fishing', 'aquaculture:iron_fishing_rod', [
        spot('aquaculture:iron_fishing_rod', '$(l)Aquaculture$() adds lots of fish, better rods, hooks and bait. $(l)Lili\'s Lucky Lures$() adds fishing gear too.'),
    ]),

    # ---------- Building & Decor ----------
    ('building', 'furniture', 'Furniture', 'handcrafted:oak_chair', [
        text('Three furniture mods, each with its own style:$(li)$(l)Handcrafted$()$(li)$(l)Another Furniture$()$(li)$(l)Let\'s Do Furniture$()$(br2)Search JEI for "chair", "table" or "sofa".'),
    ]),
    ('building', 'decor', 'Decorations', 'supplementaries:jar', [
        text('$(l)Supplementaries$() and $(l)Amendments$(): jars, signposts, flower boxes, wall lanterns and lots of small details.$(br2)$(l)Snowy Spirit$(): sleds, gingerbread and winter decor.'),
        text('$(l)Comforts$(): sleeping bags for camping trips and hammocks for napping through the day.', 'Resting'),
    ]),

    # ---------- Magic ----------
    ('magic', 'irons_spells', 'Iron\'s Spells', 'irons_spellbooks:copper_spell_book', [
        text('The pack\'s spell system. Find spell $(l)scrolls$() in dungeons, put them in a $(l)spell book$(), then cast.$(br2)$(l)V$() casts your spell, $(l)R$() opens the spell wheel.'),
        spot('patchouli:guide_book{"patchouli:book":"irons_spellbooks:iss_guide_book"}', 'The official guidebook explains schools of magic, gear and bosses. Get one with $(l)/guide spells$().'),
    ]),
    ('magic', 'ars_nouveau', 'Ars Nouveau', 'ars_nouveau:worn_notebook', [
        text('Ars magic without the spells: gather $(l)source$(), build its machines, perform rituals and bind familiars and helpers that farm, carry items and craft for you. (Spellcasting is Iron\'s job here.)$(br2)Ars mage armour and mana enchantments still raise your mana.'),
        craft('ars_nouveau:worn_notebook', 'Start with the $(l)Worn Notebook$(): craft one or type $(l)/guide ars$(). It teaches everything, step by step.'),
    ]),
    ('magic', 'which_magic', 'Which Magic?', 'minecraft:enchanted_book', [
        text('$(l)Iron\'s Spells$() is where you cast spells.$(br2)$(l)Ars Nouveau$() is for source, rituals and helpers for your base, and its gear adds to your one mana bar.$(br2)Both feed the Magic skill tree.'),
    ]),

    # ---------- Combat & Gear ----------
    ('combat', 'weapons', 'Weapons & Shields', 'spartanweaponry:iron_longsword', [
        text('$(l)Spartan Weaponry$(): daggers, spears, halberds, longbows and more, in every material.$(br2)$(l)Spartan Shields$(): more shields.'),
        text('Every weapon counts as one or more categories: sword, light, two-handed, polearm, axe, blunt, scythe (hoes too), thrown, bow, crossbow or magic. Skill perks boost their categories.$(br2)Hover a weapon to see its damage with your skills; hold $(l)Shift$() for the breakdown and its categories.', 'Weapon Types'),
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
        text('Four rare cave biomes deep underground: dinosaurs in the $(l)Primordial Caves$(), the sugary $(l)Candy Cavity$(), the deep-sea $(l)Abyssal Chasm$() and the eerie $(l)Forlorn Hollows$().$(br2)They are hard to find. Look up $(l)Cave Tablet$() and $(l)Cave Codex$() in JEI to learn how to track them down.'),
        spot('alexscaves:cave_book', 'The $(l)Cave Book$() describes every cave biome. Type $(l)/guide caves$().'),
    ]),
    ('exploring', 'twilight', 'The Twilight Forest', 'twilightforest:twilight_oak_sapling', [
        text('A magical forest dimension with bosses to beat in order.$(br2)To get there: dig a 2x2 pool of water, surround it with flowers and grass, then throw a $(l)diamond$() into it.'),
    ]),

    # ---------- Travel & Movement ----------
    ('travel', 'parcool', 'Parkour (ParCool)', 'parcool:parcool_guide', [
        text('$(l)ParCool$() turns you into a free runner. Moves use the $(l)stamina$() bar by your hunger bar; it refills when you rest. Your total skill level adds more stamina.$(br2)The basic moves are free from the start. The athletic ones unlock from the $(l)Agility$() skill tree (press $(l)K$()).'),
        text('$(li)$(l)Fast run$(): hold $(l)Ctrl$() while running$(li)$(l)Crawl$(): press $(l)C$()$(li)$(l)Slide$(): press $(l)C$() while running$(li)$(l)Vault$(): run at a low wall or fence$(li)$(l)Fast swim$() and $(l)dive$(): sprint in water, or run off a ledge into deep water', 'Running'),
        text('$(li)$(l)Grab a ledge$(): jump at an edge and hold $(l)right-click$(); move left or right while hanging$(li)$(l)Climb up$(): press jump while hanging$(li)$(l)Hang$(): hold $(l)right-click$() under a bar or beam$(li)$(l)Pole climb$(): walk into a fence, bar or chain and hold forward$(li)$(l)Wall slide$(): hold $(l)right-click$() against a wall while falling', 'Climbing'),
        text('$(li)$(l)Dodge$(): press $(l)Mouse 4$() with a direction key; it goes quite far$(li)$(l)Breakfall$(): press $(l)Mouse 4$() just before you land to roll and take less fall damage$(li)$(l)Zipline$(): craft a zipline (look it up in JEI), jump onto it and hold $(l)right-click$() to ride$(li)$(l)Hide$(): press $(l)C$() in tall grass or hay', 'Landing & Dodging'),
        text('$(l)Freerunner$():$(li)$(l)Wall run$(): sprint-jump along a wall, then press $(l)Mouse 4$()$(li)$(l)Horizontal wall run$(): the same, holding $(l)Mouse 4$()$(li)$(l)Cast away$(): while hanging on a ledge, look away from the wall and jump$(br2)$(l)Featherfall$():$(li)$(l)Skydive$(): press $(l)C$() while falling from high up', 'Agility Moves'),
        text('$(l)Spring Step$():$(li)$(l)Wall jump$(): jump into a wall in mid-air and press jump again$(li)$(l)Long jump$(): sprint for a while, then quickly tap sneak and jump$(li)$(l)Charge jump$(): hold sneak standing still, then jump$(br2)$(l)Double Jump$() (capstone):$(li)Press jump again in mid-air for a second jump with a flip; hold back for a back flip$(li)Normal jumps can flip too: jump while holding back, or jump during a fast run', 'More Agility'),
        text('$(li)Chain moves: slide into a vault, wall run into a wall jump, then breakfall$(li)A roll or breakfall saves you from most falls$(li)Watch your stamina before a long climb$(li)Keys can be changed in $(l)Options > Controls > Key Binds$() under ParCool', 'Tips'),
        craft('parcool:parcool_guide', 'The $(l)ParCool Guide$() item shows every move with animations.'),
    ]),
    ('travel', 'gliding', 'Elytra', 'minecraft:elytra', [
        spot('minecraft:elytra', 'Elytra go in their own slot, so you can still wear a chestplate.'),
    ]),
    ('travel', 'grappling', 'Grappling Hook', 'grapplemod:grapplinghook', [
        spot('grapplemod:grapplinghook', 'Left-click to throw, again to let go. Space jumps off. Hold Shift and W/S to climb the rope. Upgrades come from the $(l)Agility$() skill tree: Long Rope (longer rope), Hookmaster (faster throw, better swing) and Motor Reel (pulls you in).'),
    ]),
    ('travel', 'aircraft', 'Aircraft', 'immersive_aircraft:gyrodyne', [
        spot('immersive_aircraft:gyrodyne', 'Start with a $(l)Gyrodyne$(): it needs no fuel. Later build biplanes and airships. Look them up in JEI.'),
    ]),
    ('travel', 'ships', 'Ships', 'smallships:oak_cog', [
        spot('smallships:oak_cog', '$(l)Small Ships$(): rowboats, cogs, galleys and more, with sails, storage and cannons.'),
    ]),
    ('travel', 'music', 'Music Together', 'mimi:guide', [
        text('$(l)MIMI$(): play instruments with friends. You can even plug in a real MIDI keyboard or play MIDI files.'),
        craft('mimi:guide', 'The $(l)MIMI guide$() explains the instruments. Craft one or type $(l)/guide music$().'),
    ]),

    # ---------- Grove Rules & Server Info ----------
    ('grove', 'time', 'Days & Nights', 'minecraft:clock', [
        text('Days are long here, and sunrises and sunsets last a long time, so enjoy the view!$(br2)The night is skipped when at least half of the players online are sleeping.'),
    ]),
    ('grove', 'mail', 'Mailboxes & Letters', 'fotfmail:letter', [
        spot('endermail:locker', 'Craft a birdhouse $(l)Mailbox$() from 6 planks in a little house shape around a Stamp. The planks pick its wood!$(br2)Right-click it and set an ID, like your name. A letter peeks out when mail arrives.', 'Your Mailbox'),
        spot('fotfmail:letter', 'Craft a $(l)Letter$() (paper + feather) and right-click to write.$(br2)Press $(l)Sign$() and enter your friend\'s mailbox ID as the recipient, then right-click $(l)any$() mailbox. A mail carrier walks over and takes it to them!', 'Letters'),
        spot('endermail:package', 'Craft a $(l)Package$() (chest + stamp), place it and put up to 5 things inside.$(br2)Type a mailbox ID in $(l)Recipient$() and press $(l)Send$(). It lands in their mailbox, and disappears once they empty it.', 'Packages'),
        text('$(li)$(l)Letter$(): paper + feather$(li)$(l)Stamps$(): paper + any dye$(li)$(l)Mailbox$(): 6 planks + stamp$(li)$(l)Package$(): chest + stamp$(li)$(l)Package Controller$(): package + paper + redstone (tracks deliveries)', 'Recipes'),
    ]),
    ('grove', 'land', 'Claims, Pets & Animals', 'minecraft:lead', [
        text('Inside claimed land:$(li)Friendly animals never despawn, even without a name tag (not monsters or fish)$(li)Grappling hooks work for everyone$(li)Only your party can build or open chests'),
        text('Other players can\'t hurt your tamed pets.$(br2)Whales won\'t attack your boats.$(br2)Butterflies, fireflies and critters live in almost every biome. Bring a net and a jar!', 'Friendly Server'),
    ]),
    ('grove', 'commands', 'Handy Commands', 'minecraft:command_block', [
        text('$(li)$(l)/guide$(): a new Field Guide$(li)$(l)/guide <book>$(): other guide books (see $(l)More Guide Books$())$(li)$(l)/nick set <name>$(): change the name others see$(li)$(l)/nick clear$(): back to your real name'),
        text('Delete junk with the $(l)trash slot$() next to your inventory: drop an item in, and it\'s gone for good. Turn the slot on or off in your inventory.', 'Trash Slot'),
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
