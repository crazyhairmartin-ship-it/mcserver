package fotfskills.perk;

import java.util.HashSet;
import java.util.Set;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.TagKey;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.biome.Biome;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * Stats that depend on the situation, refreshed every 10 ticks as transient attribute modifiers with fixed UUIDs:
 * Forest Stride / Bark Skin (forest biomes), Footwork (in combat), Skirmisher (after a shot), Stonehide (after
 * mining), Iron Stomach (saturation above half), Duelist / Light Weapons (weapon held), and Iron's spell power,
 * cooldowns and mana regen (Tidecaller, Warded Mind, Gem Focus, Staff Adept, Warrior's Feast, Brain Food).
 * Also Earthbound healing and Sea's Blessing effects. Transient modifiers are never saved, so nothing needs
 * removing at logout.
 */
public final class ConditionalStats {
    private static final TagKey<Biome> FOREST = TagKey.m_203882_(ForgeRegistries.Keys.BIOMES, new ResourceLocation("minecraft", "is_forest"));
    private static final TagKey<Item> GEMS = TagKey.m_203882_(ForgeRegistries.Keys.ITEMS, new ResourceLocation("forge", "gems"));

    @SubscribeEvent
    public void onTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.player instanceof ServerPlayer player) || player.f_19797_ % 10 != 0) {
            return;
        }
        CombatState state = CombatState.of(player);
        long now = CombatState.now(player);
        boolean forest = player.m_9236_().m_204166_(player.m_20183_()).m_203656_(FOREST);
        boolean inCombat = now - state.lastCombat <= 100;
        ItemStack held = player.m_21205_();

        double speed = (forest ? Perks.get(player, "forest_speed") : 0) + (inCombat ? Perks.get(player, "combat_speed") : 0)
                + (now - state.lastShot <= 40 ? Perks.get(player, "skirmish_speed") : 0);
        Modifiers.set(player, Attributes.f_22279_, "speed", speed, AttributeModifier.Operation.MULTIPLY_TOTAL);
        Modifiers.set(player, Attributes.f_22278_, "bulwark_kb", player.m_21254_() ? Perks.get(player, "bulwark") : 0,
                AttributeModifier.Operation.ADDITION);
        Modifiers.set(player, Attributes.f_22285_, "toughness", forest ? Perks.get(player, "forest_toughness") : 0, AttributeModifier.Operation.ADDITION);
        Modifiers.set(player, Attributes.f_22284_, "armor", now - state.lastStoneMined <= 600 ? Perks.get(player, "stonehide") : 0,
                AttributeModifier.Operation.ADDITION);
        Modifiers.set(player, Attributes.f_22276_, "health", player.m_36324_().m_38722_() > 10 ? Perks.get(player, "iron_stomach") : 0,
                AttributeModifier.Operation.ADDITION);
        double attackSpeed = (Weapons.is(held, "light") || Weapons.is(held, "sword") ? Perks.get(player, "duelist_speed") : 0)
                + (Weapons.is(held, "light") ? Perks.get(player, "light_speed") : 0);
        Modifiers.set(player, Attributes.f_22283_, "attack_speed", attackSpeed, AttributeModifier.Operation.MULTIPLY_TOTAL);

        boolean staff = Weapons.is(held, "magic");
        int armourPieces = 0;
        for (ItemStack piece : player.m_6168_()) {
            armourPieces += piece.m_41619_() ? 0 : 1;
        }
        Set<Item> gems = new HashSet<>();
        for (ItemStack stack : player.m_150109_().f_35974_) {
            if (stack.m_204117_(GEMS)) {
                gems.add(stack.m_41720_());
            }
        }
        double spell = (player.m_20070_() ? Perks.get(player, "tide_spell") : 0)
                + armourPieces * Perks.get(player, "warded_spell") + gems.size() * Perks.get(player, "gem_spell")
                + (staff ? Perks.get(player, "staff_spell") : 0)
                + (player.m_36324_().m_38702_() >= 20 ? Perks.get(player, "feast_spell") : 0);
        Modifiers.set(player, attribute("irons_spellbooks", "spell_power"), "spell", spell, AttributeModifier.Operation.MULTIPLY_BASE);
        Modifiers.set(player, attribute("irons_spellbooks", "cooldown_reduction"), "cooldown", staff ? Perks.get(player, "staff_cooldown") : 0,
                AttributeModifier.Operation.ADDITION);
        Modifiers.set(player, attribute("irons_spellbooks", "mana_regen"), "regen", (now - state.lastMeal <= 1200 ? Perks.get(player, "brain_regen") : 0)
                + (now - state.lastCombat > 200 ? Perks.get(player, "wellspring") : 0),
                AttributeModifier.Operation.MULTIPLY_BASE);

        if (player.f_19797_ % 100 == 0 && Perks.get(player, "earthbound") > 0) {
            ResourceLocation below = ForgeRegistries.BLOCKS.getKey(player.m_9236_().m_8055_(player.m_20097_()).m_60734_());
            if (below != null && (below.m_135815_().equals("grass_block") || below.m_135815_().equals("farmland"))) {
                player.m_5634_((float) Perks.get(player, "earthbound"));
            }
        }
        if (Perks.get(player, "seas_blessing") > 0 && player.m_20069_()) {
            player.m_7292_(new MobEffectInstance(MobEffects.f_19593_, 60, 0, true, false));
            player.m_7292_(new MobEffectInstance(MobEffects.f_19592_, 60, 0, true, false));
        }
    }

    private static Attribute attribute(String namespace, String path) {
        return ForgeRegistries.ATTRIBUTES.getValue(new ResourceLocation(namespace, path));
    }
}
