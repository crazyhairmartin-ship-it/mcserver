package fotfskills.compat;

/** Ore Scenting's outline lasts half as long again (Domestication Innovation: 50 ticks per level). Run: sh test.sh */
public final class OreScentOutlineTest {
    public static void main(String[] args) {
        check(OreScentOutline.lifespan(50) == 75, "level I: 2.5 s -> 3.75 s");
        check(OreScentOutline.lifespan(150) == 225, "level III: 7.5 s -> 11.25 s");
        check(OreScentOutline.lifespan(0) == 0, "nothing stays nothing");
        System.out.println("OreScentOutlineTest ok");
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
