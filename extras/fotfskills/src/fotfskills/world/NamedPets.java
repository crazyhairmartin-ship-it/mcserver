package fotfskills.world;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.io.Reader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.entity.Entity;
import net.minecraftforge.common.extensions.IForgeEntity;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.loading.FMLPaths;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * Pets that turn into Dylan's real pets when they're given the right name (name tag, the Book of Familiars' rename,
 * a command...): a More Mob Variants coat and a Pehkui size, from config/fotfskills-named-pets.json. Names match without
 * caring about capitals. EntityNameMixin queues every renamed entity; the next server tick applies the look, once per
 * name (remembered in the pet's persistent data, so loading a chunk doesn't redo it).
 */
public final class NamedPets {
    // "2": re-applied once after the jump/step fix (2026-10-19), so pets named before it get it too
    private static final String APPLIED = "FotfNamedPet2";
    private static final List<Entity> QUEUE = new ArrayList<>();
    private static Map<String, Map<String, Look>> looks;

    record Look(String coat, double scale) {
    }

    /** Called from EntityNameMixin whenever an entity's name changes, on the server. */
    public static void renamed(Entity entity) {
        synchronized (QUEUE) {
            QUEUE.add(entity);
        }
    }

    @SubscribeEvent
    public void onTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END) {
            return;
        }
        List<Entity> todo;
        synchronized (QUEUE) {
            if (QUEUE.isEmpty()) {
                return;
            }
            todo = new ArrayList<>(QUEUE);
            QUEUE.clear();
        }
        for (Entity entity : todo) {
            if (entity.m_6084_() && entity.m_20194_() != null) {
                apply(entity.m_20194_(), entity);
            }
        }
    }

    private static void apply(MinecraftServer server, Entity entity) {
        Component name = entity.m_7770_();
        String key = name == null ? "" : name.getString().trim().toLowerCase(Locale.ROOT);
        CompoundTag data = ((IForgeEntity) (Object) entity).getPersistentData();
        if (key.isEmpty() || key.equals(data.m_128461_(APPLIED))) {
            return;
        }
        Map<String, Look> byName = looks().get(String.valueOf(ForgeRegistries.ENTITY_TYPES.getKey(entity.m_6095_())));
        Look look = byName == null ? null : byName.get(key);
        if (look == null) {
            return;
        }
        data.m_128359_(APPLIED, key);
        String uuid = entity.m_20149_();
        if (look.coat() != null) {
            run(server, "data merge entity " + uuid + " {VariantID:\"" + look.coat() + "\"}");
        }
        if (look.scale() > 0) {
            run(server, "scale set pehkui:base " + look.scale() + " " + uuid);
            // a smaller base scale also shrinks its jump and step, so at 0.75 Beast couldn't jump one block (Dylan,
            // 2026-10-19): scale those back up so it moves like a normal-size pet, and keep all three over restarts
            double back = 1.0 / look.scale();
            run(server, "scale set pehkui:jump_height " + back + " " + uuid);
            run(server, "scale set pehkui:step_height " + back + " " + uuid);
            for (String type : new String[] {"pehkui:base", "pehkui:jump_height", "pehkui:step_height"}) {
                run(server, "scale persist set " + type + " true " + uuid);
            }
        }
    }

    private static void run(MinecraftServer server, String command) {
        server.m_129892_().m_230957_(server.m_129893_().m_81324_(), command);
    }

    /** entity type id -> the coats named pets of that type wear (the client registers them, see client/CustomCoats). */
    public static Map<String, java.util.Set<String>> coats() {
        Map<String, java.util.Set<String>> out = new HashMap<>();
        looks().forEach((type, byName) -> byName.values().forEach(look -> {
            if (look.coat() != null) {
                out.computeIfAbsent(type, k -> new java.util.HashSet<>()).add(look.coat());
            }
        }));
        return out;
    }

    /** entity type -> lower-case name -> look, read once from config/fotfskills-named-pets.json. */
    private static Map<String, Map<String, Look>> looks() {
        if (looks == null) {
            looks = new HashMap<>();
            Path file = FMLPaths.CONFIGDIR.get().resolve("fotfskills-named-pets.json");
            if (Files.exists(file)) {
                try (Reader in = Files.newBufferedReader(file)) {
                    JsonArray pets = JsonParser.parseReader(in).getAsJsonObject().getAsJsonArray("pets");
                    for (JsonElement e : pets) {
                        JsonObject pet = e.getAsJsonObject();
                        Look look = new Look(pet.has("coat") ? pet.get("coat").getAsString() : null,
                                pet.has("scale") ? pet.get("scale").getAsDouble() : 0);
                        Map<String, Look> byName = looks.computeIfAbsent(pet.get("entity").getAsString(), k -> new HashMap<>());
                        for (JsonElement n : pet.getAsJsonArray("names")) {
                            byName.put(n.getAsString().trim().toLowerCase(Locale.ROOT), look);
                        }
                    }
                } catch (Exception ex) {
                    org.apache.logging.log4j.LogManager.getLogger("fotfskills").error("Couldn't read {}: {}", file, ex.toString());
                }
            }
        }
        return looks;
    }
}
