package fotfskills.perk;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/**
 * Double Jump's landing: once a player double-jumps, only the drop below the height they took off from counts as a fall,
 * so a full double jump back onto the same ground is safe while jumping off a cliff still hurts like the cliff.
 * Pure state (no game classes); CombatPerks feeds it the take-off height and the landing.
 */
public final class DoubleJumpLanding {
    private final Map<UUID, Float> takeoff = new HashMap<>();
    private final Set<UUID> jumped = new HashSet<>();

    /** The player is standing on the ground at this height: their next take-off height. */
    public synchronized void ground(UUID player, float y) {
        takeoff.put(player, y);
        jumped.remove(player);
    }

    public synchronized void jumped(UUID player) {
        jumped.add(player);
    }

    /** The fall distance to use for this landing. */
    public synchronized float fall(UUID player, float distance, float landY) {
        Float from = takeoff.get(player);
        if (!jumped.remove(player) || from == null) {
            return distance;
        }
        return Math.min(distance, Math.max(0, from - landY));
    }

    public synchronized void forget(UUID player) {
        takeoff.remove(player);
        jumped.remove(player);
    }
}
