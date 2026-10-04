package fotfskills.perk;

/** Turns a projectile's velocity toward a target direction, keeping its speed. */
public final class Homing {
    private Homing() {
    }

    public static double[] steer(double[] velocity, double[] toTarget, double turn) {
        double speed = length(velocity);
        double tl = length(toTarget);
        if (speed == 0 || tl == 0 || turn <= 0) {
            return velocity.clone();
        }
        double[] out = new double[3];
        for (int i = 0; i < 3; i++) {
            out[i] = velocity[i] / speed * (1 - turn) + toTarget[i] / tl * turn;
        }
        double ol = length(out);
        for (int i = 0; i < 3; i++) {
            out[i] = ol == 0 ? velocity[i] : out[i] / ol * speed;
        }
        return out;
    }

    private static double length(double[] v) {
        return Math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]);
    }
}
