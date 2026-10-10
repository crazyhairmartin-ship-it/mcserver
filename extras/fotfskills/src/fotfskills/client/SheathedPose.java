package fotfskills.client;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.Map;
import java.util.WeakHashMap;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.client.event.RenderPlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/**
 * When Weapon Master puts a held weapon away (on the back or hip after a while without attacking), Better Combat kept
 * that weapon's stance. mixin/SheathedPoseMixin makes Better Combat's pose layers set no stance for a hand whose weapon
 * is put away; this class tells it which player owns each pose layer (learned as players are drawn) and runs Weapon
 * Master's own test: no hit with that hand for hideTick ticks and its auto-hide toggle on (toggleSlots 11 main hand,
 * 12 off hand). Both mods are read by reflection; if either changes, stances are left alone.
 */
public final class SheathedPose {
    private static final Map<Object, Player> OWNERS = new WeakHashMap<>();
    private static boolean broken;
    private static Method playerData;
    private static Field hideTick, lastMain, lastOff, toggles;
    private static Field[] stacks;

    @SubscribeEvent
    public void onRender(RenderPlayerEvent.Pre event) {
        Player player = event.getEntity();
        if (broken || !(player instanceof AbstractClientPlayer)) {
            return;
        }
        try {
            if (stacks == null) {
                look();
            }
            for (Field f : stacks) {
                Object stack = f.get(player);
                if (stack != null && OWNERS.get(stack) != player) {
                    OWNERS.put(stack, player);
                }
            }
        } catch (ReflectiveOperationException | RuntimeException | LinkageError e) {
            broken = true;
        }
    }

    /** True if this Better Combat pose layer's hand holds a weapon that Weapon Master has put away. */
    public static boolean sheathed(Object poseStack, boolean mainHand) {
        Player player = OWNERS.get(poseStack);
        if (player == null || broken) {
            return false;
        }
        try {
            Object data = playerData.invoke(player);
            if (data == null) {
                return false;
            }
            int[] toggle = (int[]) toggles.get(data);
            int slot = mainHand ? 11 : 12;
            int sinceHit = (mainHand ? lastMain : lastOff).getInt(data);
            boolean holding = !(mainHand ? player.m_21205_() : player.m_21206_()).m_41619_();
            return holding && toggle.length > slot && toggle[slot] == 1 && sinceHit >= hideTick.getInt(data);
        } catch (ReflectiveOperationException | RuntimeException | LinkageError e) {
            broken = true;
            return false;
        }
    }

    private static void look() throws ReflectiveOperationException {
        Class<?> data = Class.forName("com.minecraftserverzone.weaponmaster.setup.playerdata.PlayerData");
        playerData = Class.forName("com.minecraftserverzone.weaponmaster.setup.playerdata.IPlayerData").getMethod("getPlayerData");
        hideTick = data.getField("hideTick");
        lastMain = data.getField("lastMainhandHit");
        lastOff = data.getField("lastOffhandHit");
        toggles = data.getField("toggleSlots");
        String[] names = {"mainHandBodyPose", "mainHandItemPose", "offHandBodyPose", "offHandItemPose"};
        Field[] found = new Field[names.length];
        for (int i = 0; i < names.length; i++) {
            found[i] = AbstractClientPlayer.class.getDeclaredField(names[i]);   // added by Better Combat's mixin
            found[i].setAccessible(true);
        }
        stacks = found;
    }
}
