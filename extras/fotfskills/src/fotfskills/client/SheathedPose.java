package fotfskills.client;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.client.event.RenderPlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/**
 * When Weapon Master puts a held weapon away (on the back or hip after a while without attacking), Better Combat still
 * held that weapon's stance (two-handed grips and so on). Right before each player is drawn, the stance of every hand
 * whose weapon is put away is cleared. Weapon Master's own test: no hit with that hand for hideTick ticks and its
 * auto-hide toggle on (toggleSlots 11 main hand, 12 off hand). Both mods are read by reflection; if either changes,
 * this does nothing.
 */
public final class SheathedPose {
    private boolean broken;
    private Method playerData;
    private Field hideTick, lastMain, lastOff, toggles;
    private Field mainBody, mainItem, offBody, offItem;
    private Method setPose;

    @SubscribeEvent
    public void onRender(RenderPlayerEvent.Pre event) {
        Player player = event.getEntity();
        if (broken || !(player instanceof AbstractClientPlayer)) {
            return;
        }
        try {
            if (setPose == null) {
                look(player);
            }
            Object data = playerData.invoke(player);
            if (data == null) {
                return;
            }
            int hide = hideTick.getInt(data);
            int[] toggle = (int[]) toggles.get(data);
            if (toggle.length > 11 && toggle[11] == 1 && lastMain.getInt(data) >= hide && !player.m_21205_().m_41619_()) {
                setPose.invoke(mainBody.get(player), null, false);
                setPose.invoke(mainItem.get(player), null, false);
            }
            if (toggle.length > 12 && toggle[12] == 1 && lastOff.getInt(data) >= hide && !player.m_21206_().m_41619_()) {
                setPose.invoke(offBody.get(player), null, false);
                setPose.invoke(offItem.get(player), null, false);
            }
        } catch (ReflectiveOperationException | RuntimeException | LinkageError e) {
            broken = true;
        }
    }

    private void look(Player player) throws ReflectiveOperationException {
        Class<?> data = Class.forName("com.minecraftserverzone.weaponmaster.setup.playerdata.PlayerData");
        playerData = Class.forName("com.minecraftserverzone.weaponmaster.setup.playerdata.IPlayerData").getMethod("getPlayerData");
        hideTick = data.getField("hideTick");
        lastMain = data.getField("lastMainhandHit");
        lastOff = data.getField("lastOffhandHit");
        toggles = data.getField("toggleSlots");
        mainBody = field("mainHandBodyPose");
        mainItem = field("mainHandItemPose");
        offBody = field("offHandBodyPose");
        offItem = field("offHandItemPose");
        Class<?> anim = Class.forName("dev.kosmx.playerAnim.core.data.KeyframeAnimation");
        setPose = Class.forName("net.bettercombat.client.animation.PoseSubStack").getMethod("setPose", anim, boolean.class);
    }

    private static Field field(String name) throws NoSuchFieldException {
        Field f = AbstractClientPlayer.class.getDeclaredField(name);    // added to the class by Better Combat's mixin
        f.setAccessible(true);
        return f;
    }
}
