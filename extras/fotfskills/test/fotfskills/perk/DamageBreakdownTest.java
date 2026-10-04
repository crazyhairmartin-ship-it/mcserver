package fotfskills.perk;

import java.util.Map;
import java.util.Set;

/** The weapon tooltip's damage math: flat bonuses add up, then percent bonuses multiply. Run: sh test.sh */
public final class DamageBreakdownTest {
    public static void main(String[] args) {
        Map<String, Double> perks = Map.of("dmg_axe", 1.5, "pct_two_handed", 0.3, "dmg_scythe", 0.9);
        DamageBreakdown axe = DamageBreakdown.of(9.0, 0.6, 1.0, Set.of("axe"), p -> perks.getOrDefault(p, 0.0));
        check(Math.abs(axe.total() - 12.1) < 1e-9, "axe: 9 weapon + 0.6 Sharpened + 1 Sharpness + 1.5 Axe Mastery = 12.1, got " + axe.total());
        check(axe.lines().stream().anyMatch(l -> l.contains("Axe Mastery") && l.contains("+1.5")), "names the axe node: " + axe.lines());
        check(axe.lines().stream().noneMatch(l -> l.contains("Reaper")), "scythe bonus not listed for an axe");

        DamageBreakdown greatsword = DamageBreakdown.of(10.0, 0, 0, Set.of("two_handed", "sword"), p -> perks.getOrDefault(p, 0.0));
        check(Math.abs(greatsword.total() - 13.0) < 1e-9, "two-handed: 10 x 1.3 = 13, got " + greatsword.total());
        check(greatsword.lines().stream().anyMatch(l -> l.contains("Heavy Arms") && l.contains("+30%")), "percent line: " + greatsword.lines());

        DamageBreakdown plain = DamageBreakdown.of(4.0, 0, 0, Set.of("sword"), p -> 0.0);
        check(plain.total() == 4.0 && plain.lines().size() == 1, "no perks: just the weapon line");
        System.out.println("DamageBreakdownTest ok");
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
