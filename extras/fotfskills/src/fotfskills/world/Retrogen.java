package fotfskills.world;

import com.mojang.brigadier.context.CommandContext;
import com.mojang.logging.LogUtils;
import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.IdentityHashMap;
import java.util.Iterator;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeSet;
import java.util.WeakHashMap;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Supplier;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderSet;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.biome.FeatureSorter;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.chunk.ChunkGeneratorStructureState;
import net.minecraft.world.level.chunk.ChunkStatus;
import net.minecraft.world.level.chunk.ImposterProtoChunk;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.chunk.LevelChunkSection;
import net.minecraft.world.level.levelgen.LegacyRandomSource;
import net.minecraft.world.level.levelgen.RandomSupport;
import net.minecraft.world.level.levelgen.WorldgenRandom;
import net.minecraft.world.level.levelgen.XoroshiroRandomSource;
import net.minecraft.world.level.levelgen.placement.PlacedFeature;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureSet;
import net.minecraft.world.level.levelgen.structure.StructureStart;
import net.minecraft.world.level.storage.LevelResource;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.level.ChunkDataEvent;
import net.minecraftforge.event.level.ChunkEvent;
import net.minecraftforge.event.server.ServerAboutToStartEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.fml.loading.FMLPaths;
import net.minecraftforge.fml.util.ObfuscationReflectionHelper;
import org.slf4j.Logger;

/**
 * Retrogen: adds worldgen from mods installed after a chunk was generated, as the chunk loads, the way worldgen would
 * have. Placed features (ores, decorations) get the same seed per chunk and feature, height, rarity, biome and replace
 * rules. Structure sets: a chunk that would have started one of the set's structures gets it (same placement and
 * seed), and pieces of nearby structures that reach into the chunk but were never placed there (e.g. a structure from
 * freshly generated land next to old land) are filled in. Only what config/fotfskills-retrogen.json lists, only in
 * chunks nobody has spent long near and that are clear of claims, a few chunks per tick. Each chunk remembers its
 * worldgen epoch and what it has been given, so nothing is added twice.
 *
 * /fotfskills retrogen status | reload   (ops)
 */
public final class Retrogen {
    private static final Logger LOG = LogUtils.getLogger();
    private static final String TAG = "fotfskills_retrogen";
    private static final String SET_PREFIX = "structure_set:";

    private record Target(String id, PlacedFeature feature) {
    }

    private record SetTarget(String id, StructureSet set, Set<Structure> structures) {
    }

    private enum Result { DONE, WAIT, DROP }

    private static RetrogenConfig config = new RetrogenConfig();
    private static RetrogenManifest manifest = new RetrogenManifest();
    private static int currentEpoch = 0;
    private static List<Target> targets = List.of();
    private static List<SetTarget> setTargets = List.of();
    /** Each structure's place in worldgen's per-step structure order: {step, index}, for its placement seed. */
    private static Map<Structure, int[]> structureOrder = Map.of();
    private static final Map<LevelChunk, RetrogenState> STATE = Collections.synchronizedMap(new WeakHashMap<>());
    /** Part-generated chunks that already have their features, read from disk: their epoch until they finish. */
    private static final Map<Long, Integer> PROTO_EPOCH = new ConcurrentHashMap<>();
    /** Chunks waiting to be processed, per dimension (main thread only). */
    private static final Map<ResourceKey<Level>, LinkedHashSet<Long>> PENDING = new ConcurrentHashMap<>();
    /** Structure origins waiting for chunks they cover to load: not retried before this game tick. */
    private static final Map<Long, Long> RETRY_AT = new HashMap<>();
    private static int added, skippedUnsafe, failedFeatures, structuresStarted, piecesFilled, structuresSkipped;

