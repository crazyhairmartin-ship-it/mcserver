package fotfskills.perk;

import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.AgeableMob;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.horse.AbstractHorse;
import net.minecraftforge.event.entity.living.BabyEntitySpawnEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/** Breeder (twins, faster growth), Selective Breeding, Prized Stock (foal stats, shorter breeding cooldown) and Bloodlines (rare looks) on player-caused breeding. */
public final class BreedingPerks {
    /** Breeder: a thrown egg that lands has an extra chance to hatch one more chick. */
    @SubscribeEvent
    public void onEggLands(net.minecraftforge.event.entity.ProjectileImpactEvent event) {
        if (!(event.getProjectile() instanceof net.minecraft.world.entity.projectile.ThrownEgg egg)
                || !(egg.m_19749_() instanceof net.minecraft.server.level.ServerPlayer player)
                || !(egg.m_9236_() instanceof ServerLevel level) || !Perks.roll(player, "egg_hatch")) {
            return;
        }
        net.minecraft.world.entity.animal.Chicken chick = net.minecraft.world.entity.EntityType.f_20555_.m_20615_(level);
        if (chick != null) {
            chick.m_146762_(-24000);
            chick.m_7678_(egg.m_20185_(), egg.m_20186_(), egg.m_20189_(), egg.m_146908_(), 0);
            level.m_7967_(chick);
        }
    }

    private static final Attribute[] HORSE_STATS = {Attributes.f_22276_, Attributes.f_22279_, Attributes.f_22288_};
    private static final double[] VANILLA_MAX = {30, 0.3375, 1.0};
    private record Grow(AgeableMob child, int age) {
    }
    private static final java.util.List<Grow> GROWTH = new java.util.ArrayList<>();
    private static final java.util.List<Grow> COOLDOWN = new java.util.ArrayList<>();

    @SubscribeEvent
    public void onServerTick(net.minecraftforge.event.TickEvent.ServerTickEvent event) {
        if (event.phase != net.minecraftforge.event.TickEvent.Phase.END || (GROWTH.isEmpty() && COOLDOWN.isEmpty())) {
            return;
        }
        for (Grow g : GROWTH) {
            if (g.child.m_6084_() && g.child.m_146764_() < g.age) {
                g.child.m_146762_(g.age);
            }
        }
        GROWTH.clear();
        for (Grow g : COOLDOWN) {
            if (g.child.m_6084_() && g.child.m_146764_() > g.age) {
                g.child.m_146762_(g.age);            // parents: vanilla set 6000 ticks after the event
            }
        }
        COOLDOWN.clear();
    }

    @SubscribeEvent(priority = EventPriority.LOW)
    public void onBaby(BabyEntitySpawnEvent event) {
        if (event.isCanceled() || !(event.getCausedByPlayer() instanceof ServerPlayer player) || event.getChild() == null
                || !(event.getParentA() instanceof AgeableMob a) || !(event.getParentB() instanceof AgeableMob b)) {
            return;
        }
        AgeableMob child = event.getChild();
        shape(player, child, a, b);
        double cut = Perks.get(player, "breed_cooldown");
        if (cut > 0) {
            int cooldown = Breeding.cooldown(6000, cut);
            COOLDOWN.add(new Grow(a, cooldown));
            COOLDOWN.add(new Grow(b, cooldown));
        }
        if (Perks.roll(player, "twins") && a.m_9236_() instanceof ServerLevel level) {
            AgeableMob twin = a.m_142606_(level, b);
            if (twin != null) {
                twin.m_6863_(true);
                twin.m_7678_(a.m_20185_(), a.m_20186_(), a.m_20189_(), 0, 0);
                shape(player, twin, a, b);
                level.m_7967_(twin);
            }
        }
    }

    /** Bloodlines: rewrite the baby's saved look (Bloodlines.rare) and load it back before it joins the world. */
    private static void rare(AgeableMob child) {
        net.minecraft.resources.ResourceLocation id = net.minecraft.world.entity.EntityType.m_20613_(child.m_6095_());
        java.util.Map<String, Object> look = Bloodlines.rare(id.toString(), new java.util.Random());
        if (look.isEmpty()) {
            return;
        }
        net.minecraft.nbt.CompoundTag tag = child.m_20240_(new net.minecraft.nbt.CompoundTag());
        look.forEach((key, value) -> {
            if (value instanceof Integer i) {
                tag.m_128405_(key, i);
            } else if (value instanceof Byte b) {
                tag.m_128344_(key, b);
            } else if (value instanceof Boolean b) {
                tag.m_128379_(key, b);
            } else {
                tag.m_128359_(key, value.toString());
            }
        });
        child.m_20258_(tag);
    }

    /** Faster growth for every baby; better-parent stats (and bonuses) for foals. */
    private static void shape(ServerPlayer player, AgeableMob child, AgeableMob a, AgeableMob b) {
        double rareChance = Perks.get(player, "bloodlines") * (child instanceof net.minecraft.world.entity.animal.Sheep ? 2 : 1);
        if (Perks.random() < rareChance) {           // sheep have so many colours they get twice the chance
            rare(child);
        }
        double growth = Perks.get(player, "growth");
        if (growth > 0) {
            GROWTH.add(new Grow(child, (int) (-24000 * (1 - growth))));   // set next tick: vanilla's setBaby resets age
        }
        if (Perks.get(player, "breed_bonus") > 0 && child instanceof AbstractHorse && a instanceof AbstractHorse && b instanceof AbstractHorse) {
            double prized = Perks.get(player, "prized_stock");
            for (int i = 0; i < HORSE_STATS.length; i++) {
                AttributeInstance ci = child.m_21051_(HORSE_STATS[i]);
                AttributeInstance ai = a.m_21051_(HORSE_STATS[i]);
                AttributeInstance bi = b.m_21051_(HORSE_STATS[i]);
                if (ci != null && ai != null && bi != null) {
                    ci.m_22100_(Breeding.stat(ai.m_22115_(), bi.m_22115_(), Perks.roll(player, "breed_bonus"), VANILLA_MAX[i], prized));
                }
            }
            child.m_21153_(child.m_21233_());
        }
    }
}
