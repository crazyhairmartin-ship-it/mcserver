package fotfskills.mixin;

import java.util.List;
import java.util.Map;
import net.minecraft.client.model.geom.ModelPart;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Mutable;
import org.spongepowered.asm.mixin.gen.Accessor;

/** A model part's boxes (f_104212_ = cubes) and child parts (f_104213_ = children). Used by WolfEarsMixin. */
@Mixin(value = ModelPart.class, remap = false)
public interface ModelPartAccessor {
    @Accessor(value = "f_104212_", remap = false)
    List<ModelPart.Cube> fotfskills$cubes();

    @Mutable
    @Accessor(value = "f_104212_", remap = false)
    void fotfskills$setCubes(List<ModelPart.Cube> cubes);

    @Accessor(value = "f_104213_", remap = false)
    Map<String, ModelPart> fotfskills$children();

    @Mutable
    @Accessor(value = "f_104213_", remap = false)
    void fotfskills$setChildren(Map<String, ModelPart> children);
}
