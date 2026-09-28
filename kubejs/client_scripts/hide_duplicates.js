// Hides the extra copies of duplicate items from JEI (the first item of each group stays visible).
// Groups are defined in startup_scripts/duplicate_groups.js.

JEIEvents.hideItems(event => {
  global.DUPLICATE_GROUPS.forEach(group => group.items.slice(1).forEach(itemId => event.hide(itemId)))
  global.HIDDEN_ITEMS.forEach(itemId => event.hide(itemId))
})
