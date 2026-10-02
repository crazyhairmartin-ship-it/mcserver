package fotfmail;

import java.util.function.Supplier;
import net.minecraft.core.BlockPos;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.network.NetworkEvent;

/**
 * Server -> client, sent when someone opens a package (PackageBlockEntityMixin): whether it was delivered to them
 * (then the screen just says who it's from) or is already on its way (then it says where to), else empty strings and
 * the screen shows the recipient box and Send button. Read by PackageScreenMixin through {@link #forPos}.
 */
public final class PackageInfoPacket {
    private static BlockPos lastPos;
    private static String lastFrom = "";
    private static String lastSentTo = "";

    private final BlockPos pos;
    private final String from;
    private final String sentTo;

    public PackageInfoPacket(BlockPos pos, String from, String sentTo) {
        this.pos = pos;
        this.from = from;
        this.sentTo = sentTo;
    }

    static void encode(PackageInfoPacket message, FriendlyByteBuf buffer) {
        buffer.m_130064_(message.pos);
        buffer.m_130070_(message.from);
        buffer.m_130070_(message.sentTo);
    }

    static PackageInfoPacket decode(FriendlyByteBuf buffer) {
        return new PackageInfoPacket(buffer.m_130135_(), buffer.m_130136_(64), buffer.m_130136_(64));
    }

    static void handle(PackageInfoPacket message, Supplier<NetworkEvent.Context> context) {
        context.get().enqueueWork(() -> {
            lastPos = message.pos;
            lastFrom = message.from;
            lastSentTo = message.sentTo;
        });
        context.get().setPacketHandled(true);
    }

    /** {from, sentTo} for the package at pos, or null if no info has arrived for it. */
    public static String[] forPos(BlockPos pos) {
        return pos != null && pos.equals(lastPos) ? new String[] {lastFrom, lastSentTo} : null;
    }
}