    @SubscribeEvent
    public void onAboutToStart(ServerAboutToStartEvent event) {
        MinecraftServer server = event.getServer();
        Set<String> present = new TreeSet<>();
        features(server).m_6579_().forEach(e -> present.add(e.getKey().m_135782_().toString()));
        sets(server).m_6579_().forEach(e -> present.add(SET_PREFIX + e.getKey().m_135782_()));
        Path file = manifestFile(server);
        manifest = RetrogenManifest.load(file);
        int before = manifest.epochs.size();
        currentEpoch = manifest.epochFor(present);
        if (manifest.epochs.size() != before) {
            try {
                manifest.save(file);
            } catch (IOException e) {
                LOG.warn("Retrogen: couldn't save {}", file, e);
            }
        }
        STATE.clear();
        PROTO_EPOCH.clear();
        PENDING.clear();
        RETRY_AT.clear();
        added = skippedUnsafe = failedFeatures = structuresStarted = piecesFilled = structuresSkipped = 0;
        loadConfig(server);
    }

    private static Registry<PlacedFeature> features(MinecraftServer server) {
        return server.m_206579_().m_175515_(Registries.f_256988_);
    }

    private static Registry<StructureSet> sets(MinecraftServer server) {
        return server.m_206579_().m_175515_(Registries.f_256998_);
    }

    private static Path manifestFile(MinecraftServer server) {
        return server.m_129843_(LevelResource.f_78182_).resolve("data").resolve("fotfskills_retrogen.json");
    }

    private static void loadConfig(MinecraftServer server) {
        config = RetrogenConfig.load(FMLPaths.CONFIGDIR.get().resolve("fotfskills-retrogen.json"));
        List<Target> list = new ArrayList<>();
        List<SetTarget> setList = new ArrayList<>();
        if (config.enabled) {
            features(server).m_6579_().forEach(e -> {
                String id = e.getKey().m_135782_().toString();
                if (config.wantsFeature(id)) {
                    list.add(new Target(id, e.getValue()));
                }
            });
            sets(server).m_6579_().forEach(e -> {
                String id = e.getKey().m_135782_().toString();
                if (config.wantsStructureSet(id)) {
                    Set<Structure> structures = Collections.newSetFromMap(new IdentityHashMap<>());
                    e.getValue().f_210003_().forEach(entry -> structures.add(entry.f_210026_().m_203334_()));
                    setList.add(new SetTarget(SET_PREFIX + id, e.getValue(), structures));
                }
            });
        }
        targets = List.copyOf(list);
        setTargets = List.copyOf(setList);
        // worldgen's structure order: grouped by generation step, in registry order (ChunkGenerator.applyBiomeDecoration)
        Map<Structure, int[]> order = new IdentityHashMap<>();
        Map<Integer, Integer> perStep = new HashMap<>();
        server.m_206579_().m_175515_(Registries.f_256944_).m_123024_().forEach(structure -> {
            int step = structure.m_226619_().ordinal();
            order.put(structure, new int[] {step, perStep.merge(step, 1, Integer::sum) - 1});
        });
        structureOrder = order;
        if (config.enabled) {
            LOG.info("Retrogen: {} placed features and {} structure sets to add, worldgen epoch {}", targets.size(),
                    setTargets.size(), currentEpoch);
        }
    }

    // ---- per-chunk records ----

    @SubscribeEvent
    public void onChunkRead(ChunkDataEvent.Load event) {
        ChunkAccess chunk = event.getChunk();
        CompoundTag data = event.getData();
        boolean stamped = data.m_128425_(TAG, 10);
        RetrogenState state = RetrogenState.legacy();
        if (stamped) {
            CompoundTag tag = data.m_128469_(TAG);
            Set<String> done = new HashSet<>();
            ListTag list = tag.m_128437_("done", 8);
            for (int i = 0; i < list.size(); i++) {
                done.add(list.m_128778_(i));
            }
            state = new RetrogenState(tag.m_128451_("epoch"), done);
        }
        LevelChunk full = chunk instanceof LevelChunk level ? level
                : chunk instanceof ImposterProtoChunk imposter ? imposter.m_62768_() : null;
        if (full != null) {
            STATE.put(full, state);
        } else if (chunk.m_6415_().m_62427_(ChunkStatus.f_62322_)) {
            PROTO_EPOCH.put(chunk.m_7697_().m_45588_(), state.epoch);
        }
    }

