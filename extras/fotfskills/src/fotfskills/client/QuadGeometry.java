package fotfskills.client;

/**
 * Maths on one model face (a quad): 4 corners of {x, y, z, u, v}, positions in block units (0..1). Model faces are
 * axis-aligned rectangles, so trimming one along an axis moves the corners on the cut side to the cut and slides their
 * texture coordinates the same fraction toward the opposite corner, so the texture isn't stretched. Used by
 * BanisterCornerModels.
 */
public final class QuadGeometry {
    public static final int X = 0;
    public static final int Y = 1;
    public static final int Z = 2;
    private static final float EPS = 1.0e-4f;

    private QuadGeometry() {
    }

    public static float extent(float[][] quad, int axis) {
        return max(quad, axis) - min(quad, axis);
    }

    public static float centre(float[][] quad, int axis) {
        return (max(quad, axis) + min(quad, axis)) / 2;
    }

    /** Whether the face reaches into lo..hi along the axis (a flat face counts when it lies within it). */
    public static boolean reaches(float[][] quad, int axis, float lo, float hi) {
        float a = min(quad, axis), b = max(quad, axis);
        if (b - a < EPS) {
            return a >= lo - EPS && a <= hi + EPS;
        }
        return b > lo + EPS && a < hi - EPS;
    }

    /** The part of the face with lo <= axis <= hi, or null if none of it is there. */
    public static float[][] clip(float[][] quad, int axis, float lo, float hi) {
        float a = min(quad, axis);
        float b = max(quad, axis);
        if (b - a < EPS) {                                   // face square to the axis: all or nothing
            return a >= lo - EPS && a <= hi + EPS ? copy(quad) : null;
        }
        if (b <= lo + EPS || a >= hi - EPS) {
            return null;
        }
        float newA = Math.max(a, lo);
        float newB = Math.min(b, hi);
        float[][] out = copy(quad);
        for (int i = 0; i < 4; i++) {
            float c = quad[i][axis];
            float target = Math.abs(c - a) < EPS ? newA : newB;
            if (Math.abs(target - c) < EPS) {
                continue;
            }
            float[] partner = partner(quad, i, axis);
            float frac = (target - c) / (partner[axis] - c);
            out[i][axis] = target;
            out[i][3] = quad[i][3] + (partner[3] - quad[i][3]) * frac;
            out[i][4] = quad[i][4] + (partner[4] - quad[i][4]) * frac;
        }
        return out;
    }

    /** The face moved along an axis; the texture moves with it. */
    public static float[][] shift(float[][] quad, int axis, float by) {
        float[][] out = copy(quad);
        for (float[] v : out) {
            v[axis] += by;
        }
        return out;
    }

    /** The corner across the face from corner i along the axis (same position on the other two axes). */
    private static float[] partner(float[][] quad, int i, int axis) {
        for (int j = 0; j < 4; j++) {
            if (j == i) {
                continue;
            }
            boolean same = true;
            for (int k = 0; k < 3; k++) {
                if (k != axis && Math.abs(quad[j][k] - quad[i][k]) > EPS) {
                    same = false;
                }
            }
            if (same && Math.abs(quad[j][axis] - quad[i][axis]) > EPS) {
                return quad[j];
            }
        }
        return quad[i];
    }

    private static float min(float[][] quad, int axis) {
        float m = Float.MAX_VALUE;
        for (float[] v : quad) {
            m = Math.min(m, v[axis]);
        }
        return m;
    }

    private static float max(float[][] quad, int axis) {
        float m = -Float.MAX_VALUE;
        for (float[] v : quad) {
            m = Math.max(m, v[axis]);
        }
        return m;
    }

    private static float[][] copy(float[][] quad) {
        float[][] out = new float[4][];
        for (int i = 0; i < 4; i++) {
            out[i] = quad[i].clone();
        }
        return out;
    }
}
