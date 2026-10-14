package fotfskills.compat;

import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.datafixers.util.Pair;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderSet;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructurePiece;
import net.minecraft.world.level.levelgen.structure.StructureStart;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

/**
 * /fotfverify <structure> <copies> <blocks>  (ops; meant for the test server)
 * Finds that many separate copies of a structure, generates their chunks, and counts the listed blocks ("id",
 * "#tag", or "containers") inside each copy's own pieces, so quest puzzles can be checked against what really
 * generates. Prints one line per copy and a summary of the fewest any copy had, to chat and the server log
 * ("fotfverify ..." lines, read by tools/quests/verify_puzzles.py).
 */
public final class StructureVerify {
    private static final Logger LOG = LogManager.getLogger("fotfverify");
    private static final int SPREAD = 4000;    // blocks between search origins, so each finds a different copy
    private static final String CONTAINERS = "containers";

    public static List<String> keys(String text) {
        List<String> out = new ArrayList<>();
        for (String k : text.split(",")) {
            if (!k.trim().isEmpty()) {
                out.add(k.trim());
            }
        }
        return out;
    }

    public static int[] fewest(int[][] copies, int n) {
        int[] min = new int[n];
        if (copies.length == 0) {
            return min;
        }
        for (int i = 0; i < n; i++) {
            min[i] = Integer.MAX_VALUE;
            for (int[] c : copies) {
                min[i] = Math.min(min[i], c[i]);
            }
        }
        return min;
    }

    @SubscribeEvent
    public void onRegister(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.m_82127_("fotfverify")
                .requires(src -> src.m_6761_(2))
                .then(Commands.m_82129_("structure", StringArgumentType.string())
                        .then(Commands.m_82129_("copies", IntegerArgumentType.integer(1, 8))
                                .then(Commands.m_82129_("blocks", StringArgumentType.greedyString())
                                        .executes(StructureVerify::run)))));
    }

    private static int run(CommandContext<CommandSourceStack> ctx) {
        CommandSourceStack src = ctx.getSource();
        ServerLevel level = src.m_81372_();
        String sid = StringArgumentType.getString(ctx, "structure");
        int copies = IntegerArgumentType.getInteger(ctx, "copies");
        List<String> keys = keys(StringArgumentType.getString(ctx, "blocks"));
        ResourceLocation rl = ResourceLocation.m_135820_(sid);
        Registry<Structure> reg = level.m_9598_().m_175515_(Registries.f_256944_);
        Holder<Structure> holder;
        try {
            holder = reg.m_246971_(ResourceKey.m_135785_(Registries.f_256944_, rl));
        } catch (RuntimeException e) {
            say(src, "fotfverify " + sid + " unknown structure");
            return 0;
        }
        Structure structure = holder.m_203334_();
        Set<Long> seen = new HashSet<>();
        List<int[]> found = new ArrayList<>();
        int[][] origins = {{0, 0}, {SPREAD, 0}, {-SPREAD, 0}, {0, SPREAD}, {0, -SPREAD}, {SPREAD, SPREAD},
                {-SPREAD, -SPREAD}, {SPREAD, -SPREAD}, {-SPREAD, SPREAD}, {2 * SPREAD, 0}, {0, 2 * SPREAD}};
        for (int[] o : origins) {
            if (found.size() >= copies) {
                break;
            }
            Pair<BlockPos, Holder<Structure>> hit = level.m_7726_().m_8481_().m_223037_(level,
                    HolderSet.m_205809_(holder), new BlockPos(o[0], 64, o[1]), 100, false);
            if (hit == null) {
                continue;
            }
            BlockPos pos = hit.getFirst();
            long key = (((long) pos.m_123341_() >> 4) << 32) ^ ((pos.m_123343_() >> 4) & 0xffffffffL);
            if (!seen.add(key)) {
                continue;
            }
            level.m_6325_(pos.m_123341_() >> 4, pos.m_123343_() >> 4);
            // locate gives a spot at a fixed height that may sit outside the structure's box: scan the column
            StructureStart start = level.m_215010_().m_220494_(pos, structure);
            for (int y = level.m_141937_(); !start.m_73603_() && y < level.m_151558_(); y += 4) {
                start = level.m_215010_().m_220494_(new BlockPos(pos.m_123341_(), y, pos.m_123343_()), structure);
            }
            if (!start.m_73603_()) {
                say(src, "fotfverify " + sid + " copy at " + pos.m_123341_() + "," + pos.m_123343_() + " no start");
                continue;
            }
            BoundingBox all = start.m_73601_();
            for (int cx = all.m_162395_() >> 4; cx <= all.m_162399_() >> 4; cx++) {
                for (int cz = all.m_162398_() >> 4; cz <= all.m_162401_() >> 4; cz++) {
                    level.m_6325_(cx, cz);   // generate fully, so every piece is placed
                }
            }
            int[] counts = count(level, start, keys);
            found.add(counts);
            StringBuilder line = new StringBuilder("fotfverify " + sid + " copy " + found.size() + " at "
                    + pos.m_123341_() + "," + pos.m_123343_() + " pieces=" + start.m_73602_().size());
            for (int i = 0; i < keys.size(); i++) {
                line.append(' ').append(keys.get(i)).append('=').append(counts[i]);
            }
            say(src, line.toString());
        }
        int[] min = fewest(found.toArray(new int[0][]), keys.size());
        StringBuilder sum = new StringBuilder("fotfverify " + sid + " summary copies=" + found.size());
        for (int i = 0; i < keys.size(); i++) {
            sum.append(' ').append(keys.get(i)).append("_min=").append(min[i]);
        }
        say(src, sum.toString());
        return found.size();
    }

    private static int[] count(ServerLevel level, StructureStart start, List<String> keys) {
        int[] counts = new int[keys.size()];
        Set<Long> done = new HashSet<>();
        for (StructurePiece piece : start.m_73602_()) {
            BoundingBox b = piece.m_73547_();
            for (BlockPos pos : BlockPos.m_121976_(b.m_162395_(), b.m_162396_(), b.m_162398_(), b.m_162399_(),
                    b.m_162400_(), b.m_162401_())) {
                if (!done.add(pos.m_121878_())) {
                    continue;   // pieces can overlap; count each block once
                }
                BlockState state = level.m_8055_(pos);
                if (state.m_60795_()) {
                    continue;
                }
                String id = BuiltInRegistries.f_256975_.m_7981_(state.m_60734_()).toString();
                for (int i = 0; i < keys.size(); i++) {
                    if (matches(state, id, keys.get(i))) {
                        counts[i]++;
                    }
                }
            }
        }
        return counts;
    }

    private static boolean matches(BlockState state, String id, String key) {
        if (key.equals(CONTAINERS)) {
            String path = id.substring(id.indexOf(':') + 1);
            return path.matches(".*(chest|barrel|shulker|crate|decorated_pot|basket|cabinet|drawer|cupboard|locker|safe|sack|jar).*");
        }
        if (key.startsWith("#")) {
            ResourceLocation rl = ResourceLocation.m_135820_(key.substring(1));
            return rl != null && state.m_204336_(TagKey.m_203882_(Registries.f_256747_, rl));
        }
        return key.equals(id);
    }

    private static void say(CommandSourceStack src, String text) {
        LOG.info(text);
        src.m_288197_(() -> Component.m_237113_(text), false);
    }
}
