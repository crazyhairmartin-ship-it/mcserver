package mimiandroidfix.mixin;

import javax.sound.sampled.AudioFormat;
import javax.sound.sampled.AudioSystem;
import javax.sound.sampled.DataLine;
import javax.sound.sampled.SourceDataLine;

import org.apache.commons.lang3.tuple.ImmutablePair;
import org.apache.commons.lang3.tuple.Pair;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import mimiandroidfix.MimiAndroidFix;
import mimiandroidfix.SilentSourceDataLine;

@Mixin(targets = "io.github.tofodroid.mods.mimi.client.midi.AudioOutputDeviceManager", remap = false)
public class AudioOutputDeviceManagerMixin {
    private static final AudioFormat FALLBACK_FORMAT = new AudioFormat(22050f, 16, 2, true, false);

    @Inject(method = "getOutputFormatLine", at = @At("RETURN"), cancellable = true, remap = false)
    private void mimiandroidfix$silentLineWhenNoAudio(CallbackInfoReturnable<Pair<AudioFormat, SourceDataLine>> cir) {
        Pair<AudioFormat, SourceDataLine> result = cir.getReturnValue();
        if (result != null && result.getRight() != null) return;

        AudioFormat format = result != null && result.getLeft() != null ? result.getLeft() : FALLBACK_FORMAT;
        // Only step in when the JVM genuinely has no audio output (Android). On a PC with
        // a working sound system MIMI's own default-device fallback is left alone.
        if (AudioSystem.isLineSupported(new DataLine.Info(SourceDataLine.class, format))) return;

        MimiAndroidFix.LOGGER.warn("No Java audio output available; giving MIMI a silent line (instruments will be muted).");
        cir.setReturnValue(ImmutablePair.of(format, new SilentSourceDataLine(format)));
    }
}
