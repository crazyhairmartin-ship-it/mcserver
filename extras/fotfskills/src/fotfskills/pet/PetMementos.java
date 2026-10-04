package fotfskills.pet;

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
import net.minecraftforge.items.ItemHandlerHelper;

/** A tamed animal or companion that dies leaves a Pet Memento: at its death spot, or with its owner if they're far away. */
public final class PetMementos {
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public void onDeath(LivingDeathEvent event) {
        LivingEntity pet = event.getEntity();
        if (event.isCanceled() || pet.m_9236_().f_46443_ || pet instanceof Player
                || !(pet instanceof OwnableEntity owned) || owned.m_21805_() == null) {
            return;
        }
        CompoundTag data = new CompoundTag();
        if (!pet.m_20086_(data)) {
            return;                       // passengers and entities that can't be saved
        }
        ItemStack memento = new ItemStack(ModItems.PET_MEMENTO.get());
        memento.m_41784_().m_128365_(PetMementoItem.PET, data);
        memento.m_41784_().m_128359_(PetMementoItem.NAME, pet.m_5446_().getString());
        if (owned.m_269323_() instanceof ServerPlayer owner
                && (owner.m_9236_() != pet.m_9236_() || owner.m_20280_(pet) > 32 * 32)) {
            ItemHandlerHelper.giveItemToPlayer(owner, memento);
            return;
        }
        ItemEntity drop = new ItemEntity(pet.m_9236_(), pet.m_20185_(), pet.m_20186_() + 0.5, pet.m_20189_(), memento);
        drop.m_32064_();
        pet.m_9236_().m_7967_(drop);
    }
}
