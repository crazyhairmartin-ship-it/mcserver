package fotfskills.world;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.animal.Wolf;
import net.minecraft.world.level.biome.Biome;
import net.minecraftforge.common.extensions.IForgeEntity;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/**
 * More Mob Variants gave almost every wolf the default coat: its spawn biomes only listed vanilla biomes (now widened in
 * kubejs/data/moremobvariants/tags). Each wild wolf with the default coat rolls once more as it loads, the way the mod
 * does at spawn: a coat whose biome list holds the wolf's biome, or any natural coat if none does. Tamed wolves, and
 * puppies bred from their parents' coats, are left alone.
 */
public final class WolfCoats {
    private static final String DONE = "FotfCoatRolled";
    private static final String DEFAULT = "moremobvariants:default";
    /** coat -> biome tag, from More Mob Variants' data/moremobvariants/variants/wolf. */
    private static final Map<String, String> COATS = Map.of(
            "default", "moremobvariants:wolf_pale_spawns", "woods", "moremobvariants:wolf_woods_spawns",
            "ashen", "moremobvariants:wolf_ashen_spawns", "black", "moremobvariants:wolf_black_spawns",
            "chestnut", "moremobvariants:wolf_chestnut_spawns", "rusty", "moremobvariants:wolf_rusty_spawns",
            "spotted", "moremobvariants:wolf_spotted_spawns", "striped", "moremobvariants:wolf_striped_spawns",
            "snowy", "moremobvariants:wolf_snowy_spawns", "skeleton", "minecraft:is_nether");

    @SubscribeEvent
    public void onJoin(EntityJoinLevelEvent event) {
        if (event.getLevel().m_5776_() || !(event.getEntity() instanceof Wolf wolf) || wolf.m_21824_()) {
            return;
        }
        CompoundTag data = ((IForgeEntity) (Object) wolf).getPersistentData();
        if (data.m_128471_(DONE)) {
            return;
        }
        data.m_128379_(DONE, true);
        CompoundTag save = new CompoundTag();
        wolf.m_7380_(save);
        String coat = save.m_128461_("VariantID");
        if (!coat.isEmpty() && !coat.equals(DEFAULT)) {
            return;
        }
        Holder<Biome> biome = event.getLevel().m_204166_(wolf.m_20183_());
        List<String> fits = new ArrayList<>();
        List<String> natural = new ArrayList<>();
        for (Map.Entry<String, String> e : COATS.entrySet()) {
            if (biome.m_203656_(TagKey.m_203882_(Registries.f_256952_, new ResourceLocation(e.getValue())))) {
                fits.add(e.getKey());
            }
            if (!e.getKey().equals("skeleton")) {
                natural.add(e.getKey());
            }
        }
        List<String> pool = fits.isEmpty() ? natural : fits;
        pool.sort(null);
        save.m_128359_("VariantID", "moremobvariants:" + pool.get(wolf.m_217043_().m_188503_(pool.size())));
        wolf.m_7378_(save);
    }
}
