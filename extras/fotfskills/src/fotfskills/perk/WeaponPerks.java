package fotfskills.perk;

import fotfskills.mixin.AbstractArrowAccessor;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.TagKey;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.OwnableEntity;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.event.entity.living.LivingDamageEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.entity.living.LivingEntityUseItemEvent;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.event.entity.living.ShieldBlockEvent;
import net.minecraftforge.event.entity.player.CriticalHitEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.registries.ForgeRegistries;

/** Weapon-type damage and the conditional combat perks (Attack, Defense, Range, plus cross-tree weapon nodes). */
public final class WeaponPerks {
    private static final TagKey<Item> ARROWS = TagKey.m_203882_(ForgeRegistries.Keys.ITEMS, new ResourceLocation("minecraft", "arrows"));
    private static final UUID CRUSH = UUID.nameUUIDFromBytes("fotfskills:crush".getBytes());
    /** Crushed targets: entity -> tick the armour debuff ends. */
    private final Map<LivingEntity, Long> crushed = new ConcurrentHashMap<>();
    /** Guards Cleave's splash so it never chains. */
    private boolean splashing;

    @SubscribeEvent(priority = EventPriority.LOW)
    public void onHurt(LivingHurtEvent event) {
        LivingEntity target = event.getEntity();
        Entity attacker = event.getSource().m_7639_();
        Entity direct = event.getSource().m_7640_();
        if (target instanceof ServerPlayer hurtPlayer && attacker instanceof LivingEntity && attacker != hurtPlayer) {
            CombatState.of(hurtPlayer).lastCombat = CombatState.now(hurtPlayer);
            Mana.add(hurtPlayer, Perks.get(hurtPlayer, "battlemage_mana"));
        }
        if (!(attacker instanceof ServerPlayer player) || attacker == target || splashing) {
            return;
        }
        CombatState state = CombatState.of(player);
        long now = CombatState.now(player);
        state.lastCombat = now;
        float amount = event.getAmount();
        if (direct == player) {
            ItemStack weapon = player.m_21205_();
            if (Weapons.is(weapon, "pickaxe") || Weapons.is(weapon, "blunt")) {
                amount += Perks.get(player, "dmg_pickaxe_blunt");
            }
            if (Weapons.is(weapon, "axe")) {
                amount += Perks.get(player, "dmg_axe");
                amount *= (float) ArmorPierce.multiplier(target.m_21230_(), target.m_21133_(Attributes.f_22285_), amount,
                        Perks.get(player, "armor_pierce_axe"));
            }
            if (Weapons.is(weapon, "scythe")) {
                amount += Perks.get(player, "dmg_scythe");
            }
            if (Weapons.is(weapon, "polearm")) {
                amount += Perks.get(player, "dmg_polearm");
            }
            double pct = 0;
            if (Weapons.is(weapon, "two_handed")) {
                pct += Perks.get(player, "pct_two_handed");
            }
            double momentum = Perks.get(player, "momentum");
            if (momentum > 0) {
                pct += momentum * (state.momentum.hit(now) - 1);
            }
            if (now - state.lastBlock <= 40) {
                pct += Perks.get(player, "shield_bash");
            }
            if (state.counterReady) {
                pct += Perks.get(player, "counter");
                state.counterReady = false;
            }
            if (now - state.lastCast <= 200 && Perks.get(player, "spellbound_steel") > 0) {
                pct += Perks.get(player, "spellbound_steel");
                state.lastCast = -100000;          // the next hit only
            }
            amount *= (float) (1 + pct);
            if ((Weapons.is(weapon, "light") || Weapons.is(weapon, "sword")) && Perks.get(player, "flurry") > 0
                    && state.flurry.hit(now) == 5) {
                amount *= 2;                        // Flurry: every 5th quick hit strikes twice
                state.flurry.reset();
            }
            if (Weapons.is(weapon, "blunt") && Perks.get(player, "crush_armor") > 0) {
                crush(target, Perks.get(player, "crush_armor"), now);
            }
            Mana.add(player, Perks.get(player, "spellblade_mana"));
            state.markedTarget = target.m_20148_();
            state.markedUntil = now + 200;
            event.setAmount(amount);
            double cleave = Perks.get(player, "cleave");
            if (cleave > 0 && Weapons.is(weapon, "two_handed")) {
                splash(player, target, (float) (amount * cleave));
            }
        } else if (direct instanceof Projectile projectile) {
            double pct = 0;
            if (thrown(projectile)) {
                pct += Perks.get(player, "pct_thrown");
                ItemStack item = projectile instanceof AbstractArrow arrow ? ((AbstractArrowAccessor) arrow).fotfskills$pickupItem() : ItemStack.f_41583_;
                if (Weapons.is(item, "axe")) {
                    pct += Perks.get(player, "pct_thrown_axe");
                }
            }
            if (target.m_20148_().equals(state.markedTarget) && now <= state.markedUntil) {
                pct += Perks.get(player, "hunters_mark");
            }
            event.setAmount((float) (amount * (1 + pct)));
        }
    }

    /** Second Wind: a hit that would kill leaves you on 1 health, once per 5 minutes (totems are left alone). */
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public void onDamage(LivingDamageEvent event) {
        if (event.getEntity() instanceof ServerPlayer player && event.getAmount() >= player.m_21223_()
                && Perks.get(player, "second_wind") > 0 && !holdingTotem(player)) {
            CombatState state = CombatState.of(player);
            long now = CombatState.now(player);
            if (state.secondWind.ready(now)) {
                state.secondWind.trigger(now);
                event.setAmount(Math.max(0, player.m_21223_() - 1));
            }
        }
    }

