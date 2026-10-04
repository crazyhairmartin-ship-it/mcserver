// Items that different mods add as copies of the same thing.
// First item in each group is the one we keep visible in JEI; the rest are hidden, and drops or pickups of them
// turn into the first item (server_scripts/convert_duplicates.js).
// Every recipe that asks for one of them accepts any item in its group
// (see server_scripts/unify_duplicates.js and client_scripts/hide_duplicates.js).
// `tags`: extra forge/c tags every item in the group should share, so tag-based recipes accept all of them.

global.DUPLICATE_GROUPS = [
  { name: 'tomato', items: ['farm_and_charm:tomato', 'farmersdelight:tomato'],
    tags: ['forge:crops/tomato', 'forge:vegetables/tomato', 'forge:vegetables', 'c:crops/tomato', 'c:vegetables'] },
  { name: 'tomato_seeds', items: ['farm_and_charm:tomato_seeds', 'farmersdelight:tomato_seeds'],
    tags: ['forge:seeds/tomato', 'forge:seeds', 'c:seeds'] },
  { name: 'rotten_tomato', items: ['farm_and_charm:rotten_tomato', 'farmersdelight:rotten_tomato'], tags: [] },
  { name: 'onion', items: ['farm_and_charm:onion', 'farmersdelight:onion'],
    tags: ['forge:crops/onion', 'forge:vegetables/onion', 'forge:vegetables', 'c:crops/onion', 'c:vegetables'] },
  { name: 'minced_beef', items: ['farm_and_charm:minced_beef', 'farmersdelight:minced_beef'],
    tags: ['forge:raw_beef', 'c:raw_beef'] },
  { name: 'raw_pasta', items: ['farm_and_charm:raw_pasta', 'farmersdelight:raw_pasta'],
    tags: ['forge:pasta', 'forge:pasta/raw_pasta', 'c:pasta'] },
  { name: 'dough', items: ['farm_and_charm:dough'],
    tags: ['forge:dough', 'c:dough'] },
  { name: 'bacon', items: ['farm_and_charm:bacon', 'farmersdelight:bacon'],
    tags: ['forge:raw_bacon', 'forge:raw_pork', 'c:raw_bacon', 'c:raw_pork'] },
  { name: 'dog_food', items: ['farm_and_charm:dog_food', 'farmersdelight:dog_food'], tags: [] },
  { name: 'onion_soup', items: ['farm_and_charm:onion_soup', 'farmersdelight:onion_soup'], tags: [] },
  { name: 'apple_pie', items: ['bakery:apple_pie', 'farmersdelight:apple_pie'], tags: [] },
  { name: 'dumplings', items: ['brewery:dumplings', 'farmersdelight:dumplings'], tags: [] },
  { name: 'apple_pie_slice', items: ['bakery:apple_pie_slice', 'farmersdelight:apple_pie_slice'], tags: [] },
  { name: 'venison', items: ['naturalist:venison', 'wildernature:venison'], tags: [] },
  { name: 'cooked_venison', items: ['naturalist:cooked_venison', 'wildernature:cooked_venison'], tags: [] },
  { name: 'raw_catfish', items: ['naturalist:catfish', 'alexsmobs:raw_catfish'],
    tags: ['forge:raw_fishes', 'c:raw_fish'] },
  { name: 'cooked_catfish', items: ['naturalist:cooked_catfish', 'alexsmobs:cooked_catfish'], tags: [] },
  { name: 'raw_fish_fillet', items: ['aquaculture:fish_fillet_raw'], tags: [] },
  { name: 'cooked_fish_fillet', items: ['aquaculture:fish_fillet_cooked'], tags: [] },
  { name: 'fish_bones', items: ['aquaculture:fish_bones', 'alexsmobs:fish_bones'], tags: [] },
  { name: 'fish_oil', items: ['alexsmobs:fish_oil', 'wildernature:fish_oil'], tags: [] },
  { name: 'silk', items: ['butterflies:silk', 'crittersandcompanions:silk'], tags: [] },
  { name: 'pearl', items: ['crittersandcompanions:pearl', 'alexscaves:pearl'], tags: [] },
  { name: 'flint_knife', items: ['farmersdelight:flint_knife', 'aquaculture:wooden_fillet_knife', 'aquaculture:stone_fillet_knife'], tags: [] },
  { name: 'iron_knife', items: ['farmersdelight:iron_knife', 'aquaculture:iron_fillet_knife'], tags: [] },
  { name: 'golden_knife', items: ['farmersdelight:golden_knife', 'aquaculture:gold_fillet_knife'], tags: [] },
  { name: 'diamond_knife', items: ['farmersdelight:diamond_knife', 'aquaculture:diamond_fillet_knife'], tags: [] },
  { name: 'canvas', items: ['farmersdelight:canvas', 'furniture:canvas'], tags: [] },
]

// Items with nothing left to do in this pack (hidden from JEI only).
global.HIDDEN_ITEMS = [
  'naturalist:bug_net', // Naturalist butterflies are disabled; Bok's Butterfly Net + Supplementaries jars cover every bug
]
