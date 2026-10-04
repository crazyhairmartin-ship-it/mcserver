package fotfskills.mana;

import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Shared mana between Ars Nouveau and Iron's Spells: Iron's mana is the one pool. Active whenever both mods are installed
 * (set by FotfSkills). The Ars mixins record what Ars computes for each player's max mana and regen; ManaMergeTicker
 * turns the part above Ars's base into Iron's bonuses.
 */
public final class ManaMerge {
    private static volatile boolean active;
    private static final Map<UUID, Integer> ARS_MAX = new ConcurrentHashMap<>();
    private static final Map<UUID, Double> ARS_REGEN = new ConcurrentHashMap<>();

    private ManaMerge() {
    }

    public static boolean active() {
        return active;
    }

    public static void activate() {
        active = true;
    }

    public static void recordArsMax(UUID player, int max) {
        ARS_MAX.put(player, max);
    }

    public static void recordArsRegen(UUID player, double perSecond) {
        ARS_REGEN.put(player, perSecond);
    }

    static Integer arsMax(UUID player) {
        return ARS_MAX.get(player);
    }

    static Double arsRegen(UUID player) {
        return ARS_REGEN.get(player);
    }

    static void forget(UUID player) {
        ARS_MAX.remove(player);
        ARS_REGEN.remove(player);
    }
}
