package fotfskills.world;

import java.util.List;
import java.util.Map;
import java.util.Queue;
import java.util.Set;
import java.util.concurrent.ConcurrentLinkedQueue;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.Property;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.chunk.LevelChunkSection;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.level.ChunkEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.MissingMappingsEvent;
import net.minecraftforge.registries.RegistryObject;

/**
 * Blocks and items from mods the pack dropped (Paragliders, Simply Swords) that are still in the live world.
 * On world load their ids are remapped: the Runic Forge becomes an anvil, and the statues become hidden placeholder
 * blocks that keep their facing. The first time a chunk with a placeholder loads, the placeholder is swapped:
 * goddess statues become Iron's player statues (random supporter skin and pose, like Iron's own structures), horned
 * statues become Supplementaries statues holding a random treasure.
 */
public final class RemovedBlocks {
    private static final DeferredRegister<Block> BLOCKS = DeferredRegister.create(ForgeRegistries.BLOCKS, "fotfskills");
    public static final RegistryObject<Block> GODDESS = BLOCKS.register("goddess_statue_marker", Marker::new);
    public static final RegistryObject<Block> HORNED = BLOCKS.register("horned_statue_marker", Marker::new);

    private static final Set<String> GODDESS_IDS = Set.of("goddess_statue", "kakariko_goddess_statue", "rito_goddess_statue",
            "goron_goddess_statue");
    private static final List<Item> TREASURE_POOL = List.of(Items.f_42415_, Items.f_42415_, Items.f_42415_,       // diamonds
            Items.f_42616_, Items.f_42616_, Items.f_42616_, Items.f_42417_, Items.f_42417_, Items.f_42417_,
            Items.f_42436_, Items.f_42436_, Items.f_42584_, Items.f_42656_, Items.f_42437_, Items.f_42747_);
    private static final Map<Item, Integer> COUNTS = Map.of(Items.f_42415_, 2, Items.f_42616_, 5, Items.f_42417_, 6,
            Items.f_42584_, 4);

    private record Pending(ServerLevel level, BlockPos pos) {
    }

    /** A converted statue that may have been placed facing backwards (the first live day, before the rotation fix). */
    private record Fix(ServerLevel level, BlockPos pos, Direction facing) {
    }

    private final Queue<Fix> fixes = new ConcurrentLinkedQueue<>();
    private static Map<Long, List<Fix>> goddessSpots;

    /** Where every Paragliders goddess statue stood in the live world, and its facing (res/fotfskills/goddess_statues.txt). */
    private static Map<Long, List<Fix>> goddessSpots() {
        if (goddessSpots == null) {
            Map<Long, List<Fix>> spots = new java.util.HashMap<>();
            try (var in = RemovedBlocks.class.getResourceAsStream("/fotfskills/goddess_statues.txt")) {
                if (in != null) {
                    for (String line : new String(in.readAllBytes(), java.nio.charset.StandardCharsets.UTF_8).split("\n")) {
                        String[] f = line.trim().split(" ");
                        if (f.length != 5 || !f[0].equals("overworld")) {
                            continue;
                        }
                        BlockPos pos = new BlockPos(Integer.parseInt(f[1]), Integer.parseInt(f[2]), Integer.parseInt(f[3]));
                        Direction facing = Direction.m_122402_(f[4]);
                        spots.computeIfAbsent(ChunkPos.m_45589_(pos.m_123341_() >> 4, pos.m_123343_() >> 4), k -> new java.util.ArrayList<>())
                                .add(new Fix(null, pos, facing == null ? Direction.NORTH : facing));
                    }
                }
            } catch (java.io.IOException | RuntimeException ignored) {
                // no list: nothing to fix
            }
            goddessSpots = spots;
        }
        return goddessSpots;
    }

    private final Queue<Pending> pending = new ConcurrentLinkedQueue<>();
    private int ticks;

    public static void register(IEventBus modBus) {
        BLOCKS.register(modBus);
        modBus.addListener(RemovedBlocks::addAliases);
    }

