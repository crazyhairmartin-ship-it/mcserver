package fotfmail;

import com.teammetallurgy.aquaculture.block.blockentity.TackleBoxBlockEntity;
import com.teammetallurgy.aquaculture.init.AquaBlocks;
import com.teammetallurgy.aquaculture.init.AquaSounds;
import com.teammetallurgy.aquaculture.inventory.container.TackleBoxContainer;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.ClickType;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.network.NetworkHooks;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * Aquaculture's tackle box opens from the hand: right-click the air (or water, so it works from a boat) holding one.
 * Right-clicking a block still places it. Dylan, 2026-11-01.
 *
 * Aquaculture's TackleBoxContainer looks its tackle box up as a block entity at the BlockPos it's opened with. This
 * is a stand-in block entity that isn't in the world, opened at POS (below the build limit, so never a real block);
 * mixin/TackleBoxContainerMixin hands it to the container there, so Aquaculture's own slots, rod-part logic and
 * screen all work unchanged. The contents live in the item's BlockEntityTag, the same data a tackle box broken by a
 * player keeps, so a box opened from the hand and one placed and broken again hold the same items.
 */
public class HandTackleBox extends TackleBoxBlockEntity {
    public static final BlockPos POS = new BlockPos(0, -2048, 0);
    private static final ResourceLocation TACKLE_BOX = new ResourceLocation("aquaculture", "tackle_box");
    private static final int BOX_SLOTS = 21; // rod, hook, bait, line, bobber + 16 storage, before the player's 36
    private static final ThreadLocal<HandTackleBox> OPENING = new ThreadLocal<>();

    private final ItemStack stack; // the held tackle box; null on the client, where the server syncs the slots
    private final InteractionHand hand;
    private final int heldSlot;    // menu slot of the held box (main hand), -1 for the offhand (not in the menu)

    private HandTackleBox(ItemStack stack, InteractionHand hand, int heldSlot) {
        super(POS, AquaBlocks.TACKLE_BOX.get().m_49966_());
        this.stack = stack;
        this.hand = hand;
        this.heldSlot = heldSlot;
        if (stack != null) {
            CompoundTag tag = BlockItem.m_186336_(stack);
            if (tag != null) {
                m_142466_(tag);
            }
        }
    }

    /** The container's block entity lookup: the stand-in at POS, the real world everywhere else. */
    public static BlockEntity lookup(Level level, BlockPos pos) {
        if (!POS.equals(pos)) {
            return level.m_7702_(pos);
        }
        HandTackleBox box = OPENING.get();
        return box != null ? box : new HandTackleBox(null, InteractionHand.MAIN_HAND, -1);
    }

    static void onRightClickItem(PlayerInteractEvent.RightClickItem event) {
        ItemStack stack = event.getItemStack();
        if (!TACKLE_BOX.equals(ForgeRegistries.ITEMS.getKey(stack.m_41720_()))) {
            return;
        }
        event.setCanceled(true);
        event.setCancellationResult(InteractionResult.m_19078_(event.getLevel().m_5776_()));
        if (!(event.getEntity() instanceof ServerPlayer player)) {
            return;
        }
        if (stack.m_41613_() != 1) { // the contents would be copied onto every box in the stack
            player.m_5661_(Component.m_237113_("Hold just one tackle box to open it."), true);
            return;
        }
        int heldSlot = event.getHand() == InteractionHand.MAIN_HAND ? BOX_SLOTS + 27 + player.m_150109_().f_35977_ : -1;
        HandTackleBox box = new HandTackleBox(stack, event.getHand(), heldSlot);
        NetworkHooks.openScreen(player, new SimpleMenuProvider((id, inventory, p) -> {
            OPENING.set(box);
            try {
                return new TackleBoxContainer(id, POS, inventory);
            } finally {
                OPENING.remove();
            }
        }, stack.m_41786_()), buf -> buf.m_130064_(POS));
    }

    /** Open only while the same box is still in the same hand. */
    public boolean stillValid(Player player) {
        return stack == null || (player.m_6084_() && player.m_21120_(hand) == stack);
    }

    /** The held box itself can't be picked up, swapped or thrown while it's open. */
    public boolean blocksClick(int slot, int button, ClickType type) {
        if (heldSlot >= 0 && slot == heldSlot) {
            return true;
        }
        return type == ClickType.SWAP && (heldSlot >= 0 ? button == heldSlot - BOX_SLOTS - 27 : button == 40);
    }

    private void save() {
        if (stack != null) {
            m_187476_(stack);
        }
    }

    private void sound(Player player, SoundEvent sound) {
        if (stack != null) {
            player.m_9236_().m_6263_(null, player.m_20185_(), player.m_20186_(), player.m_20189_(), sound,
                    SoundSource.PLAYERS, 0.5F, 1.0F);
        }
    }

    @Override
    public void m_6596_() { // setChanged: Aquaculture's item handler calls this on every slot change
        save();
    }

    @Override
    public void startOpen(Player player) {
        sound(player, AquaSounds.TACKLE_BOX_OPEN.get());
    }

    @Override
    public void stopOpen(Player player) {
        save();
        sound(player, AquaSounds.TACKLE_BOX_CLOSE.get());
    }
}
