package fotfskills.perk;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.UseAnim;
import net.minecraftforge.event.entity.living.LivingEntityUseItemEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * Brewer: drinking a Let's Do drink (beer, wine, tea, coffee, cocktails...) makes the effects it gave last longer, and
 * has a chance to give the drink back. Effects are compared with a snapshot taken when the player started drinking.
 */
public final class DrinkPerks {
    private static final Set<String> LETS_DO = Set.of("brewery", "vinery", "nethervinery", "herbalbrews", "beachparty",
            "farm_and_charm", "bakery", "candlelight", "meadow", "camping");
    private final Map<UUID, Map<MobEffect, Integer>> before = new HashMap<>();
    private final Map<UUID, Map<net.minecraft.world.item.Item, Integer>> inventoryBefore = new HashMap<>();

    private static Map<net.minecraft.world.item.Item, Integer> counts(ServerPlayer player) {
        Map<net.minecraft.world.item.Item, Integer> counts = new HashMap<>();
        net.minecraft.world.entity.player.Inventory inv = player.m_150109_();
        for (int i = 0; i < inv.m_6643_(); i++) {
            ItemStack s = inv.m_8020_(i);
            if (!s.m_41619_()) {
                counts.merge(s.m_41720_(), s.m_41613_(), Integer::sum);
            }
        }
        return counts;
    }

    /** Wildcrafter: potions, and the herbal teas and coffees of Let's Do HerbalBrews. */
    static boolean teaOrPotion(ItemStack stack) {
        if (stack.m_41720_() instanceof net.minecraft.world.item.PotionItem) {
            return true;
        }
        ResourceLocation id = ForgeRegistries.ITEMS.getKey(stack.m_41720_());
        return id != null && id.m_135827_().equals("herbalbrews") && stack.m_41780_() == UseAnim.DRINK;
    }

    static boolean letsDoDrink(ItemStack stack) {
        ResourceLocation id = ForgeRegistries.ITEMS.getKey(stack.m_41720_());
        return id != null && LETS_DO.contains(id.m_135827_()) && stack.m_41780_() == UseAnim.DRINK;
    }

    @SubscribeEvent
    public void onStart(LivingEntityUseItemEvent.Start event) {
        if (event.getEntity() instanceof ServerPlayer player
                && ((letsDoDrink(event.getItem()) && (Perks.get(player, "brewer_duration") > 0 || Perks.get(player, "brewer_save") > 0))
                || (teaOrPotion(event.getItem()) && Perks.get(player, "tea_duration") > 0))) {
            Map<MobEffect, Integer> snapshot = new HashMap<>();
            for (MobEffectInstance effect : player.m_21220_()) {
                snapshot.put(effect.m_19544_(), effect.m_19557_());
            }
            before.put(player.m_20148_(), snapshot);
            inventoryBefore.put(player.m_20148_(), counts(player));
        }
    }

    @SubscribeEvent
    public void onFinish(LivingEntityUseItemEvent.Finish event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) {
            return;
        }
        Map<MobEffect, Integer> snapshot = before.remove(player.m_20148_());
        boolean letsDo = letsDoDrink(event.getItem());
        if (snapshot == null || !(letsDo || teaOrPotion(event.getItem()))) {
            return;
        }
        double bonus = (letsDo ? Perks.get(player, "brewer_duration") : 0)
                + (teaOrPotion(event.getItem()) ? Perks.get(player, "tea_duration") : 0);
        for (MobEffectInstance effect : new ArrayList<>(player.m_21220_())) {
            int longer = DrinkRule.extended(snapshot.getOrDefault(effect.m_19544_(), 0), effect.m_19557_(), bonus);
            if (longer > 0) {
                player.m_7292_(new MobEffectInstance(effect.m_19544_(), longer, effect.m_19564_(), effect.m_19571_(),
                        effect.m_19572_(), effect.m_19575_()));
            }
        }
        Map<net.minecraft.world.item.Item, Integer> had = inventoryBefore.remove(player.m_20148_());
        if (letsDo && Perks.roll(player, "brewer_save")) {
            ItemStack drink = event.getItem();                     // the stack as it was before the sip
            event.setResultStack(drink.m_255036_(drink.m_41613_()));   // the sipped drink comes back
            if (had != null) {                                     // and any empty cup the drink handed out goes again
                counts(player).forEach((item, n) -> {
                    int extra = n - had.getOrDefault(item, 0);
                    if (extra > 0 && item != drink.m_41720_()) {
                        player.m_150109_().m_36022_(st -> st.m_150930_(item), extra, player.f_36095_.m_39730_());
                    }
                });
            }
        }
    }
}
