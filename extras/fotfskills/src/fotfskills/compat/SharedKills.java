package fotfskills.compat;

import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/**
 * Quest kill credit for friends questing together. FTB Quests only credits the player who lands the last hit; this
 * also credits (on their own open kill tasks) everyone who hurt the mob recently and is still nearby, and the killer's
 * Open Parties and Claims party members who are close by. Game side: SharedKillHooks.
 */
public final class SharedKills {
    private SharedKills() {}

    /**
     * Who else gets the kill. lastHit: each player's last hit on the mob (game time); a hit counts within windowTicks
     * of the death, for players in helperRange. partyInRange: the killer's party members close enough to share.
     */
    public static Set<UUID> creditees(UUID killer, Map<UUID, Long> lastHit, long now, long windowTicks,
                                      Set<UUID> helperRange, Set<UUID> partyInRange) {
        Set<UUID> out = new HashSet<>();
        lastHit.forEach((who, when) -> {
            if (now - when <= windowTicks && helperRange.contains(who)) {
                out.add(who);
            }
        });
        out.addAll(partyInRange);
        out.remove(killer);
        return out;
    }
}
