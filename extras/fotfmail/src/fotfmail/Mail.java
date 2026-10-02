package fotfmail;

import com.chaosthedude.endermail.block.entity.LockerBlockEntity;
import com.chaosthedude.endermail.data.LockerData;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BlockEntity;

/** Delivers a signed letter into the mailbox whose ID is the letter's title. */
final class Mail {
    private Mail() {
    }

    static void send(ServerPlayer player, ItemStack letter) {
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
            ItemStack delivered = letter.m_41777_();
            delivered.m_41764_(1);
            if (!mailbox.addPackage(delivered)) {
                tell(player, Component.m_237110_("message.fotfmail.full", id), ChatFormatting.RED);
                return;
            }
            letter.m_41774_(1);
            player.m_284548_().m_5594_(null, player.m_20183_(), SoundEvents.f_11713_, SoundSource.PLAYERS, 1.0F, 1.2F);
            tell(player, Component.m_237110_("message.fotfmail.sent", id), ChatFormatting.GREEN);
            return;
        }
        tell(player, Component.m_237110_("message.fotfmail.no_mailbox", id), ChatFormatting.RED);
    }

    private static void tell(ServerPlayer player, net.minecraft.network.chat.MutableComponent message, ChatFormatting color) {
        player.m_213846_(message.m_130940_(color));
    }
}
