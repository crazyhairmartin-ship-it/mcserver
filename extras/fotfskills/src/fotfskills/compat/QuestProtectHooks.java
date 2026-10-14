package fotfskills.compat;

import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.block.piston.PistonStructureResolver;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.event.level.ExplosionEvent;
import net.minecraftforge.event.level.PistonEvent;
import net.minecraftforge.event.server.ServerStoppingEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.server.ServerLifecycleHooks;

/**
 * Game side of QuestProtect: a protected block (one of a rule's blocks, standing inside one of its structures) can't be
 * broken by a survival player, is left out of explosions and stops a piston that would move or break it. Creative
 * players (ops building or fixing a puzzle) are not stopped.
 * A rule with "reset": blocks of its kind that players place inside its structure can be broken again by players, and
 * are cleared after that many seconds (or when the server stops), so the next player finds the puzzle as it was.
 */
public final class QuestProtectHooks {
    static final PlacedBlocks PLACED = new PlacedBlocks();
    /** Blocks players placed in protected areas for a quest build: theirs to pick up again until the server restarts. */
    static final PlacedBlocks AREA_PLACED = new PlacedBlocks();
    private int ticks;

    @SubscribeEvent(priority = EventPriority.HIGH)
    public void onBreak(BlockEvent.BreakEvent event) {
        Player player = event.getPlayer();
        if (player == null || player.m_7500_() || !(event.getLevel() instanceof ServerLevel level)) {
            return;
        }
        String dim = level.m_46472_().m_135782_().toString();
        if (AREA_PLACED.contains(dim, event.getPos().m_121878_())) {
            AREA_PLACED.remove(dim, event.getPos().m_121878_());   // placed for a quest build: theirs to take back
        } else if (areaBlocks(player, level, event.getPos(), event.getState())) {
            event.setCanceled(true);
            player.m_5661_(Component.m_237113_("§7This place is protected."), true);
            return;
        }
        if (PLACED.contains(dim, event.getPos().m_121878_())) {
            PLACED.remove(dim, event.getPos().m_121878_());   // a block a player put there: theirs to take back
            return;
        }
        if (rule(level, event.getPos(), event.getState()) != null) {
            event.setCanceled(true);
            player.m_5661_(Component.m_237113_("§7That's part of a puzzle. It won't budge."), true);
        }
    }

    @SubscribeEvent
    public void onPlace(BlockEvent.EntityPlaceEvent event) {
        if (!(event.getEntity() instanceof Player player) || player.m_7500_()
                || !(event.getLevel() instanceof ServerLevel level)) {
            return;
        }
        if (areaBlocks(player, level, event.getPos(), event.getPlacedBlock())) {
            if (matchesAny(event.getPlacedBlock(), QuestAreas.allowed(player.m_20148_().toString()))) {
                AREA_PLACED.add(level.m_46472_().m_135782_().toString(), event.getPos().m_121878_(), Long.MAX_VALUE);
                return;   // a block an open quest build step needs
            }
            event.setCanceled(true);
            player.m_5661_(Component.m_237113_("§7This place is protected."), true);
            return;
        }
        QuestProtect.Rule r = rule(level, event.getPos(), event.getPlacedBlock());
        if (r != null && r.resetSeconds() > 0) {
            MinecraftServer server = level.m_7654_();
            PLACED.add(level.m_46472_().m_135782_().toString(), event.getPos().m_121878_(),
                    server.m_129783_().m_46467_() + r.resetSeconds() * 20L);
        }
    }

