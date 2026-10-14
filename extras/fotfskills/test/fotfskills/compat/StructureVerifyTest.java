package fotfskills.compat;

import java.util.List;

/** The structure checker's pure parts: reading the block list and summing up copies. Run: sh test.sh */
public final class StructureVerifyTest {
    public static void main(String[] args) {
        check(StructureVerify.keys("minecraft:bell, #minecraft:buttons ,containers").equals(
                List.of("minecraft:bell", "#minecraft:buttons", "containers")), "keys split on commas and trimmed");
        check(StructureVerify.keys("").isEmpty(), "no keys from an empty string");
        int[][] copies = {{2, 5, 9}, {1, 7, 3}, {4, 0, 6}};
        int[] min = StructureVerify.fewest(copies, 3);
        check(min[0] == 1 && min[1] == 0 && min[2] == 3, "the summary is the fewest any copy had");
        check(StructureVerify.fewest(new int[0][], 2)[0] == 0, "no copies found means zero");
        System.out.println("StructureVerifyTest ok");
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
