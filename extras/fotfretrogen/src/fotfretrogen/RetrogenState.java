package fotfretrogen;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * What one chunk has had from Retrogen: the worldgen "epoch" it was generated in (the set of placed features that
 * existed then; {@link #LEGACY} for chunks generated before Retrogen was installed) and the features Retrogen has
 * already added to it.
 */
final class RetrogenState {
    static final int LEGACY = -1;

    final int epoch;
    final Set<String> done;

    RetrogenState(int epoch, Set<String> done) {
        this.epoch = epoch;
        this.done = done;
    }

    static RetrogenState legacy() {
        return new RetrogenState(LEGACY, new HashSet<>());
    }

    /**
     * Whether this chunk still needs a (wanted) feature: not added yet, and not already present when the chunk was
     * generated. Legacy chunks get every wanted feature. A chunk from an epoch the manifest doesn't know (manifest
     * lost) gets nothing, so a lost manifest can never double up features.
     */
    boolean needs(String featureId, List<Set<String>> epochs) {
        if (done.contains(featureId)) {
            return false;
        }
        if (epoch == LEGACY) {
            return true;
        }
        return epoch >= 0 && epoch < epochs.size() && !epochs.get(epoch).contains(featureId);
    }
}
