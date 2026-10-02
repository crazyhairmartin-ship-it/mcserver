// Saddles are craftable (vanilla has no recipe): 5 leather, 1 iron ingot, 2 string.
ServerEvents.recipes(event => {
  event.shaped('minecraft:saddle', [
    'LLL',
    'LIL',
    'S S'
  ], {
    L: 'minecraft:leather',
    I: '#forge:ingots/iron',
    S: '#forge:string'
  }).id('fotf:saddle')
})
