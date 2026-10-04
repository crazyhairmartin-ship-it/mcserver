package fotfskills.pet;

import fotfskills.perk.Perks;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;

/**
 * Holds a fallen pet (its whole saved data). Using it on a block brings the pet back there, healed, for one golden
 * apple from your inventory; Taming's Soul Mender gives a 25% chance per rank to keep the apple.
 */
public final class PetMementoItem extends Item {
    public static final String PET = "FotfPet";
    public static final String NAME = "FotfPetName";

    public PetMementoItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResult m_6225_(UseOnContext context) {
        ItemStack memento = context.m_43722_();
        if (!(context.m_43725_() instanceof ServerLevel level) || !(context.m_43723_() instanceof ServerPlayer player)) {
            return InteractionResult.SUCCESS;
        }
        CompoundTag tag = memento.m_41783_();
        if (tag == null || !tag.m_128441_(PET)) {
            return InteractionResult.FAIL;
        }
        int apple = findApple(player);
        if (apple < 0 && !player.m_7500_()) {
            player.m_5661_(Component.m_237113_("§cYou need a golden apple to revive " + tag.m_128461_(NAME) + "."), true);
            return InteractionResult.FAIL;
        }
        BlockPos at = context.m_8083_().m_121945_(context.m_43719_());
        CompoundTag data = tag.m_128469_(PET).m_6426_();
        data.m_128473_("DeathTime");
        data.m_128473_("HurtTime");
        Entity pet = EntityType.m_20642_(data, level).orElse(null);
        if (pet == null) {
            return InteractionResult.FAIL;
        }
        pet.m_7678_(at.m_123341_() + 0.5, at.m_123342_(), at.m_123343_() + 0.5, pet.m_146908_(), 0);
        if (pet instanceof LivingEntity living) {
            living.m_21153_(living.m_21233_());
        }
        if (level.m_8791_(pet.m_20148_()) != null) {
            player.m_5661_(Component.m_237113_("§c" + tag.m_128461_(NAME) + " is already alive."), true);
            return InteractionResult.FAIL;
        }
        level.m_7967_(pet);
        if (apple >= 0 && !player.m_7500_() && !Perks.roll(player, "soul_mender")) {
            player.m_150109_().f_35974_.get(apple).m_41774_(1);
        }
        if (!player.m_7500_()) {
            memento.m_41774_(1);
        }
        level.m_8767_(ParticleTypes.f_123750_, pet.m_20185_(), pet.m_20186_() + 1, pet.m_20189_(), 12, 0.5, 0.5, 0.5, 0.1);
        level.m_5594_(null, at, SoundEvents.f_12275_, SoundSource.PLAYERS, 1.0f, 1.2f);
        player.m_5661_(Component.m_237113_("§a" + tag.m_128461_(NAME) + " is back!"), true);
        return InteractionResult.CONSUME;
    }

    private static int findApple(ServerPlayer player) {
        List<ItemStack> items = player.m_150109_().f_35974_;
        for (int i = 0; i < items.size(); i++) {
            if (items.get(i).m_150930_(Items.f_42436_)) {
                return i;
            }
        }
        return -1;
    }

    @Override
    public void m_7373_(ItemStack stack, Level level, List<Component> tooltip, TooltipFlag flag) {
        CompoundTag tag = stack.m_41783_();
        if (tag != null && tag.m_128441_(NAME)) {
            tooltip.add(Component.m_237113_("§d" + tag.m_128461_(NAME)));
        }
        tooltip.add(Component.m_237113_("§7Use on a block with a golden apple in your inventory to bring your pet back."));
    }
}
