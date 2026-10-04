package fotfskills.perk;

import java.util.UUID;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;

/** Transient attribute modifiers with fixed per-key UUIDs: add, update or remove so the entity carries exactly value. */
public final class Modifiers {
    private Modifiers() {
    }

    public static UUID uuid(String key) {
        return UUID.nameUUIDFromBytes(("fotfskills:stat:" + key).getBytes());
    }

    public static void set(LivingEntity entity, Attribute attribute, String key, double value, AttributeModifier.Operation op) {
        if (attribute == null) {
            return;
        }
        AttributeInstance instance = entity.m_21051_(attribute);
        if (instance == null) {
            return;
        }
        UUID id = uuid(key);
        AttributeModifier old = instance.m_22111_(id);
        if (old != null && old.m_22218_() == value) {
            return;
        }
        if (old != null) {
            instance.m_22120_(id);
        }
        if (value != 0) {
            instance.m_22118_(new AttributeModifier(id, "fotfskills " + key, value, op));
        }
        if (attribute == Attributes.f_22276_ && entity.m_21223_() > entity.m_21233_()) {
            entity.m_21153_(entity.m_21233_());        // losing bonus health trims, never kills
        }
    }
}
