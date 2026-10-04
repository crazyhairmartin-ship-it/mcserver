package fotfskills.perk;

import java.util.ArrayList;
import java.util.List;
import java.util.function.BiConsumer;
import net.minecraft.server.level.ServerPlayer;

/** Gives mana in whichever magic mods are installed (bridges registered by FotfSkills when the mod is loaded). */
public final class Mana {
    private static final List<BiConsumer<ServerPlayer, Double>> BRIDGES = new ArrayList<>();

    private Mana() {
    }

    public static void register(BiConsumer<ServerPlayer, Double> bridge) {
        BRIDGES.add(bridge);
    }

    public static void add(ServerPlayer player, double amount) {
        if (amount > 0) {
            BRIDGES.forEach(bridge -> bridge.accept(player, amount));
        }
    }

    private static final List<java.util.function.BiPredicate<ServerPlayer, Double>> SPENDERS = new ArrayList<>();

    public static void registerSpender(java.util.function.BiPredicate<ServerPlayer, Double> spender) {
        SPENDERS.add(spender);
    }

    /** Takes amount from the first magic mod that has that much; false if none does. */
    public static boolean spend(ServerPlayer player, double amount) {
        for (var spender : SPENDERS) {
            if (spender.test(player, amount)) {
                return true;
            }
        }
        return false;
    }
}
