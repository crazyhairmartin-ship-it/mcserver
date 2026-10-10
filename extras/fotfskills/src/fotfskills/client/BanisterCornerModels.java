package fotfskills.client;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.block.BlockModelShaper;
import net.minecraft.client.renderer.block.model.BakedQuad;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.level.block.state.properties.Property;
import net.minecraft.world.level.block.state.properties.StairsShape;
import net.minecraftforge.client.event.ModelEvent;
import net.minecraftforge.client.model.BakedModelWrapper;
import net.minecraftforge.client.model.data.ModelData;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * Corner models for banisters, built when the game bakes its models, from each banister's own straight model (Twilight
 * Forest's woods, their random plank versions and Every Compat's modded woods alike; no model files in the pack). The
 * corner block state comes from mixin/BanisterBlockMixin; blockstates that don't list it map corner states to the
 * straight model, which is replaced here.
 *   inner (an L): the straight banister plus the one facing the side, its rail trimmed where it meets the first
 *   outer (a corner post): the straight banister cut down to the side's last 4 pixels, its nearer post moved into the
 *   corner
 */
public final class BanisterCornerModels {
    private static final float BAND = 0.25f;
    private static final float POST_SHIFT = 2.5f / 16;
    private static final float EPS = 1.0e-4f;

    private BanisterCornerModels() {
    }

    @SuppressWarnings("unchecked")
    public static void onModifyBakingResult(ModelEvent.ModifyBakingResult event) {
        Map<ResourceLocation, BakedModel> models = event.getModels();
        for (Block block : ForgeRegistries.BLOCKS) {
            if (!(block instanceof twilightforest.block.BanisterBlock)) {
                continue;
            }
            Property<?> prop = block.m_49965_().m_61081_("corner");
            if (!(prop instanceof EnumProperty<?> p) || p.m_61709_() != StairsShape.class) {
                continue;
            }
            EnumProperty<StairsShape> corner = (EnumProperty<StairsShape>) p;
            for (BlockState state : block.m_49965_().m_61056_()) {
                StairsShape shape = state.m_61143_(corner);
                if (shape == StairsShape.STRAIGHT) {
                    continue;
                }
                Direction facing = state.m_61143_(HorizontalDirectionalBlock.f_54117_);
                boolean left = shape == StairsShape.INNER_LEFT || shape == StairsShape.OUTER_LEFT;
                Direction side = left ? facing.m_122428_() : facing.m_122427_();
                BlockState straight = state.m_61124_(corner, StairsShape.STRAIGHT);
                BlockState beside = straight.m_61124_(HorizontalDirectionalBlock.f_54117_, side);
                BakedModel main = models.get(BlockModelShaper.m_110895_(straight));
                BakedModel other = models.get(BlockModelShaper.m_110895_(beside));
                if (main != null && other != null) {
                    boolean inner = shape == StairsShape.INNER_LEFT || shape == StairsShape.INNER_RIGHT;
                    models.put(BlockModelShaper.m_110895_(state), new Corner(main, other, straight, beside, facing, side, inner));
                }
            }
        }
    }

    private static final class Corner extends BakedModelWrapper<BakedModel> {
        private final BakedModel other;
        private final BlockState straight;
        private final BlockState beside;
        private final Direction facing;
        private final Direction side;
        private final boolean inner;

        Corner(BakedModel main, BakedModel other, BlockState straight, BlockState beside, Direction facing, Direction side,
               boolean inner) {
            super(main);
            this.other = other;
            this.straight = straight;
            this.beside = beside;
            this.facing = facing;
            this.side = side;
            this.inner = inner;
        }

        @Override
        public List<BakedQuad> m_213637_(BlockState state, Direction dir, RandomSource rand) {
            return getQuads(state, dir, rand, ModelData.EMPTY, null);
        }

