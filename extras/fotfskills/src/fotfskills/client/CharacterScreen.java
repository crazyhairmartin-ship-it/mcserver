package fotfskills.client;

import fotfskills.perk.ClientBuffs;
import fotfskills.perk.PerkSync;
import fotfskills.perk.SkillProfile;
import java.util.List;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.inventory.InventoryScreen;
import net.minecraft.network.chat.Component;
import net.minecraftforge.fml.ModList;

/**
 * Character screen (opened from the inventory): your character on the left with health, stamina and mana; on the right
 * an Overview tab (total level, active buffs) and one tab per skill (level, XP to the next level, points, owned nodes).
 */
public final class CharacterScreen extends Screen {
    private final Screen parent;
    private int tab = -1;                                         // -1 = Overview, else the skill's index

    public CharacterScreen(Screen parent) {
        super(Component.m_237113_("Character"));
        this.parent = parent;
    }

    @Override
    protected void m_7856_() {
        PerkSync.requestProfile();
        int left = f_96543_ / 2 - 20;
        int top = f_96544_ / 2 - 100;
        m_142416_(Button.m_253074_(Component.m_237113_("Overview"), b -> tab = -1).m_252987_(left, top, 64, 16).m_253136_());
        String[] skills = {"Min", "For", "Far", "Fis", "Coo", "Cra", "Att", "Ran", "Def", "Agi", "Mag", "Tam"};
        for (int i = 0; i < skills.length; i++) {
            final int index = i;
            int col = (i + 1) % 7, row = (i + 1) / 7;
            m_142416_(Button.m_253074_(Component.m_237113_(skills[i]), b -> tab = index)
                    .m_252987_(left + (col == 0 ? 0 : 64 + (col - 1) * 30), top + row * 18, col == 0 ? 64 : 30, 16).m_253136_());
        }
        m_142416_(Button.m_253074_(Component.m_237113_("Back"), b -> m_7379_())
                .m_252987_(f_96543_ / 2 - 50, f_96544_ - 28, 100, 20).m_253136_());
    }

    @Override
    public void m_88315_(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
        m_280273_(g);
        SkillProfile profile = SkillProfile.latest;
        int cx = f_96543_ / 2;
        int top = f_96544_ / 2 - 100;
        // left: the character and the three bars
        int modelX = cx - 120;
        if (f_96541_.f_91074_ != null) {
            InventoryScreen.m_274545_(g, modelX, top + 120, 50, modelX - mouseX, top + 40 - mouseY, f_96541_.f_91074_);
            float hp = f_96541_.f_91074_.m_21223_() + f_96541_.f_91074_.m_6103_();
            bar(g, modelX - 50, top + 132, "Health", hp, f_96541_.f_91074_.m_21233_(), 0xFFD9443B);
            if (ModList.get().isLoaded("parcool")) {
                double[] stamina = ClientStats.stamina(f_96541_.f_91074_);
                bar(g, modelX - 50, top + 152, "Stamina", stamina[0], stamina[1], 0xFFE3B341);
            }
            if (ModList.get().isLoaded("irons_spellbooks")) {
                double[] mana = ClientStats.mana(f_96541_.f_91074_);
                bar(g, modelX - 50, top + 172, "Mana", mana[0], mana[1], 0xFF5B8DEF);
            }
        }
        // right: the selected tab
        int x = cx - 20;
        int y = top + 42;
        if (profile == null) {
            g.m_280056_(f_96547_, "§7Loading...", x, y, 0xFFFFFFFF, false);
        } else if (tab < 0 || tab >= profile.skills().size()) {
            g.m_280056_(f_96547_, "§6§lTotal level " + profile.totalLevel(), x, y, 0xFFFFFFFF, false);
            y += 14;
            g.m_280056_(f_96547_, "§eActive buffs", x, y, 0xFFFFFFFF, false);
            y += 11;
            List<String> buffs = ClientBuffs.get();
            if (buffs.isEmpty()) {
                g.m_280056_(f_96547_, "§7None right now", x, y, 0xFFFFFFFF, false);
            }
            for (String line : buffs) {
                g.m_280056_(f_96547_, line, x, y, 0xFFFFFFFF, false);
                y += 10;
            }
        } else {
            SkillProfile.Entry s = profile.skills().get(tab);
            g.m_280056_(f_96547_, "§6§l" + s.name() + " §r§elevel " + s.level(), x, y, 0xFFFFFFFF, false);
            y += 13;
            if (s.level() < 50 && s.required() > 0) {
                bar(g, x, y, "XP", s.current(), s.required(), 0xFF7FCF83);
                y += 20;
            }
            g.m_280056_(f_96547_, "§7Points: " + s.spent() + " spent, " + (s.points() - s.spent()) + " to spend", x, y, 0xFFFFFFFF, false);
            y += 13;
            g.m_280056_(f_96547_, "§eYour nodes", x, y, 0xFFFFFFFF, false);
            y += 11;
            if (s.perks().isEmpty()) {
                g.m_280056_(f_96547_, "§7None yet (press K to open the tree)", x, y, 0xFFFFFFFF, false);
            }
            for (String perk : s.perks()) {
                if (y > f_96544_ - 40) {
                    g.m_280056_(f_96547_, "§7...", x, y, 0xFFFFFFFF, false);
                    break;
                }
                g.m_280056_(f_96547_, perk, x, y, 0xFFFFFFFF, false);
                y += 10;
            }
        }
        super.m_88315_(g, mouseX, mouseY, partialTick);
    }

    private void bar(GuiGraphics g, int x, int y, String label, double value, double max, int color) {
        int width = 100;
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
