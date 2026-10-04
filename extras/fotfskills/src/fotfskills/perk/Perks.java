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
            Map.entry("bite_speed", 0.8), Map.entry("rain_bite_speed", 0.8), Map.entry("fall_immunity", 64.0),
            Map.entry("dmg_pickaxe_blunt", 10.0), Map.entry("dmg_axe", 10.0), Map.entry("dmg_scythe", 10.0),
            Map.entry("dmg_polearm", 10.0), Map.entry("pct_two_handed", 2.0), Map.entry("pct_thrown", 2.0),
            Map.entry("pct_thrown_axe", 2.0), Map.entry("armor_pierce_axe", 0.9), Map.entry("crush_armor", 5.0),
            Map.entry("momentum", 1.0), Map.entry("flurry", 1.0), Map.entry("cleave", 1.0), Map.entry("lifeline", 4.0),
            Map.entry("grim_harvest", 6.0), Map.entry("berserker", 20.0), Map.entry("hunters_mark", 1.0),
            Map.entry("shield_bash", 2.0), Map.entry("counter", 2.0), Map.entry("shield_thorns", 0.95),
            Map.entry("second_wind", 1.0), Map.entry("spellbound_steel", 1.0), Map.entry("spellblade_mana", 10.0),
            Map.entry("battlemage_mana", 20.0), Map.entry("projectile_speed", 1.0), Map.entry("thrown_speed", 1.0),
            Map.entry("jump_boost", 0.5), Map.entry("forest_speed", 1.0), Map.entry("forest_toughness", 10.0),
            Map.entry("combat_speed", 1.0), Map.entry("skirmish_speed", 1.0), Map.entry("stonehide", 10.0),
            Map.entry("iron_stomach", 20.0), Map.entry("earthbound", 5.0), Map.entry("tide_spell", 1.0),
            Map.entry("warded_spell", 1.0), Map.entry("gem_spell", 1.0), Map.entry("staff_spell", 1.0),
            Map.entry("staff_cooldown", 1.0), Map.entry("feast_spell", 1.0), Map.entry("brain_regen", 2.0),
            Map.entry("duelist_speed", 1.0), Map.entry("light_speed", 1.0), Map.entry("seas_blessing", 1.0));

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
