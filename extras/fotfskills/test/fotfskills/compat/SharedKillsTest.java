package fotfskills.compat;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/** Quest kill credit shared with helpers and party members, and puzzle blocks placed by players. Run: sh test.sh */
public final class SharedKillsTest {
    public static void main(String[] args) {
        UUID killer = UUID.randomUUID(), helper = UUID.randomUUID(), stale = UUID.randomUUID(),
                far = UUID.randomUUID(), friend = UUID.randomUUID();
        Map<UUID, Long> hits = new HashMap<>();
        hits.put(killer, 1000L);
        hits.put(helper, 990L);          // hit it 10 ticks before it died
        hits.put(stale, 300L);           // hit it long ago
        hits.put(far, 995L);             // hit it, but has wandered off
        Set<UUID> nearby = Set.of(killer, helper, stale, friend);
        Set<UUID> party = Set.of(friend);
        Set<UUID> got = SharedKills.creditees(killer, hits, 1000L, 600L, nearby, party);
        check(got.contains(helper), "a recent helper nearby gets the kill");
        check(!got.contains(stale), "a hit older than the window doesn't count");
        check(!got.contains(far), "a helper out of range doesn't count");
        check(got.contains(friend), "a party member in range gets it without hitting");
        check(!got.contains(killer), "the killer already got it from FTB Quests");
        check(SharedKills.creditees(killer, Map.of(), 1000L, 600L, Set.of(killer), Set.of()).isEmpty(),
                "a solo kill shares with nobody");

        List<QuestProtect.Rule> rules = QuestProtect.parse("[{\"structures\": [\"a:b\"], \"blocks\": [\"minecraft:sea_lantern\"],"
                + " \"reset\": 600}, {\"structures\": [\"a:c\"], \"blocks\": [\"minecraft:lever\"]}]");
        check(rules.get(0).resetSeconds() == 600 && rules.get(1).resetSeconds() == 0, "reset seconds parsed, default 0");

        PlacedBlocks placed = new PlacedBlocks();
        placed.add("minecraft:overworld", 42L, 100L);
        placed.add("minecraft:overworld", 43L, 500L);
        check(placed.contains("minecraft:overworld", 42L) && !placed.contains("minecraft:the_nether", 42L),
                "placed blocks are kept per dimension");
        List<PlacedBlocks.Entry> due = placed.takeDue(450L);
        check(due.size() == 1 && due.get(0).pos() == 42L, "only blocks whose time has come are taken");
        check(!placed.contains("minecraft:overworld", 42L) && placed.contains("minecraft:overworld", 43L),
                "taken blocks are forgotten, the rest stay");
        check(placed.takeAll().size() == 1 && placed.takeAll().isEmpty(), "takeAll empties it (server stopping)");
        System.out.println("SharedKillsTest ok");
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
