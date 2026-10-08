package fotfskills.client;

import com.github.nyuppo.config.Variants;
import com.github.nyuppo.variant.MobVariant;
import fotfskills.world.NamedPets;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EntityType;
import net.minecraftforge.client.event.ClientPlayerNetworkEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * More Mob Variants only knows its built-in coats on a client connected to a server (added coats live in server data),
 * so the client turned the server's "moremobvariants:dale" back into the default skin. On joining, the coats from
 * config/fotfskills-named-pets.json are added to the client's list (weight 0: the client never rolls coats).
 */
public final class CustomCoats {
    @SubscribeEvent
    public void onJoin(ClientPlayerNetworkEvent.LoggingIn event) {
        NamedPets.coats().forEach((typeId, coats) -> {
            EntityType<?> type = ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation(typeId));
            if (type == null) {
                return;
            }
            for (String coat : coats) {
                ResourceLocation id = new ResourceLocation(coat);
                if (Variants.getVariantNullable(type, id) == null) {
                    Variants.addVariant(type, new MobVariant(id, 0));
                }
            }
        });
    }
}
