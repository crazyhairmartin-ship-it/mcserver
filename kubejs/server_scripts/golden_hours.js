// Longer sunrises and sunsets.
// Hourglass only has two speeds, and it switches from "day" to "night" halfway through sunset
// (tick 12500) and back halfway through sunrise (tick 23500). This script retunes both speeds
// through /hourglass config as the clock moves, so the whole golden hour runs slowly while
// midday and the dark part of the night keep their normal lengths.
// Speed = in-game ticks per real tick (vanilla 1.0, lower = slower).

let GOLDEN_SPEED = 0.2 // sunrise and sunset, 5x longer than vanilla
let MIDDAY_SPEED = 0.333 // rest of the day, 3x longer than vanilla
let DEEP_NIGHT_SPEED = 1.0 // dark night, same as vanilla

// Day-time ticks (0-23999). Sunset glow starts ~11000, last light ~13800; first light ~22200, sun fully up ~1000.
function isGolden(t) {
  return (t >= 11000 && t < 13800) || t >= 22200 || t < 1000
}

let appliedDaySpeed = null
let appliedNightSpeed = null

ServerEvents.tick(event => {
  let server = event.server
  if (server.tickCount % 20 != 0) return

  let t = Number(server.overworld().getDayTime() % 24000)
  let golden = isGolden(t)
  // Hourglass uses daySpeed for 23500-12500 and nightSpeed for 12500-23500.
  let wantDay = golden ? GOLDEN_SPEED : MIDDAY_SPEED
  let wantNight = golden ? GOLDEN_SPEED : DEEP_NIGHT_SPEED

  if (wantDay !== appliedDaySpeed) {
    server.runCommandSilent('hourglass config daySpeed ' + wantDay)
    appliedDaySpeed = wantDay
  }
  if (wantNight !== appliedNightSpeed) {
    server.runCommandSilent('hourglass config nightSpeed ' + wantNight)
    appliedNightSpeed = wantNight
  }
})
