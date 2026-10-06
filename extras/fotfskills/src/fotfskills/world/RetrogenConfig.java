package fotfskills.world;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import java.io.IOException;
import java.io.Reader;
import java.io.Writer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Pattern;

/**
 * config/fotfskills-retrogen.json: which placed features Retrogen adds to chunks generated before their mod was
 * installed, and the limits it works within. Off and empty by default, so nothing happens until it's set up.
 * Patterns are ids with * (any characters) and ? (one character), e.g. "realmrpg_fallen_adventurers:*".
 */
public final class RetrogenConfig {
    public boolean enabled = false;
    /** Placed features to add (id patterns). */
    public List<String> features = new ArrayList<>();
    /** Placed features never to add, even if they match {@link #features}. */
    public List<String> excludeFeatures = new ArrayList<>();
    /** Dimensions to work in (id patterns). */
    public List<String> dimensions = new ArrayList<>(List.of("*"));
    /** Skip a chunk if it or a neighbour has had players near it for longer than this (ticks; -1 = no limit). */
    public long maxInhabitedTicks = 1200;
    /** Skip a chunk within this many chunks of an Open Parties and Claims claim (-1 = don't check claims). */
    public int claimBufferChunks = 2;
    public int maxChunksPerTick = 2;
    public int maxMillisPerTick = 8;
    /** Log every chunk that gets features (for testing). */
    public boolean logChunks = false;

    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();

    /** Reads the file, writing the defaults first if it doesn't exist. A broken file reads as the (disabled) defaults. */
    public static RetrogenConfig load(Path file) {
        if (!Files.exists(file)) {
            RetrogenConfig defaults = new RetrogenConfig();
            try {
                Files.createDirectories(file.getParent());
                try (Writer out = Files.newBufferedWriter(file)) {
                    GSON.toJson(defaults, out);
                }
            } catch (IOException ignored) {
                // read-only config folder: run with the defaults
            }
            return defaults;
        }
        try (Reader in = Files.newBufferedReader(file)) {
            return parse(in);
        } catch (IOException | RuntimeException e) {
            return new RetrogenConfig();
        }
    }

    static RetrogenConfig parse(Reader in) {
        RetrogenConfig config = GSON.fromJson(in, RetrogenConfig.class);
        if (config == null) {
            return new RetrogenConfig();
        }
        if (config.features == null) config.features = new ArrayList<>();
        if (config.excludeFeatures == null) config.excludeFeatures = new ArrayList<>();
        if (config.dimensions == null) config.dimensions = new ArrayList<>(List.of("*"));
        config.maxChunksPerTick = Math.max(1, config.maxChunksPerTick);
        config.maxMillisPerTick = Math.max(1, config.maxMillisPerTick);
        return config;
    }

    public boolean wantsFeature(String id) {
        return anyMatch(features, id) && !anyMatch(excludeFeatures, id);
    }

    public boolean wantsDimension(String id) {
        return anyMatch(dimensions, id);
    }

    public boolean inhabitedOk(long inhabitedTicks) {
        return maxInhabitedTicks < 0 || inhabitedTicks <= maxInhabitedTicks;
    }

    static boolean anyMatch(List<String> patterns, String id) {
        for (String pattern : patterns) {
            if (matches(pattern, id)) {
                return true;
            }
        }
        return false;
    }

    /** Glob match: * is any run of characters, ? is one character, everything else is literal. */
    static boolean matches(String pattern, String id) {
        StringBuilder regex = new StringBuilder();
        for (char c : pattern.toCharArray()) {
            if (c == '*') regex.append(".*");
            else if (c == '?') regex.append('.');
            else regex.append(Pattern.quote(String.valueOf(c)));
        }
        return Pattern.matches(regex.toString(), id);
    }
}
