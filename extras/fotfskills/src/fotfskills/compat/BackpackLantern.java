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
    /** Ticks after joining when the backpack rule isn't enforced: on login Curios re-validates each slot as it loads,
     * and the Lantern slot can load before the back slot holding the backpack, which threw the lantern out. */
    private static final int LOGIN_GRACE = 100;

    public static void registerPredicate() {
        CuriosApi.registerCurioPredicate(new ResourceLocation("fotfskills", "backpack_lantern"),
                r -> r.stack().m_204117_(LANTERNS) && (loading(r.slotContext().entity()) || wearsBackpack(r.slotContext().entity())));
    }

    private static boolean loading(LivingEntity entity) {
        return entity != null && entity.f_19797_ < LOGIN_GRACE;
    }

    public static boolean wearsBackpack(LivingEntity entity) {
        return !backpack(entity).m_41619_();
    }

    /** The backpack the entity wears (chest slot or any curio slot), or an empty stack. */
    public static ItemStack backpack(LivingEntity entity) {
        if (entity == null) {
            return ItemStack.f_41583_;
        }
        ItemStack chest = entity.m_6844_(EquipmentSlot.CHEST);
        if (chest.m_204117_(BACKPACKS)) {
            return chest;
        }
        return CuriosApi.getCuriosInventory(entity).resolve()
                .flatMap(inv -> inv.findFirstCurio(s -> s.m_204117_(BACKPACKS)))
                .map(r -> r.stack())
                .orElse(ItemStack.f_41583_);
    }

    /**
     * The lit lantern hanging off the entity's backpack, or an empty stack. The Lantern slot's eye toggle is its on/off
     * switch: hidden = unlit (hiding the backpack itself leaves it lit). Drives both the server light (lantern_light.js)
     * and the shader glow (mixin/OculusHeldLightMixin).
     */
    public static ItemStack lantern(LivingEntity entity) {
        if (!wearsBackpack(entity)) {
            return ItemStack.f_41583_;
        }
        return CuriosApi.getCuriosInventory(entity).resolve().flatMap(inv -> inv.getStacksHandler(SLOT)).map(handler -> {
            var stacks = handler.getStacks();
            var renders = handler.getRenders();
            for (int i = 0; i < stacks.getSlots(); i++) {
                boolean lit = i >= renders.size() || renders.get(i);
                if (lit && !stacks.getStackInSlot(i).m_41619_()) {
                    return stacks.getStackInSlot(i);
                }
            }
            return ItemStack.f_41583_;
        }).orElse(ItemStack.f_41583_);
    }

    @SubscribeEvent
    public void onPlayerTick(TickEvent.PlayerTickEvent event) {
        Player player = event.player;
        if (event.phase != TickEvent.Phase.END || player.m_9236_().f_46443_ || player.f_19797_ % CHECK_EVERY != 0
                || loading(player)) {
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
