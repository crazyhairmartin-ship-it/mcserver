package fotfskills.perk;

import net.minecraft.resources.ResourceLocation;
import net.puffish.skillsmod.api.SkillsAPI;
import net.puffish.skillsmod.api.reward.Reward;
import net.puffish.skillsmod.api.reward.RewardDisposeContext;
import net.puffish.skillsmod.api.reward.RewardUpdateContext;
import net.puffish.skillsmod.api.util.Problem;
import net.puffish.skillsmod.api.util.Result;

/** fotfskills:perk reward: {"perk": "ore_drops", "value": 0.03}. Each unlocked rank adds its value. */
public final class PerkReward implements Reward {
    private final String perk;
    private final double value;

    private PerkReward(String perk, double value) {
        this.perk = perk;
        this.value = value;
    }

    public static void register() {
        SkillsAPI.registerReward(new ResourceLocation("fotfskills", "perk"), context -> context.getData()
                .andThen(data -> data.getAsObject())
                .andThen(object -> object.getString("perk").andThen(perk -> object.getDouble("value")
                        .andThen(value -> Perks.CAPS.containsKey(perk)
                                ? Result.<PerkReward, Problem>success(new PerkReward(perk, value))
                                : Result.<PerkReward, Problem>failure(Problem.message("Unknown fotfskills perk: " + perk))))));
    }

    @Override
    public void update(RewardUpdateContext context) {
        Perks.TOTALS.put(context.getPlayer().m_20148_(), this, perk, value * context.getCount());
        PerkSync.markDirty(context.getPlayer());
    }

    @Override
    public void dispose(RewardDisposeContext context) {
        Perks.TOTALS.removeSource(this);
        context.getServer().m_6846_().m_11314_().forEach(PerkSync::markDirty);
    }
}
