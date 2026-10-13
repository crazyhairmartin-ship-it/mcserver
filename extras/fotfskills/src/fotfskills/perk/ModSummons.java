package fotfskills.perk;

import net.minecraft.world.entity.Entity;

/** Summoner lookups for Artificer, one per mod; each method is only called when its mod is loaded. */
public final class ModSummons {
    private ModSummons() {
    }

    public static Entity irons(Entity entity) {
        return entity instanceof io.redspace.ironsspellbooks.entity.mobs.IMagicSummon summon ? summon.getSummoner() : null;
    }
}