    /**
     * Permanent aliases, added every start: the missing-mappings remap below only fires on the first boot after a mod
     * is removed, while chunks nobody has visited still name the old blocks years later.
     */
    @SuppressWarnings("unchecked")
    private static void addAliases(net.minecraftforge.registries.RegisterEvent event) {
        boolean paraglider = !ModList.get().isLoaded("paraglider"), swords = !ModList.get().isLoaded("simplyswords");
        if (event.getRegistryKey().equals(ForgeRegistries.Keys.BLOCKS)) {
            var reg = (net.minecraftforge.registries.ForgeRegistry<Block>) ForgeRegistries.BLOCKS;
            if (paraglider) {
                GODDESS_IDS.forEach(id -> reg.addAlias(new ResourceLocation("paraglider", id), new ResourceLocation("fotfskills", "goddess_statue_marker")));
                reg.addAlias(new ResourceLocation("paraglider", "horned_statue"), new ResourceLocation("fotfskills", "horned_statue_marker"));
            }
            if (swords) {
                reg.addAlias(new ResourceLocation("simplyswords", "runic_forge"), new ResourceLocation("minecraft", "anvil"));
            }
        } else if (event.getRegistryKey().equals(ForgeRegistries.Keys.ITEMS)) {
            var reg = (net.minecraftforge.registries.ForgeRegistry<Item>) ForgeRegistries.ITEMS;
            if (paraglider) {
                GODDESS_IDS.forEach(id -> reg.addAlias(new ResourceLocation("paraglider", id), new ResourceLocation("irons_lib", "player_statue")));
                reg.addAlias(new ResourceLocation("paraglider", "horned_statue"), new ResourceLocation("supplementaries", "statue"));
            }
            if (swords) {
                reg.addAlias(new ResourceLocation("simplyswords", "runic_forge"), new ResourceLocation("minecraft", "anvil"));
            }
        }
    }

    /** An invisible stand-in that only exists until its chunk loads. */
    public static final class Marker extends HorizontalDirectionalBlock {
        Marker() {
            super(BlockBehaviour.Properties.m_284310_().m_60955_().m_222994_().m_60910_());
        }

        @Override
        protected void m_7926_(StateDefinition.Builder<Block, BlockState> builder) {
            builder.m_61104_(f_54117_);
        }

        @Override
        public RenderShape m_7514_(BlockState state) {
            return RenderShape.INVISIBLE;
        }
    }

    @SubscribeEvent
    public void onMissing(MissingMappingsEvent event) {
        for (MissingMappingsEvent.Mapping<Block> m : event.getMappings(ForgeRegistries.Keys.BLOCKS, "paraglider")) {
            String id = m.getKey().m_135815_();
            if (GODDESS_IDS.contains(id)) {
                m.remap(GODDESS.get());
            } else if (id.equals("horned_statue")) {
                m.remap(HORNED.get());
            }
        }
        for (MissingMappingsEvent.Mapping<Block> m : event.getMappings(ForgeRegistries.Keys.BLOCKS, "simplyswords")) {
            if (m.getKey().m_135815_().equals("runic_forge")) {
                m.remap(Blocks.f_50322_);
            }
        }
        Item playerStatue = ForgeRegistries.ITEMS.getValue(new ResourceLocation("irons_lib", "player_statue"));
        Item supStatue = ForgeRegistries.ITEMS.getValue(new ResourceLocation("supplementaries", "statue"));
        for (MissingMappingsEvent.Mapping<Item> m : event.getMappings(ForgeRegistries.Keys.ITEMS, "paraglider")) {
            String id = m.getKey().m_135815_();
            if (GODDESS_IDS.contains(id) && playerStatue != null && playerStatue != Items.f_41852_) {
                m.remap(playerStatue);
            } else if (id.equals("horned_statue") && supStatue != null && supStatue != Items.f_41852_) {
                m.remap(supStatue);
            }
        }
        for (MissingMappingsEvent.Mapping<Item> m : event.getMappings(ForgeRegistries.Keys.ITEMS, "simplyswords")) {
            if (m.getKey().m_135815_().equals("runic_forge")) {
                m.remap(Items.f_42146_);
            }
        }
    }

    @SubscribeEvent
    public void onChunkLoad(ChunkEvent.Load event) {
        if (!(event.getLevel() instanceof ServerLevel level) || !(event.getChunk() instanceof LevelChunk chunk)) {
            return;
        }
        Block goddess = GODDESS.get(), horned = HORNED.get();
        LevelChunkSection[] sections = chunk.m_7103_();
        ChunkPos cp = chunk.m_7697_();
        if (level.m_46472_() == net.minecraft.world.level.Level.f_46428_) {
            for (Fix f : goddessSpots().getOrDefault(cp.m_45588_(), List.of())) {
                fixes.add(new Fix(level, f.pos, f.facing));
            }
        }
        for (int i = 0; i < sections.length; i++) {
            LevelChunkSection section = sections[i];
            if (section.m_188008_() || !section.m_63019_().m_63109_(s -> s.m_60734_() == goddess || s.m_60734_() == horned)) {
                continue;
            }
            int baseY = (chunk.m_151560_() + i) * 16;
            for (int x = 0; x < 16; x++) {
                for (int y = 0; y < 16; y++) {
                    for (int z = 0; z < 16; z++) {
                        Block b = section.m_62982_(x, y, z).m_60734_();
                        if (b == goddess || b == horned) {
                            pending.add(new Pending(level, new BlockPos(cp.m_45604_() + x, baseY + y, cp.m_45605_() + z)));
                        }
                    }
                }
            }
        }
    }

