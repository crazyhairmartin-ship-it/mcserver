package fotfskills.pet;

import fotfskills.perk.Perks;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.WeakHashMap;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.TamableAnimal;
import net.minecraft.world.entity.ai.goal.target.OwnerHurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.OwnerHurtTargetGoal;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * Fay's Fairies as companions. A tamed fairy that isn't sitting heals its hurt owner half a heart every 5 seconds while
 * within 12 blocks. Fae Bond (Magic tree, perk "fae_bond" = 0.1 per rank) gives a 10/20/30% chance that a nearby fairy
 * saves its owner from a killing blow: the fairy circles them, they're left with 4 hearts and a moment of regeneration,
 * and that fairy can't save them again for 10 minutes. Tamed fairies also pick the owner's attacker or target as their
 * own target without ever attacking, so target-based collar enchantments (Shadow Hands, Magnetic, Psychic Wall) work.
 */
public final class FairyCompanion {
    private static final double HEAL_RANGE = 12;
    private static final long HEAL_EVERY = 100;
    private static final double SAVE_RANGE = 16;
    private static final long SAVE_COOLDOWN = 12000;
    private static final int ORBIT_TICKS = 40;
    private static final String FAIRY_TAG = "FotfFairy";
    private final Map<LivingEntity, Long> lastHeal = new WeakHashMap<>();
    private final Map<LivingEntity, Long> lastSave = new WeakHashMap<>();
    private final List<Orbit> orbits = new ArrayList<>();

    private record Orbit(LivingEntity fairy, ServerPlayer player, long start) {
    }

    public static boolean isFairy(Entity entity) {
        ResourceLocation id = ForgeRegistries.ENTITY_TYPES.getKey(entity.m_6095_());
        return id != null && id.m_135827_().equals("fays_fairies");
    }

    @SubscribeEvent
    public void onJoin(EntityJoinLevelEvent event) {
        if (!event.getLevel().f_46443_ && event.getEntity() instanceof TamableAnimal fairy && isFairy(fairy)) {
            try {                                  // targets only: fairies never attack
                net.minecraft.world.entity.ai.goal.GoalSelector targets = net.minecraftforge.fml.util.ObfuscationReflectionHelper
                        .getPrivateValue(net.minecraft.world.entity.Mob.class, fairy, "f_21346_");
                targets.m_25352_(1, new OwnerHurtByTargetGoal(fairy));
                targets.m_25352_(2, new OwnerHurtTargetGoal(fairy));
                net.minecraft.world.entity.ai.goal.GoalSelector goals = net.minecraftforge.fml.util.ObfuscationReflectionHelper
                        .getPrivateValue(net.minecraft.world.entity.Mob.class, fairy, "f_21345_");
                goals.m_25352_(1, new net.minecraft.world.entity.ai.goal.SitWhenOrderedToGoal(fairy));
            } catch (RuntimeException ignored) {
                // no targets: collar enchantments that need one just stay idle
            }
        }
    }

    @SubscribeEvent
    public void onFairyTick(LivingEvent.LivingTickEvent event) {
        if (!(event.getEntity() instanceof TamableAnimal fairy) || !(fairy.m_9236_() instanceof ServerLevel level)
                || fairy.f_19797_ % 20 != 0 || !isFairy(fairy) || fairy.m_21827_()
                || !(fairy.m_269323_() instanceof ServerPlayer owner) || owner.m_9236_() != level
                || owner.m_21223_() >= owner.m_21233_() || !owner.m_6084_() || fairy.m_20280_(owner) > HEAL_RANGE * HEAL_RANGE) {
            return;
        }
        long now = level.m_46467_();
        if (now - lastHeal.getOrDefault(fairy, Long.MIN_VALUE / 2) < HEAL_EVERY) {
            return;
        }
        lastHeal.put(fairy, now);
        owner.m_5634_(1.0f);
        level.m_8767_(ParticleTypes.f_175827_, owner.m_20185_(), owner.m_20186_() + 1.0, owner.m_20189_(), 6, 0.3, 0.4, 0.3, 0.02);
        level.m_6263_(null, fairy.m_20185_(), fairy.m_20186_(), fairy.m_20189_(), SoundEvents.f_144243_, SoundSource.NEUTRAL, 0.4f, 1.8f);
    }

    @SubscribeEvent(priority = EventPriority.HIGHEST)
    public void onDeath(LivingDeathEvent event) {
        if (event.isCanceled() || !(event.getEntity() instanceof ServerPlayer player) || !(player.m_9236_() instanceof ServerLevel level)) {
            return;
        }
        double chance = Perks.get(player, "fae_bond");
        if (chance <= 0 || Perks.random() >= chance) {
            return;
        }
        long now = level.m_46467_();
        for (LivingEntity entity : level.m_45976_(LivingEntity.class, player.m_20191_().m_82400_(SAVE_RANGE))) {
            if (!(entity instanceof TamableAnimal fairy) || !isFairy(fairy) || !player.m_20148_().equals(fairy.m_21805_())
                    || !fairy.m_6084_() || now - lastSave.getOrDefault(fairy, Long.MIN_VALUE / 2) < SAVE_COOLDOWN) {
                continue;
            }
            lastSave.put(fairy, now);
            event.setCanceled(true);
            player.m_21153_(8.0f);
            player.m_20095_();
            player.m_7292_(new MobEffectInstance(MobEffects.f_19605_, 100, 1));
            orbits.add(new Orbit(fairy, player, now));
            SoundEvent hey = ForgeRegistries.SOUND_EVENTS.getValue(new ResourceLocation("fays_fairies", "navi_hey"));
            level.m_6263_(null, player.m_20185_(), player.m_20186_(), player.m_20189_(), hey != null ? hey : SoundEvents.f_144243_,
                    SoundSource.PLAYERS, 1.0f, 1.0f);
            player.m_5661_(Component.m_237113_("§dYour fairy saved you!"), true);
            return;
        }
    }

