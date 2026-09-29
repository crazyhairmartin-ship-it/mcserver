// Friends of the Forest Field Guide (Patchouli book in kubejs/data + kubejs/assets).
// New players get it (plus the Unicorn Guidebook) on first login; /guide and /guide unicorn give new copies.

let $GuideCompoundTag = Java.loadClass('net.minecraft.nbt.CompoundTag')

function fieldGuide() {
  return Item.of('patchouli:guide_book', { 'patchouli:book': 'kubejs:fotf_field_guide' })
}

function unicornGuide() {
  return Item.of('patchouli:guide_book', { 'patchouli:book': 'ultimate_unicorn_mod:unicorn_guide' })
}

PlayerEvents.loggedIn(event => {
  let guideData = event.server.persistentData
  if (!guideData.contains('fieldGuideGiven')) guideData.put('fieldGuideGiven', new $GuideCompoundTag())
  let givenTo = guideData.getCompound('fieldGuideGiven')
  let guideUuid = String(event.player.uuid)
  if (givenTo.contains(guideUuid)) return

  event.player.give(fieldGuide())
  event.player.give(unicornGuide())
  givenTo.putBoolean(guideUuid, true)
  event.player.tell(Text.green('Welcome to the forest, friend! Check your Field Guide. Lost it? Type /guide'))
})

ServerEvents.commandRegistry(event => {
  let Commands = event.commands
  event.register(Commands.literal('guide')
    .executes(ctx => {
      ctx.source.playerOrException.give(fieldGuide())
      return 1
    })
    .then(Commands.literal('unicorn').executes(ctx => {
      ctx.source.playerOrException.give(unicornGuide())
      return 1
    })))
})
