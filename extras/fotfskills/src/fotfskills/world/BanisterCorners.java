package fotfskills.world;

import java.util.function.Function;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.state.properties.StairsShape;

/**
 * Twilight Forest banisters turn corners the way stairs do. A banister's rail is on the edge it faces, like a stair's
 * tall back, so vanilla's stair rule (StairBlock.getStairsShape) carries over: a banister behind facing sideways makes
 * an L (INNER: rails on two edges), left = counter-clockwise. Banisters never become OUTER corner posts.
 * Wired up in mixin/BanisterBlockMixin; models built in game by client/BanisterCornerModels.
 */
public final class BanisterCorners {
    private BanisterCorners() {
    }

    /** facingAt(dir) = the facing of the banister next to it in that direction, or null if there's none. */
    public static StairsShape shape(Direction facing, Function<Direction, Direction> facingAt) {
        // No OUTER (corner post): unlike stairs, a banister with a sideways one in front already meets it at the corner,
        // and turning it into a post dropped its rail (three side by side, I_I, lost the outer two).
        Direction back = facingAt.apply(facing.m_122424_());
        if (back != null && back.m_122434_() != facing.m_122434_() && canTurn(facing, back, facingAt)) {
            return back == facing.m_122428_() ? StairsShape.INNER_LEFT : StairsShape.INNER_RIGHT;
        }
        return StairsShape.STRAIGHT;
    }

    /** Like stairs: no corner toward a side where a parallel banister continues the run. */
    private static boolean canTurn(Direction facing, Direction side, Function<Direction, Direction> facingAt) {
        return facingAt.apply(side) != facing;
    }
}
