package mimiandroidfix;

import javax.sound.sampled.AudioFormat;
import javax.sound.sampled.AudioSystem;
import javax.sound.sampled.Control;
import javax.sound.sampled.DataLine;
import javax.sound.sampled.LineListener;
import javax.sound.sampled.SourceDataLine;

/**
 * A SourceDataLine that discards audio but consumes it in real time.
 *
 * Used when the Java runtime has no audio mixers at all (Android launchers),
 * so MIMI's synthesizer can open instead of crashing. write() blocks for the
 * playback duration of the data, like a real line, so the synth's audio pusher
 * thread doesn't spin a core at 100%.
 */
public class SilentSourceDataLine implements SourceDataLine {
    private static final int DEFAULT_BUFFER_MS = 100;

    private AudioFormat format;
    private int bufferSize;
    private boolean open;
    private boolean running;
    private long framesWritten;
    private long startNanos;

    public SilentSourceDataLine(AudioFormat format) {
        this.format = format;
        this.bufferSize = bytesForMillis(format, DEFAULT_BUFFER_MS);
    }

    private static int bytesForMillis(AudioFormat f, int ms) {
        int frames = Math.max(1, (int) (f.getFrameRate() * ms / 1000f));
        return frames * Math.max(1, f.getFrameSize());
    }

    @Override
    public synchronized void open(AudioFormat format, int bufferSize) {
        this.format = format;
        this.bufferSize = bufferSize > 0 ? bufferSize : bytesForMillis(format, DEFAULT_BUFFER_MS);
        this.open = true;
    }

    @Override
    public void open(AudioFormat format) {
        open(format, -1);
    }

    @Override
    public void open() {
        open(format, -1);
    }

    @Override
    public int write(byte[] b, int off, int len) {
        int frameSize = Math.max(1, format.getFrameSize());
        int frames = len / frameSize;
        long sleepNanos;
        synchronized (this) {
            if (startNanos == 0) startNanos = System.nanoTime();
            framesWritten += frames;
            // Let up to one buffer's worth of audio run ahead of real time, then block.
            long playedNanos = (long) (framesWritten * 1_000_000_000d / format.getFrameRate());
            long bufferNanos = (long) ((bufferSize / frameSize) * 1_000_000_000d / format.getFrameRate());
            sleepNanos = startNanos + playedNanos - bufferNanos - System.nanoTime();
        }
        if (sleepNanos > 0) {
            try {
                Thread.sleep(sleepNanos / 1_000_000, (int) (sleepNanos % 1_000_000));
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
        return frames * frameSize;
    }

    @Override public synchronized void start() { running = true; }
    @Override public synchronized void stop() { running = false; }
    @Override public synchronized void close() { open = false; running = false; }
    @Override public synchronized boolean isOpen() { return open; }
    @Override public synchronized boolean isRunning() { return running; }
    @Override public synchronized boolean isActive() { return running; }
    @Override public void drain() { }
    @Override public synchronized void flush() { framesWritten = 0; startNanos = 0; }
    @Override public AudioFormat getFormat() { return format; }
    @Override public int getBufferSize() { return bufferSize; }
    @Override public int available() { return bufferSize; }
    @Override public synchronized int getFramePosition() { return (int) framesWritten; }
    @Override public synchronized long getLongFramePosition() { return framesWritten; }
    @Override public synchronized long getMicrosecondPosition() { return (long) (framesWritten * 1_000_000d / format.getFrameRate()); }
    @Override public float getLevel() { return AudioSystem.NOT_SPECIFIED; }
    @Override public DataLine.Info getLineInfo() { return new DataLine.Info(SourceDataLine.class, format); }
    @Override public Control[] getControls() { return new Control[0]; }
    @Override public boolean isControlSupported(Control.Type control) { return false; }
    @Override public Control getControl(Control.Type control) { throw new IllegalArgumentException("Unsupported control type: " + control); }
    @Override public void addLineListener(LineListener listener) { }
    @Override public void removeLineListener(LineListener listener) { }
}
