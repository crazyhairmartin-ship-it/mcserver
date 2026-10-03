// One-off: pull TIERS and TREES out of the design page and write tools/skills/trees.json.
const fs = require('fs');
const path = require('path');
const page = fs.readFileSync(path.join(__dirname, '..', '..', 'docs', 'superpowers', 'specs', '2026-10-03-skill-trees.html'), 'utf8');
const script = page.split('<script>')[1].split('const BRANCH_NAMES')[0];
const { TIERS, TREES } = new Function(script + '; return { TIERS, TREES };')();
const ICONS = {
  mining: ['minecraft:iron_pickaxe', 'minecraft:textures/block/stone.png'],
  forage: ['minecraft:iron_axe', 'minecraft:textures/block/oak_planks.png'],
  farm: ['minecraft:iron_hoe', 'minecraft:textures/block/farmland_moist.png'],
  fish: ['minecraft:fishing_rod', 'minecraft:textures/block/prismarine.png'],
  cook: ['farmersdelight:cooking_pot', 'minecraft:textures/block/bricks.png'],
  craft: ['minecraft:crafting_table', 'minecraft:textures/block/spruce_planks.png'],
  attack: ['minecraft:iron_sword', 'minecraft:textures/block/polished_andesite.png'],
  range: ['minecraft:bow', 'minecraft:textures/block/birch_planks.png'],
  defense: ['minecraft:shield', 'minecraft:textures/block/cobblestone.png'],
  agility: ['minecraft:feather', 'minecraft:textures/block/white_wool.png'],
  magic: ['minecraft:enchanted_book', 'minecraft:textures/block/purpur_block.png'],
  taming: ['minecraft:lead', 'minecraft:textures/block/hay_block_side.png'],
};
const out = {
  tiers: TIERS.map(t => ({ n: t.n, req: t.req })),
  trees: TREES.map(t => ({
    id: t.id, name: t.name, xp: t.xp, icon: ICONS[t.id][0], background: ICONS[t.id][1],
    nodes: t.nodes.map(n => ({ t: n.t, name: n.name, r: n.r, d: n.d, c: n.c || 1, b: n.b || null,
      cap: !!n.cap, needs: n.needs || null, syn: n.syn || null })),
  })),
};
fs.writeFileSync(path.join(__dirname, 'trees.json'), JSON.stringify(out, null, 2) + '\n');
console.log(`wrote ${out.trees.length} trees, ${out.trees.reduce((a, t) => a + t.nodes.length, 0)} nodes`);
