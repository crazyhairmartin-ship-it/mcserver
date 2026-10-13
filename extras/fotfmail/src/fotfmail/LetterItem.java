package fotfmail;

import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.network.FilteredText;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.WritableBookItem;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;

/**
 * One item from writing to reading: blank, you write on it like a book and quill. Signing it (title = the
 * recipient's mailbox ID) seals it; a sealed letter is read like a written book and is sent by
 * right-clicking any mailbox. Signing is handled in mixin/ServerGamePacketListenerImplMixin.
 */
public class LetterItem extends WritableBookItem {
    public LetterItem(Properties properties) {
        super(properties);
    }

    public static boolean isSigned(ItemStack stack) {
        CompoundTag tag = stack.m_41783_();
        return tag != null && tag.m_128441_("title");
    }

    public static String recipient(ItemStack stack) {
        return stack.m_41783_().m_128461_("title");
    }

    /** Writes the book screen's pages into the letter: plain text while editing, text components once signed. */
    public static void writePages(ItemStack stack, List<FilteredText> pages, boolean signed) {
        ListTag list = new ListTag();
        for (FilteredText page : pages) {
            String text = page.f_215168_();
            list.add(StringTag.m_129297_(signed ? Component.Serializer.m_130703_(Component.m_237113_(text)) : text));
        }
        stack.m_41700_("pages", list);
    }

    @Override
    public InteractionResultHolder<ItemStack> m_7203_(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.m_21120_(hand);
        if (level.m_5776_()) {
            ClientHooks.openLetter(player, stack, hand);
        }
        return InteractionResultHolder.m_19092_(stack, level.m_5776_());
    }

    /** A signed letter goes on an empty lectern for anyone to read (it's in #minecraft:lectern_books); blank ones don't. */
    @Override
    public InteractionResult m_6225_(UseOnContext context) {
        Level level = context.m_43725_();
        net.minecraft.core.BlockPos pos = context.m_8083_();
        net.minecraft.world.level.block.state.BlockState state = level.m_8055_(pos);
        if (isSigned(context.m_43722_()) && state.m_60713_(net.minecraft.world.level.block.Blocks.f_50624_)
                && net.minecraft.world.level.block.LecternBlock.m_269125_(context.m_43723_(), level, pos, state, context.m_43722_())) {
            return InteractionResult.m_19078_(level.m_5776_());
        }
        return InteractionResult.PASS;
    }

    @Override
    public Component m_7626_(ItemStack stack) {
        if (isSigned(stack)) {
            return Component.m_237110_("item.fotfmail.letter.to", recipient(stack));
        }
        return super.m_7626_(stack);
    }

    @Override
    public void m_7373_(ItemStack stack, Level level, List<Component> tooltip, TooltipFlag flag) {
        if (isSigned(stack)) {
            tooltip.add(Component.m_237110_("tooltip.fotfmail.from", stack.m_41783_().m_128461_("author")).m_130940_(ChatFormatting.GRAY));
            tooltip.add(Component.m_237115_("tooltip.fotfmail.send").m_130940_(ChatFormatting.DARK_GREEN));
        } else {
            tooltip.add(Component.m_237115_("tooltip.fotfmail.write").m_130940_(ChatFormatting.GRAY));
        }
    }
}
