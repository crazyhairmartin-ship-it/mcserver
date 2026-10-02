// Bookwyrm Charms are craftable: Ars Nouveau's Storage Lectern links (bookwyrms x bookwyrmLimit) chests, so a lectern
// with no bookwyrms links none, and the only other source is the Ritual of Awakening. bookwyrmLimit is 64 here
// (config/ars_nouveau-common.toml), so one charm is enough for most bases.
ServerEvents.recipes(event => {
  event.shapeless('ars_nouveau:bookwyrm_charm', ['minecraft:writable_book', 'ars_nouveau:source_gem', 'minecraft:feather'])
    .id('fotf:bookwyrm_charm')
})
