package fotfmail;

import com.chaosthedude.endermail.block.entity.LockerBlockEntity;
import com.chaosthedude.endermail.data.LockerData;
import com.chaosthedude.endermail.entity.EnderMailmanEntity;
import com.chaosthedude.endermail.registry.EnderMailEntities;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.NonNullList;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraftforge.common.extensions.IForgeEntity;

/**
 * Sends a signed letter to the mailbox whose ID is the letter's title.
 *
 * Same dimension: one of Ender Mail's mail carriers appears about 12 blocks in front of the mailbox you used and walks
 * the letter over to the friend's mailbox (CarrierGoal). Ender Mail's own carrier goals are off for these carriers,
 * so its pick-up step (which removes a package block) never runs.
 * Other dimensions: delivered instantly, since carriers can't cross dimensions.
 */
final class Mail {
    static final String LETTER_TAG = "fotfmail_letter";

    private Mail() {
    }

    static void send(ServerPlayer player, BlockPos fromMailbox, ItemStack letter) {
        String id = LetterItem.recipient(letter);
        for (ServerLevel level : player.m_20194_().m_129785_()) {
            BlockPos pos = LockerData.get(level).getLockers().get(id);
            if (pos == null) {
                continue;
            }
            BlockEntity blockEntity = level.m_7702_(pos);
            if (!(blockEntity instanceof LockerBlockEntity mailbox)) {
                continue;
            }
            if (mailbox.isFull()) {
                tell(player, Component.m_237110_("message.fotfmail.full", id), ChatFormatting.RED);
                return;
            }
            ItemStack delivered = letter.m_41777_();
            delivered.m_41764_(1);
            letter.m_41774_(1);
            if (level == player.m_284548_()) {
                EnderMailmanEntity carrier = new EnderMailmanEntity(EnderMailEntities.ENDER_MAILMAN.get(), level,
                        fromMailbox, pos, id, ItemStack.f_41583_);
                carrier.setContents(NonNullList.m_122783_(ItemStack.f_41583_, delivered));
                CompoundTag data = ((IForgeEntity) (Object) carrier).getPersistentData();
                data.m_128379_(LETTER_TAG, true);
                data.m_128405_(CarrierGoal.PHASE, 0);
                data.m_128356_(CarrierGoal.FROM, fromMailbox.m_121878_());
                data.m_128356_(CarrierGoal.TO, pos.m_121878_());
                carrier.m_21530_(); // never despawn mid-delivery
                // Arrive a few steps out in front of the mailbox and walk up to it (CarrierGoal does the rest).
                BlockPos start = CarrierGoal.spotInFront(level, fromMailbox, CarrierGoal.DISTANCE);
                if (start != null) {
                    carrier.m_6034_(start.m_123341_() + 0.5, start.m_123342_(), start.m_123343_() + 0.5);
                }
                level.m_7967_(carrier);
                level.m_8767_(ParticleTypes.f_123760_, carrier.m_20185_(), carrier.m_20186_() + 1.0, carrier.m_20189_(), 40, 0.4, 0.9, 0.4, 0.2);
                carrier.playEndermanSound();
                tell(player, Component.m_237110_("message.fotfmail.on_the_way", id), ChatFormatting.GREEN);
            } else {
                mailbox.addPackage(delivered);
                tell(player, Component.m_237110_("message.fotfmail.sent", id), ChatFormatting.GREEN);
            }
            return;
        }
        tell(player, Component.m_237110_("message.fotfmail.no_mailbox", id), ChatFormatting.RED);
    }

    private static void tell(ServerPlayer player, MutableComponent message, ChatFormatting color) {
        player.m_213846_(message.m_130940_(color));
    }
}
