package fotfskills.world;

import java.util.Map;
import java.util.WeakHashMap;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/**
 * Alex's Mobs elephants float but can't swim, so one that wades in ends up stranded at sea. In water they now:
 *   swim where their rider steers (runs on the rider's client too, which moves a ridden mount),
 *   head for the nearest shore within 96 blocks when nobody rides them (server; re-picked every 2 seconds),
 *   and get lifted over the bank when they swim into it (vanilla's hop out of water is too short for them).
 */
public final class ElephantSwim {
    private static final String ELEPHANT = "com.github.alexthe666.alexsmobs.entity.EntityElephant";
    private static final double RIDDEN_SPEED = 0.12;
    private static final double WILD_SPEED = 0.07;
    private static final int SEARCH_RADIUS = 96;
    private static final int SEARCH_EVERY = 40;
    private final Map<LivingEntity, BlockPos> shores = new WeakHashMap<>();

    @SubscribeEvent
    public void onTick(LivingEvent.LivingTickEvent event) {
        LivingEntity elephant = event.getEntity();
        if (!ELEPHANT.equals(elephant.getClass().getName())) {
            return;
        }
        if (!elephant.m_20069_()) {
            shores.remove(elephant);
            return;
        }
        Vec3 v = elephant.m_20184_();
        double vx = v.f_82479_, vy = v.f_82480_, vz = v.f_82481_;
        if (elephant.f_19862_) {
            vy = Math.max(vy, 0.32);                                         // swam into the bank: up and over
        }
        LivingEntity rider = elephant.m_6688_();
        if (rider instanceof Player player) {
            double forward = player.f_20902_, strafe = player.f_20900_;
            double length = Math.hypot(forward, strafe);
            if (length > 0) {
                double yaw = Math.toRadians(player.m_146908_());
                double dx = (strafe * Math.cos(yaw) - forward * Math.sin(yaw)) / length;
                double dz = (strafe * Math.sin(yaw) + forward * Math.cos(yaw)) / length;
                vx = dx * RIDDEN_SPEED;
                vz = dz * RIDDEN_SPEED;
            }
        } else if (rider == null && !elephant.m_9236_().f_46443_) {
            BlockPos shore = shores.get(elephant);
            if (shore == null || elephant.f_19797_ % SEARCH_EVERY == 0) {
                shore = nearestShore(elephant);
                if (shore == null) {
                    shores.remove(elephant);
                } else {
                    shores.put(elephant, shore);
                }
            }
            if (shore != null) {
                double dx = shore.m_123341_() + 0.5 - elephant.m_20185_(), dz = shore.m_123343_() + 0.5 - elephant.m_20189_();
                double length = Math.hypot(dx, dz);
                if (length > 0.5) {
                    vx = dx / length * WILD_SPEED;
                    vz = dz / length * WILD_SPEED;
                    elephant.m_146922_((float) Math.toDegrees(Math.atan2(-dx, dz)));
                    elephant.f_20883_ = elephant.m_146908_();
                }
            }
        }
        elephant.m_20334_(vx, vy, vz);
    }

    /**
     * The closest dry shore within SEARCH_RADIUS: a column whose top block is land, not water (the ocean-floor and
     * motion-blocking heightmaps agree; grass and flowers count for neither), a few blocks above or below the elephant.
     * Height maps only, so even a wide lake is cheap to search; loaded chunks only.
     */
    private static BlockPos nearestShore(LivingEntity elephant) {
        Level level = elephant.m_9236_();
        int ex = (int) Math.floor(elephant.m_20185_()), ez = (int) Math.floor(elephant.m_20189_());
        int ey = (int) Math.floor(elephant.m_20186_());
        for (int r = 2; r <= SEARCH_RADIUS; r += 2) {
            for (int dx = -r; dx <= r; dx += 2) {
                for (int dz = -r; dz <= r; dz += 2) {
                    if (Math.abs(dx) != r && Math.abs(dz) != r) {
                        continue;                                            // only the ring at this distance
                    }
                    int x = ex + dx, z = ez + dz;
                    if (!level.m_7232_(x >> 4, z >> 4)) {
                        continue;
                    }
                    int floor = level.m_6924_(Heightmap.Types.OCEAN_FLOOR, x, z);
                    int surface = level.m_6924_(Heightmap.Types.MOTION_BLOCKING, x, z);
                    if (floor == surface && surface >= ey - 2 && surface <= ey + 4) {
                        return new BlockPos(x, surface, z);
                    }
                }
            }
        }
        return null;
    }
}
