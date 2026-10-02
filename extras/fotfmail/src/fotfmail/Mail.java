package fotfmail;

import com.chaosthedude.endermail.block.PackageBlock;
import com.chaosthedude.endermail.block.entity.LockerBlockEntity;
import com.chaosthedude.endermail.block.entity.PackageBlockEntity;
import com.chaosthedude.endermail.data.LockerData;
import com.chaosthedude.endermail.entity.EnderMailmanEntity;
import com.chaosthedude.endermail.registry.EnderMailEntities;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.NonNullList;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.Level;
import net.minecraftforge.event.TickEvent;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.common.extensions.IForgeEntity;

/**
 * Sends a signed letter to the mailbox whose ID is the letter's title, and packages from the package screen.
 *
 * Same dimension: one of Ender Mail's mail carriers appears 8-12 blocks from the mailbox you used and walks
 * the letter over to the friend's mailbox (CarrierGoal). Ender Mail's own carrier goals are off for these carriers,
 * so its pick-up step (which removes a package block) never runs.
 * Other dimensions: delivered instantly, since carriers can't cross dimensions.
 */
public final class Mail {
    static final String LETTER_TAG = "fotfmail_letter";
    /** Who sent a package: on the carrier, then in the delivered package's data (BlockEntityTag.ForgeData). */
    public static final String FROM_TAG = "fotfmail_from";

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
                data.m_128405_(CarrierGoal.PHASE, CarrierGoal.WAITING);
                data.m_128356_(CarrierGoal.FROM, fromMailbox.m_121878_());
                data.m_128356_(CarrierGoal.TO, pos.m_121878_());
                carrier.m_21530_(); // never despawn mid-delivery
                // Waits out of sight above the mailbox, then appears nearby and walks up to it (CarrierGoal does the rest).
                carrier.m_20242_(true);
                carrier.m_6034_(fromMailbox.m_123341_() + 0.5, level.m_151558_() + 64, fromMailbox.m_123343_() + 0.5);
                level.m_7967_(carrier);
                tell(player, Component.m_237110_("message.fotfmail.on_the_way", id), ChatFormatting.GREEN);
            } else {
                mailbox.addPackage(delivered);
                tell(player, Component.m_237110_("message.fotfmail.sent", id), ChatFormatting.GREEN);
            }
            return;
        }
        tell(player, Component.m_237110_("message.fotfmail.no_mailbox", id), ChatFormatting.RED);
    }

    /**
     * The package screen's Send button: stamps the package for the recipient's mailbox and calls one of Ender Mail's
     * carriers, which takes it (removing the block) and drops it into that mailbox. Mailboxes only; no coordinates.
     */
    static void sendPackage(ServerPlayer player, BlockPos pos, String recipient) {
        ServerLevel level = player.m_284548_();
        String id = recipient.trim();
        if (player.m_20275_(pos.m_123341_() + 0.5, pos.m_123342_() + 0.5, pos.m_123343_() + 0.5) > 64) {
            return;
        }
        BlockState state = level.m_8055_(pos);
        if (!(state.m_60734_() instanceof PackageBlock block) || block.isStamped(state)
                || !(level.m_7702_(pos) instanceof PackageBlockEntity box)) {
            return;
        }
        if (box.m_7983_()) {
            tell(player, Component.m_237115_("message.fotfmail.package_empty"), ChatFormatting.RED);
            return;
        }
        if (id.isEmpty()) {
            tell(player, Component.m_237115_("message.fotfmail.package_no_recipient"), ChatFormatting.RED);
            return;
        }
        BlockPos mailbox = LockerData.get(level).getLockers().get(id);
        if (mailbox == null) {
            for (ServerLevel other : player.m_20194_().m_129785_()) {
                if (other != level && LockerData.get(other).getLockers().containsKey(id)) {
                    tell(player, Component.m_237110_("message.fotfmail.package_other_dimension", id), ChatFormatting.RED);
                    return;
                }
            }
            tell(player, Component.m_237110_("message.fotfmail.no_mailbox", id), ChatFormatting.RED);
            return;
        }
        PackageBlock.stampPackage(level, pos, mailbox, id, false);
        PENDING_PACKAGES.add(new PendingPackage(level.m_46472_(), pos, mailbox, id, player.m_7755_().getString(),
                level.m_7654_().m_129921_() + CarrierGoal.SEND_DELAY));
        tell(player, Component.m_237110_("message.fotfmail.package_sent", id), ChatFormatting.GREEN);
    }

    /** A stamped package waiting for its carrier, who comes CarrierGoal.SEND_DELAY ticks after it was sent. */
    private record PendingPackage(ResourceKey<Level> dimension, BlockPos pos, BlockPos mailbox, String id, String from, int dueTick) {
    }

    private static final List<PendingPackage> PENDING_PACKAGES = new ArrayList<>();

    /** Server tick: calls the carrier for packages whose wait is over (if the package is still there, stamped). */
    static void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || PENDING_PACKAGES.isEmpty()) {
            return;
        }
        MinecraftServer server = event.getServer();
        int now = server.m_129921_();
        Iterator<PendingPackage> it = PENDING_PACKAGES.iterator();
        while (it.hasNext()) {
            PendingPackage pending = it.next();
            if (now < pending.dueTick()) {
                continue;
            }
            it.remove();
            ServerLevel level = server.m_129880_(pending.dimension());
            if (level == null) {
                continue;
            }
            BlockState state = level.m_8055_(pending.pos());
            if (state.m_60734_() instanceof PackageBlock block && block.isStamped(state)) {
                EnderMailmanEntity carrier = new EnderMailmanEntity(EnderMailEntities.ENDER_MAILMAN.get(), level,
                        pending.pos(), pending.mailbox(), pending.id(), ItemStack.f_41583_);
                ((IForgeEntity) (Object) carrier).getPersistentData().m_128359_(FROM_TAG, pending.from());
                level.m_7967_(carrier);
                carrier.playEndermanSound();
            }
        }
    }

    private static void tell(ServerPlayer player, MutableComponent message, ChatFormatting color) {
        player.m_213846_(message.m_130940_(color));
    }
}
