package fotfskills.xp;

import net.minecraft.resources.ResourceLocation;
import net.puffish.skillsmod.api.SkillsAPI;
import net.puffish.skillsmod.api.util.Problem;
import net.puffish.skillsmod.api.util.Result;

/** Registers fotfskills:<kind> XP sources; each reads one number from its data (see tools/skills/xp.json). */
public final class XpSources {
    private XpSources() {
    }

    public static void register() {
        source("cast_spell", "per_mana");
        source("tame", "experience");
        source("shield_block", "per_damage");
        source("cook", "per_nutrition");
        source("craft_gear", "per_item");
        source("move", "meters_per_xp");
    }

    private static void source(String kind, String key) {
        SkillsAPI.registerExperienceSource(new ResourceLocation("fotfskills", kind), context -> context.getData()
                .andThen(data -> data.getAsObject())
                .andThen(object -> object.getDouble(key))
                .andThen(value -> value > 0 ? Result.<AmountSource, Problem>success(new AmountSource(kind, value))
                        : Result.<AmountSource, Problem>failure(Problem.message(key + " must be above 0"))));
    }
}
