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
 * show your thrown-damage bonus. Situational bonuses (Momentum, Counter, crits) aren't counted.
 */
public final class WeaponTooltips {
    private static final String[] MELEE = {"sword", "light", "two_handed", "polearm", "axe", "blunt", "scythe", "pickaxe"};

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
        if (!types.isEmpty()) {
            double weapon = 1 + additions(stack.m_41638_(EquipmentSlot.MAINHAND).get(Attributes.f_22281_));
            double skill = skillAttack(player);
            double enchant = EnchantmentHelper.m_44833_(stack, MobType.f_21640_);
            DamageBreakdown d = DamageBreakdown.of(weapon, skill, enchant, types, p -> Perks.get(player, p));
            tip.add(Component.m_237113_("§6" + DamageBreakdown.fmt(d.total()) + " damage with your skills"));
            if (Screen.m_96638_()) {
                d.lines().forEach(line -> tip.add(Component.m_237113_("§7  " + line)));
                tip.add(Component.m_237113_("§8  Not counted: crits, Momentum, Counter and other situational bonuses"));
            } else {
                tip.add(Component.m_237113_("§8Hold Shift for the breakdown"));
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

    /** Attack damage from skills: the player's own attack bonuses, without whatever they're holding right now. */
    private static double skillAttack(Player player) {
        AttributeInstance attack = player.m_21051_(Attributes.f_22281_);
        if (attack == null) {
            return 0;
        }
        Set<java.util.UUID> held = new HashSet<>();
        player.m_21205_().m_41638_(EquipmentSlot.MAINHAND).get(Attributes.f_22281_).forEach(m -> held.add(m.m_22209_()));
        double sum = 0;
        for (AttributeModifier m : attack.m_22122_()) {
            if (!held.contains(m.m_22209_()) && m.m_22217_() == AttributeModifier.Operation.ADDITION) {
                sum += m.m_22218_();
            }
        }
        return sum;
    }
}
