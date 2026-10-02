package fotfmail;

import java.lang.reflect.Method;
import net.minecraft.client.renderer.item.ClampedItemPropertyFunction;
import net.minecraft.client.renderer.item.ItemProperties;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;
import net.minecraftforge.registries.ForgeRegistries;
import org.apache.logging.log4j.LogManager;

/**
 * Item model predicates: fotfmail:wood picks the mailbox item's wood model (index / 128, since predicate
 * values are clamped to 0..1) and fotfmail:signed switches the letter to its sealed envelope.
 */
final class ClientSetup {
    private ClientSetup() {
    }

    static void init(IEventBus modBus) {
        modBus.addListener(ClientSetup::setup);
    }

    private static void setup(FMLClientSetupEvent event) {
        event.enqueueWork(() -> {
            try {
                // ItemProperties.register is private in the SRG jar we compile against; Forge opens it at runtime.
                Method register = ItemProperties.class.getDeclaredMethod("m_174570_",
                        Item.class, ResourceLocation.class, ClampedItemPropertyFunction.class);
                register.setAccessible(true);
                Item mailbox = ForgeRegistries.ITEMS.getValue(new ResourceLocation("endermail", "locker"));
                ClampedItemPropertyFunction wood = (stack, level, entity, seed) -> woodIndex(stack) / 128.0F;
                ClampedItemPropertyFunction signed = (stack, level, entity, seed) -> LetterItem.isSigned(stack) ? 1.0F : 0.0F;
                register.invoke(null, mailbox, new ResourceLocation(FotfMail.MODID, "wood"), wood);
                register.invoke(null, FotfMail.LETTER.get(), new ResourceLocation(FotfMail.MODID, "signed"), signed);
            } catch (ReflectiveOperationException e) {
                LogManager.getLogger(FotfMail.MODID).error("Couldn't register item model predicates", e);
            }
        });
    }

    private static int woodIndex(ItemStack stack) {
        CompoundTag tag = stack.m_41783_();
        if (tag == null) {
            return 0;
        }
        String wood = tag.m_128469_("BlockStateTag").m_128461_("wood");
        for (MailboxWood value : MailboxWood.values()) {
            if (value.m_7912_().equals(wood)) {
                return value.ordinal();
            }
        }
        return 0;
    }
}
