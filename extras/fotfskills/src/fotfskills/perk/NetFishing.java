package fotfskills.perk;

import fotfskills.xp.AmountSource;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.entity.living.LivingEntityUseItemEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * Lilis Lucky Lures' fishing net (hold it on floating debris, books or a fish pool): the Fishing tree's bite-speed perks
 * (Patient Angler, and Storm Fisher in the rain) shorten the hold the same way they shorten a rod's bite wait, and every
 * successful catch gives Fishing XP (source "net_fish", 5 per catch in tools/skills/xp.json).
 */
public final class NetFishing {
    private static final ResourceLocation NET = new ResourceLocation("lilis_lucky_lures", "fishing_net");

    private static boolean isNet(ItemStack stack) {
        return NET.equals(ForgeRegistries.ITEMS.getKey(stack.m_41720_()));
    }

    @SubscribeEvent
    public void onStart(LivingEntityUseItemEvent.Start event) {
        if (!(event.getEntity() instanceof Player player) || !isNet(event.getItem())) {
            return;
        }
        double faster = Perks.get(player, "bite_speed");
        if (player.m_9236_().m_46758_(player.m_20183_().m_7494_())) {
            faster += Perks.get(player, "rain_bite_speed");
        }
        event.setDuration(BiteTime.scale(event.getDuration(), faster));
    }

    /** A catch fills the net with the pool's loot ("EntityLoot"); emptying it again isn't another catch. */
    @SubscribeEvent
    public void onFinish(LivingEntityUseItemEvent.Finish event) {
        if (event.getEntity() instanceof ServerPlayer player && isNet(event.getItem())) {
            ItemStack net = event.getResultStack();
            if (net.m_41782_() && !net.m_41783_().m_128437_("EntityLoot", 10).isEmpty()) {
                AmountSource.award(player, "net_fish", 1);
            }
        }
    }
}
