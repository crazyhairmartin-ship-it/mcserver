package fotfskills.compat;

import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import top.theillusivec4.curios.api.CuriosApi;

/**
 * The Curios "Lantern" slot (kubejs/data/fotf/curios) takes a lantern only while a backpack is worn (Curios back slot
 * or chest slot, item tag fotf:lantern_backpacks); the lantern hangs off the backpack (client/BackpackLanternRenderer)
 * and lights the area (kubejs lantern_light.js). Take the backpack off and the lantern drops back into the inventory.
 */
public final class BackpackLantern {
    public static final String SLOT = "lantern";
    public static final TagKey<Item> LANTERNS = TagKey.m_203882_(Registries.f_256913_, new ResourceLocation("curios", "lantern"));
    public static final TagKey<Item> BACKPACKS = TagKey.m_203882_(Registries.f_256913_, new ResourceLocation("fotf", "lantern_backpacks"));
    private static final int CHECK_EVERY = 10;

    public static void registerPredicate() {
        CuriosApi.registerCurioPredicate(new ResourceLocation("fotfskills", "backpack_lantern"),
                r -> r.stack().m_204117_(LANTERNS) && wearsBackpack(r.slotContext().entity()));
    }

    public static boolean wearsBackpack(LivingEntity entity) {
        if (entity == null) {
            return false;
        }
        if (entity.m_6844_(EquipmentSlot.CHEST).m_204117_(BACKPACKS)) {
            return true;
        }
        return CuriosApi.getCuriosInventory(entity).resolve()
                .map(inv -> inv.findFirstCurio(s -> s.m_204117_(BACKPACKS)).isPresent())
                .orElse(false);
    }

    @SubscribeEvent
    public void onPlayerTick(TickEvent.PlayerTickEvent event) {
        Player player = event.player;
        if (event.phase != TickEvent.Phase.END || player.m_9236_().f_46443_ || player.f_19797_ % CHECK_EVERY != 0) {
            return;
        }
        CuriosApi.getCuriosInventory(player).resolve().flatMap(inv -> inv.getStacksHandler(SLOT)).ifPresent(handler -> {
            var stacks = handler.getStacks();
            for (int i = 0; i < stacks.getSlots(); i++) {
                ItemStack lantern = stacks.getStackInSlot(i);
                if (lantern.m_41619_() || wearsBackpack(player)) {
                    continue;
                }
                ItemStack back = lantern.m_41777_();
                stacks.setStackInSlot(i, ItemStack.f_41583_);
                if (!player.m_150109_().m_36054_(back)) {
                    player.m_36176_(back, false);
                }
                player.m_5661_(Component.m_237113_("Your lantern needs a backpack to hang from"), true);
            }
        });
    }
}
