package fotfskills.pet;

import net.minecraft.nbt.CompoundTag;

/**
 * What a respawned pet keeps (Domestication Innovation's pet-bed respawn): everything except what already dropped on
 * death and would come back twice (chest, saddle, armour, carpet, held and worn items, the lead) and the state that
 * killed it (fire, effects).
 */
public final class PetSaveData {
    private static final String[] DROPPED = {"Items", "SaddleItem", "ArmorItem", "DecorItem", "HandItems", "ArmorItems",
            "Leash", "Inventory", "ActiveEffects", "Passengers", "DeathTime", "HurtTime"};

    private PetSaveData() {
    }

    public static void strip(CompoundTag pet) {
        for (String key : DROPPED) {
            pet.m_128473_(key);
        }
        if (pet.m_128441_("ChestedHorse")) {
            pet.m_128379_("ChestedHorse", false);
        }
        pet.m_128376_("Fire", (short) -1);
    }
}
