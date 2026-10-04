package fotfskills.perk;

import java.util.HashMap;
import java.util.Map;

/** The local player's perk totals as last sent by the server (PerkSync). */
public final class ClientPerks {
    private static volatile Map<String, Double> totals = Map.of();

    private ClientPerks() {
    }

    static double get(String perk) {
        return totals.getOrDefault(perk, 0.0);
    }

    static void set(Map<String, Double> values) {
        totals = new HashMap<>(values);
    }
}
