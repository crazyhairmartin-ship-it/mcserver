package fotfretrogen;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import java.io.IOException;
import java.io.Reader;
import java.io.Writer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.TreeSet;

/**
 * The world's worldgen history (data/fotfskills_retrogen.json in the world folder): one "epoch" per distinct set of
 * placed features the server has started with. Each chunk records the epoch it was generated in, so Retrogen only adds
 * features that didn't exist yet when that chunk was made.
 */
final class RetrogenManifest {
    private static final Gson GSON = new Gson();
    final List<Set<String>> epochs = new ArrayList<>();

    static RetrogenManifest load(Path file) {
        RetrogenManifest manifest = new RetrogenManifest();
        if (Files.exists(file)) {
            try (Reader in = Files.newBufferedReader(file)) {
                List<List<String>> raw = GSON.fromJson(in, new TypeToken<List<List<String>>>() { }.getType());
                if (raw != null) {
                    raw.forEach(epoch -> manifest.epochs.add(new TreeSet<>(epoch)));
                }
            } catch (IOException | RuntimeException ignored) {
                // unreadable: start a new history (old stamped chunks then count as unknown epochs and get nothing)
            }
        }
        return manifest;
    }

    void save(Path file) throws IOException {
        Files.createDirectories(file.getParent());
        try (Writer out = Files.newBufferedWriter(file)) {
            GSON.toJson(epochs, out);
        }
    }

    /** The epoch for the features this server started with: the latest one if nothing changed, else a new one. */
    int epochFor(Set<String> current) {
        if (!epochs.isEmpty() && epochs.get(epochs.size() - 1).equals(current)) {
            return epochs.size() - 1;
        }
        epochs.add(new TreeSet<>(current));
        return epochs.size() - 1;
    }
}
