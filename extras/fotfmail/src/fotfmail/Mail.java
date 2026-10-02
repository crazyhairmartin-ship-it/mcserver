package fotfmail;

import com.chaosthedude.endermail.block.entity.LockerBlockEntity;
import com.chaosthedude.endermail.data.LockerData;
import com.chaosthedude.endermail.entity.EnderMailmanEntity;
import com.chaosthedude.endermail.registry.EnderMailEntities;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.NonNullList;
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
 * Same dimension: one of Ender Mail's mail carriers appears at the mailbox you used, already holding the letter
 * (so its pick-up step, which removes a package block, never runs), then teleports to the friend's mailbox
 * about 5 seconds later and drops it in. EnderMailmanEntityMixin makes it hand over the letter itself rather than
 * wrapping it in a package. Other dimensions: delivered instantly, since carriers can't cross dimensions.
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
                carrier.setCarryingPackage(true);
                carrier.setDelivering(true);
                carrier.updateTimePickedUp();
                ((IForgeEntity) (Object) carrier).getPersistentData().m_128379_(LETTER_TAG, true);
                level.m_7967_(carrier);
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
