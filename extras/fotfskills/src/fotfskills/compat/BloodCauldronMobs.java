package fotfskills.compat;

import io.redspace.ironsspellbooks.block.BloodCauldronBlock;
import io.redspace.ironsspellbooks.registries.BlockRegistry;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.LayeredCauldronBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.gameevent.GameEvent;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/**
 * Iron's blood cauldron (a cauldron over a lit campfire) only cooks mobs whose feet are inside it, so only mobs small
 * enough to drop into the 3/4-block hollow ever worked; most modded mobs are wider or stand on the rim. A mob standing
 * on top of the cauldron now counts too, through Iron's own attemptCookEntity (its campfire check, damage, blood
 * chance and fill), with mixin/BloodCauldronReachMixin letting its overlap test reach a mob on the rim. Players and
 * mobs already inside are left to Iron's own handlers.
 */
public final class BloodCauldronMobs {
    private static final int EVERY = 20;

    @SubscribeEvent
    public void onTick(LivingEvent.LivingTickEvent event) {
        LivingEntity mob = event.getEntity();
        Level level = mob.m_9236_();
        if (level.f_46443_ || mob instanceof Player || mob.f_19797_ % EVERY != 0) {
            return;
        }
        BlockPos feet = mob.m_20183_();
        if (isCauldron(level.m_8055_(feet))) {
            return;                                                      // inside it: Iron's handles this one
        }
        BlockPos pos = feet.m_7495_();
        BlockState state = level.m_8055_(pos);
        if (state.m_60713_(Blocks.f_50256_)) {                           // empty cauldron: starts filling with blood
            BloodCauldronBlock.attemptCookEntity(state, level, pos, mob, () -> {
                level.m_46597_(pos, BlockRegistry.BLOOD_CAULDRON_BLOCK.get().m_49966_());
                level.m_142346_(null, GameEvent.f_157792_, pos);
            });
        } else if (state.m_60713_(BlockRegistry.BLOOD_CAULDRON_BLOCK.get())) {
            BloodCauldronBlock.attemptCookEntity(state, level, pos, mob, () -> {
                level.m_46597_(pos, state.m_61122_(LayeredCauldronBlock.f_153514_));
                level.m_142346_(null, GameEvent.f_157792_, pos);
            });
        }
    }

    private static boolean isCauldron(BlockState state) {
        return state.m_60713_(Blocks.f_50256_) || state.m_60713_(BlockRegistry.BLOOD_CAULDRON_BLOCK.get());
    }
}