    @SubscribeEvent
    public void onTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END) {
            return;
        }
        for (int n = 0; n < 32 && !fixes.isEmpty(); n++) {
            turnAround(fixes.poll());
        }
        if (pending.isEmpty()) {
            return;
        }
        ticks++;
        boolean skinsReady = !ModList.get().isLoaded("irons_lib") || IronsStatue.hasSkins() || ticks > 1200;   // Iron's fetches its supporter list at startup
        for (int n = 0; n < 32 && !pending.isEmpty(); n++) {
            Pending p = pending.poll();
            if (!p.level.m_46749_(p.pos)) {
                continue;                       // chunk unloaded again: it converts next time it loads
            }
            BlockState state = p.level.m_8055_(p.pos);
            Direction facing = state.m_61138_(HorizontalDirectionalBlock.f_54117_) ? state.m_61143_(HorizontalDirectionalBlock.f_54117_) : Direction.NORTH;
            if (state.m_60734_() == GODDESS.get()) {
                if (!skinsReady) {
                    pending.add(p);
                    return;
                }
                if (!ModList.get().isLoaded("irons_lib") || !IronsStatue.place(p.level, p.pos, facing)) {
                    treasureStatue(p.level, p.pos, facing, false);
                }
            } else if (state.m_60734_() == HORNED.get()) {
                treasureStatue(p.level, p.pos, facing, true);
            }
        }
    }

    /** A statue converted with the old (backwards) rotation: turn both halves around, keeping its skin and pose. */
    private static void turnAround(Fix f) {
        if (!f.level.m_46749_(f.pos)) {
            return;
        }
        var rot = net.minecraft.world.level.block.state.properties.BlockStateProperties.f_61390_;
        int wrong = net.minecraft.world.level.block.state.properties.RotationSegment.m_245225_(f.facing);
        int right = net.minecraft.world.level.block.state.properties.RotationSegment.m_245225_(f.facing.m_122424_());
        for (BlockPos p : new BlockPos[] {f.pos, f.pos.m_7494_()}) {
            BlockState state = f.level.m_8055_(p);
            ResourceLocation id = ForgeRegistries.BLOCKS.getKey(state.m_60734_());
            if (id != null && id.toString().equals("irons_lib:player_statue") && state.m_61138_(rot) && state.m_61143_(rot) == wrong) {
                f.level.m_7731_(p, state.m_61124_(rot, right), 2 | 16);   // same block: the statue keeps its data
            }
        }
    }

    /** A Supplementaries statue, holding a random treasure when asked. */
    static void treasureStatue(ServerLevel level, BlockPos pos, Direction facing, boolean treasure) {
        Block statue = ForgeRegistries.BLOCKS.getValue(new ResourceLocation("supplementaries", "statue"));
        if (statue == null || statue == Blocks.f_50016_) {
            level.m_7731_(pos, Blocks.f_50016_.m_49966_(), 3);
            return;
        }
        BlockState state = withFacing(statue.m_49966_(), facing);
        level.m_7731_(pos, state, 3);
        if (treasure && level.m_7702_(pos) instanceof net.mehvahdjukaar.moonlight.api.block.ItemDisplayTile tile) {
            tile.setDisplayedItem(treasure(level.m_213780_()));
        }
    }

    static ItemStack treasure(RandomSource random) {
        Item item = TREASURE_POOL.get(random.m_188503_(TREASURE_POOL.size()));
        if (random.m_188503_(6) == 0) {
            Item tonic = ForgeRegistries.ITEMS.getValue(new ResourceLocation("fotfskills", "skill_tonic"));
            if (tonic != null && tonic != Items.f_41852_) {
                item = tonic;                   // the old heart shrines sometimes hold a Skill Tonic
            }
        }
        ItemStack stack = new ItemStack(item);
        stack.m_41764_(COUNTS.getOrDefault(item, 1));
        return stack;
    }

    @SuppressWarnings({"unchecked", "rawtypes"})
    static BlockState withFacing(BlockState state, Direction facing) {
        Property<?> prop = state.m_60734_().m_49965_().m_61081_("facing");
        if (prop != null && prop.m_6908_().contains(facing)) {
            return state.m_61124_((Property) prop, facing);
        }
        return state;
    }
}
