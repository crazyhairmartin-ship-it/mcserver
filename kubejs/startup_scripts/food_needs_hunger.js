// Solid food needs you to be hungry, like vanilla food. The Let's Do mods (and a few other food mods) mark most of
// their food as edible when full; these go back to normal. Drinks (wines, teas, coffee, ciders, fizzes, punch,
// syrup) stay drinkable any time, as do magic/effect foods (golden apples, chorus fruit, Farmer's Delight's cider,
// popsicle and custard, Supplementaries, Alex's Caves/Mobs, Cataclysm, torchberries). Dylan, 2026-11-01.
// List taken from a live probe of every food with canAlwaysEat(); re-check after adding food mods.
const FOOD_NEEDS_HUNGER = [
  'bakery:apple_cupcake', 'bakery:apple_pie_slice', 'bakery:baguette', 'bakery:braided_bread', 'bakery:bread',
  'bakery:bread_with_jam', 'bakery:bun', 'bakery:bundt_cake_slice', 'bakery:chocolate_cake_slice',
  'bakery:chocolate_gateau_slice', 'bakery:chocolate_glazed_cookie', 'bakery:chocolate_tart_slice',
  'bakery:chocolate_truffle', 'bakery:cornet', 'bakery:croissant', 'bakery:crusty_bread', 'bakery:glowberry_pie_slice',
  'bakery:grilled_bacon_sandwich', 'bakery:grilled_salmon_sandwich', 'bakery:jam_roll', 'bakery:linzer_tart_slice',
  'bakery:misslilitu_biscuit', 'bakery:pudding_slice', 'bakery:sandwich', 'bakery:strawberry_cake_slice',
  'bakery:strawberry_cupcake', 'bakery:strawberry_glazed_cookie', 'bakery:sweetberry_cake_slice',
  'bakery:sweetberry_cupcake', 'bakery:sweetberry_glazed_cookie', 'bakery:toast', 'bakery:vegetable_sandwich',
  'bakery:waffle',
  'brewery:dumplings', 'brewery:fried_chicken', 'brewery:half_chicken', 'brewery:mashed_potatoes', 'brewery:pork_knuckle',
  'brewery:potato_salad', 'brewery:pretzel', 'brewery:sausage',
  'candlelight:beef_tartare', 'candlelight:beetroot_salad', 'candlelight:chicken_teriyaki', 'candlelight:chocolate_mousse',
  'candlelight:fresh_garden_salad', 'candlelight:harvest_plate', 'candlelight:omelet', 'candlelight:pasta_with_lettuce',
  'candlelight:salad', 'candlelight:tomato_mozzarella_salad',
  'cornexpansion:buttery_popcorn', 'cornexpansion:candied_popcorn', 'cornexpansion:cheesy_popcorn', 'cornexpansion:popcorn',
  'cornexpansion:sweet_popcorn',
  'lilis_lucky_lures:cooked_cod_meal', 'lilis_lucky_lures:grilled_tropical_fish', 'lilis_lucky_lures:puffer_plater',
  'lilis_lucky_lures:salmon_rolls', 'lilis_lucky_lures:uncooked_cod_meal', 'lilis_lucky_lures:uncooked_puffer_plater',
  'lilis_lucky_lures:uncooked_tropical_fish',
  'rainbowreef:choco_ray_muffin', 'rainbowreef:clownfish_cupcake', 'rainbowreef:dried_seahorse', 'rainbowreef:jelly_sandwich',
  'rainbowreef:jelly_tart', 'rainbowreef:jellyfish_jelly', 'rainbowreef:pipefish_sushi', 'rainbowreef:raw_boxfish',
  'twilightforest:meef_stroganoff'
]

ItemEvents.modification(event => {
  FOOD_NEEDS_HUNGER.forEach(id => {
    event.modify(id, item => {
      item.foodProperties = food => {
        food.alwaysEdible(false)
      }
    })
  })
})
