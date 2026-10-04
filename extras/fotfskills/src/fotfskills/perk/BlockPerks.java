package fotfskills.perk;

import fotfskills.world.PlacedBlocks;
import fotfskills.xp.BreakSource;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.enchantment.EnchantmentHelper;
import net.minecraft.world.item.enchantment.Enchantments;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.puffish.skillsmod.api.SkillsAPI;

/** Gathering: break XP (natural blocks only), extra drops, seed back, and mining/chopping speed. */
public final class BlockPerks {
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public void onPlace(BlockEvent.EntityPlaceEvent event) {
        if (!event.isCanceled() && event.getEntity() instanceof ServerPlayer && event.getLevel() instanceof ServerLevel level
                && PlacedBlocks.tracked(new BlockFacts(event.getPlacedBlock()))) {
            PlacedBlocks.of(level).mark(event.getPos());
        }
    }

    /** LOWEST and skip cancelled: a claim mod that stops the break also stops XP and extra drops. */
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public void onBreak(BlockEvent.BreakEvent event) {
        if (event.isCanceled() || !(event.getPlayer() instanceof ServerPlayer player)
                || !(event.getLevel() instanceof ServerLevel level)) {
            return;
        }
        BlockPos pos = event.getPos();
        BlockState state = event.getState();
        boolean placed = PlacedBlocks.of(level).remove(pos);
        if (placed || player.m_7500_() || (state.m_60834_() && !player.m_36298_(state))) {
            return;
        }
        BlockFacts facts = new BlockFacts(state);
        SkillsAPI.updateExperienceSources(player, BreakSource.class, source -> source.rules().experience(facts));

        ItemStack tool = player.m_21205_();
        boolean silk = EnchantmentHelper.m_44843_(Enchantments.f_44985_, tool) > 0;
        boolean fortune = EnchantmentHelper.m_44843_(Enchantments.f_44987_, tool) > 0;
        int copies = 0;
        if (facts.hasTag("forge:ores")) {
            if (!silk && !fortune) {          // spec: never on top of Fortune; silk would duplicate the ore block
                copies += Perks.roll(player, "ore_drops") ? 1 : 0;
                copies += Perks.roll(player, "ore_triple") ? 2 : 0;
            }
        } else if (facts.hasTag("minecraft:logs")) {
            copies += Perks.roll(player, "log_drops") ? 1 : 0;
            copies += Perks.roll(player, "bounty_triple") ? 2 : 0;
        } else if (facts.matureCrop()) {
            copies += Perks.roll(player, "crop_drops") ? 1 : 0;
            copies += Perks.roll(player, "harvest_double") ? 1 : 0;
            if (Perks.roll(player, "seed_back")) {
                Block.m_49840_(level, pos, state.m_60734_().m_7397_(level, pos, state));
            }
        } else if (facts.hasTag("minecraft:flowers") || facts.id().endsWith("_mushroom")) {
            copies += Perks.roll(player, "wild_drops") ? 1 : 0;
            copies += facts.id().endsWith("_mushroom") && Perks.roll(player, "bounty_triple") ? 2 : 0;
        }
        if (copies > 0 && !silk) {
            List<ItemStack> drops = Block.m_49874_(state, level, pos, level.m_7702_(pos), player, tool);
            for (int i = 0; i < copies; i++) {
                for (ItemStack drop : drops) {
                    Block.m_49840_(level, pos, drop.m_41777_());
                }
            }
        }
    }

    /** Runs on both sides; the client reads synced totals (PerkSync) so the crack animation matches. */
    @SubscribeEvent
    public void onBreakSpeed(PlayerEvent.BreakSpeed event) {
        BlockFacts facts = new BlockFacts(event.getState());
        double bonus = 0;
        if (facts.hasTag("minecraft:logs")) {
            bonus += Perks.get(event.getEntity(), "chop_speed");
        } else if (facts.hasTag("minecraft:mineable/pickaxe")) {
            bonus += Perks.get(event.getEntity(), "mining_speed");
            if (facts.id().contains("deepslate")) {
                bonus += Perks.get(event.getEntity(), "deepslate_speed");
            }
        }
        if (bonus > 0) {
            event.setNewSpeed((float) (event.getNewSpeed() * (1 + bonus)));
        }
    }
}
