package fotfskills.perk;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkRegistry;
import net.minecraftforge.network.PacketDistributor;
import net.minecraftforge.network.simple.SimpleChannel;

/** Sends a player's perk totals to their client after changes (batched once per server tick). */
public final class PerkSync {
    private static final SimpleChannel CHANNEL = NetworkRegistry.newSimpleChannel(
            new ResourceLocation("fotfskills", "perks"), () -> "1", "1"::equals, "1"::equals);
    private static final Set<ServerPlayer> DIRTY = new HashSet<>();

    public record Totals(Map<String, Double> values) {
        static void encode(Totals msg, FriendlyByteBuf buf) {
            buf.m_130130_(msg.values.size());
            msg.values.forEach((perk, value) -> {
                buf.m_130070_(perk);
                buf.writeDouble(value);
            });
        }

        static Totals decode(FriendlyByteBuf buf) {
            int n = buf.m_130242_();
            Map<String, Double> values = new HashMap<>();
            for (int i = 0; i < n; i++) {
                values.put(buf.m_130277_(), buf.readDouble());
            }
            return new Totals(values);
        }
    }

    public PerkSync() {
    }

    public static void register() {
        CHANNEL.messageBuilder(Totals.class, 0, NetworkDirection.PLAY_TO_CLIENT)
                .encoder(Totals::encode).decoder(Totals::decode)
                .consumerMainThread((msg, context) -> {
                    ClientPerks.set(msg.values());
                    context.get().setPacketHandled(true);
                })
                .add();
        CHANNEL.messageBuilder(DoubleJumped.class, 2, NetworkDirection.PLAY_TO_SERVER)
                .encoder((msg, buf) -> { }).decoder(buf -> new DoubleJumped())
                .consumerMainThread((msg, context) -> {
                    ServerPlayer player = context.get().getSender();
                    if (player != null && Perks.get(player, "double_jump") > 0) {
                        player.f_19789_ = 0;                 // the landing after a double jump is safe
                    }
                    context.get().setPacketHandled(true);
                })
                .add();
        CHANNEL.messageBuilder(ProfileRequest.class, 3, NetworkDirection.PLAY_TO_SERVER)
                .encoder((msg, buf) -> { }).decoder(buf -> new ProfileRequest())
                .consumerMainThread((msg, context) -> {
                    ServerPlayer player = context.get().getSender();
                    if (player != null) {
                        CHANNEL.send(PacketDistributor.PLAYER.with(() -> player), SkillProfile.of(player));
                    }
                    context.get().setPacketHandled(true);
                })
                .add();
        CHANNEL.messageBuilder(SkillProfile.class, 4, NetworkDirection.PLAY_TO_CLIENT)
                .encoder(SkillProfile::encode).decoder(SkillProfile::decode)
                .consumerMainThread((msg, context) -> {
                    SkillProfile.latest = msg;
                    context.get().setPacketHandled(true);
                })
                .add();
        CHANNEL.messageBuilder(Buffs.class, 1, NetworkDirection.PLAY_TO_CLIENT)
                .encoder(Buffs::encode).decoder(Buffs::decode)
                .consumerMainThread((msg, context) -> {
                    ClientBuffs.set(msg.lines());
                    context.get().setPacketHandled(true);
                })
                .add();
    }

    /** Client to server: the player used Double Jump (the server clears their fall distance). */
    public record DoubleJumped() {
    }

    /** Client to server: the character screen opened and wants this player's skills. */
    public record ProfileRequest() {
    }

    public static void requestProfile() {
        CHANNEL.sendToServer(new ProfileRequest());
    }

    public static void sendDoubleJump() {
        CHANNEL.sendToServer(new DoubleJumped());
    }

    /** The player's active situational buffs, shown beside the inventory (sent when the list changes). */
    public record Buffs(java.util.List<String> lines) {
        static void encode(Buffs msg, FriendlyByteBuf buf) {
            buf.m_130130_(msg.lines.size());
            msg.lines.forEach(buf::m_130070_);
        }

        static Buffs decode(FriendlyByteBuf buf) {
            int n = buf.m_130242_();
            java.util.List<String> lines = new java.util.ArrayList<>();
            for (int i = 0; i < n; i++) {
                lines.add(buf.m_130277_());
            }
            return new Buffs(lines);
        }
    }

    public static void sendBuffs(ServerPlayer player, java.util.List<String> lines) {
        CHANNEL.send(PacketDistributor.PLAYER.with(() -> player), new Buffs(lines));
    }

    /** Attack damage from skills (Sharpened...): the player's own additions, without what they're holding. */
    public static double skillAttack(ServerPlayer player) {
        net.minecraft.world.entity.ai.attributes.AttributeInstance attack =
                player.m_21051_(net.minecraft.world.entity.ai.attributes.Attributes.f_22281_);
        if (attack == null) {
            return 0;
        }
        java.util.Set<java.util.UUID> held = new HashSet<>();
        player.m_21205_().m_41638_(net.minecraft.world.entity.EquipmentSlot.MAINHAND)
                .get(net.minecraft.world.entity.ai.attributes.Attributes.f_22281_).forEach(m -> held.add(m.m_22209_()));
        double sum = 0;
        for (net.minecraft.world.entity.ai.attributes.AttributeModifier m : attack.m_22122_()) {
            if (!held.contains(m.m_22209_()) && m.m_22217_() == net.minecraft.world.entity.ai.attributes.AttributeModifier.Operation.ADDITION) {
                sum += m.m_22218_();
            }
        }
        return sum;
    }

    public static synchronized void markDirty(ServerPlayer player) {
        DIRTY.add(player);
    }

    @SubscribeEvent
    public void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END) {
            return;
        }
        Set<ServerPlayer> send;
        synchronized (PerkSync.class) {
            if (DIRTY.isEmpty()) {
                return;
            }
            send = new HashSet<>(DIRTY);
            DIRTY.clear();
        }
        for (ServerPlayer player : send) {
            if (!player.m_213877_()) {
                Map<String, Double> values = new java.util.HashMap<>(Perks.TOTALS.snapshot(player.m_20148_()));
                values.put("skill_attack", skillAttack(player));    // the client never sees attack-damage modifiers
                CHANNEL.send(PacketDistributor.PLAYER.with(() -> player), new Totals(values));
            }
        }
    }

    @SubscribeEvent
    public void onLogout(PlayerEvent.PlayerLoggedOutEvent event) {
        UUID id = event.getEntity().m_20148_();
        Perks.TOTALS.removePlayer(id);
        synchronized (PerkSync.class) {
            DIRTY.removeIf(p -> p.m_20148_().equals(id));
        }
    }
}
