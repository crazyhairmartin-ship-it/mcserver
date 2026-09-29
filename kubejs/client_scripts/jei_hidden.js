// Start with the JEI item list hidden. JEI doesn't save this setting, so hide it on every join.
// Ctrl+O shows it again.

ClientEvents.loggedIn(event => {
  try {
    Java.loadClass('mezz.jei.common.Internal').getClientToggleState().setOverlayEnabled(false)
  } catch (err) {
    console.warn('[jei_hidden] Could not hide the JEI overlay: ' + err)
  }
})
