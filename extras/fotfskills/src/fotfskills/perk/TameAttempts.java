package fotfskills.perk;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * Gentle Hand's trigger: a player right-clicked a wild tamable animal (tried) and, in that same tick, the animal showed
 * vanilla's "taming failed" smoke (entity event 6). Leashing, name tags or dropping items never produce that signal.
 */
public final class TameAttempts {
    private record Attempt(UUID player, long tick) {
    }

    private final Map<UUID, Attempt> byAnimal = new HashMap<>();

    public synchronized void tried(UUID animal, UUID player, long tick) {
        byAnimal.put(animal, new Attempt(player, tick));
        if (byAnimal.size() > 256) {
            byAnimal.values().removeIf(a -> tick - a.tick > 20);
        }
    }

    /** The player whose attempt just failed, or null; each attempt rolls at most once. */
    public synchronized UUID failed(UUID animal, byte entityEvent, long tick) {
        if (entityEvent != 6) {
            return null;
        }
        Attempt attempt = byAnimal.get(animal);
        if (attempt == null || attempt.tick != tick) {
            return null;
        }
        byAnimal.remove(animal);
        return attempt.player;
    }
}
