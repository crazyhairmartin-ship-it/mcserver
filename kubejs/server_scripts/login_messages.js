// Login messages.
// - Returning players: "Welcome back, <name>!" to them, and a nudge to everyone else to say hi.
//   (First-time players get the Field Guide welcome from field_guide.js instead.)
// - Unspent skill points: a short reminder that K opens the skills menu.
// - One-time notices: shown once per player on their next login, tracked in server persistentData.
//   Bump NOTICE_ID to show a new notice to everyone once.

let $SkillsAPI = Java.loadClass('net.puffish.skillsmod.api.SkillsAPI')
let $NoticeCompoundTag = Java.loadClass('net.minecraft.nbt.CompoundTag')

let NOTICE_ID = 'keybinds_shaders_2026_10'

function hasUnspentSkillPoints(player) {
  let unspent = false
  $SkillsAPI.streamCategories().toList().forEach(category => {
    if (category.getPointsLeft(player) > 0) unspent = true
  })
  return unspent
}

function noticeSeen(server, player) {
  let data = server.persistentData
  if (!data.contains('fotfNotices')) data.put('fotfNotices', new $NoticeCompoundTag())
  let notices = data.getCompound('fotfNotices')
  if (!notices.contains(NOTICE_ID)) notices.put(NOTICE_ID, new $NoticeCompoundTag())
  let seen = notices.getCompound(NOTICE_ID)
  let uuid = String(player.uuid)
  if (seen.contains(uuid)) return true
  seen.putBoolean(uuid, true)
  return false
}

function showKeybindNotice(server, player) {
  let name = player.username
  server.runCommandSilent(`title ${name} times 10 120 30`)
  server.runCommandSilent(`title ${name} subtitle {"text":"Options > Controls > Key Binds > Reset All","color":"yellow"}`)
  server.runCommandSilent(`title ${name} title {"text":"RESET YOUR KEYBINDS","color":"red","bold":true}`)
  server.runCommandSilent(`playsound minecraft:block.note_block.pling master ${name} ~ ~ ~ 1 1`)

  let bar = Text.gold('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━').bold(true)
  player.tell(bar)
  player.tell(Text.red('⚠ RESET YOUR KEYBINDS ⚠').bold(true))
  player.tell(Text.yellow('The pack\'s keys were cleaned up. Go to ')
    .append(Text.white('Options > Controls > Key Binds').bold(true))
    .append(Text.yellow(' and press '))
    .append(Text.white('Reset All').bold(true))
    .append(Text.yellow(' to get the new layout.')))
  player.tell(bar)
  player.tell(Text.aqua('✨ New: Complementary shaders! ')
    .append(Text.gray('Turn them on in Options > Video Settings > Shader Packs if you\'d like (F7 toggles). Skip them on slower computers.')))
}

PlayerEvents.loggedIn(event => {
  let player = event.player
  let server = event.server
  let returning = player.stats.getPlayTime() > 0

  if (!returning) {
    // Brand-new players already start with the new keys; don't show them the one-time notice later.
    noticeSeen(server, player)
    return
  }

  let showNotice = !noticeSeen(server, player)
  let name = player.username

  // Give the client a moment to finish loading so titles and chat aren't missed.
  server.scheduleInTicks(40, () => {
    let online = server.getPlayer(name)
    if (!online) return

    online.tell(Text.green(`Welcome back, ${name}!`))
    server.players.forEach(other => {
      if (String(other.uuid) != String(online.uuid))
        other.tell(Text.yellow(`${name} is back in the forest. Give them a welcome!`))
    })

    if (hasUnspentSkillPoints(online)) {
      online.tell(Text.lightPurple('★ You have unspent skill points! Press ')
        .append(Text.white('K').bold(true))
        .append(Text.lightPurple(' to open the skills menu.')))
    }

    if (showNotice) showKeybindNotice(server, online)
  })
})
