package fotfskills.perk;

import java.util.Map;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.TagParser;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.projectile.FireworkRocketEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.puffish.skillsmod.api.Category;
import net.puffish.skillsmod.api.SkillsAPI;

/**
 * Level-up message naming the skill and its new level, with a sound; reaching the level cap (50) also gets a bigger
 * message, the challenge-complete sound and fireworks. Players can turn it off with /fotfskills levelups off.
 */
public final class LevelUps {
    private static final int CAP = 50;
    private static final Map<String, String> NAMES = Map.ofEntries(
            Map.entry("mining", "Mining"), Map.entry("forage", "Foraging"), Map.entry("farm", "Farming"),
            Map.entry("fish", "Fishing"), Map.entry("cook", "Cooking"), Map.entry("craft", "Crafting"),
            Map.entry("attack", "Attack"), Map.entry("range", "Range"), Map.entry("defense", "Defense"),
            Map.entry("agility", "Agility"), Map.entry("magic", "Magic"), Map.entry("taming", "Taming"));
    private static final String FIREWORK = "{Fireworks:{Flight:1b,Explosions:[{Type:1b,Flicker:1b,Trail:1b,"
            + "Colors:[I;16766720,5635925,5636095],FadeColors:[I;16777215]}]}}";

    private static final LevelGate GATE = new LevelGate();

    private LevelUps() {
    }

    public static void register() {
        SkillsAPI.registerNewPointEvent(LevelUps::onNewPoint);
    }

    private static void onNewPoint(ServerPlayer player, ResourceLocation categoryId) {
        if (!Prefs.of(player.m_20194_()).levelUpsOn(player.m_20148_())) {
            return;
        }
        Category category = SkillsAPI.getCategory(categoryId).orElse(null);
        if (category == null) {
            return;
        }
        int level = category.getExperience().map(e -> e.getLevel(player)).orElse(0);
        if (!GATE.announce(player.m_20148_(), categoryId.m_135815_(), level)) {
            return;                       // points came back (tree reset) or were granted: no new level
        }
        String name = NAMES.getOrDefault(categoryId.m_135815_(), categoryId.m_135815_());
        if (level >= CAP) {
            player.m_213846_(Component.m_237113_("§6§l" + name + " mastered! §r§eLevel " + CAP + " — every node is yours to take."));
            player.m_6330_(SoundEvents.f_12496_, SoundSource.PLAYERS, 1.0f, 1.0f);
            fireworks(player);
        } else {
            player.m_213846_(Component.m_237113_("§6" + name + "§f reached level §e" + level
                    + "§f — a new skill point is ready. §7(/fotfskills levelups off to hide)"));
            player.m_6330_(SoundEvents.f_12275_, SoundSource.PLAYERS, 0.6f, 1.4f);
        }
    }

    private static void fireworks(ServerPlayer player) {
        if (!player.m_9236_().m_45527_(player.m_20183_().m_7494_())) {    // underground: rockets would explode on the ceiling
            ((net.minecraft.server.level.ServerLevel) player.m_9236_()).m_8767_(net.minecraft.core.particles.ParticleTypes.f_123767_,
                    player.m_20185_(), player.m_20186_() + 1, player.m_20189_(), 80, 0.6, 0.8, 0.6, 0.4);
            return;
        }
        try {
            CompoundTag tag = TagParser.m_129359_(FIREWORK);
            for (int i = 0; i < 3; i++) {
                ItemStack rocket = new ItemStack(Items.f_42688_);
                rocket.m_41751_(tag.m_6426_());
                double dx = (i - 1) * 1.5;
                player.m_9236_().m_7967_(new FireworkRocketEntity(player.m_9236_(), player.m_20185_() + dx, player.m_20186_() + 0.5,
                        player.m_20189_(), rocket));
            }
        } catch (com.mojang.brigadier.exceptions.CommandSyntaxException e) {
            // fixed text; cannot fail
        }
    }
}
