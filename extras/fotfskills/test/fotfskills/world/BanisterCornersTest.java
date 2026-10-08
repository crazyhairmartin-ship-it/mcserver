package fotfskills.world;

import java.util.HashMap;
import java.util.Map;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.state.properties.StairsShape;

/** Banister corners follow the stair rules (rail on the facing edge = a stair's tall back). Run: sh test.sh */
public final class BanisterCornersTest {
    public static void main(String[] args) {
        // facing north: counter-clockwise is west, clockwise is east
        check(shape(Direction.NORTH, Map.of()) == StairsShape.STRAIGHT, "alone: straight");
        check(shape(Direction.NORTH, Map.of(Direction.NORTH, Direction.NORTH, Direction.SOUTH, Direction.NORTH))
                == StairsShape.STRAIGHT, "in a straight run: straight");
        check(shape(Direction.NORTH, Map.of(Direction.SOUTH, Direction.WEST)) == StairsShape.INNER_LEFT,
                "banister behind facing west: L with the west edge");
        check(shape(Direction.NORTH, Map.of(Direction.SOUTH, Direction.EAST)) == StairsShape.INNER_RIGHT,
                "banister behind facing east: L with the east edge");
        check(shape(Direction.NORTH, Map.of(Direction.NORTH, Direction.WEST)) == StairsShape.OUTER_LEFT,
                "banister in front facing west: corner post on the west side");
        check(shape(Direction.NORTH, Map.of(Direction.NORTH, Direction.EAST)) == StairsShape.OUTER_RIGHT,
                "banister in front facing east: corner post on the east side");
        check(shape(Direction.NORTH, Map.of(Direction.NORTH, Direction.WEST, Direction.EAST, Direction.NORTH))
                == StairsShape.STRAIGHT, "a parallel banister beside it keeps the run straight (like stairs)");
        check(shape(Direction.EAST, Map.of(Direction.WEST, Direction.NORTH)) == StairsShape.INNER_LEFT,
                "rotates: facing east, banister behind facing north (counter-clockwise) is inner left");
        System.out.println("BanisterCornersTest ok");
    }

    private static StairsShape shape(Direction facing, Map<Direction, Direction> neighbours) {
        Map<Direction, Direction> around = new HashMap<>(neighbours);
        return BanisterCorners.shape(facing, around::get);
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
