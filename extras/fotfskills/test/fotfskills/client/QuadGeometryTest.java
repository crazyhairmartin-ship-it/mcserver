package fotfskills.client;

/** Trimming and shifting model faces for the banister corners (pure maths, no game classes). Run: sh test.sh */
public final class QuadGeometryTest {
    public static void main(String[] args) {
        // the south face of a rail running the whole block (x 0..1) at z = 1, y 0.75..1, texture u 0..16
        float[][] rail = {{0, 1, 1, 0, 0}, {0, 0.75f, 1, 0, 4}, {1, 0.75f, 1, 16, 4}, {1, 1, 1, 16, 0}};
        float[][] end = QuadGeometry.clip(rail, QuadGeometry.X, 0.75f, 1);
        check(end != null, "the corner end of the rail is kept");
        check(min(end, 0) == 0.75f && max(end, 0) == 1, "trimmed to x 0.75..1");
        check(min(end, 3) == 12 && max(end, 3) == 16, "texture follows: u 12..16 (no stretching)");
        check(min(end, 1) == 0.75f && max(end, 1) == 1, "height unchanged");

        check(QuadGeometry.clip(rail, QuadGeometry.X, 1.2f, 2) == null, "nothing left: dropped");

        // a face square to the clip axis survives only inside the range
        float[][] cap = {{1, 1, 0.75f, 0, 0}, {1, 0.75f, 0.75f, 0, 4}, {1, 0.75f, 1, 4, 4}, {1, 1, 1, 4, 0}};
        check(QuadGeometry.clip(cap, QuadGeometry.X, 0.75f, 1) != null, "end cap at x = 1 stays");
        check(QuadGeometry.clip(cap, QuadGeometry.X, 0, 0.75f) == null, "end cap outside the range goes");

        float[][] moved = QuadGeometry.shift(rail, QuadGeometry.Z, -0.25f);
        check(min(moved, 2) == 0.75f && min(moved, 3) == 0, "shift moves the face, keeps its texture");
        check(QuadGeometry.extent(rail, QuadGeometry.X) == 1 && QuadGeometry.centre(rail, QuadGeometry.X) == 0.5f,
                "extent and centre along an axis");
        // a post face spanning z 10.5..13.5 (px) reaches into a rail band at z 12..16; one at z 2.5..5.5 doesn't
        float[][] nearPost = {{1, 0, 10.5f / 16, 0, 0}, {1, 0.25f, 10.5f / 16, 0, 4}, {1, 0.25f, 13.5f / 16, 3, 4}, {1, 0, 13.5f / 16, 3, 0}};
        float[][] farPost = {{1, 0, 2.5f / 16, 0, 0}, {1, 0.25f, 2.5f / 16, 0, 4}, {1, 0.25f, 5.5f / 16, 3, 4}, {1, 0, 5.5f / 16, 3, 0}};
        check(QuadGeometry.reaches(nearPost, QuadGeometry.Z, 0.75f, 1), "post near the corner reaches into the rail band");
        check(!QuadGeometry.reaches(farPost, QuadGeometry.Z, 0.75f, 1), "far post stays clear of the rail band");
        check(QuadGeometry.reaches(cap, QuadGeometry.X, 0.75f, 1), "an end cap on the band's edge counts as inside");
        check(!QuadGeometry.reaches(cap, QuadGeometry.X, 0, 0.75f), "touching the band's edge from outside doesn't");
        System.out.println("QuadGeometryTest ok");
    }

    private static float min(float[][] q, int i) {
        float m = Float.MAX_VALUE;
        for (float[] v : q) m = Math.min(m, v[i]);
        return m;
    }

    private static float max(float[][] q, int i) {
        float m = -Float.MAX_VALUE;
        for (float[] v : q) m = Math.max(m, v[i]);
        return m;
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
