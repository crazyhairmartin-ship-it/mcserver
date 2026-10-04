package fotfskills.perk;

import java.util.List;

/** The local player's active situational buffs as last sent by the server (drawn beside the inventory). */
public final class ClientBuffs {
    private static volatile List<String> lines = List.of();

    private ClientBuffs() {
    }

    public static List<String> get() {
        return lines;
    }

    static void set(List<String> values) {
        lines = List.copyOf(values);
    }
}