        @Override
        public List<BakedQuad> getQuads(BlockState state, Direction dir, RandomSource rand, ModelData data, RenderType type) {
            // the same plank pick for both halves (woods with random plank textures)
            List<BakedQuad> out = new ArrayList<>();
            for (BakedQuad q : ((net.minecraftforge.client.extensions.IForgeBakedModel) originalModel).getQuads(straight, dir, RandomSource.m_216335_(42L), data, type)) {
                BakedQuad kept = inner ? q : stub(q);
                if (kept != null) {
                    out.add(kept);
                }
            }
            if (inner) {
                for (BakedQuad q : ((net.minecraftforge.client.extensions.IForgeBakedModel) other).getQuads(beside, dir, RandomSource.m_216335_(42L), data, type)) {
                    BakedQuad kept = trimmed(q);
                    if (kept != null) {
                        out.add(kept);
                    }
                }
            }
            return out;
        }

        /**
         * Inner corner: the side banister's rail stops at the straight banister's rail, and anything of it reaching into
         * that rail goes (its end cap, and the post nearest the corner, which would poke through the straight
         * banister's rail and post).
         */
        private BakedQuad trimmed(BakedQuad q) {
            int axis = axis(facing);
            float[][] f = read(q);
            float ext = QuadGeometry.extent(f, axis);
            if (ext > 0.5f) {
                return write(q, positive(facing) ? QuadGeometry.clip(f, axis, 0, 1 - BAND) : QuadGeometry.clip(f, axis, BAND, 1));
            }
            boolean intoRail = positive(facing) ? QuadGeometry.reaches(f, axis, 1 - BAND, 1) : QuadGeometry.reaches(f, axis, 0, BAND);
            return intoRail ? null : q;
        }

        /** Outer corner: only the side's corner of the straight banister, with its nearer post moved into the corner. */
        private BakedQuad stub(BakedQuad q) {
            int axis = axis(side);
            float[][] f = read(q);
            float ext = QuadGeometry.extent(f, axis);
            float centre = QuadGeometry.centre(f, axis);
            if (ext > 0.5f) {
                return write(q, positive(side) ? QuadGeometry.clip(f, axis, 1 - BAND, 1) : QuadGeometry.clip(f, axis, 0, BAND));
            }
            if (ext < EPS && onEdge(centre)) {
                return inBand(centre, side) ? q : null;      // keep the rail's outer end cap only
            }
            boolean nearer = positive(side) ? centre > 0.5f : centre < 0.5f;
            return nearer ? write(q, QuadGeometry.shift(f, axis, positive(side) ? POST_SHIFT : -POST_SHIFT)) : null;
        }
    }

    private static int axis(Direction d) {
        return d.m_122434_() == Direction.Axis.X ? QuadGeometry.X : QuadGeometry.Z;
    }

    private static boolean positive(Direction d) {
        return d.m_122421_() == Direction.AxisDirection.POSITIVE;
    }

    private static boolean onEdge(float c) {
        return c < EPS || c > 1 - EPS;
    }

    private static boolean inBand(float c, Direction d) {
        return positive(d) ? c >= 1 - BAND - EPS : c <= BAND + EPS;
    }

    /** BakedQuad vertex data (block format: x, y, z, colour, u, v, light, normal per corner) to {x, y, z, u, v}. */
    private static float[][] read(BakedQuad q) {
        int[] v = q.m_111303_();
        int stride = v.length / 4;
        float[][] f = new float[4][5];
        for (int i = 0; i < 4; i++) {
            int o = i * stride;
            f[i][0] = Float.intBitsToFloat(v[o]);
            f[i][1] = Float.intBitsToFloat(v[o + 1]);
            f[i][2] = Float.intBitsToFloat(v[o + 2]);
            f[i][3] = Float.intBitsToFloat(v[o + 4]);
            f[i][4] = Float.intBitsToFloat(v[o + 5]);
        }
        return f;
    }

    private static BakedQuad write(BakedQuad q, float[][] f) {
        if (f == null) {
            return null;
        }
        int[] v = q.m_111303_().clone();
        int stride = v.length / 4;
        for (int i = 0; i < 4; i++) {
            int o = i * stride;
            v[o] = Float.floatToRawIntBits(f[i][0]);
            v[o + 1] = Float.floatToRawIntBits(f[i][1]);
            v[o + 2] = Float.floatToRawIntBits(f[i][2]);
            v[o + 4] = Float.floatToRawIntBits(f[i][3]);
            v[o + 5] = Float.floatToRawIntBits(f[i][4]);
        }
        return new BakedQuad(v, q.m_111305_(), q.m_111306_(), q.m_173410_(), q.m_111307_());
    }
}
