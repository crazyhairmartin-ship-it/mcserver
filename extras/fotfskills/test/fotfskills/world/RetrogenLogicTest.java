package fotfskills.world;

import java.io.StringReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/** Retrogen's config patterns, the per-chunk "still needs it" rule and the worldgen history. Run: sh test.sh */
public final class RetrogenLogicTest {
    public static void main(String[] args) throws Exception {
        check(RetrogenConfig.matches("mod:*", "mod:ore_tin"), "* matches any run");
        check(!RetrogenConfig.matches("mod:*", "othermod:ore"), "namespace must match");
        check(RetrogenConfig.matches("mod:ore_?", "mod:ore_a") && !RetrogenConfig.matches("mod:ore_?", "mod:ore_ab"), "? is one char");
        check(RetrogenConfig.matches("a.b:c", "a.b:c") && !RetrogenConfig.matches("a.b:c", "axb:c"), "dots are literal");

        RetrogenConfig defaults = RetrogenConfig.parse(new StringReader("{}"));
        check(!defaults.enabled && !defaults.wantsFeature("any:thing"), "off and empty by default");
        check(defaults.wantsDimension("minecraft:the_nether"), "all dimensions by default");
        check(defaults.inhabitedOk(1200) && !defaults.inhabitedOk(1201), "inhabited limit is 1200 ticks by default");

        RetrogenConfig config = RetrogenConfig.parse(new StringReader(
                "{\"enabled\":true,\"features\":[\"fa:*\"],\"excludeFeatures\":[\"fa:big_*\"],"
                        + "\"dimensions\":[\"minecraft:overworld\"],\"maxInhabitedTicks\":-1,\"maxChunksPerTick\":0}"));
        check(config.wantsFeature("fa:skeleton") && !config.wantsFeature("fa:big_chamber"), "exclude wins over include");
        check(!config.wantsDimension("minecraft:the_end"), "dimension filter");
        check(config.inhabitedOk(Long.MAX_VALUE), "-1 means no inhabited limit");
        check(config.maxChunksPerTick == 1, "per-tick limits are at least 1");
        check(!defaults.wantsStructureSet("mss:sky_islands") && defaults.structureRadius == 8, "no structures by default");
        RetrogenConfig structures = RetrogenConfig.parse(new StringReader(
                "{\"structures\":[\"mss:*\"],\"excludeStructures\":[\"mss:big_*\"],\"structureRadius\":40}"));
        check(structures.wantsStructureSet("mss:sky_islands") && !structures.wantsStructureSet("mss:big_ship"),
                "structure exclude wins over include");
        check(!structures.wantsFeature("mss:sky_islands"), "structure patterns don't add features");
        check(structures.structureRadius == 16 && RetrogenConfig.parse(new StringReader("{\"structureRadius\":0}")).structureRadius == 1,
                "structure radius is clamped to 1-16");
        check(!RetrogenConfig.parse(new StringReader("null")).enabled, "empty file reads as defaults");
        Path shipped = Path.of("../../config/fotfskills-retrogen.json");
        if (Files.exists(shipped)) {
            RetrogenConfig pack = RetrogenConfig.load(shipped);
            check(pack.maxChunksPerTick == 2 && pack.claimBufferChunks == 2 && pack.structureRadius == 8 && pack.structures.isEmpty(), "the pack's config file parses");
        }

        // worldgen history
        RetrogenManifest manifest = new RetrogenManifest();
        check(manifest.epochFor(Set.of("a:1", "a:2")) == 0, "first start is epoch 0");
        check(manifest.epochFor(new HashSet<>(List.of("a:2", "a:1"))) == 0, "same features keep the epoch");
        check(manifest.epochFor(Set.of("a:1", "a:2", "fa:skeleton")) == 1, "a new mod starts a new epoch");
        Path file = Files.createTempDirectory("retrogen").resolve("data").resolve("fotfskills_retrogen.json");
        manifest.save(file);
        RetrogenManifest reread = RetrogenManifest.load(file);
        check(reread.epochs.equals(manifest.epochs) && reread.epochFor(Set.of("a:1", "a:2", "fa:skeleton")) == 1,
                "history survives a restart");
        check(RetrogenManifest.load(file.resolveSibling("missing.json")).epochs.isEmpty(), "no file: empty history");

        // which chunks still need a feature
        List<Set<String>> epochs = manifest.epochs;
        check(RetrogenState.legacy().needs("fa:skeleton", epochs), "chunks from before Retrogen get it");
        check(new RetrogenState(0, new HashSet<>()).needs("fa:skeleton", epochs), "chunks from before the mod get it");
        check(!new RetrogenState(1, new HashSet<>()).needs("fa:skeleton", epochs), "chunks made with the mod don't");
        check(!new RetrogenState(7, new HashSet<>()).needs("fa:skeleton", epochs), "unknown epoch (lost history) gets nothing");
        check(!new RetrogenState(RetrogenState.LEGACY, new HashSet<>(Set.of("fa:skeleton"))).needs("fa:skeleton", epochs),
                "never added twice");
        System.out.println("RetrogenLogicTest ok");
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
