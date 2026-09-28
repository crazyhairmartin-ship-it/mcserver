// Makes duplicate items from different mods interchangeable in recipes.
// Groups are defined in startup_scripts/duplicate_groups.js.

ServerEvents.tags('item', event => {
  global.DUPLICATE_GROUPS.forEach(group => {
    event.add('kubejs:unified/' + group.name, group.items)
    group.tags.forEach(tag => event.add(tag, group.items))
  })
})

ServerEvents.recipes(event => {
  global.DUPLICATE_GROUPS.forEach(group => {
    let groupTag = '#kubejs:unified/' + group.name
    group.items.forEach(itemId => event.replaceInput({ input: itemId }, itemId, groupTag))
  })
})
