package fotfskills.client;

import java.lang.reflect.Field;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/**
 * YDM's Weapon Master moves the weapon in your hand onto your body once you haven't clicked for its hide time; Better
 * Combat takes over the attack button during combos, so mid-combo it looked idle. Every tick your arm is mid-swing,
 * this resets Weapon Master's own idle counter for that hand (ClientOnlyForgeSetup.lastMainhandHit / lastOffhandHit).
 */
public final class WeaponMasterCombo {
    private static Field mainHit;
    private static Field offHit;
    private static boolean lookedUp;

    @SubscribeEvent
    public void onTick(TickEvent.ClientTickEvent event) {
        LocalPlayer player = Minecraft.m_91087_().f_91074_;
        if (event.phase != TickEvent.Phase.END || player == null || !player.f_20911_) {
            return;
        }
        if (!lookedUp) {
            lookedUp = true;
            try {
                Class<?> setup = Class.forName("com.minecraftserverzone.weaponmaster.setup.events_on_client.ClientOnlyForgeSetup");
                mainHit = setup.getField("lastMainhandHit");
                offHit = setup.getField("lastOffhandHit");
            } catch (ReflectiveOperationException | RuntimeException e) {
                mainHit = null;                        // no Weapon Master (or it changed): nothing to do
            }
        }
        if (mainHit == null) {
            return;
        }
        try {
            (player.f_20912_ == InteractionHand.OFF_HAND ? offHit : mainHit).setInt(null, 1);
        } catch (IllegalAccessException | RuntimeException ignored) {
            // leave Weapon Master alone
        }
    }
}
