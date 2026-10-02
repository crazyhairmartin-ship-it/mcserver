// Ender Mail's locker looks like a wooden birdhouse here (kubejs/assets/endermail), so it's made from planks
// instead of 8 iron ingots. Any planks work; the birdhouse's wood comes from where it's placed, not the recipe.
ServerEvents.recipes(event => {
  event.remove({ id: 'endermail:locker' })
  event.shaped('endermail:locker', [
    'PPP',
    'PSP',
    'PPP'
  ], {
    P: '#minecraft:planks',
    S: 'endermail:stamp'
  }).id('fotf:mailbox')
})
