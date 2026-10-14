// Quest characters on the live server ahead of the quest system: place them in Reece now, and the full quest scripts
// (FTB Quests, on the quest branch) take them over at release because they use the same tags (fq_npc, fq_npc.<id>).
// DELETE THIS FILE when the quest system is merged into main: quest_npcs.js and quest_givers.js replace it.
// /questnpc place <id> (op): put the character where you stand, facing your way (placing again moves them)
// /questnpc remove <id>, /questnpc list. Right-click a character for an idle line; they never open a trade screen.

const LIVE_QUEST_CHARACTERS = {
  "maren": {
    "name": "Elder Maren",
    "profession": "minecraft:librarian",
    "idle": [
      "Reece is small, but it's never quiet for long.",
      "Read the Field Guide when you're unsure. I wrote half of it."
    ]
  },
  "wren": {
    "name": "Sister Wren",
    "profession": "minecraft:cleric",
    "idle": [
      "The forest still hasn't answered me.",
      "Light a candle at the shrine if you pass it."
    ]
  },
  "edda": {
    "name": "Old Edda",
    "profession": "minecraft:nitwit",
    "idle": [
      "Everyone comes back to the graveyard eventually. Some come back sooner.",
      "Mind how you go."
    ]
  },
  "hale": {
    "name": "Captain Hale",
    "entity": "guardvillagers:guard",
    "idle": [
      "Watch the tree line at dusk.",
      "Keep your shield up and your back to a wall."
    ]
  },
  "dagna": {
    "name": "Guildmaster Dagna Holt",
    "profession": "minecraft:toolsmith",
    "idle": [
      "A good pick and a better lantern. That's all a miner needs.",
      "Mind the gravel."
    ]
  },
  "marta": {
    "name": "Marta Furrow",
    "profession": "minecraft:farmer",
    "idle": [
      "Rain's coming. The barley knows it before I do.",
      "There's always work in the fields."
    ]
  },
  "halloway": {
    "name": "Commodore Marlow Halloway",
    "profession": "minecraft:fisherman",
    "idle": [
      "The society meets on the jetty. Bring a rod.",
      "Tide's turning. Good time to fish."
    ]
  },
  "bess": {
    "name": "Bess Copperpot",
    "profession": "minecraft:butcher",
    "idle": [
      "Stew's on. Pull up a stool.",
      "Nobody leaves my tavern hungry."
    ]
  },
  "rue": {
    "name": "Mother Rue",
    "profession": "minecraft:cleric",
    "idle": [
      "Every weed is a medicine to someone.",
      "Pick only what you need."
    ]
  },
  "bram": {
    "name": "Bram the Baker",
    "profession": "minecraft:farmer",
    "idle": [
      "Smell that? No, nor do I. No flour, no bread.",
      "Mind the oven, it bites."
    ]
  },
  "hesk": {
    "name": "Miller Hesk",
    "profession": "minecraft:farmer",
    "idle": [
      "The mill turns when the wind does.",
      "Grain in, flour out. Usually."
    ]
  },
  "nell": {
    "name": "Nell the Weaver",
    "profession": "minecraft:shepherd",
    "idle": [
      "Straw, canvas, wool. Everything starts as something plainer.",
      "Don't touch the loom."
    ]
  },
  "olsen": {
    "name": "Olsen the Carpenter",
    "profession": "minecraft:mason",
    "idle": [
      "Measure twice. Then measure again, because you got it wrong.",
      "Only the old birch will do."
    ]
  },
  "silas": {
    "name": "Silas Pike",
    "profession": "minecraft:fisherman",
    "idle": [
      "Back again? I'll still out-fish you."
    ]
  }
}

function liveNpcId(target) {
  let found = ''
  target.tags.forEach(tag => {
    let t = String(tag)
    if (t.indexOf('fq_npc.') == 0) found = t.substring(7)
  })
  return found
}

ServerEvents.commandRegistry(event => {
  let { commands: Commands, arguments: Arguments } = event
  event.register(Commands.literal('questnpc')
    .requires(src => src.hasPermission(2))
    .then(Commands.literal('place').then(Commands.argument('id', Arguments.STRING.create(event)).executes(ctx => {
      let player = ctx.source.player
      let id = Arguments.STRING.getResult(ctx, 'id')
      let info = LIVE_QUEST_CHARACTERS[id]
      if (!player || !info) {
        ctx.source.sendSystemMessage(Text.red('No character "' + id + '". /questnpc list shows them.'))
        return 0
      }
      ctx.source.server.runCommandSilent('kill @e[tag=fq_npc.' + id + ']')
      let entity = player.level.createEntity(info.entity || 'minecraft:villager')
      entity.setPos(player.x, player.y, player.z)
      let nbt = { CustomName: JSON.stringify({ text: info.name }), CustomNameVisible: true, PersistenceRequired: true,
        Invulnerable: true, NoAI: true, Silent: true }
      if (info.profession) nbt.VillagerData = { profession: info.profession, level: 5, type: 'minecraft:plains' }
      entity.mergeNbt(nbt)
      entity.addTag('fq_npc')
      entity.addTag('fq_npc.' + id)
      entity.spawn()
      ctx.source.server.runCommandSilent('tp ' + entity.uuid + ' ' + player.x + ' ' + player.y + ' ' + player.z
        + ' ' + player.yaw + ' 0')
      player.tell(Text.green('Placed ' + info.name + '. Place again to move them.'))
      return 1
    })))
    .then(Commands.literal('remove').then(Commands.argument('id', Arguments.STRING.create(event)).executes(ctx => {
      let id = Arguments.STRING.getResult(ctx, 'id')
      ctx.source.server.runCommandSilent('kill @e[tag=fq_npc.' + id + ']')
      ctx.source.sendSystemMessage(Text.of('Removed every "' + id + '" character in loaded chunks.'))
      return 1
    })))
    .then(Commands.literal('list').executes(ctx => {
      ctx.source.sendSystemMessage(Text.of(Object.keys(LIVE_QUEST_CHARACTERS)
        .map(k => k + ' (' + LIVE_QUEST_CHARACTERS[k].name + ')').join(', ')))
      return 1
    })))
})

ItemEvents.entityInteracted(event => {
  let { player, target } = event
  if (String(event.hand) != 'MAIN_HAND' || player.level.clientSide || !target.tags.contains('fq_npc')) return
  let info = LIVE_QUEST_CHARACTERS[liveNpcId(target)] || {}
  let idle = info.idle || ['...']
  player.tell(Text.of([Text.gold(String(target.displayName.string) + ': '), Text.of(idle[Math.floor(Math.random() * idle.length)])]))
  event.cancel()
})
