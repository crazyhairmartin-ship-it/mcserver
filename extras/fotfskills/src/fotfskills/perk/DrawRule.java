package fotfskills.perk;

/**
 * Steady Hands / Rapid Volley: extra draw progress for this tick, worked out from progress alone so the client
 * (bow animation) and the server (arrow power) always agree. Progress then runs (1 + rate) times as fast.
 */
public final class DrawRule {
    private DrawRule() {
    }

    public static int extra(int elapsed, double rate) {
        if (rate <= 0) {
            return 0;
        }
        double step = rate / (1 + rate);
        return (int) Math.floor((elapsed + 1) * step) - (int) Math.floor(elapsed * step);
    }
}
