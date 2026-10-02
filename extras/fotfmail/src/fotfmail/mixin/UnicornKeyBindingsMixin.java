package fotfmail.mixin;

import com.hackshop.ultimate_unicorn.entity.horses.MagicalHorse;
import com.hackshop.ultimate_unicorn.input.KeyBindings;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraftforge.event.TickEvent;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Ultimate Unicorn Mod crashes the game if "Charge with Unicorn" (F by default) is pressed while you're not riding one
 * of its magical horses: it reads the horse's equipment without checking there is a horse. All its keys (charge,
 * kirin breath, pegasus up/down) only do something while riding a magical horse, so its key handling is skipped
 * otherwise, and stray charge/breath presses are used up so they don't fire later.
 */
@Mixin(KeyBindings.class)
public abstract class UnicornKeyBindingsMixin {
    @Inject(method = "onClientTick", at = @At("HEAD"), cancellable = true, remap = false)
    private static void fotfmail$onlyWhenRiding(TickEvent.ClientTickEvent event, CallbackInfo ci) {
        LocalPlayer player = Minecraft.m_91087_().f_91074_;
        if (player != null && player.m_20202_() instanceof MagicalHorse) {
            return;
        }
        while (KeyBindings.chargeUnicorn.get().m_90859_()) {
            // used up: no horse to charge with
        }
        while (KeyBindings.breatheKirin.get().m_90859_()) {
            // used up: no kirin to breathe fire
        }
        ci.cancel();
    }
}
