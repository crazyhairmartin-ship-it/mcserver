package fotfskills.perk;

import com.google.common.collect.Multimap;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.inventory.AnvilMenu;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.EnchantedBookItem;
import net.minecraft.world.item.enchantment.Enchantment;
import net.minecraft.world.item.enchantment.EnchantmentHelper;
import net.minecraft.world.item.enchantment.EnchantmentInstance;
import net.minecraftforge.event.ItemAttributeModifierEvent;
import net.minecraftforge.event.entity.player.AnvilRepairEvent;
import net.minecraftforge.event.entity.player.PlayerDestroyItemEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.items.ItemHandlerHelper;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * Crafted gear (crafting grid, including shift-click via ItemCraftedByMixin): Enchanted Crafts I/II and Masterwork (guaranteed random enchantments), Smith (a
 * durability-saving chance stored on the item), Whetstone / Weaponsmith (+attack damage on weapons) and Armourer
 * (+toughness on armour), each applied once per item. Whetstone also applies to anvil repairs. Book Saver turns a
 * breaking enchanted tool into a book; Repair Kit refunds part of an anvil's XP cost.
 */
public final class CraftPerks {
    public static final String SMITH = "FotfSmith";
    private static final String STATS_DONE = "FotfStats";
    private static final String WHET_DONE = "FotfWhet";
    private static final String PERK_ENCHANTED = "FotfEnchanted";
    private static final String BONUS_DAMAGE = "FotfBonusDamage";
    private static final String BONUS_TOUGHNESS = "FotfBonusToughness";
    private static final UUID DAMAGE_ID = UUID.nameUUIDFromBytes("fotfskills:crafted_damage".getBytes());
    private static final UUID TOUGHNESS_ID = UUID.nameUUIDFromBytes("fotfskills:crafted_toughness".getBytes());

    /** Crafted gear only: damageable items. */
    public static void improve(ServerPlayer player, ItemStack stack) {
        if (stack.m_41619_() || !stack.m_41763_()) {
            return;
        }
        int cap = (int) Math.round(Perks.get(player, "enchant_level"));
        if (cap > 0) {
            int bonus = (int) Math.round(Perks.get(player, "enchant_bonus"));
            int count = Perks.get(player, "masterwork") > 0 ? 2 : 1;
            for (int i = 0; i < count; i++) {
                enchant(stack, cap, bonus);
            }
            stack.m_41784_().m_128379_(PERK_ENCHANTED, true);      // never turned into books by Book Saver
        }
        double smith = Perks.get(player, "smith");
        if (smith > 0) {
            stack.m_41784_().m_128350_(SMITH, (float) smith);
        }
        if (!stack.m_41784_().m_128441_(STATS_DONE)) {
            EquipmentSlot slot = LivingEntity.m_147233_(stack);
            double damage = Perks.get(player, "whetstone") + Perks.get(player, "weaponsmith");
            if (slot == EquipmentSlot.MAINHAND && damage > 0 && hasDefault(stack, slot, Attributes.f_22281_)) {
                stack.m_41784_().m_128347_(BONUS_DAMAGE, damage);
                stack.m_41784_().m_128379_(STATS_DONE, true);
                stack.m_41784_().m_128379_(WHET_DONE, true);
            } else if (stack.m_41720_() instanceof ArmorItem && Perks.get(player, "armourer") > 0) {
                stack.m_41784_().m_128347_(BONUS_TOUGHNESS, Perks.get(player, "armourer"));
                stack.m_41784_().m_128379_(STATS_DONE, true);
            }
        }
    }

