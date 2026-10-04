package fotfskills.perk;

import com.mojang.datafixers.util.Pair;
import java.util.Set;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.TagKey;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.food.FoodData;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.entity.living.LivingEntityUseItemEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * Eating: Hearty Meals (extra saturation), Chef (the meal's effects last longer), Harvest Feast (crop foods fill more),
 * Sushi Chef (fish foods give Water Breathing and saturation), Picnic (heals you and party members nearby).
 */
public final class FoodPerks {
    private static final Set<String> CROP_TAGS = Set.of("forge:vegetables", "forge:fruits", "forge:crops", "forge:bread");
    private static final Set<String> FISH_TAGS = Set.of("forge:raw_fishes", "forge:cooked_fishes", "minecraft:fishes");

    @SubscribeEvent
    public void onEat(LivingEntityUseItemEvent.Finish event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) {
            return;
        }
        ItemStack stack = event.getItem();
        FoodProperties food = stack.m_41720_().m_41473_();
        if (food == null) {
            return;
        }
        FoodData data = player.m_36324_();
        float saturation = food.m_38744_() * food.m_38745_() * 2;
        double hearty = Perks.get(player, "hearty_meals");
        if (hearty > 0) {
            data.m_38717_((float) Math.min(data.m_38702_(), data.m_38722_() + saturation * hearty));
        }
        double feast = Perks.get(player, "harvest_feast");
        if (feast > 0 && tagged(stack, CROP_TAGS)) {
            data.m_38707_((int) Math.round(food.m_38744_() * feast), 0);
        }
        double sushi = Perks.get(player, "sushi_chef");
        if (sushi > 0 && tagged(stack, FISH_TAGS)) {
            player.m_7292_(new MobEffectInstance(MobEffects.f_19608_, (int) (600 * sushi), 0, false, true));
            data.m_38717_((float) Math.min(data.m_38702_(), data.m_38722_() + 2 * sushi));
        }
        double chef = Perks.get(player, "chef");
        if (chef > 0) {
            for (Pair<MobEffectInstance, Float> pair : food.m_38749_()) {
                MobEffectInstance base = pair.getFirst();
                MobEffectInstance active = player.m_21124_(base.m_19544_());
                if (active != null && active.m_19564_() == base.m_19564_()) {      // the meal's own effect landed
                    player.m_7292_(new MobEffectInstance(base.m_19544_(), chefDuration(base.m_19557_(), chef),
                            base.m_19564_(), base.m_19571_(), base.m_19572_()));
                }
            }
        }
        double picnic = Perks.get(player, "picnic");
        if (picnic > 0) {
            player.m_5634_((float) picnic);
            for (ServerPlayer friend : player.m_284548_().m_6907_()) {
                if (friend != player && friend.m_20280_(player) < 64
                        && Parties.same(player.m_20194_(), player.m_20148_(), friend.m_20148_())) {
                    friend.m_5634_((float) picnic);
                }
            }
        }
    }

    private static boolean tagged(ItemStack stack, Set<String> tags) {
        for (String tag : tags) {
            if (stack.m_204117_(TagKey.m_203882_(ForgeRegistries.Keys.ITEMS, new ResourceLocation(tag)))) {
                return true;
            }
        }
        return false;
    }

    /** Chef: the food's own effect duration, stretched once (never the time an effect already has left). */
    public static int chefDuration(int foodDuration, double chef) {
        return (int) Math.round(foodDuration * (1 + chef));
    }
}
