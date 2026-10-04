package fotfskills.perk;

import net.minecraft.world.item.Item;
import net.minecraft.world.item.Rarity;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

/** The add-on's items. */
public final class ModItems {
    private static final DeferredRegister<Item> ITEMS = DeferredRegister.create(ForgeRegistries.ITEMS, "fotfskills");
    public static final RegistryObject<Item> SKILL_TONIC = ITEMS.register("skill_tonic",
            () -> new SkillTonicItem(new Item.Properties().m_41487_(16).m_41497_(Rarity.RARE)));

    private ModItems() {
    }

    public static void register(IEventBus modBus) {
        ITEMS.register(modBus);
    }
}