    /** Whetstone on anvil repairs (once per item); Repair Kit refunds part of the anvil's level cost. */
    @SubscribeEvent
    public void onRepair(AnvilRepairEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) {
            return;
        }
        ItemStack out = event.getOutput();
        double whet = Perks.get(player, "whetstone");
        EquipmentSlot slot = LivingEntity.m_147233_(out);
        if (whet > 0 && out.m_41763_() && slot == EquipmentSlot.MAINHAND && !out.m_41784_().m_128441_(WHET_DONE)
                && hasDefault(out, slot, Attributes.f_22281_)) {
            out.m_41784_().m_128347_(BONUS_DAMAGE, out.m_41784_().m_128459_(BONUS_DAMAGE) + whet);
            out.m_41784_().m_128379_(WHET_DONE, true);
        }
        if (player.f_36096_ instanceof AnvilMenu anvil) {
            int refund = (int) Math.floor(anvil.m_39028_() * Perks.get(player, "repair_kit"));
            if (refund > 0) {
                player.m_6749_(refund);
            }
        }
    }

    @SubscribeEvent
    public void onBreak(PlayerDestroyItemEvent event) {
        ItemStack original = event.getOriginal();
        if (!(event.getEntity() instanceof ServerPlayer player) || Perks.get(player, "book_saver") <= 0
                || !BookSaverRule.isBreak(original.m_41763_(), original.m_41773_(), original.m_41776_(),
                        original.m_41783_() != null && original.m_41783_().m_128441_(PERK_ENCHANTED))) {
            return;
        }
        Map<Enchantment, Integer> enchants = EnchantmentHelper.m_44831_(event.getOriginal());
        if (enchants.isEmpty()) {
            return;
        }
        ItemStack book = new ItemStack(Items.f_42690_);
        enchants.forEach((enchantment, level) -> EnchantedBookItem.m_41153_(book, new EnchantmentInstance(enchantment, level)));
        ItemHandlerHelper.giveItemToPlayer(player, book);
    }

    private static void enchant(ItemStack stack, int cap, int bonus) {
        Map<Enchantment, Integer> current = EnchantmentHelper.m_44831_(stack);
        List<Enchantment> options = new ArrayList<>();
        for (Enchantment e : ForgeRegistries.ENCHANTMENTS.getValues()) {
            if (e.m_6081_(stack) && !e.m_6589_() && !e.m_6591_() && !current.containsKey(e)
                    && current.keySet().stream().allMatch(other -> other.m_44695_(e))) {
                options.add(e);
            }
        }
        if (!options.isEmpty()) {
            Enchantment pick = options.get((int) (Perks.random() * options.size()));
            stack.m_41663_(pick, Tuning.enchantLevel(cap, bonus, pick.m_6586_(), Perks.random()));
        }
    }

    private static boolean hasDefault(ItemStack stack, EquipmentSlot slot, Attribute attribute) {
        return stack.m_41720_().m_7167_(slot).containsKey(attribute);
    }

    /**
     * Whetstone / Weaponsmith / Armourer bonuses are numbers on the item (FotfBonusDamage / FotfBonusToughness) added
     * on top of whatever the item itself provides; writing NBT attribute modifiers would replace a modded item's own
     * (stack-sensitive) stats.
     */
    @SubscribeEvent
    public void onAttributes(ItemAttributeModifierEvent event) {
        CompoundTag tag = event.getItemStack().m_41783_();
        if (tag == null) {
            return;
        }
        if (tag.m_128441_(BONUS_DAMAGE) && event.getSlotType() == EquipmentSlot.MAINHAND) {
            event.addModifier(Attributes.f_22281_, new AttributeModifier(DAMAGE_ID, "fotfskills crafted", tag.m_128459_(BONUS_DAMAGE),
                    AttributeModifier.Operation.ADDITION));
        }
        if (tag.m_128441_(BONUS_TOUGHNESS) && event.getSlotType() == LivingEntity.m_147233_(event.getItemStack())) {
            event.addModifier(Attributes.f_22285_, new AttributeModifier(TOUGHNESS_ID, "fotfskills crafted", tag.m_128459_(BONUS_TOUGHNESS),
                    AttributeModifier.Operation.ADDITION));
        }
    }

    /** Any menu with a crafting grid: a vanilla result slot, or a slot backed by a CraftingContainer. */
    public static boolean craftingGrid(net.minecraft.world.inventory.AbstractContainerMenu menu) {
        for (net.minecraft.world.inventory.Slot slot : menu.f_38839_) {
            if (slot instanceof net.minecraft.world.inventory.ResultSlot
                    || slot.f_40218_ instanceof net.minecraft.world.inventory.CraftingContainer) {
                return true;
            }
        }
        return false;
    }
}
