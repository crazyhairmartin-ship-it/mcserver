package fotfskills.perk;

/** Homing arrows keep their speed and turn toward the target. Run: sh test.sh */
public final class HomingTest {
    public static void main(String[] args) {
        double[] v = Homing.steer(new double[] {2, 0, 0}, new double[] {0, 0, 5}, 0);
        check(close(v[0], 2) && close(v[2], 0), "turn 0 changes nothing");
        v = Homing.steer(new double[] {2, 0, 0}, new double[] {0, 0, 5}, 1);
        check(close(v[0], 0) && close(v[2], 2), "turn 1 points straight at the target at the same speed");
        v = Homing.steer(new double[] {2, 0, 0}, new double[] {0, 0, 5}, 0.5);
        check(close(Math.sqrt(v[0] * v[0] + v[2] * v[2]), 2) && v[0] > 0 && v[2] > 0, "half turn keeps speed");
        System.out.println("HomingTest ok");
    }

    private static boolean close(double a, double b) {
        return Math.abs(a - b) < 1e-9;
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
