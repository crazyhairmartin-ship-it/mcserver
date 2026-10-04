package fotfskills.mixin;

import fotfskills.perk.Perks;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.Constant;
import org.spongepowered.asm.mixin.injection.ModifyConstant;

/**
 * Bulwark: shields block a wider arc. isDamageSourceBlocked (m_21275_) blocks when the hit direction's dot product with
 * the view vector is below 0.0 (the second dconst_0, ordinal 1); Bulwark raises that threshold for the player.
 */
@Mixin(value = LivingEntity.class, remap = false)
public abstract class LivingEntityBlockMixin {
    @ModifyConstant(method = "m_21275_", remap = false, constant = @Constant(doubleValue = 0.0, ordinal = 1))
    private double fotfskills$widerBlock(double threshold) {
        if ((Object) this instanceof ServerPlayer player) {
            return threshold + Perks.get(player, "bulwark");
        }
        return threshold;
    }
}
