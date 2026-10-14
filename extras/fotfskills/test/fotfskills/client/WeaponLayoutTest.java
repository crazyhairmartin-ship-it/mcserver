package fotfskills.client;

import java.util.Arrays;

/** Weapon Master display slots chosen by weapon type: back weapons to back slots, hip weapons to hip slots. Run: sh test.sh */
public final class WeaponLayoutTest {
    private static final int E = WeaponLayout.EMPTY, N = WeaponLayout.OTHER, B = WeaponLayout.BACK, H = WeaponLayout.HIP;
    // default Weapon Master attachments: slots 1,2,7,8 on the body (back), 3-6 and 9 on the legs (hips)
    private static final int[] PLACES = WeaponLayout.places("1-body,2-body,3-rleg,4-lleg,5-rleg,6-lleg,7-body,8-body,9-rleg,shield-body,banner-head,offhand-lleg,quiver-body");

    public static void main(String[] args) {
        check(Arrays.equals(PLACES, new int[]{B, B, H, H, H, H, B, B, H}), "attachments read as back/hip");

        int[] same = WeaponLayout.arrange(new int[]{B, B, H, H, E, E, E, E, E}, PLACES);
        check(Arrays.equals(same, new int[]{0, 1, 2, 3, 4, 5, 6, 7, 8}), "already in place: nothing moves");

        // a sword in slot 1 and a greatsword in slot 3 swap places
        int[] swap = WeaponLayout.arrange(new int[]{H, E, B, E, E, E, E, E, E}, PLACES);
        check(PLACES[indexOf(swap, 2)] == B && PLACES[indexOf(swap, 0)] == H, "greatsword (slot 3) shows on the back, sword (slot 1) on a hip: " + Arrays.toString(swap));
        check(isPermutation(swap), "every slot shown once");

        // tools and blocks keep their slot when weapons don't need it
        int[] tools = WeaponLayout.arrange(new int[]{N, H, N, E, E, E, E, E, B}, PLACES);
        check(tools[2] == 2, "a tool in a hip slot stays when a free hip slot exists: " + Arrays.toString(tools));
        check(PLACES[indexOf(tools, 1)] == H && PLACES[indexOf(tools, 8)] == B, "typed items go to their kind: " + Arrays.toString(tools));

        // Dylan's hotbar: rapier (hip) in slot 1, pickaxes/grapple/blocks/food elsewhere, scythe (back) in slot 5
        int[] dylan = WeaponLayout.arrange(new int[]{H, N, N, N, B, E, N, N, N}, PLACES);
        check(PLACES[indexOf(dylan, 4)] == B, "scythe shows on the back: " + Arrays.toString(dylan));
        check(PLACES[indexOf(dylan, 0)] == H, "rapier shows on a hip: " + Arrays.toString(dylan));
        check(isPermutation(dylan), "every slot shown once");

        // back slots all held by tools: a back weapon still takes one (tools give way to weapons)
        int[] full = WeaponLayout.arrange(new int[]{N, N, E, E, B, E, N, N, E}, PLACES);
        check(PLACES[indexOf(full, 4)] == B, "back weapon displaces a tool: " + Arrays.toString(full));
        check(isPermutation(full), "every slot shown once");

        // five back weapons, four back places: the fifth shows wherever there's room
        int[] crowd = WeaponLayout.arrange(new int[]{B, B, B, B, B, E, E, E, E}, PLACES);
        check(isPermutation(crowd), "overflow still shows every slot once: " + Arrays.toString(crowd));
        int onBack = 0;
        for (int d = 0; d < 9; d++) if (PLACES[d] == B && crowd[d] < 5) onBack++;
        check(onBack == 4, "all four back places used by back weapons");

        check(swap[WeaponLayout.displayOf(swap, 2)] == 2, "the selected slot follows its item");
        System.out.println("WeaponLayoutTest ok");
    }

    private static int indexOf(int[] a, int v) { for (int i = 0; i < a.length; i++) if (a[i] == v) return i; return -1; }

    private static boolean isPermutation(int[] a) {
        boolean[] seen = new boolean[a.length];
        for (int v : a) { if (v < 0 || v >= a.length || seen[v]) return false; seen[v] = true; }
        return true;
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
