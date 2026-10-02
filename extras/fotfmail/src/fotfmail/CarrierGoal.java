package fotfmail;

import com.chaosthedude.endermail.block.LockerBlock;
import com.chaosthedude.endermail.block.entity.LockerBlockEntity;
import com.chaosthedude.endermail.entity.EnderMailmanEntity;
import java.util.EnumSet;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.NonNullList;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.common.extensions.IForgeEntity;

/**
 * The walk of an Ender Mail carrier taking a letter (persistent data "fotfmail_letter", set by Mail.send):
 *   5 (WAITING) out of sight for SEND_DELAY, then appears 8-DISTANCE blocks from the sender's mailbox, any direction
 *   0 walk up to the sender's mailbox, pause, pick up the letter (shows the parcel in its hands)
 *   1 walk a few blocks away, wait LINGER, then teleport ('in transit' high above the world for TRANSIT ticks)
 *   2 appear 8-DISTANCE blocks from the friend's mailbox (if nobody is near it, deliver straight in instead)
 *   3 walk up, pause, drop the letter in
 *   4 walk away empty-handed, wait LINGER, then teleport out
 * Phase and both mailbox positions are in the carrier's persistent data, so a restart resumes the walk.
 * Ender Mail's own carrier goals and random teleports are switched off for these carriers (mixins).
 */
public final class CarrierGoal extends Goal {
    static final String PHASE = "fotfmail_phase";
    static final String FROM = "fotfmail_from";
    static final String TO = "fotfmail_to";
    static final int WAITING = 5; // phase: called, not here yet
    static final int SEND_DELAY = 200; // the carrier shows up this long after you send (10 s)
    static final int DISTANCE = 12; // how far from a mailbox the carrier appears and walks off to (any direction)
    private static final int WALK_TIMEOUT = 400;
    private static final int AWAY_TIMEOUT = 200;
    private static final int PAUSE = 60; // stands at each mailbox this long (3 s)
    private static final int LINGER = 60; // waits where it walked off to before teleporting (3 s)
    private static final int TRANSIT = 80; // 'travelling' between mailboxes, out of sight (4 s)
    private final EnderMailmanEntity carrier;
    private int ticks;
    private int pause;
    private BlockPos walkTarget;

    public CarrierGoal(EnderMailmanEntity carrier) {
        this.carrier = carrier;
        m_7021_(EnumSet.of(Goal.Flag.MOVE, Goal.Flag.LOOK, Goal.Flag.JUMP));
    }

    public static boolean isLetterCarrier(EnderMailmanEntity carrier) {
        return data(carrier).m_128471_(Mail.LETTER_TAG);
    }

    static CompoundTag data(EnderMailmanEntity carrier) {
        return ((IForgeEntity) (Object) carrier).getPersistentData();
    }

    @Override
    public boolean m_8036_() {
        return isLetterCarrier(carrier) && !carrier.m_9236_().m_5776_();
    }

    @Override
    public boolean m_8045_() {
        return m_8036_() && !carrier.m_213877_();
    }

    @Override
    public void m_8056_() {
        ticks = 0;
        pause = 0;
        walkTarget = null;
    }

    @Override
    public void m_8037_() {
        CompoundTag data = data(carrier);
        BlockPos from = BlockPos.m_122022_(data.m_128454_(FROM));
        BlockPos to = BlockPos.m_122022_(data.m_128454_(TO));
        ticks++;
        switch (data.m_128451_(PHASE)) {
            case WAITING -> {
                if (ticks < SEND_DELAY) {
                    carrier.m_21573_().m_26573_();
                    carrier.m_20256_(net.minecraft.world.phys.Vec3.f_82478_);
                    return;
                }
                BlockPos start = spotAround(carrier.m_9236_(), from, carrier.m_217043_());
                if (start == null) {
                    start = from.m_7494_();
                }
                carrier.m_20242_(false);
                carrier.m_6021_(start.m_123341_() + 0.5, start.m_123342_(), start.m_123343_() + 0.5);
                poof();
                carrier.playEndermanSound();
                nextPhase(data, 0);
            }
            case 0 -> {
                if (walkUpTo(from)) {
                    carrier.setCarryingPackage(true);
                    carrier.playEndermanSound();
                    nextPhase(data, 1);
                }
            }
            case 1 -> {
                if (walkAwayFrom(from) && ++pause >= LINGER) {
                    poof();
                    carrier.playEndermanSound();
                    // 'In transit': parked far above the world, out of sight, until it appears at the other mailbox.
                    carrier.m_20242_(true);
                    carrier.m_6021_(carrier.m_20185_(), carrier.m_9236_().m_151558_() + 64, carrier.m_20189_());
                    nextPhase(data, 2);
                }
            }
            case 2 -> {
                if (ticks < TRANSIT) {
                    carrier.m_21573_().m_26573_();
                    carrier.m_20256_(net.minecraft.world.phys.Vec3.f_82478_);
                    return;
                }
                carrier.m_20242_(false);
                ServerLevel level = (ServerLevel) carrier.m_9236_();
                BlockPos arrival = spotAround(level, to, carrier.m_217043_());
                if (!level.m_143340_(to) || arrival == null) {
                    deliver(to); // nobody near the friend's mailbox: straight in, no walk
                    carrier.m_146870_();
                    return;
                }
                carrier.m_6021_(arrival.m_123341_() + 0.5, arrival.m_123342_(), arrival.m_123343_() + 0.5);
                poof();
                carrier.playEndermanSound();
                nextPhase(data, 3);
            }
            case 3 -> {
                if (walkUpTo(to)) {
                    deliver(to);
                    nextPhase(data, 4);
                }
            }
            default -> {
                if (walkAwayFrom(to) && ++pause >= LINGER) {
                    poof();
                    carrier.playEndermanSound();
                    carrier.m_146870_();
                }
            }
        }
    }

