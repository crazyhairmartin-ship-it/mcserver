package fotfskills.perk;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.function.ToDoubleFunction;

/** Per-player perk totals: each unlocked reward (source) contributes a value to one perk; totals are capped. */
public final class PerkTotals {
    private record Part(String perk, double value) {
    }

    private final Map<UUID, Map<Object, Part>> parts = new HashMap<>();
    private final ToDoubleFunction<String> caps;

    public PerkTotals(ToDoubleFunction<String> caps) {
        this.caps = caps;
    }

    public synchronized void put(UUID player, Object source, String perk, double value) {
        Map<Object, Part> map = parts.computeIfAbsent(player, id -> new HashMap<>());
        if (value == 0) {
            map.remove(source);
        } else {
            map.put(source, new Part(perk, value));
        }
    }

    public synchronized void removeSource(Object source) {
        parts.values().forEach(map -> map.remove(source));
    }

    public synchronized void removePlayer(UUID player) {
        parts.remove(player);
    }

    public synchronized double total(UUID player, String perk) {
        double sum = 0;
        for (Part part : parts.getOrDefault(player, Map.of()).values()) {
            if (part.perk.equals(perk)) {
                sum += part.value;
            }
        }
        return Math.min(sum, caps.applyAsDouble(perk));
    }

    /** Every active perk's capped total, for syncing to the client. */
    public synchronized Map<String, Double> snapshot(UUID player) {
        Map<String, Double> out = new HashMap<>();
        for (Part part : parts.getOrDefault(player, Map.of()).values()) {
            out.merge(part.perk, part.value, Double::sum);
        }
        out.replaceAll((perk, sum) -> Math.min(sum, caps.applyAsDouble(perk)));
        return out;
    }
}
