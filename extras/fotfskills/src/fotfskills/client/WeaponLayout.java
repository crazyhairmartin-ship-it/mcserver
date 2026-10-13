package fotfskills.client;

/**
 * Which hotbar item Weapon Master shows in each of its nine display slots, so weapons sit where their type belongs:
 * back weapons (two-handed, polearms, scythes, bows, staffs) in the slots attached to the body, hip weapons (swords,
 * light weapons, axes, blunt, thrown) in the slots attached to the legs. Weapon Master still positions, toggles and
 * moves by display slot; this only decides which item fills each one. Pure logic; WeaponLayoutMixin feeds it.
 */
public final class WeaponLayout {
    public static final int EMPTY = 0;
    public static final int OTHER = 1;
    public static final int BACK = 2;
    public static final int HIP = 3;

    private WeaponLayout() {
    }

    /** Weapon Master's slot attachments ("1-body,2-body,3-rleg,...") as the kind of each display slot. */
    public static int[] places(String attachments) {
        int[] out = new int[9];
        java.util.Arrays.fill(out, OTHER);
        for (String part : attachments.split(",")) {
            String[] kv = part.trim().split("-");
            if (kv.length != 2) {
                continue;
            }
            try {
                int slot = Integer.parseInt(kv[0]) - 1;
                if (slot >= 0 && slot < 9) {
                    out[slot] = kv[1].equals("body") ? BACK : kv[1].endsWith("leg") ? HIP : OTHER;
                }
            } catch (NumberFormatException e) {
                // shield, banner, offhand, quiver: not hotbar slots
            }
        }
        return out;
    }

    /** For each display slot, the hotbar slot whose item shows there (a permutation of 0..8). */
    public static int[] arrange(int[] kinds, int[] places) {
        int n = kinds.length;
        int[] shown = new int[n];
        boolean[] placed = new boolean[n];
        java.util.Arrays.fill(shown, -1);
        for (int s = 0; s < n; s++) {               // weapons already in a slot of their kind, and other items, stay put
            if (kinds[s] == OTHER || (kinds[s] != EMPTY && kinds[s] == places[s])) {
                shown[s] = s;
                placed[s] = true;
            }
        }
        for (int s = 0; s < n; s++) {               // weapons in the wrong kind of slot move to a free one of their kind
            if (!placed[s] && kinds[s] != EMPTY) {
                for (int d = 0; d < n; d++) {
                    if (shown[d] < 0 && places[d] == kinds[s]) {
                        shown[d] = s;
                        placed[s] = true;
                        break;
                    }
                }
            }
        }
        for (int s = 0; s < n; s++) {               // empty slots and overflow fill what's left, their own slot first
            if (placed[s]) {
                continue;
            }
            int d = shown[s] < 0 ? s : 0;
            while (shown[d] >= 0) {
                d++;
            }
            shown[d] = s;
            placed[s] = true;
        }
        return shown;
    }

    /** The display slot showing this hotbar slot's item. */
    public static int displayOf(int[] shown, int slot) {
        for (int d = 0; d < shown.length; d++) {
            if (shown[d] == slot) {
                return d;
            }
        }
        return slot;
    }
}