    /**
     * The owner's right-click: with an empty hand a tamed fairy stays put / follows again; with a glass bottle she goes
     * into a Fairy Bottle that keeps everything about her (name, colour, owner, health).
     */
    @SubscribeEvent(priority = EventPriority.HIGHEST)
    public void onInteract(net.minecraftforge.event.entity.player.PlayerInteractEvent.EntityInteract event) {
        if (!(event.getTarget() instanceof TamableAnimal fairy) || !isFairy(fairy) || !fairy.m_21824_()
                || !event.getEntity().m_20148_().equals(fairy.m_21805_()) || event.getHand() != net.minecraft.world.InteractionHand.MAIN_HAND) {
            return;
        }
        net.minecraft.world.entity.player.Player player = event.getEntity();
        net.minecraft.world.item.ItemStack held = player.m_21120_(event.getHand());
        if (held.m_41619_()) {
            if (!fairy.m_9236_().f_46443_) {
                boolean sit = !fairy.m_21827_();
                fairy.m_21839_(sit);
                fairy.m_21837_(sit);
                fairy.m_21573_().m_26573_();
                player.m_5661_(Component.m_237113_(sit ? "§dYour fairy will wait here." : "§dYour fairy follows you."), true);
            }
            event.setCanceled(true);
            event.setCancellationResult(net.minecraft.world.InteractionResult.SUCCESS);
        } else if (held.m_150930_(net.minecraft.world.item.Items.f_42590_)) {
            net.minecraft.world.item.Item bottle = ForgeRegistries.ITEMS.getValue(new ResourceLocation("fays_fairies", "fairy_bottle"));
            if (bottle != null && !fairy.m_9236_().f_46443_) {
                net.minecraft.nbt.CompoundTag saved = new net.minecraft.nbt.CompoundTag();
                if (fairy.m_20223_(saved)) {
                    net.minecraft.world.item.ItemStack filled = new net.minecraft.world.item.ItemStack(bottle);
                    filled.m_41784_().m_128365_(FAIRY_TAG, saved);
                    if (fairy.m_8077_()) {
                        filled.m_41714_(fairy.m_7770_());
                    }
                    held.m_41774_(1);
                    net.minecraftforge.items.ItemHandlerHelper.giveItemToPlayer(player, filled);
                    fairy.m_146870_();
                    fairy.m_9236_().m_6263_(null, fairy.m_20185_(), fairy.m_20186_(), fairy.m_20189_(), SoundEvents.f_11770_,
                            SoundSource.PLAYERS, 1.0f, 1.4f);
                }
            }
            event.setCanceled(true);
            event.setCancellationResult(net.minecraft.world.InteractionResult.SUCCESS);
        }
    }

    /** A filled Fairy Bottle used on a block lets her out there and gives the glass bottle back. */
    @SubscribeEvent
    public void onUseBottle(net.minecraftforge.event.entity.player.PlayerInteractEvent.RightClickBlock event) {
        net.minecraft.world.item.ItemStack held = event.getItemStack();
        if (!held.m_41782_() || !held.m_41783_().m_128441_(FAIRY_TAG) || !(event.getLevel() instanceof ServerLevel level)) {
            return;
        }
        net.minecraft.core.BlockPos at = event.getPos().m_121945_(event.getFace() == null ? net.minecraft.core.Direction.UP : event.getFace());
        net.minecraft.nbt.CompoundTag saved = held.m_41783_().m_128469_(FAIRY_TAG).m_6426_();
        Entity fairy = net.minecraft.world.entity.EntityType.m_20645_(saved, level, e -> {
            e.m_7678_(at.m_123341_() + 0.5, at.m_123342_() + 0.2, at.m_123343_() + 0.5, e.m_146908_(), e.m_146909_());
            return e;
        });
        if (fairy != null && level.m_7967_(fairy)) {
            if (fairy instanceof TamableAnimal tame) {
                tame.m_21839_(false);
                tame.m_21837_(false);
            }
            held.m_41774_(1);
            net.minecraftforge.items.ItemHandlerHelper.giveItemToPlayer(event.getEntity(),
                    new net.minecraft.world.item.ItemStack(net.minecraft.world.item.Items.f_42590_));
        }
        event.setCanceled(true);
        event.setCancellationResult(net.minecraft.world.InteractionResult.SUCCESS);
    }

    /** The saving fairy flies two circles around its owner, trailing sparkles. */
    @SubscribeEvent
    public void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || orbits.isEmpty()) {
            return;
        }
        for (Iterator<Orbit> it = orbits.iterator(); it.hasNext(); ) {
            Orbit o = it.next();
            if (!(o.player.m_9236_() instanceof ServerLevel level) || o.fairy.m_9236_() != level || !o.fairy.m_6084_()) {
                it.remove();
                continue;
            }
            long t = level.m_46467_() - o.start;
            if (t > ORBIT_TICKS) {
                it.remove();
                continue;
            }
            double angle = t / (double) ORBIT_TICKS * Math.PI * 4;
            double x = o.player.m_20185_() + Math.cos(angle) * 1.3, z = o.player.m_20189_() + Math.sin(angle) * 1.3;
            double y = o.player.m_20186_() + 0.6 + t / (double) ORBIT_TICKS;
            o.fairy.m_6021_(x, y, z);
            level.m_8767_(ParticleTypes.f_123810_, x, y + 0.2, z, 2, 0.05, 0.05, 0.05, 0.01);
        }
    }
}
