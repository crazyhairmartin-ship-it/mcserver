package fotfskills.client;

import fotfskills.perk.ClientBuffs;
import fotfskills.perk.PerkSync;
import fotfskills.perk.SkillProfile;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.Tooltip;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.inventory.InventoryScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * Character screen (opened from the inventory): your character on the left with health, stamina and mana; on the right
 * a big Overview tab (total level, every skill's level, active buffs) and one icon tab per skill (level, XP to the next
 * level, points, and each node you own with its ranks and exactly what it does). The right side scrolls.
 */
public final class CharacterScreen extends Screen {
    /** Skill tree id, tab name, icon item (the same icons as the skill trees). */
    private static final String[][] SKILLS = {
            {"mining", "Mining", "minecraft:iron_pickaxe"}, {"forage", "Foraging", "minecraft:iron_axe"},
            {"farm", "Farming", "minecraft:iron_hoe"}, {"fish", "Fishing", "minecraft:fishing_rod"},
            {"cook", "Cooking", "farmersdelight:cooking_pot"}, {"craft", "Crafting", "minecraft:crafting_table"},
            {"attack", "Attack", "minecraft:iron_sword"}, {"range", "Range", "minecraft:bow"},
            {"defense", "Defense", "minecraft:shield"}, {"agility", "Agility", "minecraft:feather"},
            {"magic", "Magic", "minecraft:enchanted_book"}, {"taming", "Taming", "minecraft:lead"}};
    private static final int PANEL_W = 196;

    private final Screen parent;
    private String tab = null;                                    // null = Overview, else a skill tree id
    private final List<Button> tabButtons = new ArrayList<>();
    private final ItemStack[] icons = new ItemStack[SKILLS.length];
    private Button overview;
    private int scroll;
    private int contentHeight;

    public CharacterScreen(Screen parent) {
        super(Component.m_237113_("Character"));
        this.parent = parent;
    }

    private int panelX() {
        return f_96543_ / 2 - 20;
    }

    private int top() {
        return f_96544_ / 2 - 100;
    }

    @Override
    protected void m_7856_() {
        PerkSync.requestProfile();
        tabButtons.clear();
        int left = panelX(), top = top();
        overview = m_142416_(Button.m_253074_(Component.m_237113_("Overview"), b -> select(null))
                .m_252987_(left, top, 64, 35).m_253136_());
        for (int i = 0; i < SKILLS.length; i++) {
            String[] skill = SKILLS[i];
            Item item = ForgeRegistries.ITEMS.getValue(new ResourceLocation(skill[2]));
            icons[i] = new ItemStack(item == null ? Items.f_42127_ : item);
            int col = i % 6, row = i / 6;
            tabButtons.add(m_142416_(Button.m_253074_(Component.m_237119_(), b -> select(skill[0]))
                    .m_252987_(left + 68 + col * 21, top + row * 18, 20, 17)
                    .m_257505_(Tooltip.m_257550_(Component.m_237113_(skill[1]))).m_253136_()));
        }
        m_142416_(Button.m_253074_(Component.m_237113_("Back"), b -> m_7379_())
                .m_252987_(f_96543_ / 2 - 50, f_96544_ - 28, 100, 20).m_253136_());
    }

    private void select(String id) {
        tab = id;
        scroll = 0;
    }

    @Override
    public void m_88315_(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
        m_280273_(g);
        int cx = f_96543_ / 2;
        int top = top();
        // left: the character and the three bars
        int modelX = cx - 120;
        if (f_96541_.f_91074_ != null) {
            InventoryScreen.m_274545_(g, modelX, top + 120, 50, modelX - mouseX, top + 40 - mouseY, f_96541_.f_91074_);
            float hp = f_96541_.f_91074_.m_21223_() + f_96541_.f_91074_.m_6103_();
            bar(g, modelX - 50, top + 132, "Health", hp, f_96541_.f_91074_.m_21233_(), 0xFFD9443B, 100);
            if (ModList.get().isLoaded("parcool")) {
                double[] stamina = ClientStats.stamina(f_96541_.f_91074_);
                bar(g, modelX - 50, top + 152, "Stamina", stamina[0], stamina[1], 0xFFE3B341, 100);
            }
            if (ModList.get().isLoaded("irons_spellbooks")) {
                double[] mana = ClientStats.mana(f_96541_.f_91074_);
                bar(g, modelX - 50, top + 172, "Mana", mana[0], mana[1], 0xFF5B8DEF, 100);
            }
        }
        super.m_88315_(g, mouseX, mouseY, partialTick);
        // tab icons and the selected-tab outline (drawn over the buttons)
        for (int i = 0; i < SKILLS.length; i++) {
            Button b = tabButtons.get(i);
            g.m_280480_(icons[i], b.m_252754_() + 2, b.m_252907_() + 1);
            if (SKILLS[i][0].equals(tab)) {
                g.m_280637_(b.m_252754_() - 1, b.m_252907_() - 1, 22, 19, 0xFFFFD84A);
            }
        }
        if (tab == null) {
            g.m_280637_(overview.m_252754_() - 1, overview.m_252907_() - 1, 66, 37, 0xFFFFD84A);
        }
        // right: the selected tab, clipped and scrolled
        int x = panelX(), y0 = top + 42, bottom = f_96544_ - 34;
        g.m_280588_(x, y0, x + PANEL_W, bottom);
        int y = y0 - scroll;
        SkillProfile profile = SkillProfile.latest;
        if (profile == null) {
            y = text(g, "§7Loading...", x, y);
        } else if (tab == null || entry(profile) == null) {
            y = overview(g, profile, x, y);
        } else {
            y = skill(g, entry(profile), x, y);
        }
        g.m_280618_();
        contentHeight = y + scroll - y0;
        int view = bottom - y0;
        if (contentHeight > view) {                               // scrollbar
            int barH = Math.max(12, view * view / contentHeight);
            int barY = y0 + (view - barH) * scroll / Math.max(1, contentHeight - view);
            g.m_280509_(x + PANEL_W + 2, y0, x + PANEL_W + 4, bottom, 0xFF2A2A2A);
            g.m_280509_(x + PANEL_W + 2, barY, x + PANEL_W + 4, barY + barH, 0xFFAAAAAA);
        }
    }

