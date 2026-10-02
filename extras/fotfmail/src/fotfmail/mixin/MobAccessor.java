package fotfmail.mixin;

import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.goal.GoalSelector;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/** Mob.goalSelector (f_21345_) is protected; used to add goals to other mods' mobs. */
@Mixin(Mob.class)
public interface MobAccessor {
    @Accessor(value = "f_21345_", remap = false)
    GoalSelector fotfmail$goalSelector();
}
