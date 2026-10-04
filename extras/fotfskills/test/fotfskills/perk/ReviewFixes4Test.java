package fotfskills.perk;

import fotfskills.pet.PetSaveData;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;

/** Phase 4 review fixes: respawned pets never carry inventories or leads, and only plain or skill-managed hooks are rewritten. */
public final class ReviewFixes4Test {
    public static void main(String[] args) {
        CompoundTag donkey = new CompoundTag();
        donkey.m_128365_("Items", new ListTag());
        donkey.m_128365_("SaddleItem", new CompoundTag());
        donkey.m_128365_("ArmorItem", new CompoundTag());
        donkey.m_128365_("DecorItem", new CompoundTag());
        donkey.m_128365_("HandItems", new ListTag());
        donkey.m_128365_("ArmorItems", new ListTag());
        donkey.m_128365_("Leash", new CompoundTag());
        donkey.m_128365_("ActiveEffects", new ListTag());
        donkey.m_128379_("ChestedHorse", true);
        donkey.m_128376_("Fire", (short) 120);
        donkey.m_128359_("CustomName", "{\"text\":\"Biscuit\"}");
        PetSaveData.strip(donkey);
        for (String key : new String[] {"Items", "SaddleItem", "ArmorItem", "DecorItem", "HandItems", "ArmorItems", "Leash", "ActiveEffects"}) {
            check(!donkey.m_128441_(key), key + " removed (it already dropped or would duplicate)");
        }
        check(!donkey.m_128471_("ChestedHorse"), "the chest is gone with its contents");
        check(donkey.m_128448_("Fire") <= 0, "a revived pet isn't on fire");
        check(donkey.m_128441_("CustomName"), "name kept");

        check(HookRule.shouldWrite(100L, 100L, false), "a plain hook (default settings) gets the skill upgrades");
        check(HookRule.shouldWrite(555L, 100L, true), "a hook the skills already manage keeps updating");
        check(!HookRule.shouldWrite(777L, 100L, false), "an existing rocket/ender/motor hook is left alone");
        System.out.println("ReviewFixes4Test ok");
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
