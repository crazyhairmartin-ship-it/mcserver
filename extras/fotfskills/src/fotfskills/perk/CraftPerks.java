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
import net.minecraftforge.event.entity.player.AnvilRepairEvent;
import net.minecraftforge.event.entity.player.PlayerDestroyItemEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.items.ItemHandlerHelper;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * Crafted gear (crafting grid): Enchanted Crafts I/II and Masterwork (guaranteed random enchantments), Smith (a
 * durability-saving chance stored on the item), Whetstone / Weaponsmith (+attack damage on weapons) and Armourer
 * (+toughness on armour), each applied once per item. Whetstone also applies to anvil repairs. Book Saver turns a
 * breaking enchanted tool into a book; Repair Kit refunds part of an anvil's XP cost.
 */
public final class CraftPerks {
    public static final String SMITH = "FotfSmith";
    private static final String STATS_DONE = "FotfStats";
    private static final String WHET_DONE = "FotfWhet";

    @SubscribeEvent
    public void onCraft(PlayerEvent.ItemCraftedEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) {
            improve(player, event.getCrafting());
        }
    }

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
        }
        double smith = Perks.get(player, "smith");
        if (smith > 0) {
            stack.m_41784_().m_128350_(SMITH, (float) smith);
        }
        if (!stack.m_41784_().m_128441_(STATS_DONE)) {
            EquipmentSlot slot = LivingEntity.m_147233_(stack);
            double damage = Perks.get(player, "whetstone") + Perks.get(player, "weaponsmith");
            if (slot == EquipmentSlot.MAINHAND && damage > 0 && hasDefault(stack, slot, Attributes.f_22281_)) {
                addModifier(stack, slot, Attributes.f_22281_, damage);
                stack.m_41784_().m_128379_(STATS_DONE, true);
                stack.m_41784_().m_128379_(WHET_DONE, true);
            } else if (stack.m_41720_() instanceof ArmorItem && Perks.get(player, "armourer") > 0) {
                addModifier(stack, slot, Attributes.f_22285_, Perks.get(player, "armourer"));
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
            addModifier(out, slot, Attributes.f_22281_, whet);
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
        if (!(event.getEntity() instanceof ServerPlayer player) || Perks.get(player, "book_saver") <= 0) {
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

    /** An NBT modifier turns off the item's default attributes, so the slot's defaults are copied in first. */
    private static void addModifier(ItemStack stack, EquipmentSlot slot, Attribute attribute, double amount) {
        CompoundTag tag = stack.m_41784_();
        if (!tag.m_128441_("AttributeModifiers")) {
            Multimap<Attribute, AttributeModifier> defaults = stack.m_41720_().m_7167_(slot);
            defaults.forEach((attr, modifier) -> stack.m_41643_(attr, modifier, slot));
        }
        stack.m_41643_(attribute, new AttributeModifier(UUID.randomUUID(), "fotfskills crafted", amount,
                AttributeModifier.Operation.ADDITION), slot);
    }
}
