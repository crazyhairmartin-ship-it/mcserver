package fotfskills.perk;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Set;
import java.util.WeakHashMap;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.Arrow;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.entity.projectile.ThrownTrident;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.enchantment.EnchantmentHelper;
import net.minecraft.world.item.enchantment.Enchantments;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.event.entity.ProjectileImpactEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.items.ItemHandlerHelper;

/**
 * Arrows: Homing Arrows and Seeker (curve toward the nearest hostile mob; Seeker triples the chance and makes them
 * crits, and does the same for thrown weapons), Multishot (two extra un-pickable arrows), Arcane Arrows (a full-draw arrow spends 5 mana for bonus damage).
 * Thrown weapons: Retriever (may fly back to you on impact: Spartan weapons and tridents use their own return, so the
 * catch keeps the right ammo count and nothing is left on the ground; other mods' weapons go straight to the inventory).
 */
public final class RangePerks {
    private record Homer(AbstractArrow arrow, long until) {
    }

    private final List<Homer> homers = new ArrayList<>();
    private record Retrieve(ServerPlayer player, AbstractArrow thrown) {
    }
    private final List<Retrieve> retrieving = new ArrayList<>();
    private final Set<Projectile> clones = Collections.newSetFromMap(new WeakHashMap<>());
    private final Set<Projectile> arcane = Collections.newSetFromMap(new WeakHashMap<>());

    @SubscribeEvent
    public void onJoin(EntityJoinLevelEvent event) {
        if (event.loadedFromDisk() || event.getLevel().f_46443_ || !(event.getEntity() instanceof AbstractArrow arrow)
                || !(arrow.m_19749_() instanceof ServerPlayer player) || arrow.f_19797_ > 0 || clones.contains(arrow)) {
            return;
        }
        Projectiles.Kind kind = Projectiles.kind(arrow);
        if (kind != Projectiles.Kind.ARROW && kind != Projectiles.Kind.THROWN) {
            return;
        }
        long now = CombatState.now(player);
        boolean fullDraw = arrow.m_36792_();      // read before Seeker marks every arrow as a crit
        double seeker = Perks.get(player, "seeker");
        boolean seeks = kind == Projectiles.Kind.ARROW || seeker > 0;   // thrown weapons home only with Seeker
        if (seeks && Perks.random() < Perks.get(player, "homing") * (1 + 2 * seeker)) {
            homers.add(new Homer(arrow, now + 60));
        }
        if (seeker > 0) {
            arrow.m_36762_(true);
        }
        if (kind == Projectiles.Kind.THROWN) {
            return;                               // Arcane Arrows and Multishot are for arrows only
        }
        if (arcaneShot(fullDraw, Perks.get(player, "arcane_arrows")) && Mana.spend(player, 5)) {
            arcane.add(arrow);
        }
        if (Perks.roll(player, "multishot") && event.getLevel() instanceof ServerLevel level) {
            for (double angle : new double[] {-0.17, 0.17}) {
                Arrow extra = new Arrow(level, player);
                Vec3 v = arrow.m_20184_();
                double cos = Math.cos(angle), sin = Math.sin(angle);
                extra.m_20256_(new Vec3(v.f_82479_ * cos - v.f_82481_ * sin, v.f_82480_, v.f_82479_ * sin + v.f_82481_ * cos));
                extra.m_6034_(arrow.m_20185_(), arrow.m_20186_(), arrow.m_20189_());
                extra.m_36781_(arrow.m_36789_());
                extra.m_36762_(arrow.m_36792_());
                extra.f_36705_ = AbstractArrow.Pickup.CREATIVE_ONLY;
                clones.add(extra);
                level.m_7967_(extra);
            }
        }
    }

    /** Arcane Arrows spends mana only on a real full-draw shot (Seeker's crits don't count). */
    static boolean arcaneShot(boolean fullDraw, double arcaneArrows) {
        return fullDraw && arcaneArrows > 0;
    }

    @SubscribeEvent
    public void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END) {
            return;
        }
        for (Retrieve r : retrieving) {
            if (!r.thrown.m_213877_()) {          // still in the world (stuck or bouncing): take it back, give the item
                ItemStack item = Projectiles.item(r.thrown).m_41777_();
                r.thrown.m_146870_();
                ItemHandlerHelper.giveItemToPlayer(r.player, item);
            }
        }
        retrieving.clear();
        if (homers.isEmpty()) {
            return;
        }
        homers.removeIf(h -> {
            AbstractArrow arrow = h.arrow;
            if (arrow.m_213877_() || arrow.m_20096_() || arrow.m_20184_().m_82556_() < 0.04
                    || arrow.m_9236_().m_46467_() > h.until) {
                return true;
            }
            LivingEntity target = null;
            double best = Double.MAX_VALUE;
            Vec3 pos = arrow.m_20182_();
            for (LivingEntity mob : arrow.m_9236_().m_45976_(LivingEntity.class, arrow.m_20191_().m_82400_(12))) {
                Vec3 to = mob.m_20182_().m_82520_(0, mob.m_20206_() / 2, 0).m_82546_(pos);
                if (mob instanceof Enemy && mob.m_6084_() && to.m_82526_(arrow.m_20184_()) > 0 && to.m_82556_() < best) {
                    best = to.m_82556_();
                    target = mob;
                }
            }
            if (target != null) {
                Vec3 to = target.m_20182_().m_82520_(0, target.m_20206_() / 2, 0).m_82546_(pos);
                Vec3 v = arrow.m_20184_();
                double[] s = Homing.steer(new double[] {v.f_82479_, v.f_82480_, v.f_82481_}, new double[] {to.f_82479_, to.f_82480_, to.f_82481_}, 0.25);
                arrow.m_20256_(new Vec3(s[0], s[1], s[2]));
                arrow.f_19812_ = true;          // send the new motion to clients so the curve is visible
            }
            return false;
        });
    }

    @SubscribeEvent
    public void onHurt(LivingHurtEvent event) {
        if (event.getSource().m_7640_() instanceof Projectile projectile && arcane.remove(projectile)
                && event.getSource().m_7639_() instanceof ServerPlayer player) {
            event.setAmount((float) (event.getAmount() * (1 + Perks.get(player, "arcane_arrows"))));
        }
    }

    /** Retriever: a thrown weapon that hits something may jump straight back to your inventory. */
    @SubscribeEvent
    public void onImpact(ProjectileImpactEvent event) {
        if (!(event.getProjectile() instanceof AbstractArrow thrown) || !(thrown.m_19749_() instanceof ServerPlayer player)
                || thrown.f_36705_ != AbstractArrow.Pickup.ALLOWED || Projectiles.kind(thrown) != Projectiles.Kind.THROWN
                || !(event.getRayTraceResult() instanceof EntityHitResult)) {
            return;
        }
        if (thrown instanceof ThrownTrident && EnchantmentHelper.m_44843_(Enchantments.f_44955_, Projectiles.item(thrown)) > 0) {
            return;                                   // Loyalty already brings it back
        }
        if (Perks.roll(player, "retriever") && !ReturnHelper.sendBack(thrown)) {
            thrown.f_36705_ = AbstractArrow.Pickup.CREATIVE_ONLY;
            retrieving.add(new Retrieve(player, thrown));     // other mods' weapons: back to the inventory next tick
        }
    }
}
