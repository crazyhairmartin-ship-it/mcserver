// Quest givers: villagers, mobs, dropped letters and other items hand out FTB Quests quests.
// The list of givers is generated (quest_givers.generated.js, from tools/quests/src); this file is the behaviour.
//
// - Sneak + right-click a villager or mob: if it has a quest for you (right profession / mob type / name, an
//   organisation's representative, and you've finished what it requires), it says its lines in chat with a
//   clickable [Accept]. Accepting adds the quest's stage, which completes the quest's hidden first task, so the
//   quest appears in your book. Named characters (placed with /questnpc, see quest_npcs.js) answer a plain
//   right-click.
// - Pools: an organisation's side quests can be a pool. Each representative offers one quest from it, picked by
//   that villager's own identity, so different villages hand out different work.
// - "talk" tasks: sneak + right-click the right villager or mob while on that quest to finish the task.
// - Drop givers: the listed mobs sometimes drop a quest item when you kill them; right-clicking it shows the lines
//   and [Accept]. Item givers work the same for an item you find any other way.
// - "drop" tasks: while a quest is open, the listed mobs can drop its unique quest item (a trophy, a stolen
//   heirloom...), which the quest then asks for.
// Stages are plain player tags (FTB Library's stage provider), so `/tag @s list` shows them and `/tag @s remove`
// resets one.

let $QuestCompoundTag = Java.loadClass('net.minecraft.nbt.CompoundTag')
let $QuestStageTask = null
let $QuestFile = null
let $QuestLong = Java.loadClass('java.lang.Long')
try {
  $QuestStageTask = Java.loadClass('dev.ftb.mods.ftbquests.quest.task.StageTask')
  $QuestFile = Java.loadClass('dev.ftb.mods.ftbquests.quest.ServerQuestFile')
} catch (e) {
  console.warn('quest_givers: FTB Quests not found; stages are added but no quest will notice')
}

const QUEST_OFFER_MS = 5 * 60 * 1000       // [Accept] works for 5 minutes after the offer
const QUEST_DROP_RETRY_MS = 20 * 60 * 1000  // a lost quest item can drop again after 20 minutes

function questGivers() {
  return global.QUEST_GIVERS || []
}

function questHasAll(player, stages) {
  return stages.every(stage => player.tags.contains(stage))
}

// A talk step only answers while its quest is open: earlier quests done, the quest itself not finished, and (for a
// quest that's discovered or handed out) its first task done. Asked of FTB Quests directly.
function questOpen(player, giver) {
  if (!giver.quest_id || !$QuestFile || !$QuestFile.INSTANCE) return true
  try {
    let file = $QuestFile.INSTANCE
    let data = file.getOrCreateTeamData(player)
    let quest = file.getQuest($QuestLong.parseLong(giver.quest_id, 16))
    if (!quest || !data.canStartTasks(quest) || data.isCompleted(quest)) return false
    if (giver.open_task) {
      let first = file.getTask($QuestLong.parseLong(giver.open_task, 16))
      if (first && !data.isCompleted(first)) return false
    }
    if (giver.prev_tasks) {
      for (let i = 0; i < giver.prev_tasks.length; i++) {
        let prev = file.getTask($QuestLong.parseLong(giver.prev_tasks[i], 16))
        if (prev && !data.isCompleted(prev)) return false
      }
    }
    return true
  } catch (e) {
    console.warn('quest_givers: could not read quest ' + giver.quest + ': ' + e)
    return false
  }
}

function questAddStage(player, stage) {
  player.addTag(stage)
  if ($QuestStageTask) {
    try {
      $QuestStageTask.checkStages(player)
    } catch (e) {
      console.warn('quest_givers: could not tell FTB Quests about stage ' + stage + ': ' + e)
    }
  }
}

function questOffers(player) {
  let data = player.persistentData
  if (!data.contains('fqOffers')) data.put('fqOffers', new $QuestCompoundTag())
  return data.getCompound('fqOffers')
}

function questSay(player, speaker, lines) {
  lines.forEach(line => {
    player.tell(speaker ? Text.of([Text.gold(speaker + ': '), Text.of(line)]) : Text.italic(line).gray())
  })
}

function questOffer(player, giver, speaker) {
  questSay(player, speaker, giver.lines)
  questOffers(player).putLong(giver.stage, Date.now())
  player.tell(Text.of([
    Text.green('[' + giver.accept + ']').clickRunCommand('/quest accept ' + giver.stage).hover('Start this quest'),
    Text.gray('  (click)')
  ]))
}

function questProfession(target) {
  if (String(target.type) != 'minecraft:villager') return ''
  return String(target.nbt.getCompound('VillagerData').getString('profession'))
}

function questMatches(giver, target) {
  if (giver.match == 'org') {
    // a representative: a villager with one of the organisation's professions, or a mob of a listed type (guards)
    let type = String(target.type)
    return giver.professions.indexOf(type) >= 0 || giver.professions.indexOf(questProfession(target)) >= 0
  }
  if (giver.match == 'character') {
    return target.tags.contains('fq_npc.' + giver.character)
  }
  if (giver.match == 'villager') {
    if (String(target.type) != 'minecraft:villager') return false
    if (giver.profession == 'any') return true
    let data = target.nbt.getCompound('VillagerData')
    return String(data.getString('profession')) == giver.profession
  }
  if (giver.match == 'entity') {
    if (String(target.type) != giver.entity) return false
    return !giver.named || (target.customName && String(target.customName.string) == giver.named)
  }
  return false
}

// A stable number for a villager + quest, so each representative prefers its own quests from a pool.
function questHash(text) {
  let h = 0
  for (let i = 0; i < text.length; i++) h = (h * 31 + text.charCodeAt(i)) | 0
  return h
}

