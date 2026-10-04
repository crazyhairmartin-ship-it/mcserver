package fotfskills.perk;

import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.NeutralMob;
import net.minecraft.world.entity.animal.Bee;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.BeehiveBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.ComposterBlock;
import net.minecraft.world.level.block.CropBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.level.block.state.properties.Property;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * Farming and foraging extras: Green Thumb (planted crops start a stage later), Fertile Soil (crops near you get extra
 * growth ticks), Sweeping Harvest (scythes reap mature crops around the broken one), and right-click harvests checked
 * one tick later: Berry Picker (a bush's age went down: berries picked), Beekeeper (a full hive was emptied), Compost
 * King (a composter filled a layer).
 */
public final class FarmPerks {
    private record Click(ServerPlayer player, ServerLevel level, BlockPos pos, BlockState before) {
    }

    private final List<Click> clicks = new ArrayList<>();
    private static boolean sweeping;

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public void onPlace(BlockEvent.EntityPlaceEvent event) {
        if (event.isCanceled() || !(event.getEntity() instanceof ServerPlayer player)
                || !(event.getPlacedBlock().m_60734_() instanceof CropBlock crop) || !Perks.roll(player, "green_thumb")) {
            return;
        }
        BlockState placed = event.getPlacedBlock();
        IntegerProperty age = age(placed);
        if (age != null && placed.m_61143_(age) < max(age)) {
            event.getLevel().m_7731_(event.getPos(), placed.m_61124_(age, placed.m_61143_(age) + 1), 3);
        }
    }

    /** Fertile Soil: extra random ticks on crops around the player (about 20 attempts a second per 1.0). */
    @SubscribeEvent
    public void onPlayerTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.player instanceof ServerPlayer player) || player.f_19797_ % 20 != 0) {
            return;
        }
        double fertile = Perks.get(player, "fertile_soil");
        if (fertile <= 0 || !(player.m_9236_() instanceof ServerLevel level)) {
            return;
        }
        int tries = (int) Math.round(fertile * 20);
        BlockPos center = player.m_20183_();
        for (int i = 0; i < tries; i++) {
            BlockPos pos = center.m_7918_(level.f_46441_.m_188503_(9) - 4, level.f_46441_.m_188503_(3) - 1, level.f_46441_.m_188503_(9) - 4);
            BlockState state = level.m_8055_(pos);
            if (state.m_60734_() instanceof CropBlock && state.m_60823_()) {
                state.m_222972_(level, pos, level.f_46441_);
            }
        }
    }

    /** Sweeping Harvest: called from BlockPerks.onBroken for a mature crop broken with a scythe. */
    public static void sweep(ServerPlayer player, BlockPos pos, BlockState state) {
        int radius = Math.min(2, (int) Math.round(Perks.get(player, "sweeping_harvest")));   // 3x3x3, then 5x3x5
        if (sweeping || radius <= 0 || !Weapons.is(player.m_21205_(), "scythe")) {
            return;
        }
        sweeping = true;
        try {
            for (int dy = -1; dy <= 1; dy++) {             // one block up and down, for sloped and terraced fields
                for (int dx = -radius; dx <= radius; dx++) {
                    for (int dz = -radius; dz <= radius; dz++) {
                        BlockPos other = pos.m_7918_(dx, dy, dz);
                        if ((dx != 0 || dy != 0 || dz != 0) && new BlockFacts(player.m_9236_().m_8055_(other)).matureCrop()) {
                            player.f_8941_.m_9280_(other);      // through the game mode: claims, XP and drop perks apply
                        }
                    }
                }
            }
        } finally {
            sweeping = false;
        }
    }

    @SubscribeEvent
    public void onRightClick(PlayerInteractEvent.RightClickBlock event) {
        if (event.getEntity() instanceof ServerPlayer player && event.getLevel() instanceof ServerLevel level) {
            BlockState state = level.m_8055_(event.getPos());
            if (age(state) != null || state.m_60734_() instanceof BeehiveBlock || state.m_60734_() instanceof ComposterBlock) {
                clicks.add(new Click(player, level, event.getPos(), state));
            }
        }
    }

    @SubscribeEvent
    public void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || clicks.isEmpty()) {
            return;
        }
        for (Click c : new ArrayList<>(clicks)) {
            BlockState now = c.level.m_8055_(c.pos);
            if (now.m_60734_() != c.before.m_60734_()) {
                continue;
            }
            Block block = now.m_60734_();
            if (block instanceof ComposterBlock) {
                int before = c.before.m_61143_(ComposterBlock.f_51913_);
                int after = now.m_61143_(ComposterBlock.f_51913_);
                if (after == before + 1 && after < 7 && Perks.roll(c.player, "compost_king")) {
                    c.level.m_7731_(c.pos, now.m_61124_(ComposterBlock.f_51913_, after + 1), 3);
                }
            } else if (block instanceof BeehiveBlock) {
                if (c.before.m_61143_(BeehiveBlock.f_49564_) == 5 && now.m_61143_(BeehiveBlock.f_49564_) == 0
                        && Perks.get(c.player, "beekeeper") > 0) {
                    if (Perks.roll(c.player, "beekeeper")) {
                        Block.m_49840_(c.level, c.pos, new ItemStack(ForgeRegistries.ITEMS.getValue(new ResourceLocation("minecraft", "honeycomb")), 2));
                    }
                    for (Bee bee : c.level.m_45976_(Bee.class, c.player.m_20191_().m_82400_(16))) {
                        bee.m_21662_();                 // bees stay calm
                    }
                }
            } else if (!(block instanceof CropBlock)) {
                IntegerProperty age = age(now);
                if (age != null && c.before.m_61143_(age) > now.m_61143_(age) && Perks.roll(c.player, "berry_picker")) {
                    Block.m_49840_(c.level, c.pos, block.m_7397_(c.level, c.pos, c.before));
                }
            }
        }
        clicks.clear();
    }

    private static IntegerProperty age(BlockState state) {
        for (Property<?> property : state.m_61147_()) {
            if (property instanceof IntegerProperty age && age.m_61708_().equals("age")) {
                return age;
            }
        }
        return null;
    }

    private static int max(IntegerProperty age) {
        return age.m_6908_().stream().max(Integer::compare).orElse(0);
    }
}
