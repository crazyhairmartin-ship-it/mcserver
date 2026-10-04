package fotfskills.pet;

import net.minecraft.world.item.Item;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

/** The add-on's items. */
public final class ModItems {
    private static final DeferredRegister<Item> ITEMS = DeferredRegister.create(ForgeRegistries.ITEMS, "fotfskills");
    public static final RegistryObject<Item> PET_MEMENTO = ITEMS.register("pet_memento",
            () -> new PetMementoItem(new Item.Properties().m_41487_(1).m_41486_()));

    private ModItems() {
    }

    public static void register(IEventBus modBus) {
        ITEMS.register(modBus);
    }
}
