package fotfskills.xp;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/** Caps Defense XP per (player, attacker) per window of ticks, so a caged mob can't be farmed. Self hits never count. */
public final class HitLimiter {
    private record Key(UUID player, UUID attacker) {
    }

    private static final class Window {
        long start;
        double used;
    }

    private final double cap;
    private final long windowTicks;
    private final Map<Key, Window> windows = new HashMap<>();

    public HitLimiter(double cap, long windowTicks) {
        this.cap = cap;
        this.windowTicks = windowTicks;
    }

    /** How much of this hit's damage still earns XP. */
    public synchronized double grant(UUID player, UUID attacker, double amount, long now) {
        if (player.equals(attacker) || amount <= 0) {
            return 0;
        }
        if (windows.size() > 4096) {
            windows.values().removeIf(w -> now - w.start > windowTicks);
        }
        Window w = windows.computeIfAbsent(new Key(player, attacker), k -> new Window());
        if (now - w.start > windowTicks) {
            w.start = now;
            w.used = 0;
        }
        double granted = Math.min(amount, cap - w.used);
        w.used += Math.max(granted, 0);
        return Math.max(granted, 0);
    }

    public synchronized void removePlayer(UUID player) {
        windows.keySet().removeIf(k -> k.player.equals(player));
    }
}
