package fotfskills.client;

import fotfskills.perk.DamageBreakdown;
import fotfskills.perk.Perks;
import fotfskills.perk.Weapons;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.MobType;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.enchantment.EnchantmentHelper;
import net.minecraftforge.event.entity.player.ItemTooltipEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/**
 * Melee weapons show the damage one swing does with your skills; hold Shift for what makes it up. Thrown weapons also
 * show your thrown-damage bonus.
 */
public final class WeaponTooltips {
    private static final String[] MELEE = {"sword", "light", "two_handed", "polearm", "axe", "blunt", "scythe", "pickaxe"};
    private static final String[] CATEGORIES = {"sword", "light", "two_handed", "polearm", "axe", "blunt", "scythe", "thrown", "bow",
            "crossbow", "magic", "pickaxe"};
    private static final java.util.Map<String, String> LABELS = java.util.Map.of("two_handed", "Two-handed");

    @SubscribeEvent
    public void onTooltip(ItemTooltipEvent event) {
        Player player = event.getEntity();
        ItemStack stack = event.getItemStack();
        if (player == null || stack.m_41619_()) {
            return;
        }
        Set<String> types = new HashSet<>();
        for (String type : MELEE) {
            if (Weapons.is(stack, type)) {
                types.add(type);
            }
        }
        List<Component> tip = event.getToolTip();
        if (Screen.m_96638_()) {
            List<String> all = new java.util.ArrayList<>();
            for (String type : CATEGORIES) {
                if (Weapons.is(stack, type)) {
                    all.add(LABELS.getOrDefault(type, Character.toUpperCase(type.charAt(0)) + type.substring(1)));
                }
            }
            if (!all.isEmpty()) {
                tip.add(Component.m_237113_("§8Counts as: §7" + String.join(", ", all)));
            }
        }
        boolean offHandBusy = types.contains("two_handed") && !Weapons.twoHanded(player, stack);
        if (offHandBusy) {
            types.remove("two_handed");
        }
        if (!types.isEmpty() || offHandBusy) {
            double weapon = 1 + additions(stack.m_41638_(EquipmentSlot.MAINHAND).get(Attributes.f_22281_));
            double skill = fotfskills.perk.ClientPerks.raw("skill_attack");
            double enchant = EnchantmentHelper.m_44833_(stack, MobType.f_21640_);
            DamageBreakdown d = DamageBreakdown.of(weapon, skill, enchant, types, p -> Perks.get(player, p));
            tip.add(Component.m_237113_("§6" + DamageBreakdown.fmt(d.total()) + " damage with your skills"));
            double baseSpeed = 4 + additions(stack.m_41638_(EquipmentSlot.MAINHAND).get(Attributes.f_22283_));
            double speedBonus = (Weapons.is(stack, "light") || Weapons.is(stack, "sword") ? Perks.get(player, "duelist_speed") : 0)
                    + (Weapons.is(player.m_21206_(), "light") && player.m_21206_() != stack ? Perks.get(player, "light_speed") : 0);
            tip.add(Component.m_237113_("§6" + DamageBreakdown.fmt(baseSpeed * (1 + speedBonus)) + " attack speed with your skills"
                    + (speedBonus > 0 ? " §7(+" + Math.round(speedBonus * 100) + "%)" : "")));
            if (Screen.m_96638_()) {
                d.lines().forEach(line -> tip.add(Component.m_237113_("§7  " + line)));
            } else {
                tip.add(Component.m_237113_("§8Hold Shift for the breakdown"));
            }
            if (offHandBusy) {
                tip.add(Component.m_237113_("§8Two-handed perks need an empty off hand"));
            }
        }
        if (Weapons.is(stack, "thrown")) {
            double thrown = Perks.get(player, "pct_thrown") + (Weapons.is(stack, "axe") ? Perks.get(player, "pct_thrown_axe") : 0);
            if (thrown > 0) {
                tip.add(Component.m_237113_("§6+" + Math.round(thrown * 100) + "% damage when thrown"));
            }
        }
    }

    private static double additions(java.util.Collection<AttributeModifier> modifiers) {
        double sum = 0;
        for (AttributeModifier m : modifiers) {
            if (m.m_22217_() == AttributeModifier.Operation.ADDITION) {
                sum += m.m_22218_();
            }
        }
        return sum;
    }

}
