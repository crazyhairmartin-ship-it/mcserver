package fotfskills.compat;

import dev.ftb.mods.ftbultimine.FTBUltimine;
import dev.ftb.mods.ftbultimine.client.FTBUltimineClient;
import io.redspace.ironsspellbooks.api.spells.CastType;
import io.redspace.ironsspellbooks.player.ClientMagicData;
import java.lang.reflect.Field;
import net.minecraftforge.fml.ModList;

/**
 * Third-person (Shoulder Surfing) fixes for Iron's Spells and FTB Ultimine, replacing the two add-ons that only work
 * with Shoulder Surfing 4.x. Client only. Spells cast from the spellbook, quick-cast or a scroll turn the player to the
 * crosshair first (the mixins call faceCrosshair), continuous spells keep them facing it and holding the Ultimine key
 * couples the camera so the outline follows the crosshair (ShoulderSurfingPlugin).
 */
public final class ThirdPerson {
    private static Boolean shoulderSurfing;
    private static Field ultiminePressed;

    private ThirdPerson() {
    }

    /** Turns the player to what the crosshair points at, when Shoulder Surfing is installed and in use. */
    public static void faceCrosshair() {
        if (shoulderSurfing == null) {
            shoulderSurfing = ModList.get().isLoaded("shouldersurfing");
        }
        if (shoulderSurfing) {
            Hook.faceCrosshair();
        }
    }

    static boolean castingContinuousSpell() {
        return ClientMagicData.isCasting() && ClientMagicData.getCastType() == CastType.CONTINUOUS;
    }

    static boolean ultimineKeyHeld() {
        if (FTBUltimine.instance == null || !(FTBUltimine.instance.proxy instanceof FTBUltimineClient client)) {
            return false;
        }
        try {
            if (ultiminePressed == null) {
                ultiminePressed = FTBUltimineClient.class.getDeclaredField("pressed");
                ultiminePressed.setAccessible(true);
            }
            return ultiminePressed.getBoolean(client);
        } catch (ReflectiveOperationException e) {
            return false;
        }
    }

    /** Only loaded when Shoulder Surfing is. */
    private static final class Hook {
        static void faceCrosshair() {
            com.github.exopandora.shouldersurfing.client.ShoulderSurfing ss =
                    com.github.exopandora.shouldersurfing.client.ShoulderSurfing.getInstance();
            if (ss.isShoulderSurfing()) {
                ss.lookAtCrosshairTarget();
            }
        }
    }
}
