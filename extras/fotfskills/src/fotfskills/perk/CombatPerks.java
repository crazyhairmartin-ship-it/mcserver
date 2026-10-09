package fotfskills.perk;

import fotfskills.mixin.AbstractArrowAccessor;
import java.util.ArrayList;
import java.util.Set;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.animal.horse.AbstractHorse;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.item.BowItem;
import net.minecraft.world.item.CrossbowItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.event.entity.living.LivingDropsEvent;
import net.minecraftforge.event.entity.living.LivingEntityUseItemEvent;
import net.minecraftforge.event.entity.living.LivingFallEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.event.entity.player.CriticalHitEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.items.ItemHandlerHelper;
import net.minecraftforge.registries.ForgeRegistries;

/** Ammo saving, draw speed, falls, fire/blast wards, simple damage bonuses, crit damage, and butchering. */
public final class CombatPerks {
    private static final TagKey<Item> ARROWS = TagKey.m_203882_(ForgeRegistries.Keys.ITEMS, new ResourceLocation("minecraft", "arrows"));
    private static final Set<String> FIRE = Set.of("inFire", "onFire", "lava", "hotFloor", "fireball", "unattributedFireball");
    private static final Set<String> HIDES = Set.of("minecraft:leather", "minecraft:rabbit_hide", "minecraft:feather");

    /** Quiver Care: refund the arrow and make the fired one un-pickable, so nothing is duplicated. */
    @SubscribeEvent
    public void onJoin(EntityJoinLevelEvent event) {
        if (event.loadedFromDisk() || event.getLevel().f_46443_ || !(event.getEntity() instanceof AbstractArrow arrow)
                || !(arrow.m_19749_() instanceof ServerPlayer player) || arrow.f_36705_ != AbstractArrow.Pickup.ALLOWED) {
            return;
        }
        ItemStack ammo = ((AbstractArrowAccessor) arrow).fotfskills$pickupItem();
        if (ammo.m_204117_(ARROWS) && Perks.roll(player, "ammo_save")) {
            arrow.f_36705_ = AbstractArrow.Pickup.CREATIVE_ONLY;
            ItemHandlerHelper.giveItemToPlayer(player, ammo.m_41777_());
        }
    }

    /**
     * Steady Hands / Rapid Volley: bows, crossbows and charged throwing weapons (tridents, javelins, knives) draw faster.
     * Runs on the client too (synced perk totals) with a deterministic rule, so the animation and the server agree.
     */
    @SubscribeEvent
    public void onUseTick(LivingEntityUseItemEvent.Tick event) {
        if (!(event.getEntity() instanceof net.minecraft.world.entity.player.Player player)) {
            return;
        }
        ItemStack item = event.getItem();
        if (!(item.m_41720_() instanceof BowItem || item.m_41720_() instanceof CrossbowItem || Weapons.is(item, "thrown"))) {
            return;
        }
        int extra = DrawRule.extra(item.m_41779_() - event.getDuration(), Perks.get(player, "draw_speed"));
        if (extra > 0 && event.getDuration() > extra) {
            event.setDuration(event.getDuration() - extra);
        }
    }

    @SubscribeEvent
    public void onFall(LivingFallEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) {
            return;
        }
        if (event.getDistance() < Perks.get(player, "fall_immunity")) {
            event.setCanceled(true);
            return;
        }
        event.setDamageMultiplier((float) (event.getDamageMultiplier() * (1 - Perks.get(player, "fall_reduction"))));
    }

    @SubscribeEvent
    public void onHurt(LivingHurtEvent event) {
        LivingEntity target = event.getEntity();
        float amount = event.getAmount();
        String type = event.getSource().m_19385_();
        if (target instanceof ServerPlayer player) {
            if (FIRE.contains(type)) {
                amount *= (float) (1 - Perks.get(player, "fire_ward"));
            } else if (type.startsWith("explosion")) {
                amount *= (float) (1 - Perks.get(player, "blast_ward"));
            }
        }
        Entity attacker = event.getSource().m_7639_();
        if (attacker instanceof ServerPlayer player && attacker != target) {
            Entity direct = event.getSource().m_7640_();
            double bonus = 0;
            if (direct instanceof Projectile) {
                bonus += Perks.get(player, "projectile_damage");
            }
            boolean weaponHit = (direct == player && "player".equals(event.getSource().m_19385_()))
                    || !fotfskills.compat.IronsThrow.weapon(direct).m_41619_();     // a swing, or Iron's Throw
            if (weaponHit && target.m_21223_() < 0.3f * target.m_21233_()) {
                bonus += Perks.get(player, "executioner");
            }
            if (player.m_20186_() < 40) {
                bonus += Perks.get(player, "deep_delver");
            }
            if (player.m_36324_().m_38702_() >= 20) {
                bonus += Perks.get(player, "well_fed");
            }
            amount *= (float) (1 + bonus);
        }
        event.setAmount(amount);
    }

    @SubscribeEvent
    public void onCrit(CriticalHitEvent event) {
        if (event.getEntity() instanceof ServerPlayer player && (event.isVanillaCritical() || event.getDamageModifier() > 1)) {
            event.setDamageModifier((float) (event.getDamageModifier() + Perks.get(player, "crit_damage")));
        }
    }

    /**
     * Butcher / Husbandry: animals you kill may drop an extra copy of each meat, leather or feather stack. Only loot:
     * horses/donkeys/llamas (their chests spill into the drops), held or worn items and stacks with NBT are skipped.
     */
    @SubscribeEvent
    public void onDrops(LivingDropsEvent event) {
        if (!(event.getEntity() instanceof Animal animal) || animal instanceof AbstractHorse
                || !(event.getSource().m_7639_() instanceof ServerPlayer player)) {
            return;
        }
        for (ItemEntity drop : new ArrayList<>(event.getDrops())) {
            ItemStack stack = drop.m_32055_();
            ResourceLocation key = ForgeRegistries.ITEMS.getKey(stack.m_41720_());
            boolean animalGood = (stack.m_41614_() || (key != null && HIDES.contains(key.toString())))
                    && !stack.m_41782_() && !equipped(animal, stack);
            if (animalGood && Perks.roll(player, "animal_drops")) {
                event.getDrops().add(new ItemEntity(animal.m_9236_(), animal.m_20185_(), animal.m_20186_(), animal.m_20189_(), stack.m_41777_()));
            }
        }
    }

    private static boolean equipped(Animal animal, ItemStack stack) {
        for (EquipmentSlot slot : EquipmentSlot.values()) {
            if (ItemStack.m_41656_(animal.m_6844_(slot), stack)) {
                return true;
            }
        }
        return false;
    }
}
