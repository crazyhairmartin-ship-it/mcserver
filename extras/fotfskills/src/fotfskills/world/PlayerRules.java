package fotfskills.world;

import com.mojang.brigadier.context.CommandContext;
import fotfskills.perk.CombatState;
import java.util.ArrayList;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.OwnableEntity;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.entity.living.LivingAttackEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/**
 * Opt-in PvP: /pvp on|off (off by default, saved per player). A player (or their projectile or pet) can only hurt another
 * player or that player's pets when both have it on; turning it off needs 10 seconds out of combat.
 * Also clears the Paragliders "Heart Containers" health bonus still saved on players from before that mod was removed.
 */
public final class PlayerRules {
    private static final String PVP = "FotfPvp";
    private static final String OLD_HEARTS = "Heart Containers";

    private static CompoundTag saved(Player player) {
        CompoundTag data = ((net.minecraftforge.common.extensions.IForgeEntity) (Object) player).getPersistentData();
        CompoundTag kept = data.m_128469_("PlayerPersisted");   // Forge copies this part over on death
        data.m_128365_("PlayerPersisted", kept);
        return kept;
    }

    public static boolean pvp(Player player) {
        return saved(player).m_128471_(PVP);
    }

    /** The player behind a hit: the attacker itself, a projectile's shooter (already resolved by getEntity) or a pet's owner. */
    private static Player responsible(Entity attacker) {
        if (attacker instanceof Player p) {
            return p;
        }
        if (attacker instanceof OwnableEntity pet && pet.m_269323_() instanceof Player owner) {
            return owner;
        }
        return null;
    }

    /** Players and their pets are both covered: hurting another player's pet counts as PvP too. */
    @SubscribeEvent(priority = EventPriority.HIGH)
    public void onAttack(LivingAttackEvent event) {
        Player target = responsible(event.getEntity());
        if (target == null || event.getEntity().m_9236_().f_46443_) {
            return;
        }
        Player attacker = responsible(event.getSource().m_7639_());
        if (attacker != null && attacker != target && !(pvp(attacker) && pvp(target))) {
            event.setCanceled(true);
        }
    }

    @SubscribeEvent
    public void onLogin(PlayerEvent.PlayerLoggedInEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) {
            return;
        }
        AttributeInstance health = player.m_21051_(Attributes.f_22276_);
        if (health == null) {
            return;
        }
        for (AttributeModifier m : new ArrayList<>(health.m_22122_())) {
            if (OLD_HEARTS.equals(m.m_22214_())) {
                health.m_22120_(m.m_22209_());
            }
        }
        if (player.m_21223_() > player.m_21233_()) {
            player.m_21153_(player.m_21233_());
        }
    }

    @SubscribeEvent
    public void onRegister(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.m_82127_("pvp")
                .executes(ctx -> status(ctx))
                .then(Commands.m_82127_("on").executes(ctx -> set(ctx, true)))
                .then(Commands.m_82127_("off").executes(ctx -> set(ctx, false))));
    }

    private static int status(CommandContext<CommandSourceStack> ctx) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        ServerPlayer player = ctx.getSource().m_81375_();
        boolean on = pvp(player);
        ctx.getSource().m_288197_(() -> Component.m_237113_(on
                ? "§cPvP is on§r for you. You can fight other players who have it on too. §7/pvp off§r to stop."
                : "§aPvP is off§r for you: no player can hurt you and you can't hurt them. §7/pvp on§r to fight players who also opted in."), false);
        return 1;
    }

    private static int set(CommandContext<CommandSourceStack> ctx, boolean on) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        ServerPlayer player = ctx.getSource().m_81375_();
        if (!on && pvp(player) && CombatState.now(player) - CombatState.of(player).lastCombat < 200) {
            ctx.getSource().m_288197_(() -> Component.m_237113_("§eYou're in a fight. Wait 10 seconds without combat, then try again."), false);
            return 0;
        }
        saved(player).m_128379_(PVP, on);
        ctx.getSource().m_288197_(() -> Component.m_237113_(on
                ? "§cPvP on.§r You can fight other players who have PvP on."
                : "§aPvP off.§r Players can't hurt you, and you can't hurt them."), false);
        return 1;
    }
}
