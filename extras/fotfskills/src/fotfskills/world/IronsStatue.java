package fotfskills.world;

import io.redspace.ironslib.patreon.PatreonData;
import io.redspace.ironslib.patreon.data.ProfileResult;
import io.redspace.ironslib.statue.PlayerStatuePose;
import io.redspace.ironslib.statue.block.statue_block.player.PlayerStatueBlockEntity;
import java.util.List;
import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.RotationSegment;
import net.minecraftforge.registries.ForgeRegistries;

/** Iron's player statues for RemovedBlocks (kept apart so nothing loads Iron's classes when it's absent). */
final class IronsStatue {
    private IronsStatue() {
    }

    private static List<UUID> skins() {
        return PatreonData.getInstance().getProfileValues().stream()
                .filter(p -> p.permissions().supportsStatues()).map(ProfileResult::uuid).toList();
    }

    static boolean hasSkins() {
        return !skins().isEmpty();
    }

    /** Places a 1x2 player statue facing the old statue's way, with a random supporter skin and pose; false if it can't fit. */
    static boolean place(ServerLevel level, BlockPos pos, Direction facing) {
        Block statue = ForgeRegistries.BLOCKS.getValue(new ResourceLocation("irons_lib", "player_statue"));
        if (statue == null || statue == Blocks.f_50016_ || !level.m_8055_(pos.m_7494_()).m_247087_()) {
            return false;
        }
        BlockState state = statue.m_49966_().m_61124_(BlockStateProperties.f_61390_, RotationSegment.m_245225_(facing.m_122424_()));   // Iron's rotation faces the other way
        level.m_7731_(pos, state, 3);
        statue.m_6402_(level, pos, state, null, ItemStack.f_41583_);          // builds the upper half
        if (level.m_7702_(pos) instanceof PlayerStatueBlockEntity be) {
            PlayerStatueBlockEntity main = be.getPrimaryController();
            List<UUID> skins = skins();
            if (!skins.isEmpty()) {
                main.setPlayerUuid(skins.get(level.m_213780_().m_188503_(skins.size())));
            }
            PlayerStatuePose[] poses = PlayerStatuePose.values();
            main.setPose(poses[level.m_213780_().m_188503_(poses.length)]);
        }
        return true;
    }
}