    private void nextPhase(CompoundTag data, int phase) {
        data.m_128405_(PHASE, phase);
        ticks = 0;
        pause = 0;
        walkTarget = null;
    }

    /** Walks to the front of the mailbox, then pauses facing it. True once the pause is over. */
    private boolean walkUpTo(BlockPos mailbox) {
        Level level = carrier.m_9236_();
        if (walkTarget == null) {
            walkTarget = standableNear(level, inFrontOf(level, mailbox, 1));
            if (walkTarget == null) {
                walkTarget = mailbox;
            }
        }
        boolean there = carrier.m_20275_(walkTarget.m_123341_() + 0.5, walkTarget.m_123342_(), walkTarget.m_123343_() + 0.5) < 2.5;
        if (!there && ticks < WALK_TIMEOUT) {
            if (ticks % 20 == 1) {
                carrier.m_21573_().m_26519_(walkTarget.m_123341_() + 0.5, walkTarget.m_123342_(), walkTarget.m_123343_() + 0.5, 1.0);
            }
            return false;
        }
        carrier.m_21573_().m_26573_();
        carrier.m_21563_().m_24946_(mailbox.m_123341_() + 0.5, mailbox.m_123342_() + 0.6, mailbox.m_123343_() + 0.5);
        return ++pause >= PAUSE;
    }

    /** Walks a few blocks off from the mailbox. True when there (or after a while). */
    private boolean walkAwayFrom(BlockPos mailbox) {
        Level level = carrier.m_9236_();
        if (walkTarget == null) {
            walkTarget = spotAround(level, mailbox, carrier.m_217043_());
            if (walkTarget == null) {
                return true;
            }
        }
        if (ticks % 20 == 1) {
            carrier.m_21573_().m_26519_(walkTarget.m_123341_() + 0.5, walkTarget.m_123342_(), walkTarget.m_123343_() + 0.5, 1.0);
        }
        return ticks >= AWAY_TIMEOUT
                || carrier.m_20275_(walkTarget.m_123341_() + 0.5, walkTarget.m_123342_(), walkTarget.m_123343_() + 0.5) < 2.5;
    }

    /** Puts the letter in the mailbox (dropped beside it if the mailbox is gone or full). */
    private void deliver(BlockPos mailbox) {
        Level level = carrier.m_9236_();
        NonNullList<ItemStack> contents = carrier.getContents();
        ItemStack letter = contents.isEmpty() ? ItemStack.f_41583_ : contents.get(0);
        if (!letter.m_41619_()) {
            BlockEntity blockEntity = level.m_7702_(mailbox);
            if (!(blockEntity instanceof LockerBlockEntity locker) || !locker.addPackage(letter.m_41777_())) {
                level.m_7967_(new ItemEntity(level, mailbox.m_123341_() + 0.5, mailbox.m_123342_() + 1.0, mailbox.m_123343_() + 0.5, letter.m_41777_()));
            }
        }
        carrier.setContents(NonNullList.m_122780_(1, ItemStack.f_41583_));
        carrier.setCarryingPackage(false);
    }

    private void poof() {
        ((ServerLevel) carrier.m_9236_()).m_8767_(ParticleTypes.f_123760_,
                carrier.m_20185_(), carrier.m_20186_() + 1.0, carrier.m_20189_(), 40, 0.4, 0.9, 0.4, 0.2);
    }

    /** The block `distance` steps out from the mailbox's front (the side its entry hole faces). */
    static BlockPos inFrontOf(Level level, BlockPos mailbox, int distance) {
        BlockState state = level.m_8055_(mailbox);
        Direction facing = state.m_60734_() instanceof LockerBlock ? state.m_61143_(LockerBlock.FACING) : Direction.NORTH;
        return mailbox.m_5484_(facing, distance);
    }

    /**
     * Somewhere to stand 8-DISTANCE blocks from the mailbox in a random direction; falls back to spots in front of it,
     * closer in, if nothing around is standable.
     */
    static BlockPos spotAround(Level level, BlockPos mailbox, RandomSource random) {
        for (int attempt = 0; attempt < 16; attempt++) {
            double angle = random.m_188500_() * Math.PI * 2;
            double distance = 8 + random.m_188500_() * (DISTANCE - 8);
            BlockPos spot = standableNear(level, mailbox.m_7918_(
                    (int) Math.round(Math.cos(angle) * distance), 0, (int) Math.round(Math.sin(angle) * distance)));
            if (spot != null) {
                return spot;
            }
        }
        return spotInFront(level, mailbox, DISTANCE);
    }

    /** Somewhere to stand `distance` blocks in front of the mailbox, trying closer spots if that's blocked. */
    static BlockPos spotInFront(Level level, BlockPos mailbox, int distance) {
        for (int d = distance; d >= 2; d -= 3) {
            BlockPos spot = standableNear(level, inFrontOf(level, mailbox, d));
            if (spot != null) {
                return spot;
            }
        }
        return null;
    }

    /** A spot near pos (a few blocks up or down) with two air blocks over solid ground, or null. */
    static BlockPos standableNear(Level level, BlockPos pos) {
        for (int dy = 2; dy >= -4; dy--) {
            BlockPos feet = pos.m_7918_(0, dy, 0);
            BlockPos below = feet.m_7495_();
            if (level.m_46859_(feet) && level.m_46859_(feet.m_7494_()) && level.m_8055_(below).m_60783_(level, below, Direction.UP)) {
                return feet;
            }
        }
        return null;
    }
}
