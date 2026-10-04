package fotfskills.perk;

import com.yyon.grapplinghook.items.GrapplehookItem;
import com.yyon.grapplinghook.utils.GrappleCustomization;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/**
 * The single grappling hook is upgraded by Agility nodes instead of upgrade items: every second, each hook in the
 * player's inventory gets the customization their perks give (Long Rope: rope length; Hookmaster: throw speed and swing
 * control; Motor Reel: motor; Twin Hooks: double hook). Written only when it changes.
 */
public final class GrapplePerks {
    private static final double BASE_ROPE = 30;
    private static final double MAX_ROPE = 60;

    @SubscribeEvent
    public void onTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.player instanceof ServerPlayer player) || player.f_19797_ % 20 != 10) {
            return;
        }
        for (ItemStack stack : player.m_150109_().f_35974_) {
            if (stack.m_41720_() instanceof GrapplehookItem hook) {
                GrappleCustomization wanted = customization(player);
                if (hook.getCustomization(stack).getChecksum() != wanted.getChecksum()) {
                    hook.setCustomOnServer(stack, wanted, player);
                }
            }
        }
    }

    private static GrappleCustomization customization(ServerPlayer player) {
        GrappleCustomization c = new GrappleCustomization();
        c.maxlen = Math.min(MAX_ROPE, BASE_ROPE + Perks.get(player, "hook_range"));
        double speed = Perks.get(player, "hook_speed");
        c.throwspeed *= 1 + speed;
        c.playermovementmult *= 1 + speed;
        double motor = Perks.get(player, "hook_motor");
        if (motor > 0) {
            c.motor = true;
            c.motormaxspeed *= 1 + 0.25 * (motor - 1);
        }
        if (Perks.get(player, "hook_double") > 0) {
            c.doublehook = true;
        }
        return c;
    }
}
