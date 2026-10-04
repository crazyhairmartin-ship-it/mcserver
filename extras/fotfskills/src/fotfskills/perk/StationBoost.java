package fotfskills.perk;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.server.ServerLifecycleHooks;

/**
 * Quick Hands (cooking stations) and Crafting's Smelter (furnaces): a station a player has used in the last 5 minutes
 * runs faster by ticking its block entity extra times (25% faster = one extra tick every 4). Which blocks count:
 * block tags fotfskills:cooking_stations and fotfskills:furnaces. Not saved; a restart forgets who used what.
 */
public final class StationBoost {
    private static final TagKey<Block> COOKING = TagKey.m_203882_(Registries.f_256747_, new ResourceLocation("fotfskills", "cooking_stations"));
    private static final TagKey<Block> FURNACES = TagKey.m_203882_(Registries.f_256747_, new ResourceLocation("fotfskills", "furnaces"));
    private static final long LASTS = 6000;

    /** Fractional extra ticks: the remainder carries to the next server tick. */
    static final class Ticks {
        private double carry;

        int extra(double rate) {
            carry += rate;
            int whole = (int) carry;
            carry -= whole;
            return whole;
        }
    }

    private record Key(ResourceKey<Level> dimension, long pos) {
    }

    private static final class Station {
        final double rate;
        final long until;
        final Ticks ticks = new Ticks();

        Station(double rate, long until) {
            this.rate = rate;
            this.until = until;
        }
    }

    private final Map<Key, Station> stations = new HashMap<>();

    @SubscribeEvent
    public void onUse(PlayerInteractEvent.RightClickBlock event) {
        if (!(event.getEntity() instanceof ServerPlayer player) || !(event.getLevel() instanceof ServerLevel level)) {
            return;
        }
        BlockState state = level.m_8055_(event.getPos());
        String perk = state.m_204336_(COOKING) ? "quick_hands" : state.m_204336_(FURNACES) ? "furnace_speed" : null;
        double rate = perk == null ? 0 : Perks.get(player, perk);
        if (rate > 0) {
            stations.put(new Key(level.m_46472_(), event.getPos().m_121878_()), new Station(rate, level.m_46467_() + LASTS));
        }
    }

    @SubscribeEvent
    @SuppressWarnings({"unchecked", "rawtypes"})
    public void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || stations.isEmpty()) {
            return;
        }
        MinecraftServer server = ServerLifecycleHooks.getCurrentServer();
        Iterator<Map.Entry<Key, Station>> it = stations.entrySet().iterator();
        while (it.hasNext()) {
            Map.Entry<Key, Station> entry = it.next();
            ServerLevel level = server.m_129880_(entry.getKey().dimension);
            Station station = entry.getValue();
            if (level == null || level.m_46467_() > station.until) {
                it.remove();
                continue;
            }
            BlockPos pos = BlockPos.m_122022_(entry.getKey().pos);
            if (!level.m_46749_(pos)) {
                continue;
            }
            BlockState state = level.m_8055_(pos);
            BlockEntity be = level.m_7702_(pos);
            BlockEntityTicker ticker = be == null ? null : state.m_155944_(level, (BlockEntityType) be.m_58903_());
            if (ticker == null || !(state.m_204336_(COOKING) || state.m_204336_(FURNACES))) {
                it.remove();
                continue;
            }
            for (int i = station.ticks.extra(station.rate); i > 0; i--) {
                ticker.m_155252_(level, pos, state, be);
            }
        }
    }
}
