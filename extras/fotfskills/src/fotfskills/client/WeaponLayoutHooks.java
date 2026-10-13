package fotfskills.client;

import com.minecraftserverzone.weaponmaster.setup.playerdata.IPlayerData;
import com.minecraftserverzone.weaponmaster.setup.playerdata.PlayerData;
import fotfskills.perk.Weapons;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;

/** Game side of WeaponLayout: weapon kinds from our weapon tags, and the arrangement for the player being drawn. */
public final class WeaponLayoutHooks {
    private static final String[] BACK = {"two_handed", "polearm", "scythe", "bow", "crossbow", "magic"};
    private static final String[] HIP = {"sword", "light", "axe", "blunt", "thrown"};

    /** The arrangement for the player Weapon Master is drawing right now (render thread only), or null. */
    public static int[] current;

    private WeaponLayoutHooks() {
    }

    public static int kind(ItemStack stack) {
        if (stack == null || stack.m_41619_()) {
            return WeaponLayout.EMPTY;
        }
        for (String type : BACK) {
            if (Weapons.is(stack, type)) {
                return WeaponLayout.BACK;
            }
        }
        for (String type : HIP) {
            if (Weapons.is(stack, type)) {
                return WeaponLayout.HIP;
            }
        }
        return WeaponLayout.OTHER;
    }

    /** Weapon Master's own default slot attachments, for when a player's settings haven't arrived. */
    private static final String DEFAULT_ATTACHMENTS = "1-body,2-body,3-rleg,4-lleg,5-rleg,6-lleg,7-body,8-body,9-rleg";

    /** The local player's slot attachments: Weapon Master keeps those client-side, not in the synced PlayerData. */
    public static String localAttachments() {
        String own = com.minecraftserverzone.weaponmaster.setup.events_on_client.ClientOnlyForgeSetup.slotAttachment;
        return own == null || own.isEmpty() ? DEFAULT_ATTACHMENTS : own;
    }

    /** Another player's slot attachments, from the PlayerData Weapon Master syncs for them. */
    public static String attachments(Player player) {
        PlayerData data = ((IPlayerData) player).getPlayerData();
        return data == null || data.slotAttachments == null || data.slotAttachments.isEmpty() ? DEFAULT_ATTACHMENTS : data.slotAttachments;
    }

    /** Arrangement for a hotbar (first nine stacks) under these Weapon Master slot attachments, or null. */
    public static int[] arrange(String attachments, ItemStack[] hotbar) {
        if (hotbar == null || hotbar.length < 9) {
            return null;
        }
        int[] kinds = new int[9];
        for (int i = 0; i < 9; i++) {
            kinds[i] = kind(hotbar[i]);
        }
        return WeaponLayout.arrange(kinds, WeaponLayout.places(attachments));
    }

    /** The stacks rearranged into display order (anything past the hotbar, e.g. the off hand, unchanged). */
    public static ItemStack[] shown(ItemStack[] stacks, int[] shown) {
        if (shown == null || stacks == null || stacks.length < 9) {
            return stacks;
        }
        ItemStack[] out = stacks.clone();
        for (int d = 0; d < 9; d++) {
            out[d] = stacks[shown[d]];
        }
        return out;
    }
}
