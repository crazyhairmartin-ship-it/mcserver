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

/**
 * /fotfskills levelups on|off  - show or hide skill level-up messages (saved per player)
 * /fotfskills perks            - list every perk you have and its total (for checking nodes while playtesting)
 */
public final class FotfCommands {
    @SubscribeEvent
    public void onRegister(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.m_82127_("fotfskills")
                .then(Commands.m_82127_("levelups")
                        .then(Commands.m_82127_("on").executes(ctx -> levelUps(ctx, true)))
                        .then(Commands.m_82127_("off").executes(ctx -> levelUps(ctx, false))))
                .then(Commands.m_82127_("perks").executes(FotfCommands::perks)));
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
}
