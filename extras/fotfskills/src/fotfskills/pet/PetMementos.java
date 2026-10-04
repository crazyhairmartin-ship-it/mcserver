package fotfskills.pet;

import java.util.Collections;
import java.util.Set;
import java.util.WeakHashMap;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.OwnableEntity;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.ModList;

/**
 * A tamed animal or companion that dies leaves a Pet Memento: in its owner's inventory when they're online, otherwise
 * at the death spot (it never despawns). Not for magic summons (Ars Nouveau, Iron's Spells) or pets that Domestication
 * Innovation will respawn at their pet bed. The saved pet has no inventory or lead: those already dropped.
 */
public final class PetMementos {
    private static final String[] SUMMON_INTERFACES = {"com.hollingsworth.arsnouveau.api.entity.ISummon",
            "io.redspace.ironsspellbooks.entity.mobs.IMagicSummon"};
    /** Guards against a second death event for the same pet (mods calling die() twice). */
    private final Set<LivingEntity> handled = Collections.newSetFromMap(new WeakHashMap<>());

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public void onDeath(LivingDeathEvent event) {
        LivingEntity pet = event.getEntity();
        if (event.isCanceled() || pet.m_9236_().f_46443_ || pet instanceof Player
                || !(pet instanceof OwnableEntity owned) || owned.m_21805_() == null
                || isSummon(pet.getClass()) || hasPetBed(pet) || !handled.add(pet)) {
            return;
        }
        CompoundTag data = new CompoundTag();
        if (!pet.m_20086_(data)) {
            return;                       // entities the game won't save (e.g. ones marked not to persist)
        }
        MementoData.strip(data);
        ItemStack memento = new ItemStack(ModItems.PET_MEMENTO.get());
        memento.m_41784_().m_128365_(PetMementoItem.PET, data);
        memento.m_41784_().m_128359_(PetMementoItem.NAME, pet.m_5446_().getString());
        if (owned.m_269323_() instanceof ServerPlayer owner && owner.m_150109_().m_36054_(memento)) {
            return;                       // straight to the owner
        }
        ItemEntity drop = new ItemEntity(pet.m_9236_(), pet.m_20185_(), pet.m_20186_() + 0.5, pet.m_20189_(), memento);
        drop.m_149678_();                 // never despawns
        pet.m_9236_().m_7967_(drop);
    }

    private static boolean isSummon(Class<?> type) {
        for (Class<?> c = type; c != null; c = c.getSuperclass()) {
            for (Class<?> iface : c.getInterfaces()) {
                if (implementsSummon(iface)) {
                    return true;
                }
            }
        }
        return false;
    }

    private static boolean implementsSummon(Class<?> iface) {
        for (String name : SUMMON_INTERFACES) {
            if (iface.getName().equals(name)) {
                return true;
            }
        }
        for (Class<?> parent : iface.getInterfaces()) {
            if (implementsSummon(parent)) {
                return true;
            }
        }
        return false;
    }

    private static boolean hasPetBed(LivingEntity pet) {
        return ModList.get().isLoaded("domesticationinnovation") && DomesticationBeds.hasBed(pet);
    }
}
