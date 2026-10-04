package fotfskills.perk;

import java.util.Map;
import java.util.concurrent.ThreadLocalRandom;
import net.minecraft.world.entity.player.Player;

/**
 * Perk ids, their caps, and every player's totals. Server totals come from PerkReward; the client reads the
 * copy PerkSync sends (only break speed needs it). tools/skills/perks.json may only use ids listed here.
 */
public final class Perks {
    public static final Map<String, Double> CAPS = Map.ofEntries(
            Map.entry("ore_drops", 0.95), Map.entry("ore_triple", 0.95), Map.entry("log_drops", 0.95),
            Map.entry("crop_drops", 0.95), Map.entry("harvest_double", 0.95), Map.entry("wild_drops", 0.95),
            Map.entry("bounty_triple", 0.95), Map.entry("seed_back", 0.95),
            Map.entry("pickaxe_durability", 0.95), Map.entry("armour_durability", 0.95),
            Map.entry("craft_save", 0.95), Map.entry("craft_free", 0.95), Map.entry("craft_arrows", 0.95),
            Map.entry("extra_serving", 0.95), Map.entry("double_catch", 0.95), Map.entry("animal_drops", 0.95),
            Map.entry("ammo_save", 0.95), Map.entry("treat_saver", 0.95), Map.entry("free_spell", 0.95),
            Map.entry("mining_speed", 2.0), Map.entry("deepslate_speed", 2.0), Map.entry("chop_speed", 2.0),
            Map.entry("draw_speed", 1.0), Map.entry("crit_damage", 2.0), Map.entry("projectile_damage", 2.0),
            Map.entry("executioner", 2.0), Map.entry("well_fed", 2.0), Map.entry("deep_delver", 2.0),
            Map.entry("fire_ward", 0.9), Map.entry("blast_ward", 0.9), Map.entry("fall_reduction", 0.9),
            Map.entry("bite_speed", 0.8), Map.entry("rain_bite_speed", 0.8), Map.entry("fall_immunity", 64.0));

    public static final PerkTotals TOTALS = new PerkTotals(perk -> CAPS.getOrDefault(perk, 0.0));

    private Perks() {
    }

    public static double get(Player player, String perk) {
        if (player.m_9236_().f_46443_) {
            return Math.min(ClientPerks.get(perk), CAPS.getOrDefault(perk, 0.0));
        }
        return TOTALS.total(player.m_20148_(), perk);
    }

    public static boolean roll(Player player, String perk) {
        double chance = get(player, perk);
        return chance > 0 && ThreadLocalRandom.current().nextDouble() < chance;
    }

    public static double random() {
        return ThreadLocalRandom.current().nextDouble();
    }
}
