package fotfskills.compat;

import java.util.HashSet;
import java.util.List;
import java.util.Set;
import net.blay09.mods.waystones.api.IMutableWaystone;
import net.blay09.mods.waystones.api.IWaystone;
import net.blay09.mods.waystones.api.WaystoneOrigin;
import net.blay09.mods.waystones.core.WaystoneManager;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.server.ServerLifecycleHooks;

/**
 * Village waystones name themselves after their setting (compat/WaystoneNames) as soon as their chunk is loaded, so
 * every village has a descriptive name and nobody has to type one; mixin/VillageWaystoneLockMixin then keeps it.
 * Checks every ten seconds; only unnamed village waystones in loaded chunks are touched.
 */
public final class VillageWaystones {
    private static final int EVERY = 200;
    private int ticks;

    @SubscribeEvent
    public void onTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || ++ticks % EVERY != 0) {
            return;
        }
        MinecraftServer server = ServerLifecycleHooks.getCurrentServer();
        if (server == null) {
            return;
        }
        WaystoneManager manager = WaystoneManager.get(server);
        List<IWaystone> all = manager.getWaystones().toList();
        Set<String> taken = new HashSet<>();
        for (IWaystone w : all) {
            if (w.hasName()) {
                taken.add(w.getName());
            }
        }
        for (IWaystone w : all) {
            if (w.getOrigin() != WaystoneOrigin.VILLAGE || w.hasName() || !(w instanceof IMutableWaystone mutable)) {
                continue;
            }
            ServerLevel level = server.m_129880_(w.getDimension());
            if (level == null || !level.m_46805_(w.getPos())) {
                continue;
            }
            String biome = level.m_204166_(w.getPos()).m_203543_().map(k -> k.m_135782_().toString()).orElse("minecraft:plains");
            String name = WaystoneNames.name(biome, w.getWaystoneUid(), taken);
            mutable.setName(name);
            taken.add(name);
            manager.updateWaystone(w);
        }
    }
}
