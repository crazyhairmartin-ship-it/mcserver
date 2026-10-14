package fotfskills.compat;

import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.block.piston.PistonStructureResolver;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.event.level.ExplosionEvent;
import net.minecraftforge.event.level.PistonEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/**
 * Game side of QuestProtect: a protected block (one of a rule's blocks, standing inside one of its structures) can't be
 * broken by a survival player, is left out of explosions and stops a piston that would move or break it. Creative
 * players (ops building or fixing a puzzle) are not stopped.
 */
public final class QuestProtectHooks {
    @SubscribeEvent(priority = EventPriority.HIGH)
    public void onBreak(BlockEvent.BreakEvent event) {
        Player player = event.getPlayer();
        if (player == null || player.m_7500_() || !(event.getLevel() instanceof ServerLevel level)) {
            return;
        }
        if (isProtected(level, event.getPos(), event.getState())) {
            event.setCanceled(true);
            player.m_5661_(Component.m_237113_("§7That's part of a puzzle. It won't budge."), true);
        }
    }

    @SubscribeEvent
    public void onExplosion(ExplosionEvent.Detonate event) {
        if (QuestProtect.rules().isEmpty() || !(event.getLevel() instanceof ServerLevel level)) {
            return;
        }
        event.getAffectedBlocks().removeIf(pos -> isProtected(level, pos, level.m_8055_(pos)));
    }

    @SubscribeEvent
    public void onPiston(PistonEvent.Pre event) {
        if (QuestProtect.rules().isEmpty() || !(event.getLevel() instanceof ServerLevel level)) {
            return;
        }
        PistonStructureResolver resolver = event.getStructureHelper();
        if (resolver == null || !resolver.m_60422_()) {
            return;
        }
        if (anyProtected(level, resolver.m_60436_()) || anyProtected(level, resolver.m_60437_())) {
            event.setCanceled(true);
        }
    }

    private static boolean anyProtected(ServerLevel level, List<BlockPos> positions) {
        for (BlockPos pos : positions) {
            if (isProtected(level, pos, level.m_8055_(pos))) {
                return true;
            }
        }
        return false;
    }

    static boolean isProtected(ServerLevel level, BlockPos pos, BlockState state) {
        List<QuestProtect.Rule> rules = QuestProtect.rules();
        if (rules.isEmpty()) {
            return false;
        }
        String id = BuiltInRegistries.f_256975_.m_7981_(state.m_60734_()).toString();
        List<QuestProtect.Rule> hits = QuestProtect.candidates(rules, id, tag -> {
            ResourceLocation rl = ResourceLocation.m_135820_(tag);
            return rl != null && state.m_204336_(TagKey.m_203882_(Registries.f_256747_, rl));
        });
        if (hits.isEmpty()) {
            return false;
        }
        StructureManager structures = level.m_215010_();
        for (QuestProtect.Rule rule : hits) {
            for (String s : rule.structures()) {
                ResourceLocation rl = ResourceLocation.m_135820_(s.startsWith("#") ? s.substring(1) : s);
                if (rl == null) {
                    continue;
                }
                boolean inside = s.startsWith("#")
                        ? structures.m_220491_(pos, TagKey.m_203882_(Registries.f_256944_, rl)).m_73603_()
                        : structures.m_220488_(pos, ResourceKey.m_135785_(Registries.f_256944_, rl)).m_73603_();
                if (inside) {
                    return true;
                }
            }
        }
        return false;
    }
}
