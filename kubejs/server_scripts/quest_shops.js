// Character shops (tools/quests/src/pack.json characters > "shop"): finishing a character's quests unlocks better
// deals with them, for that player only. Right-clicking a character with nothing for you shows [See deals] when any
// are unlocked; /quest shop <id> lists them and /quest buy <id> <n> buys one (you must be within 8 blocks of them).
// Each offer: {"cost": [{"item", "count"}], "give": {"item", "count", "name"?, "lore"?}, "requires": "chapter:quest"}.
// The generator turns "requires" into quest_id, checked live against FTB Quests.

function shopCharacter(id) {
  return (global.QUEST_CHARACTERS || {})[id]
}

function shopQuestDone(player, questId) {
  if (!questId) return true
  if (!$QuestFile || !$QuestFile.INSTANCE) return false
  try {
    let file = $QuestFile.INSTANCE
    let data = file['getOrCreateTeamData(net.minecraft.world.entity.Entity)'](player)
    let quest = file.getQuest($QuestLong.parseLong(questId, 16))
    return quest != null && data.isCompleted(quest)
  } catch (e) {
    console.warn('quest_shops: could not read quest ' + questId + ': ' + e)
    return false
  }
}

// the offers this player has unlocked, with their index in the character's list
function shopOffers(player, id) {
  let info = shopCharacter(id)
  if (!info || !info.shop) return []
  let out = []
  info.shop.forEach((offer, i) => { if (shopQuestDone(player, offer.quest_id)) out.push({ offer: offer, index: i }) })
  return out
}

function shopItemText(spec) {
  let name = spec.name || String(spec.item).split(':')[1].split('_').map(w => w.charAt(0).toUpperCase() + w.substring(1)).join(' ')
  return (spec.count > 1 ? spec.count + ' ' : '') + name
}

function shopNear(player, id) {
  return player.server.runCommandSilent('execute as ' + player.uuid + ' at @s if entity @e[tag=fq_npc.' + id
    + ',distance=..8]') > 0
}

// called by quest_givers.js after a character's idle line
function shopHint(player, id) {
  if (!shopOffers(player, id).length) return
  player.tell(Text.green('[See deals]').clickRunCommand('/quest shop ' + id).hover('What ' + shopCharacter(id).name + ' can offer you'))
}

function shopShow(player, id) {
  let info = shopCharacter(id)
  let offers = shopOffers(player, id)
  if (!info || !offers.length) {
    player.tell(Text.gray('Nothing on offer for you yet.'))
    return
  }
  player.tell(Text.gold(info.name + "'s deals for you:"))
  offers.forEach(o => {
    let cost = o.offer.cost.map(shopItemText).join(', ')
    player.tell(Text.of([Text.green('[Buy] ').clickRunCommand('/quest buy ' + id + ' ' + o.index).hover('Pay ' + cost),
      Text.white(shopItemText(o.offer.give)), Text.gray(' for ' + cost)]))
  })
}

function shopBuy(player, id, index) {
  let info = shopCharacter(id)
  let offer = info && info.shop ? info.shop[index] : null
  if (!offer || !shopQuestDone(player, offer.quest_id)) {
    player.tell(Text.gray('That deal isn\'t open to you.'))
    return
  }
  if (!shopNear(player, id)) {
    player.tell(Text.gray('You need to be with ' + info.name + ' to buy that.'))
    return
  }
  let server = player.server
  let name = player.username
  let short = offer.cost.find(c => server.runCommandSilent('clear ' + name + ' ' + c.item + ' 0') < c.count)
  if (short) {
    player.tell(Text.red('You need ' + shopItemText(short) + '.'))
    return
  }
  offer.cost.forEach(c => server.runCommandSilent('clear ' + name + ' ' + c.item + ' ' + c.count))
  let give = offer.give
  let nbt = ''
  if (give.name || give.lore) {
    let display = {}
    if (give.name) display.Name = JSON.stringify({ text: give.name, italic: false, color: 'gold' })
    if (give.lore) display.Lore = give.lore.map(l => JSON.stringify({ text: l, italic: false, color: 'gray' }))
    nbt = JSON.stringify({ display: display })
  }
  server.runCommandSilent('give ' + name + ' ' + give.item + nbt + ' ' + give.count)
  player.tell(Text.green('Bought ' + shopItemText(give) + '.'))
}

ServerEvents.commandRegistry(event => {
  let { commands: Commands, arguments: Arguments } = event
  event.register(Commands.literal('quest')
    .then(Commands.literal('shop').then(Commands.argument('id', Arguments.STRING.create(event)).executes(ctx => {
      let player = ctx.source.player
      if (player) shopShow(player, Arguments.STRING.getResult(ctx, 'id'))
      return 1
    })))
    .then(Commands.literal('buy').then(Commands.argument('id', Arguments.STRING.create(event))
      .then(Commands.argument('n', Arguments.INTEGER.create(event)).executes(ctx => {
        let player = ctx.source.player
        if (player) shopBuy(player, Arguments.STRING.getResult(ctx, 'id'), Arguments.INTEGER.getResult(ctx, 'n'))
        return 1
      })))))
})
