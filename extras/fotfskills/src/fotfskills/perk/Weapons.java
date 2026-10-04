package fotfskills.perk;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.ForgeRegistries;

/** Weapon types from the fotfskills:<type> item tags (tools/skills/make_weapon_tags.py); "pickaxe" = #minecraft:pickaxes. */
public final class Weapons {
    private static final Map<String, TagKey<Item>> TAGS = new ConcurrentHashMap<>();

    private Weapons() {
    }

    public static boolean is(ItemStack stack, String type) {
        if (stack.m_41619_()) {
            return false;
        }
        TagKey<Item> tag = TAGS.computeIfAbsent(type, t -> TagKey.m_203882_(ForgeRegistries.Keys.ITEMS,
                t.equals("pickaxe") ? new ResourceLocation("minecraft", "pickaxes") : t.equals("hoe") ? new ResourceLocation("minecraft", "hoes") : new ResourceLocation("fotfskills", t)));
        return stack.m_204117_(tag);
    }
}