    @SubscribeEvent
    public void onChunkWrite(ChunkDataEvent.Save event) {
        ChunkAccess chunk = event.getChunk();
        CompoundTag tag = new CompoundTag();
        if (chunk instanceof LevelChunk full) {
            RetrogenState state = STATE.get(full);
            if (state == null) {
                return;
            }
            tag.m_128405_("epoch", state.epoch);
            ListTag done = new ListTag();
            synchronized (state.done) {
                state.done.forEach(id -> done.add(StringTag.m_129297_(id)));
            }
            tag.m_128365_("done", done);
        } else if (chunk.m_6415_().m_62427_(ChunkStatus.f_62322_)) {
            tag.m_128405_("epoch", PROTO_EPOCH.getOrDefault(chunk.m_7697_().m_45588_(), currentEpoch));
        } else {
            return;
        }
        event.getData().m_128365_(TAG, tag);
    }

    @SubscribeEvent
    public void onChunkLoad(ChunkEvent.Load event) {
        if (!(event.getLevel() instanceof ServerLevel level) || !(event.getChunk() instanceof LevelChunk chunk)) {
            return;
        }
        long pos = chunk.m_7697_().m_45588_();
        RetrogenState state = STATE.get(chunk);
        if (state == null) {
            Integer protoEpoch = PROTO_EPOCH.remove(pos);
            // a brand-new chunk was just generated with everything installed now; one read whole from disk without
            // our record predates Retrogen
            state = event.isNewChunk() ? new RetrogenState(protoEpoch != null ? protoEpoch : currentEpoch, new HashSet<>())
                    : RetrogenState.legacy();
            STATE.put(chunk, state);
        } else {
            PROTO_EPOCH.remove(pos);
        }
        queueIfNeeded(level, chunk, state);
    }

    private static void queueIfNeeded(ServerLevel level, LevelChunk chunk, RetrogenState state) {
        if (!config.enabled || (targets.isEmpty() && setTargets.isEmpty())
                || !config.wantsDimension(level.m_46472_().m_135782_().toString())
                || (needed(state).isEmpty() && neededSets(state).isEmpty())) {
            return;
        }
        PENDING.computeIfAbsent(level.m_46472_(), k -> new LinkedHashSet<>()).add(chunk.m_7697_().m_45588_());
    }

    private static List<Target> needed(RetrogenState state) {
        List<Target> list = new ArrayList<>();
        synchronized (state.done) {
            for (Target target : targets) {
                if (state.needs(target.id, manifest.epochs)) {
                    list.add(target);
                }
            }
        }
        return list;
    }

    private static List<SetTarget> neededSets(RetrogenState state) {
        List<SetTarget> list = new ArrayList<>();
        synchronized (state.done) {
            for (SetTarget target : setTargets) {
                if (state.needs(target.id, manifest.epochs)) {
                    list.add(target);
                }
            }
        }
        return list;
    }

    // ---- processing ----

