package fotfskills.perk;

import com.mojang.brigadier.context.CommandContext;
import java.util.Map;
import java.util.TreeMap;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.puffish.skillsmod.api.Category;
import net.puffish.skillsmod.api.SkillsAPI;

/**
 * /fotfskills levelups on|off  - show or hide skill level-up messages (saved per player)
 * /fotfskills perks            - list every perk you have and its total (for checking nodes while playtesting)
 * /fotfskills reset <tree>     - get a tree's points back for 1 XP level per 2 points spent (at least 5)
 */
public final class FotfCommands {
    @SubscribeEvent
    public void onRegister(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.m_82127_("fotfskills")
                .then(Commands.m_82127_("levelups")
                        .then(Commands.m_82127_("on").executes(ctx -> levelUps(ctx, true)))
                        .then(Commands.m_82127_("off").executes(ctx -> levelUps(ctx, false))))
                .then(Commands.m_82127_("perks").executes(FotfCommands::perks))
                .then(Commands.m_82127_("reset")
                        .then(Commands.m_82129_("tree", com.mojang.brigadier.arguments.StringArgumentType.word())
                                .suggests((ctx, builder) -> {
                                    SkillsAPI.streamCategories().forEach(c -> builder.suggest(c.getId().m_135815_()));
                                    return builder.buildFuture();
                                })
                                .executes(FotfCommands::reset))));
    }

    private static int levelUps(CommandContext<CommandSourceStack> ctx, boolean on) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        ServerPlayer player = ctx.getSource().m_81375_();
        Prefs.of(player.m_20194_()).setLevelUps(player.m_20148_(), on);
        ctx.getSource().m_288197_(() -> Component.m_237113_("Skill level-up messages " + (on ? "on." : "off.")), false);
        return 1;
    }

    private static int perks(CommandContext<CommandSourceStack> ctx) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        ServerPlayer player = ctx.getSource().m_81375_();
        Map<String, Double> totals = new TreeMap<>(Perks.TOTALS.snapshot(player.m_20148_()));
        if (totals.isEmpty()) {
            ctx.getSource().m_288197_(() -> Component.m_237113_("You have no perks yet."), false);
            return 1;
        }
        StringBuilder text = new StringBuilder("§6Your perks (" + totals.size() + "):§r");
        totals.forEach((perk, value) -> text.append("\n §e").append(perk).append("§f ")
                .append(value < 1 && value > 0 ? Math.round(value * 1000) / 10.0 + "%" : String.valueOf(Math.round(value * 100) / 100.0)));
        ctx.getSource().m_288197_(() -> Component.m_237113_(text.toString()), false);
        return 1;
    }

    /** Gives back every point in one tree for 1 XP level per 2 points spent (at least 5). */
    private static int reset(CommandContext<CommandSourceStack> ctx) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        ServerPlayer player = ctx.getSource().m_81375_();
        String tree = com.mojang.brigadier.arguments.StringArgumentType.getString(ctx, "tree");
        Category category = SkillsAPI.streamCategories().filter(c -> c.getId().m_135815_().equals(tree)).findFirst().orElse(null);
        if (category == null) {
            ctx.getSource().m_288197_(() -> Component.m_237113_("§cNo skill tree called " + tree + "."), false);
            return 0;
        }
        int spent = category.getSpentPoints(player);
        int cost = ResetCost.levels(spent);
        if (spent == 0) {
            ctx.getSource().m_288197_(() -> Component.m_237113_("You haven't spent any points in " + tree + "."), false);
            return 0;
        }
        if (player.f_36078_ < cost) {
            ctx.getSource().m_288197_(() -> Component.m_237113_("§cResetting " + tree + " costs " + cost
                    + " XP levels (1 per 2 points spent, at least 5). You have " + player.f_36078_ + "."), false);
            return 0;
        }
        player.m_6749_(-cost);
        category.resetSkills(player);
        ctx.getSource().m_288197_(() -> Component.m_237113_("§6" + tree + "§f reset: " + spent
                + " points back for " + cost + " XP levels."), false);
        return 1;
    }
}
