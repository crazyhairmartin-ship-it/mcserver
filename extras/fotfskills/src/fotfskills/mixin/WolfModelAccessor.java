package fotfskills.mixin;

import net.minecraft.client.model.WolfModel;
import net.minecraft.client.model.geom.ModelPart;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/** The wolf model's head parts (f_104107_ = head, f_104108_ = real_head), for client/DaleEarsLayer. */
@Mixin(value = WolfModel.class, remap = false)
public interface WolfModelAccessor {
    @Accessor(value = "f_104107_", remap = false)
    ModelPart fotfskills$head();

    @Accessor(value = "f_104108_", remap = false)
    ModelPart fotfskills$realHead();
}