    private SkillProfile.Entry entry(SkillProfile profile) {
        for (SkillProfile.Entry e : profile.skills()) {
            if (e.id().equals(tab)) {
                return e;
            }
        }
        return null;
    }

    private int overview(GuiGraphics g, SkillProfile profile, int x, int y) {
        y = text(g, "§6§lTotal level " + profile.totalLevel(), x, y) + 4;
        for (int i = 0; i < SKILLS.length; i++) {                 // two columns of skill levels
            SkillProfile.Entry e = null;
            for (SkillProfile.Entry s : profile.skills()) {
                if (s.id().equals(SKILLS[i][0])) {
                    e = s;
                }
            }
            int col = i % 2, cellX = x + col * 98, cellY = y + (i / 2) * 18;
            g.m_280480_(icons[i], cellX, cellY);
            g.m_280056_(f_96547_, "§f" + SKILLS[i][1] + " §e" + (e == null ? 0 : e.level()), cellX + 19, cellY + 4, 0xFFFFFFFF, false);
        }
        y += 18 * ((SKILLS.length + 1) / 2) + 6;
        y = text(g, "§eActive buffs", x, y);
        List<String> buffs = ClientBuffs.get();
        if (buffs.isEmpty()) {
            y = text(g, "§7None right now", x, y);
        }
        for (String line : buffs) {
            y = wrap(g, line, x, y, "");
        }
        return y;
    }

    private int skill(GuiGraphics g, SkillProfile.Entry s, int x, int y) {
        y = text(g, "§6§l" + s.name() + " §r§elevel " + s.level(), x, y) + 2;
        if (s.level() < 50 && s.required() > 0) {
            bar(g, x, y, "XP", s.current(), s.required(), 0xFF7FCF83, PANEL_W - 6);
            y += 20;
        }
        y = text(g, "§7Points: " + s.spent() + " spent, " + (s.points() - s.spent()) + " to spend", x, y) + 3;
        y = text(g, "§eYour nodes", x, y);
        if (s.perks().isEmpty()) {
            y = text(g, "§7None yet (press K to open the tree)", x, y);
        }
        for (SkillProfile.Node node : s.perks()) {
            String ranks = node.maxRank() > 1 ? " §7" + node.rank() + "/" + node.maxRank() : "";
            y = text(g, "§f" + node.title() + ranks, x, y);
            y = wrap(g, node.description(), x + 6, y, "§7") + 3;
        }
        return y;
    }

    private int text(GuiGraphics g, String line, int x, int y) {
        g.m_280056_(f_96547_, line, x, y, 0xFFFFFFFF, false);
        return y + 10;
    }

    /** Word-wraps a line to the panel width; continuation lines keep the given colour code. */
    private int wrap(GuiGraphics g, String line, int x, int y, String colour) {
        int width = PANEL_W - (x - panelX());
        StringBuilder current = new StringBuilder();
        for (String word : line.split(" ")) {
            String next = current.length() == 0 ? word : current + " " + word;
            if (current.length() > 0 && f_96547_.m_92895_(colour + next) > width) {
                y = text(g, colour + current, x, y);
                current = new StringBuilder(word);
            } else {
                current = new StringBuilder(next);
            }
        }
        if (current.length() > 0) {
            y = text(g, colour + current, x, y);
        }
        return y;
    }

    @Override
    public boolean m_6050_(double mouseX, double mouseY, double delta) {
        int view = (f_96544_ - 34) - (top() + 42);
        scroll = (int) Math.max(0, Math.min(Math.max(0, contentHeight - view), scroll - delta * 20));
        return true;
    }

    private void bar(GuiGraphics g, int x, int y, String label, double value, double max, int color, int width) {
        int filled = max <= 0 ? 0 : (int) Math.round(width * Math.min(1, value / max));
        g.m_280056_(f_96547_, "§f" + label + " §7" + Math.round(value) + " / " + Math.round(max), x, y, 0xFFFFFFFF, false);
        g.m_280509_(x, y + 10, x + width, y + 15, 0xFF2A2A2A);
        g.m_280509_(x, y + 10, x + filled, y + 15, color);
    }

    @Override
    public void m_7379_() {
        f_96541_.m_91152_(parent);
    }
}
