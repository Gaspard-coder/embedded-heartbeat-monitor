# This repository contains all of the necessary file to make a working heartbeat sensor
- Schematics
- PCB design files
- Embedded code running on MCUs

## Embedded software (`software/hsensor/`)

MicroPython application running on a Raspberry Pi Pico. It samples the
output of the TCRT5000 reflectance sensor (amplified by an op-amp), detects
heartbeats and displays the BPM together with the live waveform on the
0.96" ST7735 LCD.

### Files
- `ST7735.py` — driver for the 0.96" LCD (SPI, same wiring as the demo:
  DC=GP8, CS=GP9, SCK=GP10, MOSI=GP11, RST=GP12, BL=GP13).
- `main.py` — acquisition, heart rate detection and display loop.

### Wiring
- TCRT5000 + op-amp output → **pin 31 (GPIO26 / ADC0)** of the Pico.
- LCD: SPI1 on GP8–GP13 (see above).

### How the algorithm works

1. **Sampling.** `ADC(Pin(26))` is read every 10 ms (≈100 Hz), which is
   well above the highest expected heart-beat frequency (~3 Hz at 180 BPM)
   and matches the cutoff of the analog front-end.

2. **DC removal (high-pass filter).** The raw photoplethysmographic signal
   coming from the TCRT5000 is dominated by a large DC component (ambient
   reflectance of the skin) with a small pulsatile AC component on top. We
   subtract a slowly-tracking baseline computed as an exponential moving
   average:

   ```
   baseline ← (31 · baseline + raw) / 32
   x       ← raw − baseline
   ```

   With `α = 1/32` at 100 Hz, the equivalent cutoff is roughly 0.5 Hz —
   slow enough to leave the heartbeats untouched but fast enough to track
   drift in finger pressure or ambient light.

3. **Peak detection.** A heartbeat appears as a local maximum on the
   filtered signal `x`. For every new sample we check the *previous*
   sample: if it is greater than its two neighbours and above
   `PEAK_THRESHOLD`, it is declared a peak.

4. **Refractory period.** Once a peak has been detected, any new peak
   occurring within 300 ms is ignored. This caps the detected rate at
   200 BPM and avoids counting the dicrotic notch (the small secondary
   bump after each beat) as a separate heartbeat.

5. **BPM computation.** The time difference `dt` between two consecutive
   accepted peaks is pushed into a rolling buffer of the last 5
   intervals. The current heart rate is the average of that buffer:

   ```
   BPM = 60000 / mean(intervals_ms)
   ```

   Averaging over several beats smooths jitter due to noise and gives a
   stable reading on the display. If no peak is seen for more than 2 s
   (i.e. < 30 BPM, almost certainly a lost-contact event) the buffer is
   cleared and the BPM goes back to `--`.

6. **Display.** The LCD is refreshed every 200 ms — redrawing the full
   framebuffer is slow, so we deliberately do not refresh at the sampling
   rate. The top of the screen shows `BPM: XX`, and below it the last
   160 filtered samples are plotted (oldest on the left, newest on the
   right) with a blue zero-line.

### Tuning knobs (top of `main.py`)
- `PEAK_THRESHOLD` — minimum amplitude (in ADC LSB on the filtered signal)
  for a sample to qualify as a peak. Lower it if the analog gain is small,
  raise it if the signal is noisy.
- `BPM_WINDOW` — number of inter-beat intervals averaged.
- `REFRACTORY_MS` / `MAX_INTERVAL_MS` — accepted BPM range (currently
  30–200 BPM).
- `v // 30` in the plotting code — vertical scale of the waveform on the
  LCD.

### Running
Copy `ST7735.py` and `main.py` to the Pico (Thonny, `mpremote cp`, …).
`main.py` runs automatically at boot.
