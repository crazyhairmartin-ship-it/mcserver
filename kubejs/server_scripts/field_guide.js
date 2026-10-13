// Friends of the Forest Field Guide (external Patchouli book in pack/patchouli_books/, id patchouli:fotf_field_guide).
// New players get it on first login (the only starting book). /guide gives a copy; /guide <name> gives a mod's own
// guide book (see GUIDE_BOOKS).

let $GuideCompoundTag = Java.loadClass('net.minecraft.nbt.CompoundTag')

function fieldGuide() {
  return Item.of('patchouli:guide_book', { 'patchouli:book': 'patchouli:fotf_field_guide' })
}

function patchouliBook(bookId) {
  return () => Item.of('patchouli:guide_book', { 'patchouli:book': bookId })
}

// /guide <name> -> that mod's guide book. (Tinkers' books are trimmed along with the rest of Tinkers.)
let GUIDE_BOOKS = {
  unicorn: patchouliBook('ultimate_unicorn_mod:unicorn_guide'),
  spells: patchouliBook('irons_spellbooks:iss_guide_book'),
  animals: () => Item.of('alexsmobs:animal_dictionary'),
  caves: () => Item.of('alexscaves:cave_book'),
  cookbook: patchouliBook('patchouli:fotf_cookbook'),
}

PlayerEvents.loggedIn(event => {
  let guideData = event.server.persistentData
  if (!guideData.contains('fieldGuideGiven')) guideData.put('fieldGuideGiven', new $GuideCompoundTag())
  let givenTo = guideData.getCompound('fieldGuideGiven')
  let guideUuid = String(event.player.uuid)
  if (givenTo.contains(guideUuid)) return

  event.player.give(fieldGuide())
  givenTo.putBoolean(guideUuid, true)
  event.player.tell(Text.green('Welcome to the forest, friend! Check your Field Guide. Lost it? Type /guide'))
})

ServerEvents.commandRegistry(event => {
  let Commands = event.commands
  let guide = Commands.literal('guide').executes(ctx => {
    ctx.source.playerOrException.give(fieldGuide())
    return 1
  })
  Object.keys(GUIDE_BOOKS).forEach(name => {
    guide.then(Commands.literal(name).executes(ctx => {
      ctx.source.playerOrException.give(GUIDE_BOOKS[name]())
      return 1
    }))
  })
  event.register(guide)
})