    @SubscribeEvent
    public void onDeath(LivingDeathEvent event) {
        if (!(event.getSource().m_7639_() instanceof ServerPlayer player) || event.getSource().m_7640_() != player) {
            return;
        }
        ItemStack weapon = player.m_21205_();
        if (Weapons.is(weapon, "scythe")) {
            player.m_5634_((float) Perks.get(player, "grim_harvest"));
        }
        double berserk = Perks.get(player, "berserker");
        if (berserk > 0 && Weapons.is(weapon, "axe")) {
            player.m_7292_(new MobEffectInstance(MobEffects.f_19600_, (int) (berserk * 20), 0, false, true));
        }
    }

    @SubscribeEvent
    public void onCrit(CriticalHitEvent event) {
        if (event.getEntity() instanceof ServerPlayer player && (event.isVanillaCritical() || event.getDamageModifier() > 1)) {
            player.m_5634_((float) Perks.get(player, "lifeline"));
        }
    }

    @SubscribeEvent
    public void onBlock(ShieldBlockEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) {
            return;
        }
        CombatState state = CombatState.of(player);
        state.lastBlock = CombatState.now(player);
        state.counterReady = Perks.get(player, "counter") > 0;
        Entity attacker = event.getDamageSource().m_7639_();
        if (attacker instanceof LivingEntity living && attacker != player && Perks.roll(player, "shield_thorns")) {
            living.m_6469_(player.m_269291_().m_269075_(player), event.getBlockedDamage() * 0.3f);
        }
    }

    /** Projectiles a player fires: Eagle Eye (all) and Throwing Arm (thrown) speed; marks the shot for Skirmisher. */
    @SubscribeEvent
    public void onJoin(EntityJoinLevelEvent event) {
        if (event.loadedFromDisk() || event.getLevel().f_46443_ || !(event.getEntity() instanceof Projectile projectile)
                || !(projectile.m_19749_() instanceof ServerPlayer player) || projectile.f_19797_ > 0) {
            return;
        }
        CombatState.of(player).lastShot = CombatState.now(player);
        double speed = Perks.get(player, "projectile_speed") + (thrown(projectile) ? Perks.get(player, "thrown_speed") : 0);
        if (speed > 0) {
            projectile.m_20256_(projectile.m_20184_().m_82490_(1 + speed));
        }
    }

    /** Spring Step: jump higher. Runs on the client too (player movement is client-side); reads synced totals. */
    @SubscribeEvent
    public void onJump(LivingEvent.LivingJumpEvent event) {
        if (event.getEntity() instanceof Player player) {
            double boost = Perks.get(player, "jump_boost");
            if (boost > 0) {
                player.m_20256_(player.m_20184_().m_82520_(0, boost, 0));
            }
        }
    }

    /** Brain Food: finishing a meal starts the mana-regen window (ConditionalStats). */
    @SubscribeEvent
    public void onEat(LivingEntityUseItemEvent.Finish event) {
        if (event.getEntity() instanceof ServerPlayer player && event.getItem().m_41614_()) {
            CombatState.of(player).lastMeal = CombatState.now(player);
        }
    }

    @SubscribeEvent
    public void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || crushed.isEmpty()) {
            return;
        }
        crushed.entrySet().removeIf(entry -> {
            LivingEntity target = entry.getKey();
            if (target.m_213877_() || target.m_9236_().m_46467_() >= entry.getValue()) {
                AttributeInstance armor = target.m_21051_(Attributes.f_22284_);
                if (armor != null) {
                    armor.m_22120_(CRUSH);
                }
                return true;
            }
            return false;
        });
    }

    @SubscribeEvent
    public void onLogout(PlayerEvent.PlayerLoggedOutEvent event) {
        CombatState.forget(event.getEntity().m_20148_());
    }

    /** Thrown weapons: any player projectile except a normal arrow (tridents, javelins, tomahawks, knives). */
    private static boolean thrown(Projectile projectile) {
        if (projectile instanceof AbstractArrow arrow) {
            return !((AbstractArrowAccessor) arrow).fotfskills$pickupItem().m_204117_(ARROWS);
        }
        return true;
    }

    private static boolean holdingTotem(Player player) {
        ResourceLocation totem = new ResourceLocation("minecraft", "totem_of_undying");
        return totem.equals(ForgeRegistries.ITEMS.getKey(player.m_21205_().m_41720_()))
                || totem.equals(ForgeRegistries.ITEMS.getKey(player.m_21206_().m_41720_()));
    }

    /** Crusher: the target loses armour for 5 s, stacking with each hit up to 5 points. */
    private void crush(LivingEntity target, double perHit, long now) {
        AttributeInstance armor = target.m_21051_(Attributes.f_22284_);
        if (armor == null) {
            return;
        }
        AttributeModifier old = armor.m_22111_(CRUSH);
        double value = Math.max(-5, (old == null ? 0 : old.m_22218_()) - perHit);
        armor.m_22120_(CRUSH);
        armor.m_22118_(new AttributeModifier(CRUSH, "fotfskills crush", value, AttributeModifier.Operation.ADDITION));
        crushed.put(target, now + 100);
    }

    /** Cleave: part of a two-handed hit splashes to mobs around the target; never players or the attacker's pets. */
    private void splash(ServerPlayer player, LivingEntity target, float damage) {
        splashing = true;
        try {
            for (LivingEntity other : target.m_9236_().m_45976_(LivingEntity.class, target.m_20191_().m_82400_(2.5))) {
                if (other == target || other == player || other instanceof Player
                        || (other instanceof OwnableEntity pet && player.m_20148_().equals(pet.m_21805_()))) {
                    continue;
                }
                other.m_6469_(player.m_269291_().m_269075_(player), damage);
            }
        } finally {
            splashing = false;
        }
    }
}
