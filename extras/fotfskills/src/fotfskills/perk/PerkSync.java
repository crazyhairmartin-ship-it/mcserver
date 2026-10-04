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
        CHANNEL.messageBuilder(Buffs.class, 1, NetworkDirection.PLAY_TO_CLIENT)
                .encoder(Buffs::encode).decoder(Buffs::decode)
                .consumerMainThread((msg, context) -> {
                    ClientBuffs.set(msg.lines());
                    context.get().setPacketHandled(true);
                })
                .add();
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
                CHANNEL.send(PacketDistributor.PLAYER.with(() -> player), new Totals(Perks.TOTALS.snapshot(player.m_20148_())));
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
