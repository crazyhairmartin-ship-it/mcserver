package fotfskills.perk;

import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.Projectile;
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
    private static final UUID CRUSH = UUID.nameUUIDFromBytes("fotfskills:crush".getBytes());
    /** Crushed targets: entity -> tick the armour debuff ends. */
    private final Map<LivingEntity, Long> crushed = new ConcurrentHashMap<>();
    /** Second Wind cooldowns by player; kept across logout so relogging doesn't reset it. */
    private static final Map<UUID, Cooldown> SECOND_WIND = new ConcurrentHashMap<>();
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
        if (abilityHit(player, direct, event.getSource())) {   // a weapon's special attack: same boost as its swings
            event.setAmount((float) (amount * abilityMultiplier(player, player.m_21205_())));
            return;
        }
        if (direct == player && "player".equals(event.getSource().m_19385_())) {   // a real swing, not thorns or spells
            boolean swing = state.swing.first(now);          // the main target; sweep targets share the tick
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
            if (Weapons.twoHanded(player, weapon)) {
                pct += Perks.get(player, "pct_two_handed");
            }
            double momentum = Perks.get(player, "momentum");
            if (swing && momentum > 0) {
                pct += momentum * (state.momentum.hit(now) - 1);
            }
            if (swing && now - state.lastBlock <= 40) {
                pct += Perks.get(player, "shield_bash");
            }
            if (swing && state.counterReady) {
                pct += Perks.get(player, "counter");
                state.counterReady = false;
            }
            if (swing && now - state.lastCast <= 200 && Perks.get(player, "spellbound_steel") > 0) {
                pct += Perks.get(player, "spellbound_steel");
                state.lastCast = -100000;          // the next hit only
            }
            amount *= (float) (1 + pct);
            if (swing && Perks.get(player, "flurry") > 0 && state.flurry.hit(now) == 5) {
                amount *= 2;                        // Flurry: every 5th quick hit strikes twice
                state.flurry.reset();
            }
            if (Weapons.is(weapon, "blunt") && Perks.get(player, "crush_armor") > 0) {
                crush(target, Perks.get(player, "crush_armor"), now);
            }
            event.setAmount(amount);
            if (!swing) {
                return;
            }
            Mana.add(player, Perks.get(player, "spellblade_mana"));
            state.markedTarget = target.m_20148_();
            state.markedUntil = now + 200;
            double cleave = Perks.get(player, "cleave");
            if (cleave > 0 && Weapons.twoHanded(player, weapon)) {
                splash(player, target, target, (float) (amount * cleave), 2.5);
            }
            if (Perks.get(player, "reapers_due") > 0 && Weapons.is(weapon, "scythe") && thirdOfCombo(player, state, now)) {
                splash(player, player, target, amount, 3);   // Reaper's Due: the combo's 3rd attack spins through every
                                                              // hostile mob within 3 blocks at full damage
                reaperSpin(player);
            }
        } else if (direct instanceof Projectile projectile) {
            Projectiles.Kind kind = Projectiles.kind(projectile);
            double pct = 0;
            if (kind == Projectiles.Kind.THROWN) {
                pct += Perks.get(player, "pct_thrown");
                if (Weapons.is(Projectiles.item(projectile), "axe")) {
                    pct += Perks.get(player, "pct_thrown_axe");
                }
            }
            if (kind == Projectiles.Kind.ARROW && target.m_20148_().equals(state.markedTarget) && now <= state.markedUntil) {
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
            Cooldown cooldown = SECOND_WIND.computeIfAbsent(player.m_20148_(), id -> new Cooldown(6000));
            if (cooldown.ready(now)) {
                cooldown.trigger(now);
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
            if (Perks.get(player, "earthshaker") > 0 && Weapons.is(player.m_21205_(), "blunt")) {   // Earthshaker
                for (LivingEntity mob : event.getTarget().m_9236_().m_45976_(LivingEntity.class, event.getTarget().m_20191_().m_82400_(3))) {
                    if (mob instanceof Enemy) {
                        mob.m_7292_(new MobEffectInstance(MobEffects.f_19597_, 30, 3, false, true));
                    }
                }
            }
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
            living.m_6469_(player.m_269291_().m_269374_(player), event.getBlockedDamage() * 0.3f);   // thorns, not a swing
        }
    }

    /** Arrows and thrown weapons a player fires: Eagle Eye (both) and Throwing Arm (thrown) speed; marks the shot for Skirmisher. */
    @SubscribeEvent
    public void onJoin(EntityJoinLevelEvent event) {
        if (event.loadedFromDisk() || event.getLevel().f_46443_ || !(event.getEntity() instanceof Projectile projectile)
                || !(projectile.m_19749_() instanceof ServerPlayer player) || projectile.f_19797_ > 0) {
            return;
        }
        Projectiles.Kind kind = Projectiles.kind(projectile);
        if (kind == Projectiles.Kind.OTHER) {
            return;                                 // spells, pearls, bobbers, snowballs, fireworks
        }
        CombatState.of(player).lastShot = CombatState.now(player);
        double speed = Perks.get(player, "projectile_speed") + (kind == Projectiles.Kind.THROWN ? Perks.get(player, "thrown_speed") : 0);
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

    /**
     * Cleave / Reaper's Due: damage to hostile mobs around center (never pets, villagers, players or armour stands);
     * frontOnly keeps only mobs in front of the player.
     */
    private static final java.util.Set<String> WEAPON_MODS = java.util.Set.of("cataclysm", "mowziesmobs", "alexsmobs",
            "alexscaves", "twilightforest");
    private static final String[] MELEE = {"sword", "light", "two_handed", "polearm", "axe", "blunt", "scythe", "pickaxe"};

    /**
     * A weapon mod's special attack: damage from that mod (its damage type or the entity it sent) that isn't a plain
     * swing and isn't an arrow or thrown weapon (those have their own perks). Iron's spells scale with spell power instead.
     */
    private static boolean abilityHit(ServerPlayer player, Entity direct, net.minecraft.world.damagesource.DamageSource source) {
        if ((direct == player && "player".equals(source.m_19385_()))
                || (direct instanceof Projectile p && Projectiles.kind(p) != Projectiles.Kind.OTHER)) {
            return false;
        }
        String typeMod = source.m_269150_().m_203543_().map(k -> k.m_135782_().m_135827_()).orElse("");
        String entityMod = direct == null || direct == player ? ""
                : net.minecraft.world.entity.EntityType.m_20613_(direct.m_6095_()).m_135827_();
        return WEAPON_MODS.contains(typeMod) || WEAPON_MODS.contains(entityMod);
    }

    private static double abilityMultiplier(ServerPlayer player, ItemStack weapon) {
        if (Weapons.is(weapon, "magic")) {          // magic weapons' special attacks scale with spell power, not weapon perks
            net.minecraft.world.entity.ai.attributes.Attribute spell = net.minecraftforge.registries.ForgeRegistries.ATTRIBUTES
                    .getValue(new net.minecraft.resources.ResourceLocation("irons_spellbooks", "spell_power"));
            double power = spell == null || player.m_21051_(spell) == null ? 1.0 : Math.max(0, player.m_21133_(spell));
            if (Weapons.is(weapon, "thrown")) {     // thrown + magic: the thrown-weapon perks boost the ability too
                power *= 1 + Perks.get(player, "pct_thrown") + (Weapons.is(weapon, "axe") ? Perks.get(player, "pct_thrown_axe") : 0);
            }
            return power;
        }
        java.util.Set<String> types = new java.util.HashSet<>();
        for (String type : MELEE) {
            if (Weapons.is(weapon, type)) {
                types.add(type);
            }
        }
        if (!Weapons.twoHanded(player, weapon)) {
            types.remove("two_handed");
        }
        if (types.isEmpty()) {
            return 1.0;
        }
        double base = 1;
        for (net.minecraft.world.entity.ai.attributes.AttributeModifier m
                : weapon.m_41638_(net.minecraft.world.entity.EquipmentSlot.MAINHAND).get(Attributes.f_22281_)) {
            if (m.m_22217_() == net.minecraft.world.entity.ai.attributes.AttributeModifier.Operation.ADDITION) {
                base += m.m_22218_();
            }
        }
        return DamageBreakdown.abilityMultiplier(base, types, p -> Perks.get(player, p));
    }

    /** The 3rd attack of a Better Combat combo (and the 6th, 9th...); without Better Combat, every 3rd swing in a row. */
    private static boolean thirdOfCombo(ServerPlayer player, CombatState state, long now) {
        if (net.minecraftforge.fml.ModList.get().isLoaded("bettercombat")) {
            int step = ComboStep.of(player);
            if (step >= 0) {
                return step % 3 == 2;
            }
        }
        if (state.reaper.hit(now) == 3) {
            state.reaper.reset();
            return true;
        }
        return false;
    }

    /** The Reaper's Due finisher: a ring of sweeps, the sweep sound, and a spin everyone nearby sees. */
    private static void reaperSpin(ServerPlayer player) {
        if (player.m_9236_() instanceof net.minecraft.server.level.ServerLevel level) {
            for (int i = 0; i < 8; i++) {
                double a = i * Math.PI / 4;
                level.m_8767_(net.minecraft.core.particles.ParticleTypes.f_123766_, player.m_20185_() + Math.cos(a) * 2,
                        player.m_20186_() + 1, player.m_20189_() + Math.sin(a) * 2, 1, 0, 0, 0, 0);
            }
            level.m_6263_(null, player.m_20185_(), player.m_20186_(), player.m_20189_(),
                    net.minecraft.sounds.SoundEvents.f_12317_, net.minecraft.sounds.SoundSource.PLAYERS, 1.0f, 0.8f);
        }
        PerkSync.sendSpin(player);
    }

    /** Hits every hostile mob within radius of center, except center itself and the mob the swing already hit. */
    private void splash(ServerPlayer player, LivingEntity center, LivingEntity alreadyHit, float damage, double radius) {
        splashing = true;
        try {
            for (LivingEntity other : center.m_9236_().m_45976_(LivingEntity.class, center.m_20191_().m_82400_(radius))) {
                if (other == center || other == alreadyHit || !(other instanceof Enemy)) {
                    continue;
                }
                other.m_6469_(player.m_269291_().m_269075_(player), damage);
            }
        } finally {
            splashing = false;
        }
    }
}
