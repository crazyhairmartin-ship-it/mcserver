package fotfskills.perk;

import java.util.List;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.ItemUtils;
import net.minecraft.world.item.UseAnim;
import net.minecraft.world.level.Level;

/** Skill Tonic (comes with a record catch from Leviathan Bait): drinking it gives 300 XP to a random skill. */
public final class SkillTonicItem extends Item {
    public static final int XP = 300;
    private static final List<String> SKILLS = List.of("mining", "forage", "farm", "fish", "cook", "craft", "attack",
            "range", "defense", "agility", "magic", "taming");

    public SkillTonicItem(Properties properties) {
        super(properties);
    }

    @Override
    public UseAnim m_6164_(ItemStack stack) {
        return UseAnim.DRINK;
    }

    @Override
    public int m_8105_(ItemStack stack) {
        return 32;
    }

    @Override
    public boolean m_5812_(ItemStack stack) {
        return true;
    }

    @Override
    public InteractionResultHolder<ItemStack> m_7203_(Level level, Player player, InteractionHand hand) {
        return ItemUtils.m_150959_(level, player, hand);
    }

    @Override
    public ItemStack m_5922_(ItemStack stack, Level level, LivingEntity entity) {
        if (entity instanceof ServerPlayer player) {
            String skill = SKILLS.get(level.f_46441_.m_188503_(SKILLS.size()));
            level.m_7654_().m_129892_().m_230957_(level.m_7654_().m_129893_().m_81324_(),
                    "puffish_skills experience add " + player.m_36316_().getName() + " " + skill + " " + XP);
            player.m_213846_(Component.m_237113_("§dThe tonic sharpens your " + LevelUps.displayName(skill)
                    + "! §e+" + XP + " XP"));
            if (!player.m_150110_().f_35937_) {
                stack.m_41774_(1);
            }
        }
        return stack;
    }
}
