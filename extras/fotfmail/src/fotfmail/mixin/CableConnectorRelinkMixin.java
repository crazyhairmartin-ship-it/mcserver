package fotfmail.mixin;

import com.obscura.storage.tile.AbstractInventoryCableConnectorBlockEntity;
import com.obscura.storage.tile.InventoryConnectorBlockEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Obscura's cable connectors (plain and Inventory Link) join their network by handing the Inventory Connector an
 * entry, then refresh its timestamp each search. The connector throws out entries more than 40 ticks old, but the
 * cable connector only hands in a new one when its network changes, so one late search (chunks ticking unevenly,
 * e.g. coming back from another dimension) dropped it for good: the base lost its link to the barrels and bamboo
 * farm over and over until the block was replaced (Dylan, 2026-11-02). After each search this hands the entry back
 * in if the network no longer has it.
 */
@Mixin(value = AbstractInventoryCableConnectorBlockEntity.class, remap = false)
public abstract class CableConnectorRelinkMixin {
    @Shadow(remap = false)
    protected InventoryConnectorBlockEntity master;
    @Shadow(remap = false)
    protected InventoryConnectorBlockEntity.LinkedInv linv;

    @Inject(method = "search", at = @At("TAIL"), remap = false)
    private void fotfmail$relinkIfDropped(long now, long generation, boolean force, CallbackInfo ci) {
        if (master == null || linv == null || master.m_58901_()) {
            return;
        }
        if (!((InventoryConnectorAccessor) master).fotfmail$linkedInvs().contains(linv)) {
            linv.time = now;
            master.addLinked(linv);
        }
    }
}