    @SubscribeEvent
    public void onTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || ++ticks % 100 != 0) {
            return;
        }
        MinecraftServer server = ServerLifecycleHooks.getCurrentServer();
        if (server != null) {
            clear(server, PLACED.takeDue(server.m_129783_().m_46467_()));
        }
    }

    @SubscribeEvent
    public void onStopping(ServerStoppingEvent event) {
        clear(event.getServer(), PLACED.takeAll());
    }

    private static void clear(MinecraftServer server, List<PlacedBlocks.Entry> entries) {
        for (PlacedBlocks.Entry e : entries) {
            ResourceLocation rl = ResourceLocation.m_135820_(e.dimension());
            ServerLevel level = rl == null ? null : server.m_129880_(ResourceKey.m_135785_(Registries.f_256858_, rl));
            BlockPos pos = BlockPos.m_122022_(e.pos());
            if (level != null && level.m_46805_(pos) && !level.m_8055_(pos).m_60795_()) {
                level.m_7471_(pos, false);
            }
        }
    }

    @SubscribeEvent
    public void onExplosion(ExplosionEvent.Detonate event) {
        if ((QuestProtect.rules().isEmpty() && QuestAreas.areas().isEmpty()) || !(event.getLevel() instanceof ServerLevel level)) {
            return;
        }
        event.getAffectedBlocks().removeIf(pos -> inArea(level, pos) || rule(level, pos, level.m_8055_(pos)) != null);
    }

    @SubscribeEvent
    public void onPiston(PistonEvent.Pre event) {
        if ((QuestProtect.rules().isEmpty() && QuestAreas.areas().isEmpty()) || !(event.getLevel() instanceof ServerLevel level)) {
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
            if (inArea(level, pos) || rule(level, pos, level.m_8055_(pos)) != null) {
                return true;
            }
        }
        return false;
    }

    static boolean inArea(ServerLevel level, BlockPos pos) {
        List<QuestAreas.Area> areas = QuestAreas.areas();
        return !areas.isEmpty() && QuestAreas.inside(areas, level.m_46472_().m_135782_().toString(),
                pos.m_123341_(), pos.m_123342_(), pos.m_123343_());
    }

    /** A protected area stops this player breaking or placing this block here (ops and crops are let through). */
    private static boolean areaBlocks(Player player, ServerLevel level, BlockPos pos, BlockState state) {
        if (player.m_20310_(2) || !inArea(level, pos)) {
            return false;
        }
        ResourceLocation crops = ResourceLocation.m_135820_("minecraft:crops");
        return !state.m_204336_(TagKey.m_203882_(Registries.f_256747_, crops));
    }

    private static boolean matchesAny(BlockState state, List<String> keys) {
        if (keys.isEmpty()) {
            return false;
        }
        String id = BuiltInRegistries.f_256975_.m_7981_(state.m_60734_()).toString();
        for (String k : keys) {
            if (k.startsWith("#")) {
                ResourceLocation rl = ResourceLocation.m_135820_(k.substring(1));
                if (rl != null && state.m_204336_(TagKey.m_203882_(Registries.f_256747_, rl))) {
                    return true;
                }
            } else if (k.equals(id)) {
                return true;
            }
        }
        return false;
    }

    /** The rule protecting this block here, or null. */
    static QuestProtect.Rule rule(ServerLevel level, BlockPos pos, BlockState state) {
        List<QuestProtect.Rule> rules = QuestProtect.rules();
        if (rules.isEmpty()) {
            return null;
        }
        String id = BuiltInRegistries.f_256975_.m_7981_(state.m_60734_()).toString();
        List<QuestProtect.Rule> hits = QuestProtect.candidates(rules, id, tag -> {
            ResourceLocation rl = ResourceLocation.m_135820_(tag);
            return rl != null && state.m_204336_(TagKey.m_203882_(Registries.f_256747_, rl));
        });
        for (QuestProtect.Rule rule : hits) {
            for (String s : rule.structures()) {
                if (inStructure(level, pos, s)) {
                    return rule;
                }
            }
        }
        return null;
    }

    /** Is pos inside a structure with this id ("#namespace:tag" for a tag)? */
    static boolean inStructure(ServerLevel level, BlockPos pos, String structure) {
        boolean tag = structure.startsWith("#");
        ResourceLocation rl = ResourceLocation.m_135820_(tag ? structure.substring(1) : structure);
        if (rl == null) {
            return false;
        }
        StructureManager structures = level.m_215010_();
        return tag
                ? structures.m_220491_(pos, TagKey.m_203882_(Registries.f_256944_, rl)).m_73603_()
                : structures.m_220488_(pos, ResourceKey.m_135785_(Registries.f_256944_, rl)).m_73603_();
    }
}
