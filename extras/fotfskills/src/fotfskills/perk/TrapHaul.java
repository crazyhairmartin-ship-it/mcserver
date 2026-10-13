package fotfskills.perk;

import fotfskills.xp.AmountSource;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.TagKey;
import net.minecraft.world.Container;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.items.ItemHandlerHelper;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * Lilis Lucky Lures' fish trap: a player who right-clicks one to take the catch gets 5 Fishing XP per fish taken
 * (source "trap_fish"), and Trap Haul (perk "trap_haul", 1/3 per rank) may double each of those fish. The trap's
 * contents are compared before the click and a tick later, so only what the player actually took counts (never
 * hoppers, never the bait they put in).
 */
public final class TrapHaul {
    private static final ResourceLocation TRAP = new ResourceLocation("lilis_lucky_lures", "fish_trap");
    private static final TagKey<Item> FISHES = TagKey.m_203882_(ForgeRegistries.Keys.ITEMS, new ResourceLocation("minecraft", "fishes"));
    private static final TagKey<Item> RAW_FISHES = TagKey.m_203882_(ForgeRegistries.Keys.ITEMS, new ResourceLocation("forge", "raw_fishes"));

    private record Look(ServerPlayer player, ServerLevel level, BlockPos pos, Map<Item, Integer> before) {
    }

    private final List<Look> pending = new ArrayList<>();

    private static Map<Item, Integer> contents(Container trap) {
        Map<Item, Integer> counts = new HashMap<>();
        for (int i = 0; i < trap.m_6643_(); i++) {
            ItemStack stack = trap.m_8020_(i);
            if (!stack.m_41619_()) {
                counts.merge(stack.m_41720_(), stack.m_41613_(), Integer::sum);
            }
        }
        return counts;
    }

    @SubscribeEvent(priority = EventPriority.HIGHEST)
    public void onClick(PlayerInteractEvent.RightClickBlock event) {
        if (!(event.getEntity() instanceof ServerPlayer player) || !(event.getLevel() instanceof ServerLevel level)
                || !TRAP.equals(ForgeRegistries.BLOCKS.getKey(level.m_8055_(event.getPos()).m_60734_()))
                || !(level.m_7702_(event.getPos()) instanceof Container trap)) {
            return;
        }
        pending.add(new Look(player, level, event.getPos().m_7949_(), contents(trap)));
    }

    @SubscribeEvent
    public void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || pending.isEmpty()) {
            return;
        }
        List<Look> looks = new ArrayList<>(pending);
        pending.clear();
        for (Look look : looks) {
            if (!(look.level.m_7702_(look.pos) instanceof Container trap)) {
                continue;
            }
            Map<Item, Integer> after = contents(trap);
            double chance = Perks.get(look.player, "trap_haul");
            int fish = 0;
            for (Map.Entry<Item, Integer> e : look.before.entrySet()) {
                int taken = e.getValue() - after.getOrDefault(e.getKey(), 0);
                ItemStack sample = new ItemStack(e.getKey());
                if (taken <= 0 || !(sample.m_204117_(FISHES) || sample.m_204117_(RAW_FISHES))) {
                    continue;
                }
                fish += taken;
                int extra = Chance.successes(taken, chance, Perks::random);
                if (extra > 0) {
                    ItemHandlerHelper.giveItemToPlayer(look.player, new ItemStack(e.getKey(), extra));
                }
            }
            if (fish > 0) {
                AmountSource.award(look.player, "trap_fish", fish);
            }
        }
    }
}
