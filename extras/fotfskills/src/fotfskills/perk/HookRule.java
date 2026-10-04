package fotfskills.perk;

/**
 * Agility hook upgrades only rewrite a plain grappling hook (default settings) or one they already manage; a player's
 * existing motor/rocket/ender hook (settings stored on the same item) is left as it is.
 */
public final class HookRule {
    private HookRule() {
    }

    public static boolean shouldWrite(long currentChecksum, long defaultChecksum, boolean managedBySkills) {
        return managedBySkills || currentChecksum == defaultChecksum;
    }
}
