package fotfskills.perk;

import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Level-up messages only for a level the player hasn't been told about yet. Pufferfish's new-point event also fires
 * when points come back (tree reset) or are granted by an admin, without any new level.
 */
public final class LevelGate {
    private final Map<String, Integer> announced = new ConcurrentHashMap<>();

    public boolean announce(UUID player, String skill, int level) {
        String key = player + "/" + skill;
        Integer last = announced.get(key);
        if (last != null && level <= last) {
            return false;
        }
        announced.put(key, level);
        return true;
    }
}
