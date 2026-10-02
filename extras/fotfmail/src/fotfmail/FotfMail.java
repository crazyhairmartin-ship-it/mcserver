package fotfmail;

import com.chaosthedude.endermail.block.LockerBlock;
import java.util.Optional;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import net.minecraftforge.fml.loading.FMLEnvironment;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkRegistry;
import net.minecraftforge.network.simple.SimpleChannel;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

/**
 * Friends of the Forest mail add-on for Ender Mail.
 *
 * - Mailboxes (Ender Mail lockers) get a "wood" block state, set from the crafting recipe's planks
 *   (item NBT BlockStateTag) and kept when broken (loot table copy_state).
 * - Letters: write on one like a book and quill, sign it with the recipient's mailbox ID as the title,
 *   then right-click any mailbox: one of Ender Mail's carriers (wearing a mail cap) takes it to theirs.
 * - Packages: chest + stamp; the package screen has a recipient box and Send button (SendPackagePacket) that send it
 *   to a mailbox, and a received package disappears once it's emptied.
 *
 * Compiled against SRG-named Minecraft (see build.sh), so vanilla methods appear as m_XXXX_.
 */
@Mod(FotfMail.MODID)
public class FotfMail {
    public static final String MODID = "fotfmail";

    public static final EnumProperty<MailboxWood> WOOD = EnumProperty.m_61587_("wood", MailboxWood.class);

    private static final String PROTOCOL = "1";
    public static final SimpleChannel NETWORK = NetworkRegistry.newSimpleChannel(
            new ResourceLocation(MODID, "main"), () -> PROTOCOL, PROTOCOL::equals, PROTOCOL::equals);

    private static final DeferredRegister<Item> ITEMS = DeferredRegister.create(ForgeRegistries.ITEMS, MODID);
    public static final RegistryObject<Item> LETTER = ITEMS.register("letter",
            () -> new LetterItem(new Item.Properties().m_41487_(1)));

    public FotfMail() {
        IEventBus modBus = FMLJavaModLoadingContext.get().getModEventBus();
        ITEMS.register(modBus);
        NETWORK.registerMessage(0, SendPackagePacket.class, SendPackagePacket::encode, SendPackagePacket::decode,
                SendPackagePacket::handle, Optional.of(NetworkDirection.PLAY_TO_SERVER));
        NETWORK.registerMessage(1, PackageInfoPacket.class, PackageInfoPacket::encode, PackageInfoPacket::decode,
                PackageInfoPacket::handle, Optional.of(NetworkDirection.PLAY_TO_CLIENT));
        MinecraftForge.EVENT_BUS.addListener(FotfMail::onRightClickBlock);
        MinecraftForge.EVENT_BUS.addListener(Mail::onServerTick);
        if (FMLEnvironment.dist == Dist.CLIENT) {
            ClientSetup.init(modBus);
        }
    }

    /** A signed letter used on any mailbox gets sent. */
    private static void onRightClickBlock(PlayerInteractEvent.RightClickBlock event) {
        ItemStack stack = event.getItemStack();
        if (!(stack.m_41720_() instanceof LetterItem) || !LetterItem.isSigned(stack)) {
            return;
        }
        Level level = event.getLevel();
        if (!(level.m_8055_(event.getPos()).m_60734_() instanceof LockerBlock)) {
            return;
        }
        event.setCanceled(true);
        event.setCancellationResult(InteractionResult.m_19078_(level.m_5776_()));
        if (!level.m_5776_() && event.getEntity() instanceof ServerPlayer player) {
            Mail.send(player, event.getPos(), stack);
        }
    }
}
