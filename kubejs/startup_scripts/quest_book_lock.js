// While an op has run /quests off (server_scripts/quest_givers.js), players without op get the "fq_paused" stage and
// the FTB Quests book won't open for them (the sidebar button, keybind and book item all do nothing). Client only.
if (Platform.isClientEnvironment()) {
  let $LockScreenWrapper = Java.loadClass('dev.ftb.mods.ftblibrary.ui.IScreenWrapper')
  let $LockQuestScreen = Java.loadClass('dev.ftb.mods.ftbquests.client.gui.quests.QuestScreen')
  let $LockStages = Java.loadClass('dev.latvian.mods.kubejs.stages.Stages')
  let $LockMinecraft = Java.loadClass('net.minecraft.client.Minecraft')

  ForgeEvents.onEvent('net.minecraftforge.client.event.ScreenEvent$Opening', event => {
    try {
      let screen = event.getNewScreen()
      if (!(screen instanceof $LockScreenWrapper) || !(screen.getGui() instanceof $LockQuestScreen)) return
      let player = $LockMinecraft.getInstance().player
      if (player && $LockStages.get(player).has('fq_paused')) {
        event.setCanceled(true)
        player.displayClientMessage(Text.gray('Quests are resting for now.'), true)
      }
    } catch (e) {
      console.error('quest_book_lock: ' + e)
    }
  })
}
