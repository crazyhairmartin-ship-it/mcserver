package fotfskills.perk;

import java.util.ArrayList;
import java.util.List;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.items.ItemHandlerHelper;

/** Treat Saver: after you feed or tame an animal, the food it ate may come back. */
public final class TamingPerks {
    private record Fed(ServerPlayer player, InteractionHand hand, Item item, int before) {
    }

    private final List<Fed> pending = new ArrayList<>();

    @SubscribeEvent
    public void onInteract(PlayerInteractEvent.EntityInteract event) {
        if (event.getEntity() instanceof ServerPlayer player && event.getTarget() instanceof Animal animal) {
            ItemStack held = player.m_21120_(event.getHand());
            if (!held.m_41619_() && animal.m_6898_(held) && Perks.get(player, "treat_saver") > 0) {
                pending.add(new Fed(player, event.getHand(), held.m_41720_(), held.m_41613_()));
            }
        }
    }

    /** Checked one tick later: only food that was really used up is refunded. */
    @SubscribeEvent
    public void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || pending.isEmpty()) {
            return;
        }
        for (Fed fed : pending) {
            ItemStack now = fed.player.m_21120_(fed.hand);
            int count = now.m_150930_(fed.item) ? now.m_41613_() : 0;
            if (count == fed.before - 1 && Perks.roll(fed.player, "treat_saver")) {
                if (count > 0) {
                    now.m_41769_(1);
                } else {
                    ItemHandlerHelper.giveItemToPlayer(fed.player, new ItemStack(fed.item));
                }
            }
        }
        pending.clear();
    }
}
