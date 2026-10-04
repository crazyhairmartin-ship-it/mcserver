package fotfskills.perk;

import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.function.Function;

/**
 * A weapon's damage per swing with your skills, the same way WeaponPerks applies them: flat bonuses add up (weapon,
 * attack from skills, enchantments, the weapon type's node), then percent bonuses multiply. Situational bonuses
 * (Momentum, Counter, crits...) aren't included. Lines are for the weapon tooltip's breakdown.
 */
public record DamageBreakdown(double total, List<String> lines) {
    private record Flat(String perk, String type, String label) {
    }

    private static final Flat[] FLATS = {
        new Flat("dmg_pickaxe_blunt", "pickaxe", "Miner's Might (Mining)"),
        new Flat("dmg_pickaxe_blunt", "blunt", "Miner's Might (Mining)"),
        new Flat("dmg_axe", "axe", "Axe Mastery (Foraging)"),
        new Flat("dmg_scythe", "scythe", "Reaper (Farming)"),
        new Flat("dmg_polearm", "polearm", "Trident Master (Fishing)"),
    };

    public static DamageBreakdown of(double weapon, double skillAttack, double enchant, Set<String> types,
                                     Function<String, Double> perk) {
        List<String> lines = new ArrayList<>();
        double flat = weapon;
        lines.add("Weapon: " + fmt(weapon));
        if (skillAttack > 0) {
            flat += skillAttack;
            lines.add("Sharpened (Attack): +" + fmt(skillAttack));
        }
        if (enchant > 0) {
            flat += enchant;
            lines.add("Enchantments: +" + fmt(enchant));
        }
        java.util.Set<String> counted = new java.util.HashSet<>();
        for (Flat f : FLATS) {
            double v = perk.apply(f.perk);
            if (v > 0 && types.contains(f.type) && counted.add(f.perk)) {
                flat += v;
                lines.add(f.label + ": +" + fmt(v));
            }
        }
        double pct = 0;
        if (types.contains("two_handed") && perk.apply("pct_two_handed") > 0) {
            pct += perk.apply("pct_two_handed");
            lines.add("Heavy Arms (Attack): +" + Math.round(perk.apply("pct_two_handed") * 100) + "%");
        }
        return new DamageBreakdown(flat * (1 + pct), lines);
    }

    /** Special attacks (weapon abilities) scale by the ratio the weapon type's perks give a swing. */
    public static double abilityMultiplier(double weapon, Set<String> types, Function<String, Double> perk) {
        return weapon <= 0 ? 1.0 : of(weapon, 0, 0, types, perk).total() / weapon;
    }

    public static String fmt(double v) {
        double r = Math.round(v * 10) / 10.0;
        return r == Math.floor(r) ? String.valueOf((long) r) : String.valueOf(r);
    }
}
