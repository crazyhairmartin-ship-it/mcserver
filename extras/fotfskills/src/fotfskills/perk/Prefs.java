package fotfskills.perk;

import java.util.HashSet;
import java.util.Set;
import java.util.UUID;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;

/** Per-player settings that survive restarts (saved with the overworld): who turned level-up messages off. */
public final class Prefs extends SavedData {
    private static final String NAME = "fotfskills_prefs";
    private final Set<UUID> quietLevelUps = new HashSet<>();

    public static Prefs of(MinecraftServer server) {
        return server.m_129783_().m_8895_().m_164861_(Prefs::load, Prefs::new, NAME);
    }

    private static Prefs load(CompoundTag tag) {
        Prefs prefs = new Prefs();
        ListTag list = tag.m_128437_("quiet", 8);
        for (int i = 0; i < list.size(); i++) {
            prefs.quietLevelUps.add(UUID.fromString(list.m_128778_(i)));
        }
        return prefs;
    }

    @Override
    public CompoundTag m_7176_(CompoundTag tag) {
        ListTag list = new ListTag();
        quietLevelUps.forEach(id -> list.add(StringTag.m_129297_(id.toString())));
        tag.m_128365_("quiet", list);
        return tag;
    }

    public boolean levelUpsOn(UUID player) {
        return !quietLevelUps.contains(player);
    }

    public void setLevelUps(UUID player, boolean on) {
        boolean changed = on ? quietLevelUps.remove(player) : quietLevelUps.add(player);
        if (changed) {
            m_77762_();
        }
    }
}
