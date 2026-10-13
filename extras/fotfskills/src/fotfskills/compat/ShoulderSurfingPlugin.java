package fotfskills.compat;

import com.github.exopandora.shouldersurfing.api.client.event.handler.ComputeCameraCouplingEventHandler;
import com.github.exopandora.shouldersurfing.api.client.event.handler.ComputePlayerAimStateEventHandler;
import com.github.exopandora.shouldersurfing.api.event.IEventBus;
import com.github.exopandora.shouldersurfing.api.plugin.IShoulderSurfingPlugin;
import net.minecraft.client.Minecraft;

/** Shoulder Surfing 5 plugin (named in shouldersurfing_plugin.json, loaded by Shoulder Surfing on the client). See ThirdPerson. */
public class ShoulderSurfingPlugin implements IShoulderSurfingPlugin {
    @Override
    public void register(IEventBus bus) {
        bus.register((ComputePlayerAimStateEventHandler) event -> {
            if (!event.getResult() && event.getEntity() == Minecraft.m_91087_().f_91074_ && ThirdPerson.castingContinuousSpell()) {
                event.setResult(true);
            }
        });
        bus.register((ComputeCameraCouplingEventHandler) event -> {
            if (!event.getResult() && ThirdPerson.ultimineKeyHeld()) {
                event.setResult(true);
            }
        });
    }
}
