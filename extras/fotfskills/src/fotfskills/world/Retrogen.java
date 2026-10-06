package fotfskills.world;

import com.mojang.brigadier.context.CommandContext;
import com.mojang.logging.LogUtils;
import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
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
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.biome.FeatureSorter;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.chunk.ChunkStatus;
import net.minecraft.world.level.chunk.ImposterProtoChunk;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.chunk.LevelChunkSection;
import net.minecraft.world.level.levelgen.RandomSupport;
import net.minecraft.world.level.levelgen.WorldgenRandom;
import net.minecraft.world.level.levelgen.XoroshiroRandomSource;
import net.minecraft.world.level.levelgen.placement.PlacedFeature;
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
 * Retrogen: adds placed features (ores, decorations) from mods installed after a chunk was generated, as the chunk
 * loads, the same way worldgen would have placed them (same seed per chunk and feature, same height, rarity, biome and
 * replace rules). Only features listed in config/fotfskills-retrogen.json, only in chunks nobody has spent time near and
 * that are clear of claims, and a few chunks per tick. Each chunk remembers its worldgen epoch and what it has been
 * given, so nothing is added twice. Structures aren't handled yet.
 *
 * /fotfskills retrogen status | reload   (ops)
 */
public final class Retrogen {
    private static final Logger LOG = LogUtils.getLogger();
    private static final String TAG = "fotfskills_retrogen";

    private record Target(String id, PlacedFeature feature) {
    }

    private enum Result { DONE, WAIT, DROP }

    private static RetrogenConfig config = new RetrogenConfig();
    private static RetrogenManifest manifest = new RetrogenManifest();
    private static int currentEpoch = 0;
    private static List<Target> targets = List.of();
    private static final Map<LevelChunk, RetrogenState> STATE = Collections.synchronizedMap(new WeakHashMap<>());
    /** Part-generated chunks that already have their features, read from disk: their epoch until they finish. */
    private static final Map<Long, Integer> PROTO_EPOCH = new ConcurrentHashMap<>();
    /** Chunks waiting to be processed, per dimension (main thread only). */
    private static final Map<ResourceKey<Level>, LinkedHashSet<Long>> PENDING = new ConcurrentHashMap<>();
    private static int added, skippedUnsafe, failedFeatures;

    @SubscribeEvent
    public void onAboutToStart(ServerAboutToStartEvent event) {
        MinecraftServer server = event.getServer();
        Set<String> present = new TreeSet<>();
        registry(server).m_6579_().forEach(e -> present.add(e.getKey().m_135782_().toString()));
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
        added = skippedUnsafe = failedFeatures = 0;
        loadConfig(server);
    }

    private static Registry<PlacedFeature> registry(MinecraftServer server) {
        return server.m_206579_().m_175515_(Registries.f_256988_);
    }

    private static Path manifestFile(MinecraftServer server) {
        return server.m_129843_(LevelResource.f_78182_).resolve("data").resolve("fotfskills_retrogen.json");
    }

    private static void loadConfig(MinecraftServer server) {
        config = RetrogenConfig.load(FMLPaths.CONFIGDIR.get().resolve("fotfskills-retrogen.json"));
        List<Target> list = new ArrayList<>();
        if (config.enabled) {
            registry(server).m_6579_().forEach(e -> {
                String id = e.getKey().m_135782_().toString();
                if (config.wantsFeature(id)) {
                    list.add(new Target(id, e.getValue()));
                }
            });
        }
        targets = List.copyOf(list);
        if (config.enabled) {
            LOG.info("Retrogen: {} placed features to add, worldgen epoch {}", targets.size(), currentEpoch);
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
            // a brand-new chunk was just decorated with everything installed now; one read whole from disk without
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
        if (!config.enabled || targets.isEmpty() || !config.wantsDimension(level.m_46472_().m_135782_().toString())
                || needed(state).isEmpty()) {
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

    // ---- processing ----

    @SubscribeEvent
    public void onTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !config.enabled || targets.isEmpty() || PENDING.isEmpty()) {
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
        if (need.isEmpty()) {
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
        if (config.claimBufferChunks >= 0 && ModList.get().isLoaded("openpartiesandclaims")
                && RetrogenClaims.near(level, x, z, 1 + config.claimBufferChunks)) {
            skippedUnsafe++;
            return Result.DROP;
        }
        decorate(level, chunk, need);
        resend(level, x, z);
        synchronized (state.done) {
            need.forEach(target -> state.done.add(target.id));
        }
        chunk.m_8092_(true);
        added++;
        if (config.logChunks) {
            LOG.info("Retrogen: added {} feature(s) to chunk {}, {} in {}", need.size(), x, z, level.m_46472_().m_135782_());
        }
        return Result.DONE;
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
        Set<PlacedFeature> wanted = Collections.newSetFromMap(new java.util.IdentityHashMap<>());
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
                    LOG.warn("Retrogen: feature {} failed in chunk {}, {}", registry(level.m_7654_()).m_7981_(feature),
                            cp.f_45578_, cp.f_45579_, e);
                }
            }
        }
    }

    /**
     * Ores and some other features write straight into chunk sections without telling clients, so players who
     * already have the area loaded get the 3x3 chunks sent again.
     */
    private static void resend(ServerLevel level, int x, int z) {
        for (int dx = -1; dx <= 1; dx++) {
            for (int dz = -1; dz <= 1; dz++) {
                LevelChunk near = level.m_7726_().m_7131_(x + dx, z + dz);
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
                .append(", ").append(targets.size()).append(" feature(s), worldgen epoch ").append(currentEpoch)
                .append("\nQueued chunks: ").append(pending).append(", done this session: ").append(added)
                .append(", skipped (players/claims nearby): ").append(skippedUnsafe)
                .append(", feature errors: ").append(failedFeatures);
        targets.stream().limit(10).forEach(target -> text.append("\n §e").append(target.id));
        if (targets.size() > 10) {
            text.append("\n §7…and ").append(targets.size() - 10).append(" more");
        }
        ctx.getSource().m_288197_(() -> Component.m_237113_(text.toString()), false);
        return 1;
    }

    /** Re-reads the config and re-checks every loaded chunk against it. */
    private static int reload(CommandContext<CommandSourceStack> ctx) {
        MinecraftServer server = ctx.getSource().m_81377_();
        loadConfig(server);
        PENDING.clear();
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
