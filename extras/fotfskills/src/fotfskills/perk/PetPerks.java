package fotfskills.perk;

import fotfskills.xp.AmountSource;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.OwnableEntity;
import net.minecraft.world.entity.TamableAnimal;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.animal.horse.AbstractHorse;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingAttackEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * Taming tree and pet/mount nodes. Every second: owned pets within 32 blocks of their online owner, and anything a
 * player rides, get transient stat modifiers (Bonded, Bonded II, Beastmaster, Alpha, Mount Training, Rider, Saddler);
 * buffed animals that leave range lose them. Event hooks: Pack Tactics, Falconer, Alpha stun, Loyal Guard,
 * Guardian, Caretaker, Pet Treats, Gentle Hand, Pet Scavenging.
 */
public final class PetPerks {
    private static final String[] KEYS = {"pet_health", "pet_damage", "pet_armor", "pet_speed", "pet_jump"};
    /** Animals carrying fotfskills pet modifiers, so they can be cleared when no longer in range. */
    private final List<LivingEntity> buffed = new ArrayList<>();
    private record Attempt(ServerPlayer player, TamableAnimal animal, InteractionHand hand, Item item, int before) {
    }
    private final List<Attempt> attempts = new ArrayList<>();
    private long ticks;

    @SubscribeEvent
    public void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END) {
            return;
        }
        resolveTamingAttempts();
        if (++ticks % 20 != 0) {
            return;
        }
        Map<LivingEntity, double[]> stats = new HashMap<>();   // health, damage, armor, speed, jump
        for (ServerPlayer player : event.getServer().m_6846_().m_11314_()) {
            for (LivingEntity pet : ownedNear(player, 32)) {
                double[] s = stats.computeIfAbsent(pet, p -> new double[5]);
                s[0] += Perks.get(player, "pet_health");
                s[1] += Perks.get(player, "pet_damage");
                s[2] += Perks.get(player, "pet_armor");
                s[3] += Perks.get(player, "pet_speed");
                if (pet instanceof AbstractHorse) {
                    s[0] += Perks.get(player, "mount_health");
                    s[3] += Perks.get(player, "mount_speed");
                    s[4] += Perks.get(player, "mount_jump");
                }
                double regen = Perks.get(player, "pet_regen");
                if (regen > 0 && ticks % 100 == 0) {
                    pet.m_5634_((float) regen);
                }
                if (ticks % 2400 == 0 && Perks.roll(player, "scavenging") && pet.m_20280_(player) < 16 * 16) {
                    scavenge(pet);
                }
            }
            if (player.m_20202_() instanceof LivingEntity mount) {
                double[] s = stats.computeIfAbsent(mount, p -> new double[5]);
                s[2] += Perks.get(player, "ride_armor");
                s[3] += Perks.get(player, "ride_speed");
                s[4] += Perks.get(player, "ride_jump");
            }
        }
        for (LivingEntity old : buffed) {
            if (!stats.containsKey(old) && !old.m_213877_()) {
                apply(old, new double[5]);
            }
        }
        buffed.clear();
        stats.forEach((animal, s) -> {
            apply(animal, s);
            buffed.add(animal);
        });
    }

    private static void apply(LivingEntity animal, double[] s) {
        Modifiers.set(animal, Attributes.f_22276_, KEYS[0], s[0], AttributeModifier.Operation.MULTIPLY_BASE);
        Modifiers.set(animal, Attributes.f_22281_, KEYS[1], s[1], AttributeModifier.Operation.MULTIPLY_BASE);
        Modifiers.set(animal, Attributes.f_22284_, KEYS[2], s[2], AttributeModifier.Operation.ADDITION);
        Modifiers.set(animal, Attributes.f_22279_, KEYS[3], s[3], AttributeModifier.Operation.MULTIPLY_BASE);
        Modifiers.set(animal, Attributes.f_22288_, KEYS[4], s[4], AttributeModifier.Operation.MULTIPLY_BASE);
    }

    /** The player's owned animals within range (any OwnableEntity: tamed pets, tamed horses, modded companions). */
    static List<LivingEntity> ownedNear(ServerPlayer player, double range) {
        List<LivingEntity> out = new ArrayList<>();
        for (LivingEntity entity : player.m_9236_().m_45976_(LivingEntity.class, player.m_20191_().m_82400_(range))) {
            if (entity instanceof OwnableEntity pet && player.m_20148_().equals(pet.m_21805_()) && entity.m_6084_()) {
                out.add(entity);
            }
        }
        return out;
    }

    private static ServerPlayer owner(Entity entity) {
        return entity instanceof OwnableEntity pet && pet.m_269323_() instanceof ServerPlayer player ? player : null;
    }

    private static void scavenge(LivingEntity pet) {
        Item item = ForgeRegistries.ITEMS.getValue(new ResourceLocation(Scavenge.pick(Perks.random())));
        if (item != null) {
            pet.m_9236_().m_7967_(new ItemEntity(pet.m_9236_(), pet.m_20185_(), pet.m_20186_() + 0.5, pet.m_20189_(), new ItemStack(item)));
        }
    }

    @SubscribeEvent(priority = EventPriority.LOW)
    public void onHurt(LivingHurtEvent event) {
        LivingEntity target = event.getEntity();
        Entity attacker = event.getSource().m_7639_();
        Entity direct = event.getSource().m_7640_();
        float amount = event.getAmount();

        // Falconer: the owner's arrow marks the target and sends nearby pets at it.
        if (attacker instanceof ServerPlayer shooter && direct instanceof Projectile && owner(target) == null
                && !(target instanceof Player) && Perks.get(shooter, "falconer") > 0) {
            CombatState state = CombatState.of(shooter);
            state.falconTarget = target.m_20148_();
            state.falconUntil = CombatState.now(shooter) + 200;
            for (LivingEntity pet : ownedNear(shooter, 24)) {
                if (pet instanceof Mob mob && !(pet instanceof TamableAnimal sitter && sitter.m_21827_())) {
                    mob.m_6710_(target);
                }
            }
        }

        // Pack Tactics (owner's melee target) and Falconer (owner's arrow target) damage; Alpha stun.
        ServerPlayer petOwner = owner(attacker);
        if (petOwner != null && target != petOwner) {
            CombatState state = CombatState.of(petOwner);
            long now = CombatState.now(petOwner);
            double pct = 0;
            if (target.m_20148_().equals(state.markedTarget) && now <= state.markedUntil) {
                pct += Perks.get(petOwner, "pack_tactics");
            }
            if (target.m_20148_().equals(state.falconTarget) && now <= state.falconUntil) {
                pct += Perks.get(petOwner, "falconer");
            }
            amount *= (float) (1 + pct);
            if (Perks.roll(petOwner, "pet_stun")) {
                target.m_7292_(new MobEffectInstance(MobEffects.f_19597_, 20, 3, false, true));
            }
        }

        // Guardian: pets and party members near you take less damage.
        double guard = 0;
        ServerPlayer targetOwner = owner(target);
        if (targetOwner != null && targetOwner.m_20280_(target) < 64) {
            guard = Perks.get(targetOwner, "guardian");
        } else if (target instanceof ServerPlayer hurt) {
            for (ServerPlayer friend : hurt.m_284548_().m_6907_()) {
                if (friend != hurt && friend.m_20280_(hurt) < 64
                        && Parties.same(hurt.m_20194_(), hurt.m_20148_(), friend.m_20148_())) {
                    guard = Math.max(guard, Perks.get(friend, "guardian"));
                }
            }
        }
        event.setAmount((float) (amount * (1 - guard)));
    }

    /** Loyal Guard: a nearby pet leaps in and takes nothing; the hit is cancelled for you. */
    @SubscribeEvent
    public void onAttack(LivingAttackEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player) || !(event.getSource().m_7639_() instanceof LivingEntity attacker)
                || attacker == player || Perks.get(player, "loyal_guard") <= 0) {
            return;
        }
        List<LivingEntity> pets = ownedNear(player, 8);
        if (!pets.isEmpty() && Perks.roll(player, "loyal_guard")) {
            event.setCanceled(true);
            LivingEntity pet = pets.get(0);
            if (pet instanceof Mob mob && !(attacker instanceof Player)) {
                mob.m_6710_(attacker);
            }
        }
    }

    /** Caretaker / Pet Treats when feeding your own pet; Gentle Hand when trying to tame. */
    @SubscribeEvent
    public void onInteract(PlayerInteractEvent.EntityInteract event) {
        if (!(event.getEntity() instanceof ServerPlayer player) || !(event.getTarget() instanceof Animal animal)) {
            return;
        }
        ItemStack held = player.m_21120_(event.getHand());
        if (held.m_41619_()) {
            return;
        }
        if (animal instanceof OwnableEntity pet && player.m_20148_().equals(pet.m_21805_()) && animal.m_6898_(held)) {
            animal.m_5634_((float) Perks.get(player, "caretaker"));
            double treat = Perks.get(player, "pet_treats");
            if (treat > 0) {
                animal.m_7292_(new MobEffectInstance(MobEffects.f_19605_, (int) (treat * 20), 0, false, true));
            }
        }
        if (animal instanceof TamableAnimal tamable && !tamable.m_21824_() && Perks.get(player, "gentle_hand") > 0) {
            attempts.add(new Attempt(player, tamable, event.getHand(), held.m_41720_(), held.m_41613_()));
        }
    }

    /** One tick after a taming attempt: if the taming item was used up but the animal is still wild, roll Gentle Hand. */
    private void resolveTamingAttempts() {
        if (attempts.isEmpty()) {
            return;
        }
        for (Attempt a : attempts) {
            ItemStack now = a.player.m_21120_(a.hand);
            int count = now.m_150930_(a.item) ? now.m_41613_() : 0;
            if (count == a.before - 1 && !a.animal.m_21824_() && a.animal.m_6084_() && Perks.roll(a.player, "gentle_hand")) {
                a.animal.m_21828_(a.player);
                a.animal.m_21839_(true);
                a.animal.m_9236_().m_7605_(a.animal, (byte) 7);     // hearts
                AmountSource.award(a.player, "tame", 1);
            }
        }
        attempts.clear();
    }

    /** Nature's Mend: called when the player casts a healing spell. */
    public static void healPets(ServerPlayer player, double amount) {
        if (amount > 0) {
            for (LivingEntity pet : ownedNear(player, 8)) {
                pet.m_5634_((float) amount);
            }
        }
    }
}
