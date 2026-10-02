package fotfmail;

import java.util.function.Supplier;
import net.minecraft.core.BlockPos;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkEvent;

/** Client -> server: the package screen's Send button (package position + recipient mailbox ID). */
public final class SendPackagePacket {
    private final BlockPos pos;
    private final String recipient;

    public SendPackagePacket(BlockPos pos, String recipient) {
        this.pos = pos;
        this.recipient = recipient;
    }

    static void encode(SendPackagePacket message, FriendlyByteBuf buffer) {
        buffer.m_130064_(message.pos);
        buffer.m_130070_(message.recipient);
    }

    static SendPackagePacket decode(FriendlyByteBuf buffer) {
        return new SendPackagePacket(buffer.m_130135_(), buffer.m_130136_(32));
    }

    static void handle(SendPackagePacket message, Supplier<NetworkEvent.Context> context) {
        context.get().enqueueWork(() -> {
            ServerPlayer player = context.get().getSender();
            if (player != null) {
                Mail.sendPackage(player, message.pos, message.recipient);
            }
        });
        context.get().setPacketHandled(true);
    }
}
