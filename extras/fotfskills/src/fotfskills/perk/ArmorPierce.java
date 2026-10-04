package fotfskills.perk;

/** Damage multiplier for ignoring part of the target's armour (vanilla CombatRules.getDamageAfterAbsorb). */
public final class ArmorPierce {
    private ArmorPierce() {
    }

    public static double multiplier(double armor, double toughness, double damage, double pierce) {
        if (armor <= 0 || pierce <= 0 || damage <= 0) {
            return 1;
        }
        double full = afterArmor(armor, toughness, damage);
        return full <= 0 ? 1 : afterArmor(armor * (1 - Math.min(pierce, 1)), toughness, damage) / full;
    }

    private static double afterArmor(double armor, double toughness, double damage) {
        double t = 2 + toughness / 4;
        double effective = Math.max(Math.min(armor - damage / t, 20), armor * 0.2);
        return damage * (1 - Math.min(effective, 20) / 25);
    }
}
