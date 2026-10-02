// Ender Mail made cheap enough to use on day one (the stock recipes need ender pearls, slimeballs and 9 iron).
// - Mailbox (locker): 6 planks of one wood in a little house shape around a stamp. The fotfmail add-on gives mailboxes a "wood" block
//   state, so the planks pick the birdhouse's wood (global.MAILBOX_WOODS, startup_scripts/mailbox_woods.js).
// - Letter (fotfmail add-on): paper + feather. Write, sign with a friend's mailbox ID, right-click a mailbox.
// - Stamp: paper + any dye (4). Packing tape: paper + string (4). Package controller: package + paper + redstone.
// - Package: stock recipe (chest + packing tape), plus an envelope recipe: 3 paper + packing tape.
// - Book and quill: also paper + feather + any dye, no ink sac needed.
ServerEvents.recipes(event => {
  ;['endermail:locker', 'endermail:stamp', 'endermail:packing_tape', 'endermail:package', 'endermail:package_controller']
    .forEach(id => event.remove({ id: id }))

  global.MAILBOX_WOODS.forEach(([wood, planks]) => {
    event.shaped(Item.of('endermail:locker', { BlockStateTag: { wood: wood } }), [
      ' P ',
      'PSP',
      'PPP'
    ], {
      P: planks,
      S: 'endermail:stamp'
    }).id(`fotf:mailbox/${wood}`)
  })

  event.shapeless('fotfmail:letter', ['minecraft:paper', 'minecraft:feather']).id('fotf:letter')
  event.shapeless('4x endermail:stamp', ['minecraft:paper', '#forge:dyes']).id('fotf:stamp')
  event.shapeless('endermail:package_controller', ['endermail:package', 'minecraft:paper', 'minecraft:redstone'])
    .id('fotf:package_controller')
  event.shapeless('endermail:package', ['#forge:chests/wooden', 'endermail:stamp']).id('fotf:package')
  event.shapeless('minecraft:writable_book', ['minecraft:paper', 'minecraft:feather', '#forge:dyes']).id('fotf:quick_book_and_quill')
})
