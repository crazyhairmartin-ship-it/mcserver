package fotfskills.xp;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.TickEvent;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraftforge.event.entity.living.AnimalTameEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.event.entity.living.ShieldBlockEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.puffish.skillsmod.api.SkillsAPI;

/** Taming, hits taken and shield blocks (Defense, capped per attacker), and sprinting/climbing distance (Agility). */
public final class ForgeXpEvents {
    private final Map<UUID, double[]> lastPos = new HashMap<>();
    private final Map<UUID, MoveBank> banks = new HashMap<>();
    /** At most 30 damage per attacker per 5 minutes earns Defense XP (hits and blocks together). */
    private final HitLimiter limiter = new HitLimiter(30, 6000);

    @SubscribeEvent
    public void onTame(AnimalTameEvent event) {
        if (event.getTamer() instanceof ServerPlayer player) {
            AmountSource.award(player, "tame", 1);
        }
    }

    @SubscribeEvent
    public void onShieldBlock(ShieldBlockEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) {
            defense(player, event.getDamageSource().m_7639_(), event.getBlockedDamage(), "shield_block");
        }
    }

    /** Hits from living attackers only: falls, fire, drowning and your own arrows or TNT give nothing. */
    @SubscribeEvent
    public void onHurt(LivingHurtEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) {
            defense(player, event.getSource().m_7639_(), event.getAmount(), "take_hit");
        }
    }

    private void defense(ServerPlayer player, Entity attacker, float amount, String kind) {
        if (attacker instanceof LivingEntity && attacker != player) {
            double granted = limiter.grant(player.m_20148_(), attacker.m_20148_(), amount, player.m_9236_().m_46467_());
            AmountSource.award(player, kind, granted);
        }
    }

    @SubscribeEvent
    public void onTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.player instanceof ServerPlayer player)) {
            return;
        }
        double x = player.m_20185_();
        double z = player.m_20189_();
        double[] last = lastPos.put(player.m_20148_(), new double[] {x, player.m_20186_(), z});
        if (last == null || player.m_20159_() || !(player.m_20142_() || player.m_6147_())) {
            return;
        }
        double moved = player.m_6147_() ? Math.abs(player.m_20186_() - last[1]) : Math.hypot(x - last[0], z - last[2]);
        if (moved > 2) {
            return;                 // teleport, not movement
        }
        MoveBank bank = banks.computeIfAbsent(player.m_20148_(), id -> new MoveBank());
        SkillsAPI.updateExperienceSources(player, AmountSource.class,
                source -> source.kind().equals("move") ? bank.add(moved, source.factor()) : 0);
    }

    @SubscribeEvent
    public void onLogout(PlayerEvent.PlayerLoggedOutEvent event) {
        UUID id = event.getEntity().m_20148_();
        lastPos.remove(id);
        banks.remove(id);
        limiter.removePlayer(id);
    }
}
