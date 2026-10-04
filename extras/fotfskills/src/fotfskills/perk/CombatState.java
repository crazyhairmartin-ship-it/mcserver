package fotfskills.perk;

import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import net.minecraft.server.level.ServerPlayer;

/** Per-player combat timestamps (game ticks) and streaks. Cleared on logout (WeaponPerks). */
public final class CombatState {
    private static final Map<UUID, CombatState> STATES = new ConcurrentHashMap<>();
    public long lastCombat = -100000, lastShot = -100000, lastBlock = -100000, lastCast = -100000;
    public long lastStoneMined = -100000, lastMeal = -100000;
    public boolean counterReady;
    public final Streak momentum = new Streak(60, 3);
    public final Streak flurry = new Streak(40, 5);
    public final Cooldown secondWind = new Cooldown(6000);
    public UUID markedTarget;
    public long markedUntil;

    public static CombatState of(ServerPlayer player) {
        return STATES.computeIfAbsent(player.m_20148_(), id -> new CombatState());
    }

    public static long now(ServerPlayer player) {
        return player.m_9236_().m_46467_();
    }

    public static void forget(UUID player) {
        STATES.remove(player);
    }
}
