package fotfskills.perk;

import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.OwnableEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.FishingHook;
import net.minecraft.world.entity.vehicle.Boat;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.ProjectileImpactEvent;
import net.minecraftforge.event.entity.player.ItemFishedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.items.ItemHandlerHelper;
import net.minecraftforge.registries.ForgeRegistries;

/** Hook Shot (the bobber hits mobs), Leviathan Bait (a hoard or a record catch), Sea Legs (faster boats, on the driver's client). */
public final class FishingPerks {
    @SubscribeEvent
    public void onHookHit(ProjectileImpactEvent event) {
        if (event.getProjectile() instanceof FishingHook hook && hook.m_37168_() instanceof ServerPlayer player
                && event.getRayTraceResult() instanceof EntityHitResult hit && hit.m_82443_() instanceof LivingEntity target
                && !(target instanceof Player) && !(target instanceof OwnableEntity owned && owned.m_21805_() != null)) {
            double shot = Perks.get(player, "hook_shot");
            if (shot > 0) {
                target.m_6469_(player.m_269291_().m_269075_(player), (float) shot);
                Vec3 pull = player.m_20182_().m_82546_(target.m_20182_()).m_82541_().m_82490_(0.4 * shot);
                target.m_5997_(pull.f_82479_, 0.2, pull.f_82481_);
            }
        }
    }

    /**
     * Leviathan Bait: each catch has the perk's chance (5%) of something special, split evenly: a Leviathan's Hoard
     * (three rolls of the fishing treasure table) or a record catch (a random Aquaculture fish, named and glinting, ready
     * for a fish mount) worth 250 bonus Fishing XP.
     */
    @SubscribeEvent
    public void onFished(ItemFishedEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player) || !Perks.roll(player, "leviathan")
                || !(player.m_9236_() instanceof net.minecraft.server.level.ServerLevel level)) {
            return;
        }
        if (Perks.random() < 0.5) {
            net.minecraft.world.level.storage.loot.LootParams params = new net.minecraft.world.level.storage.loot.LootParams.Builder(level)
                    .m_287286_(net.minecraft.world.level.storage.loot.parameters.LootContextParams.f_81460_, player.m_20182_())
                    .m_287286_(net.minecraft.world.level.storage.loot.parameters.LootContextParams.f_81463_, player.m_21205_())
                    .m_287286_(net.minecraft.world.level.storage.loot.parameters.LootContextParams.f_81455_, player)
                    .m_287235_(net.minecraft.world.level.storage.loot.parameters.LootContextParamSets.f_81414_);
            net.minecraft.world.level.storage.loot.LootTable treasure = level.m_7654_().m_278653_()
                    .m_278676_(net.minecraft.world.level.storage.loot.BuiltInLootTables.f_78722_);
            for (int i = 0; i < 3; i++) {
                treasure.m_287195_(params).forEach(stack -> ItemHandlerHelper.giveItemToPlayer(player, stack));
            }
            player.m_5661_(Component.m_237113_("§6You hauled up a Leviathan's Hoard!"), true);
        } else {
            java.util.List<net.minecraft.world.item.Item> fish = ForgeRegistries.ITEMS.getValues().stream()
                    .filter(i -> "FishItem".equals(i.getClass().getSimpleName())
                            && "aquaculture".equals(ForgeRegistries.ITEMS.getKey(i).m_135827_()))
                    .toList();
            if (fish.isEmpty()) {
                return;
            }
            ItemStack trophy = new ItemStack(fish.get(level.f_46441_.m_188503_(fish.size())));
            trophy.m_41714_(Component.m_237113_("§6Record " + trophy.m_41720_().m_41466_().getString()));
            trophy.m_41663_(net.minecraft.world.item.enchantment.Enchantments.f_44986_, 1);   // glint
            ItemHandlerHelper.giveItemToPlayer(player, trophy);
            level.m_7654_().m_129892_().m_230957_(level.m_7654_().m_129893_().m_81324_(),
                    "puffish_skills experience add " + player.m_36316_().getName() + " fish 250");
            player.m_5661_(Component.m_237113_("§6A record catch! §e+250 Fishing XP"), true);
        }
    }

    /** Sea Legs: boats are driven client-side, so the driver's client scales the boat's speed (synced perk totals). */
    @SubscribeEvent
    public void onPlayerTick(TickEvent.PlayerTickEvent event) {
        Player player = event.player;
        if (event.phase != TickEvent.Phase.END || !player.m_9236_().f_46443_ || !(player.m_20202_() instanceof Boat boat)
                || boat.m_6688_() != player) {
            return;
        }
        double faster = Perks.get(player, "sea_legs");
        if (faster > 0 && boat.m_20069_()) {
            double f = Tuning.boatFactor(faster);
            Vec3 v = boat.m_20184_();
            boat.m_20256_(new Vec3(v.f_82479_ * f, v.f_82480_, v.f_82481_ * f));
        }
    }
}
