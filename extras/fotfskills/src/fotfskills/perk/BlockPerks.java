package fotfskills.perk;

import fotfskills.world.PlacedBlocks;
import fotfskills.xp.BreakSource;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.crafting.RecipeType;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.enchantment.EnchantmentHelper;
import net.minecraft.world.item.enchantment.Enchantments;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.piston.PistonStructureResolver;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.event.level.PistonEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.puffish.skillsmod.api.SkillsAPI;

/**
 * Gathering: break XP (natural blocks only), extra drops, seed back, and mining/chopping speed. XP and drops are paid
 * from ServerPlayerGameModeMixin after a block is really destroyed: BreakEvent is also posted as a "may I break?"
 * check (Ars spells, claim checks) that breaks nothing.
 */
public final class BlockPerks {
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public void onPlace(BlockEvent.EntityPlaceEvent event) {
        if (!event.isCanceled() && event.getEntity() instanceof ServerPlayer && event.getLevel() instanceof ServerLevel level
                && PlacedBlocks.tracked(new BlockFacts(event.getPlacedBlock()))) {
            PlacedBlocks.of(level).mark(event.getPos());
        }
    }

    /** Before a piston moves blocks (and only if the move will happen), their placed marks move with them. */
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public void onPiston(PistonEvent.Pre event) {
        if (event.isCanceled() || !(event.getLevel() instanceof ServerLevel level)) {
            return;
        }
        PistonStructureResolver structure = event.getStructureHelper();
        if (structure == null || !structure.m_60422_()) {
            return;
        }
        PlacedBlocks placed = PlacedBlocks.of(level);
        structure.m_60437_().forEach(placed::remove);
        placed.move(structure.m_60436_(), structure.m_155942_());
    }

    /** A block the player really destroyed (state, block entity and tool captured before the break). */
    public static void onBroken(ServerPlayer player, ServerLevel level, BlockPos pos, BlockState state, BlockEntity blockEntity,
                                ItemStack tool) {
        boolean placed = PlacedBlocks.of(level).remove(pos);
        if (placed || player.m_7500_() || (state.m_60834_() && !player.m_36298_(state))) {
            return;
        }
        BlockFacts facts = new BlockFacts(state);
        SkillsAPI.updateExperienceSources(player, BreakSource.class, source -> source.rules().experience(facts));
        if (facts.hasTag("forge:ores") || facts.hasTag("minecraft:base_stone_overworld") || facts.hasTag("minecraft:base_stone_nether")) {
            CombatState.of(player).lastStoneMined = CombatState.now(player);      // Stonehide
        }

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
            FarmPerks.sweep(player, pos, state);
            copies += Perks.roll(player, "crop_drops") ? 1 : 0;
            copies += Perks.roll(player, "harvest_double") ? 1 : 0;
            if (Perks.roll(player, "seed_back")) {
                Block.m_49840_(level, pos, state.m_60734_().m_7397_(level, pos, state));
            }
        } else if (facts.hasTag("minecraft:flowers") || facts.id().endsWith("_mushroom")) {
            copies += Perks.roll(player, "wild_drops") ? 1 : 0;
            copies += facts.id().endsWith("_mushroom") && Perks.roll(player, "bounty_triple") ? 2 : 0;
        }
        if (facts.hasTag("forge:ores") && !silk && Perks.roll(player, "autosmelt")) {
            autosmelt(level, pos);
        }
        if (facts.hasTag("minecraft:base_stone_overworld") && Perks.roll(player, "ore_nose")) {
            Block.m_49840_(level, pos, new ItemStack(ForgeRegistries.ITEMS.getValue(new ResourceLocation("minecraft",
                    Perks.random() < 0.7 ? "iron_nugget" : "gold_nugget"))));
        }
        if (copies > 0 && !silk) {
            List<ItemStack> drops = Block.m_49874_(state, level, pos, blockEntity, player, tool);
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

    /** Auto-smelt: this break's fresh drops at pos (spawned this tick) become their smelting result. */
    private static void autosmelt(ServerLevel level, BlockPos pos) {
        for (ItemEntity drop : level.m_45976_(ItemEntity.class, new AABB(pos).m_82400_(0.75))) {
            if (drop.f_19797_ != 0) {
                continue;
            }
            ItemStack stack = drop.m_32055_();
            level.m_7465_().m_44015_(RecipeType.f_44108_, new SimpleContainer(stack.m_41777_()), level).ifPresent(recipe -> {
                ItemStack result = recipe.m_8043_(level.m_9598_()).m_41777_();
                if (!result.m_41619_()) {
                    result.m_41764_(stack.m_41613_() * result.m_41613_());
                    drop.m_32045_(result);
                }
            });
        }
    }
}
