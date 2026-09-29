# MIMI Android Fix

Tiny client-only Forge mod so the pack runs on Android launchers (Zalith, Pojav, FCL).

MIMI 4.3.0 opens a `javax.sound` audio line for its MIDI synth. Android's Java has no
audio mixers, so the open fails, MIMI sets its synth to null and then calls it anyway,
crashing at the loading screen. This mod hands MIMI a silent line **only** when Java
reports no audio output at all, so on a normal PC it does nothing. On Android the game
loads and MIMI instruments are just muted.

Rebuild with `./build.sh` (needs a JDK 17+). Bump the version in the filename,
`mods.toml`, and `mods/mimiandroidfix.pw.toml` if you change it.
