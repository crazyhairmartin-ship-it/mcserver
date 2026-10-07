package fotfskills.perk;

import net.minecraft.server.level.ServerPlayer;

/**
 * Which attack of a Better Combat combo the player's current swing is (0 = first). Better Combat sends the combo count
 * with each attack and sets it on the player while the hits land. Only called when Better Combat is loaded.
 */
final class ComboStep {
    private ComboStep() {
    }

    static int of(ServerPlayer player) {
        return player instanceof net.bettercombat.logic.PlayerAttackProperties props ? props.getComboCount() : -1;
    }
}
