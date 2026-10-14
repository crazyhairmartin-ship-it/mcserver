package fotfskills.compat;

import dev.ftb.mods.ftbquests.quest.ServerQuestFile;
import dev.ftb.mods.ftbquests.quest.TeamData;
import dev.ftb.mods.ftbquests.quest.task.KillTask;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.common.extensions.IForgeEntity;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.ModList;
import xaero.pac.common.server.api.OpenPACServerAPI;
import xaero.pac.common.server.parties.party.api.IServerPartyAPI;

/**
 * Game side of SharedKills: remembers which players hurt a mob (in its Forge persistent data), and when it dies,
 * adds the kill to the open FTB Quests kill tasks of the recent helpers still within 64 blocks and of the killer's
 * party members within 32 blocks. The killer is credited by FTB Quests itself.
 */
public final class SharedKillHooks {
    private static final String HITS = "fotfQuestHits";
    private static final long WINDOW_TICKS = 30 * 20;
    private static final double HELPER_RANGE = 64, PARTY_RANGE = 32;

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public void onHurt(LivingHurtEvent event) {
        LivingEntity victim = event.getEntity();
        if (event.isCanceled() || victim instanceof Player || !(victim.m_9236_() instanceof ServerLevel level)
                || !(event.getSource().m_7639_() instanceof ServerPlayer attacker)) {
            return;
        }
        CompoundTag data = ((IForgeEntity) (Object) victim).getPersistentData();
        CompoundTag hits = data.m_128469_(HITS);
        hits.m_128356_(attacker.m_20148_().toString(), level.m_46467_());
        data.m_128365_(HITS, hits);
    }

    @SubscribeEvent(priority = EventPriority.LOW)
    public void onDeath(LivingDeathEvent event) {
        LivingEntity victim = event.getEntity();
        if (event.isCanceled() || victim instanceof Player || !(victim.m_9236_() instanceof ServerLevel level)
                || !(event.getSource().m_7639_() instanceof ServerPlayer killer) || ServerQuestFile.INSTANCE == null) {
            return;
        }
        Map<UUID, Long> hits = new HashMap<>();
        CompoundTag tag = ((IForgeEntity) (Object) victim).getPersistentData().m_128469_(HITS);
        for (String key : tag.m_128431_()) {
            try {
                hits.put(UUID.fromString(key), tag.m_128454_(key));
            } catch (IllegalArgumentException ignored) {
                // not ours
            }
        }
        Set<UUID> helperRange = new HashSet<>();
        Map<UUID, ServerPlayer> byId = new HashMap<>();
        for (ServerPlayer p : level.m_6907_()) {
            byId.put(p.m_20148_(), p);
            if (p.m_20280_(victim) <= HELPER_RANGE * HELPER_RANGE) {
                helperRange.add(p.m_20148_());
            }
        }
        Set<UUID> party = new HashSet<>();
        if (ModList.get().isLoaded("openpartiesandclaims")) {
            IServerPartyAPI p = OpenPACServerAPI.get(level.m_7654_()).getPartyManager().getPartyByMember(killer.m_20148_());
            if (p != null) {
                p.getOnlineMemberStream()
                        .filter(m -> m.m_9236_() == level && m.m_20280_(victim) <= PARTY_RANGE * PARTY_RANGE)
                        .forEach(m -> party.add(m.m_20148_()));
            }
        }
        Set<UUID> others = SharedKills.creditees(killer.m_20148_(), hits, level.m_46467_(), WINDOW_TICKS, helperRange, party);
        if (others.isEmpty()) {
            return;
        }
        ServerQuestFile file = ServerQuestFile.INSTANCE;
        TeamData killerData = file.getOrCreateTeamData(killer);
        List<KillTask> tasks = file.collect(KillTask.class);
        for (UUID id : others) {
            ServerPlayer p = byId.get(id);
            if (p == null) {
                continue;
            }
            TeamData data = file.getOrCreateTeamData(p);
            if (data == killerData) {
                continue;   // same FTB team: progress is already shared
            }
            for (KillTask t : tasks) {
                if (data.getProgress(t) < t.getMaxProgress() && data.canStartTasks(t.getQuest())) {
                    t.kill(data, victim);
                }
            }
        }
    }
}