    @SubscribeEvent
    public void onTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !config.enabled || PENDING.isEmpty()) {
            return;
        }
        long deadline = System.nanoTime() + config.maxMillisPerTick * 1_000_000L;
        int processed = 0;
        for (ServerLevel level : event.getServer().m_129785_()) {
            LinkedHashSet<Long> queue = PENDING.get(level.m_46472_());
            if (queue == null || queue.isEmpty()) {
                continue;
            }
            List<Long> later = new ArrayList<>();
            Iterator<Long> it = queue.iterator();
            int scanned = 0;
            while (it.hasNext() && processed < config.maxChunksPerTick && scanned < 64 && System.nanoTime() < deadline) {
                long pos = it.next();
                it.remove();
                scanned++;
                Result result = process(level, pos);
                if (result == Result.WAIT) {
                    later.add(pos);
                } else if (result == Result.DONE) {
                    processed++;
                }
            }
            queue.addAll(later);
        }
    }

    private static Result process(ServerLevel level, long pos) {
        int x = ChunkPos.m_45592_(pos), z = ChunkPos.m_45602_(pos);
        LevelChunk chunk = level.m_7726_().m_7131_(x, z);
        RetrogenState state = chunk == null ? null : STATE.get(chunk);
        if (state == null) {
            return Result.DROP;                     // unloaded: it's queued again when it loads
        }
        List<Target> need = needed(state);
        List<SetTarget> needSets = neededSets(state);
        if (need.isEmpty() && needSets.isEmpty()) {
            return Result.DROP;
        }
        // features can spill into the 8 neighbours, as in normal worldgen: all must be loaded and untouched by players
        for (int dx = -1; dx <= 1; dx++) {
            for (int dz = -1; dz <= 1; dz++) {
                LevelChunk near = level.m_7726_().m_7131_(x + dx, z + dz);
                if (near == null) {
                    return Result.WAIT;
                }
                if (!config.inhabitedOk(near.m_6319_())) {
                    skippedUnsafe++;
                    return Result.DROP;
                }
            }
        }
        if (claimed(level, x, z, 1)) {
            skippedUnsafe++;
            return Result.DROP;
        }
        Set<Long> changed = new HashSet<>();
        if (!need.isEmpty()) {
            decorate(level, chunk, need);
            synchronized (state.done) {
                need.forEach(target -> state.done.add(target.id));
            }
            for (int dx = -1; dx <= 1; dx++) {
                for (int dz = -1; dz <= 1; dz++) {
                    changed.add(ChunkPos.m_45589_(x + dx, z + dz));
                }
            }
            added++;
        }
        boolean wait = !needSets.isEmpty() && !structures(level, chunk, state, needSets, changed);
        chunk.m_8092_(true);
        resend(level, changed);
        if (config.logChunks && (!need.isEmpty() || !changed.isEmpty())) {
            LOG.info("Retrogen: chunk {}, {} in {}: {} feature(s), {} structure set(s) checked", x, z,
                    level.m_46472_().m_135782_(), need.size(), needSets.size());
        }
        return wait ? Result.WAIT : Result.DONE;
    }

    private static boolean claimed(ServerLevel level, int x, int z, int extra) {
        return config.claimBufferChunks >= 0 && ModList.get().isLoaded("openpartiesandclaims")
                && RetrogenClaims.near(level, x, z, extra + config.claimBufferChunks);
    }

    /** Places the features like ChunkGenerator.applyBiomeDecoration: biomes of the 3x3 area, each step in order, same seeds. */
    private static void decorate(ServerLevel level, LevelChunk chunk, List<Target> need) {
        ChunkGenerator generator = level.m_7726_().m_8481_();
        ChunkPos cp = chunk.m_7697_();
        BlockPos origin = new BlockPos(cp.m_45604_(), level.m_141937_(), cp.m_45605_());
        Supplier<List<FeatureSorter.StepFeatureData>> perStep =
                ObfuscationReflectionHelper.getPrivateValue(ChunkGenerator.class, generator, "f_223020_");
        List<FeatureSorter.StepFeatureData> steps = perStep.get();
        Set<Holder<Biome>> biomes = new HashSet<>();
        for (int dx = -1; dx <= 1; dx++) {
            for (int dz = -1; dz <= 1; dz++) {
                for (LevelChunkSection section : level.m_7726_().m_7131_(cp.f_45578_ + dx, cp.f_45579_ + dz).m_7103_()) {
                    section.m_187996_().m_196879_(biomes::add);
                }
            }
        }
        biomes.retainAll(generator.m_62218_().m_207840_());
        Set<PlacedFeature> wanted = Collections.newSetFromMap(new IdentityHashMap<>());
        need.forEach(target -> wanted.add(target.feature));
        WorldgenRandom random = new WorldgenRandom(new XoroshiroRandomSource(RandomSupport.m_224599_()));
        long seed = random.m_64690_(level.m_7328_(), origin.m_123341_(), origin.m_123343_());
        for (int step = 0; step < steps.size(); step++) {
            FeatureSorter.StepFeatureData data = steps.get(step);
            TreeSet<Integer> indices = new TreeSet<>();
            for (Holder<Biome> biome : biomes) {
                List<HolderSet<PlacedFeature>> lists = generator.m_223131_(biome).m_47818_();
                if (step < lists.size()) {
                    lists.get(step).m_203614_().map(Holder::m_203334_).filter(wanted::contains).forEach(feature -> {
                        int index = data.f_220625_().applyAsInt(feature);
                        if (index >= 0) {
                            indices.add(index);
                        }
                    });
                }
            }
            for (int index : indices) {
                PlacedFeature feature = data.f_220624_().get(index);
                random.m_190064_(seed, index, step);
                try {
                    feature.m_226377_(level, generator, random, origin);
                } catch (RuntimeException e) {
                    failedFeatures++;
                    LOG.warn("Retrogen: feature {} failed in chunk {}, {}", features(level.m_7654_()).m_7981_(feature),
                            cp.f_45578_, cp.f_45579_, e);
                }
            }
        }
    }

    /**
     * Structure sets for one chunk. Needs every chunk within structureRadius loaded. For each set: fills in pieces of
     * already-started structures nearby that reach into this chunk but were never placed here, then starts the set's
     * structure here if worldgen would have. Returns false if it has to wait for chunks to load (the set isn't marked
     * done then).
     */
    private static boolean structures(ServerLevel level, LevelChunk chunk, RetrogenState state, List<SetTarget> needSets,
                                      Set<Long> changed) {
        ChunkPos cp = chunk.m_7697_();
        int radius = config.structureRadius;
        long now = level.m_7654_().m_129921_();
        Long retry = RETRY_AT.get(cp.m_45588_());
        if (retry != null && now < retry) {
            return false;
        }
        List<LevelChunk> around = new ArrayList<>();
        for (int dx = -radius; dx <= radius; dx++) {
            for (int dz = -radius; dz <= radius; dz++) {
                LevelChunk near = level.m_7726_().m_7131_(cp.f_45578_ + dx, cp.f_45579_ + dz);
                if (near == null) {
                    RETRY_AT.put(cp.m_45588_(), now + 200);
                    return false;
                }
                around.add(near);
            }
        }
        StructureManager manager = level.m_215010_();
        boolean allDone = true;
        for (SetTarget target : needSets) {
            boolean done = true;
            if (manager.m_220467_()) {
                // pieces of structures that start nearby but were never placed in this chunk
                for (LevelChunk near : around) {
                    for (Map.Entry<Structure, StructureStart> e : near.m_6633_().entrySet()) {
                        StructureStart start = e.getValue();
                        if (target.structures.contains(e.getKey()) && start.m_73603_() && covers(start.m_73601_(), cp)
                                && !chunk.m_213649_(e.getKey()).contains(near.m_7697_().m_45588_())) {
                            place(level, manager, e.getKey(), start, near.m_7697_(), chunk);
                            changed.add(cp.m_45588_());
                            piecesFilled++;
                        }
                    }
                }
                Boolean started = startHere(level, manager, chunk, target, changed);
                if (started == null) {
                    done = false;
                }
            }
            if (done) {
                synchronized (state.done) {
                    state.done.add(target.id);
                }
            } else {
                allDone = false;
            }
        }
        if (!allDone) {
            RETRY_AT.put(cp.m_45588_(), now + 200);
        } else {
            RETRY_AT.remove(cp.m_45588_());
        }
        return allDone;
    }

    /**
     * Starts the set's structure in this chunk if worldgen would have (ChunkGenerator.createStructures): same
     * placement check, same weighted pick and seed. Returns true if started, false if not (none here, or not safe),
     * null if a chunk it would cover isn't loaded yet.
     */
    private static Boolean startHere(ServerLevel level, StructureManager manager, LevelChunk chunk, SetTarget target,
                                     Set<Long> changed) {
        ChunkPos cp = chunk.m_7697_();
        for (Structure structure : target.structures) {
            StructureStart existing = chunk.m_213652_(structure);
            if (existing != null && existing.m_73603_()) {
                return false;
            }
        }
        ChunkGeneratorStructureState genState = level.m_7726_().m_255415_();
        if (!target.set.f_210004_().m_255071_(genState, cp.f_45578_, cp.f_45579_)) {
            return false;
        }
        Structure structure = null;
        StructureStart start = null;
        List<StructureSet.StructureSelectionEntry> entries = target.set.f_210003_();
        if (entries.size() == 1) {
            structure = entries.get(0).f_210026_().m_203334_();
            start = generate(level, chunk, structure, genState);
        } else {
            List<StructureSet.StructureSelectionEntry> left = new ArrayList<>(entries);
            WorldgenRandom random = new WorldgenRandom(new LegacyRandomSource(0L));
            random.m_190068_(genState.m_254887_(), cp.f_45578_, cp.f_45579_);
            int total = 0;
            for (StructureSet.StructureSelectionEntry entry : left) {
                total += entry.f_210027_();
            }
            while (!left.isEmpty()) {
                int pick = random.m_188503_(total);
                int i = 0;
                for (StructureSet.StructureSelectionEntry entry : left) {
                    pick -= entry.f_210027_();
                    if (pick < 0) {
                        break;
                    }
                    i++;
                }
                StructureSet.StructureSelectionEntry entry = left.get(i);
                StructureStart tried = generate(level, chunk, entry.f_210026_().m_203334_(), genState);
                if (tried != null) {
                    structure = entry.f_210026_().m_203334_();
                    start = tried;
                    break;
                }
                left.remove(i);
                total -= entry.f_210027_();
            }
        }
        if (start == null) {
            return false;
        }
        BoundingBox box = start.m_73601_();
        List<LevelChunk> covered = new ArrayList<>();
        for (int x = box.m_162395_() >> 4; x <= box.m_162399_() >> 4; x++) {
            for (int z = box.m_162398_() >> 4; z <= box.m_162401_() >> 4; z++) {
                LevelChunk c = level.m_7726_().m_7131_(x, z);
                if (c == null) {
                    return null;
                }
                covered.add(c);
            }
        }
        for (LevelChunk c : covered) {
            if (!config.inhabitedOk(c.m_6319_()) || claimed(level, c.m_7697_().f_45578_, c.m_7697_().f_45579_, 0)) {
                structuresSkipped++;
                return false;
            }
        }
        chunk.m_213792_(structure, start);
        for (LevelChunk c : covered) {
            place(level, manager, structure, start, cp, c);
            changed.add(c.m_7697_().m_45588_());
        }
        structuresStarted++;
        if (config.logChunks) {
            LOG.info("Retrogen: started {} at chunk {}, {} in {} ({} chunks)", target.id.substring(SET_PREFIX.length()),
                    cp.f_45578_, cp.f_45579_, level.m_46472_().m_135782_(), covered.size());
        }
        return true;
    }

    private static StructureStart generate(ServerLevel level, LevelChunk chunk, Structure structure,
                                           ChunkGeneratorStructureState genState) {
        ChunkGenerator generator = level.m_7726_().m_8481_();
        StructureStart start = structure.m_226596_(level.m_9598_(), generator, generator.m_62218_(), genState.m_255046_(),
                level.m_215082_(), genState.m_254887_(), chunk.m_7697_(), 0, chunk, structure.m_226559_()::m_203333_);
        return start.m_73603_() ? start : null;
    }

    private static boolean covers(BoundingBox box, ChunkPos cp) {
        return box.m_162395_() <= cp.m_45604_() + 15 && box.m_162399_() >= cp.m_45604_()
                && box.m_162398_() <= cp.m_45605_() + 15 && box.m_162401_() >= cp.m_45605_();
    }

    /** Places one chunk's share of a structure, as the decoration step would, and records it as placed there. */
    private static void place(ServerLevel level, StructureManager manager, Structure structure, StructureStart start,
                              ChunkPos origin, LevelChunk target) {
        ChunkPos cp = target.m_7697_();
        target.m_213843_(structure, origin.m_45588_());
        int[] order = structureOrder.getOrDefault(structure, new int[] {structure.m_226619_().ordinal(), 0});
        WorldgenRandom random = new WorldgenRandom(new XoroshiroRandomSource(RandomSupport.m_224599_()));
        long seed = random.m_64690_(level.m_7328_(), cp.m_45604_(), cp.m_45605_());
        random.m_190064_(seed, order[1], order[0]);
        BoundingBox area = new BoundingBox(cp.m_45604_(), level.m_141937_() + 1, cp.m_45605_(),
                cp.m_45604_() + 15, level.m_151558_() - 1, cp.m_45605_() + 15);
        try {
            start.m_226850_(level, manager, level.m_7726_().m_8481_(), random, area, cp);
        } catch (RuntimeException e) {
            failedFeatures++;
            LOG.warn("Retrogen: structure piece failed in chunk {}, {}", cp.f_45578_, cp.f_45579_, e);
        }
        target.m_8092_(true);
    }

    /**
     * Ores and some other features write straight into chunk sections without telling clients, so players who
     * already have the area loaded get the changed chunks sent again.
     */
    private static void resend(ServerLevel level, Set<Long> chunks) {
        for (long pos : chunks) {
            LevelChunk near = level.m_7726_().m_7131_(ChunkPos.m_45592_(pos), ChunkPos.m_45602_(pos));
            if (near == null) {
                continue;
            }
            List<net.minecraft.server.level.ServerPlayer> players =
                    level.m_7726_().f_8325_.m_183262_(near.m_7697_(), false);
            if (players.isEmpty()) {
                continue;
            }
            var packet = new net.minecraft.network.protocol.game.ClientboundLevelChunkWithLightPacket(
                    near, level.m_5518_(), null, null);
            players.forEach(player -> player.f_8906_.m_9829_(packet));
        }
    }

    // ---- commands ----

    @SubscribeEvent
    public void onRegisterCommands(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.m_82127_("fotfskills")
                .then(Commands.m_82127_("retrogen").requires(source -> source.m_6761_(2))
                        .then(Commands.m_82127_("status").executes(Retrogen::status))
                        .then(Commands.m_82127_("reload").executes(Retrogen::reload))));
    }

    private static int status(CommandContext<CommandSourceStack> ctx) {
        int pending = PENDING.values().stream().mapToInt(Set::size).sum();
        StringBuilder text = new StringBuilder("§6Retrogen§r: ").append(config.enabled ? "§aon" : "§coff").append("§r")
                .append(", ").append(targets.size()).append(" feature(s), ").append(setTargets.size())
                .append(" structure set(s), worldgen epoch ").append(currentEpoch)
                .append("\nQueued chunks: ").append(pending).append(", chunks given features: ").append(added)
                .append(", structures started: ").append(structuresStarted)
                .append(", pieces filled in: ").append(piecesFilled)
                .append("\nSkipped (players/claims nearby): ").append(skippedUnsafe).append(" chunk(s), ")
                .append(structuresSkipped).append(" structure(s); errors: ").append(failedFeatures);
        targets.stream().limit(5).forEach(target -> text.append("\n §e").append(target.id));
        setTargets.stream().limit(5).forEach(target -> text.append("\n §b").append(target.id.substring(SET_PREFIX.length())));
        int more = Math.max(0, targets.size() - 5) + Math.max(0, setTargets.size() - 5);
        if (more > 0) {
            text.append("\n §7…and ").append(more).append(" more");
        }
        ctx.getSource().m_288197_(() -> Component.m_237113_(text.toString()), false);
        return 1;
    }

    /** Re-reads the config and re-checks every loaded chunk against it. */
    private static int reload(CommandContext<CommandSourceStack> ctx) {
        MinecraftServer server = ctx.getSource().m_81377_();
        loadConfig(server);
        PENDING.clear();
        RETRY_AT.clear();
        List<Map.Entry<LevelChunk, RetrogenState>> loaded;
        synchronized (STATE) {
            loaded = new ArrayList<>(STATE.entrySet());
        }
        for (Map.Entry<LevelChunk, RetrogenState> entry : loaded) {
            if (entry.getKey().m_62953_() instanceof ServerLevel level) {
                queueIfNeeded(level, entry.getKey(), entry.getValue());
            }
        }
        return status(ctx);
    }
}
