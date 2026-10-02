// Ender Mail made cheap enough to use on day one (the stock recipes need ender pearls, slimeballs and 9 iron).
// - Mailbox (locker): 8 planks around a stamp; it looks like a wooden birdhouse here (kubejs/assets/endermail),
//   and its wood comes from where it's placed, not the recipe.
// - Stamp: paper + any dye (4). Packing tape: paper + string (4). Package controller: package + paper + redstone.
// - Package: stock recipe (chest + packing tape), plus an envelope recipe for letters: 3 paper + packing tape.
// - Book and quill (for writing letters): also paper + feather + any dye, no ink sac needed.
ServerEvents.recipes(event => {
  ;['endermail:locker', 'endermail:stamp', 'endermail:packing_tape', 'endermail:package_controller']
    .forEach(id => event.remove({ id: id }))

  event.shaped('endermail:locker', [
    'PPP',
    'PSP',
    'PPP'
  ], {
    P: '#minecraft:planks',
    S: 'endermail:stamp'
  }).id('fotf:mailbox')

  event.shapeless('4x endermail:stamp', ['minecraft:paper', '#forge:dyes']).id('fotf:stamp')
  event.shapeless('4x endermail:packing_tape', ['minecraft:paper', '#forge:string']).id('fotf:packing_tape')
  event.shapeless('endermail:package_controller', ['endermail:package', 'minecraft:paper', 'minecraft:redstone'])
    .id('fotf:package_controller')

  event.shapeless('endermail:package', ['3x minecraft:paper', 'endermail:packing_tape']).id('fotf:envelope')
  event.shapeless('minecraft:writable_book', ['minecraft:paper', 'minecraft:feather', '#forge:dyes']).id('fotf:quick_book_and_quill')
})
