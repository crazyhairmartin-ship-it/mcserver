package fotfskills.perk;

/** Tunnel Vision: Ultimine's hunger cost shrinks by the perk's fraction, never by more than 90%. */
public final class Tunnel {
    private Tunnel() {
    }

    public static float scale(float exhaustion, double perk) {
        return (float) (exhaustion * (1 - Math.min(perk, 0.9)));
    }
}