function questSpeaker(giver, target) {
  if (giver.name) return giver.name
  let name = String(target.displayName.string)
  return giver.org_name ? name + ' (' + giver.org_name + ')' : name
}

// What this villager or mob offers this player now: storyline quests first, then one quest from each pool.
function questOfferFor(player, target) {
  let candidates = questGivers().filter(g => (g.type == 'villager' || g.type == 'entity' || g.type == 'org'
    || g.type == 'character') && questMatches(g, target) && questHasAll(player, g.requires)
    && !player.tags.contains(g.stage))
  let story = candidates.find(g => !g.pool)
  if (story) return story
  let uuid = String(target.uuid)
  candidates.sort((a, b) => questHash(uuid + a.stage) - questHash(uuid + b.stage))
  return candidates[0]
}

// Talk to villagers and mobs.
ItemEvents.entityInteracted(event => {
  let { player, target } = event
  if (String(event.hand) != 'MAIN_HAND' || player.level.clientSide) return
  if (target.tags.contains('fq_enc')) return            // encounters are handled in quest_npcs.js
  let character = target.tags.contains('fq_npc')
  if (!player.crouching && !character) return
  let givers = questGivers()
  // Quests in progress first: a talk task for this villager or mob.
  let talk = givers.find(g => g.type == 'talk' && questMatches(g, target) && questHasAll(player, g.requires)
    && !player.tags.contains(g.stage) && questOpen(player, g))
  if (talk) {
    questSay(player, questSpeaker(talk, target), talk.lines)
    questAddStage(player, talk.stage)
    player.tell(Text.yellow('Quest updated.'))
    event.cancel()
    return
  }
  let offer = questOfferFor(player, target)
  if (offer) {
    questOffer(player, offer, questSpeaker(offer, target))
    event.cancel()
    return
  }
  if (character) {
    // named characters never open a trading screen; with nothing for you they say an idle line
    let info = (global.QUEST_CHARACTERS || {})[questCharacterId(target)] || {}
    let idle = info.idle || ['...']
    questSay(player, String(target.displayName.string), [idle[Math.floor(Math.random() * idle.length)]])
    event.cancel()
  }
})

function questCharacterId(target) {
  let found = ''
  target.tags.forEach(tag => {
    let t = String(tag)
    if (t.indexOf('fq_npc.') == 0) found = t.substring(7)
  })
  return found
}

// Quest items from drops (or found anywhere) start quests when read.
ItemEvents.rightClicked(event => {
  let { player, item } = event
  if (player.level.clientSide) return
  let id = String(item.id)
  let giver = questGivers().find(g => (g.type == 'drop' || g.type == 'item') && g.item == id)
  if (!giver) return
  if (player.tags.contains(giver.stage)) {
    player.tell(Text.gray('You already know what this is about. Check your quest book.'))
  } else if (!questHasAll(player, giver.requires)) {
    player.tell(Text.gray("You can't make sense of this yet."))
  } else {
    questOffer(player, giver, giver.name)
  }
  event.cancel()
})

// Mobs drop quest items: quest starters for players who don't have that quest yet, and unique quest drops
// ("drop" tasks) only while their quest is open.
EntityEvents.death(event => {
  let { entity, source } = event
  let player = source.player
  if (!player || entity.level.clientSide) return
  let type = String(entity.type)
  questGivers().forEach(giver => {
    if (giver.type == 'task_drop' && giver.from.indexOf(type) >= 0 && questHasAll(player, giver.requires)
      && Math.random() < giver.chance && questOpen(player, giver)) {
      entity.block.popItem(Item.of(giver.item))
    }
    if (giver.type != 'drop' || giver.from.indexOf(type) < 0) return
    if (player.tags.contains(giver.stage) || !questHasAll(player, giver.requires)) return
    if (Math.random() >= giver.chance) return
    let dropped = player.persistentData.getCompound('fqDropped')
    if (Date.now() - dropped.getLong(giver.stage) < QUEST_DROP_RETRY_MS) return
    dropped.putLong(giver.stage, Date.now())
    player.persistentData.put('fqDropped', dropped)
    entity.block.popItem(Item.of(giver.item))
  })
})

// /quest accept <stage>: what the [Accept] button runs. Only works for an offer made to you in the last 5 minutes.
ServerEvents.commandRegistry(event => {
  let { commands: Commands, arguments: Arguments } = event
  event.register(Commands.literal('quest')
    .then(Commands.literal('accept')
      .then(Commands.argument('stage', Arguments.STRING.create(event))
        .executes(ctx => {
          let player = ctx.source.player
          if (!player) return 0
          let stage = Arguments.STRING.getResult(ctx, 'stage')
          let giver = questGivers().find(g => g.stage == stage && g.type != 'talk' && g.type != 'encounter'
            && g.type != 'timed' && g.type != 'task_drop')
          let offers = questOffers(player)
          if (!giver || !offers.contains(stage) || Date.now() - offers.getLong(stage) > QUEST_OFFER_MS) {
            player.tell(Text.gray('That offer has expired. Talk to them again.'))
            return 0
          }
          offers.remove(stage)
          if (player.tags.contains(stage)) return 0
          if ((giver.type == 'drop' || giver.type == 'item') && giver.consume) {
            let hand = [player.mainHandItem, player.offHandItem].find(stack => String(stack.id) == giver.item)
            if (!hand) {
              player.tell(Text.gray('Hold the item and try again.'))
              return 0
            }
            hand.shrink(1)
          }
          questAddStage(player, stage)
          player.tell(Text.yellow('New quest! Open your quest book to see it.'))
          return 1
        }))))
})
