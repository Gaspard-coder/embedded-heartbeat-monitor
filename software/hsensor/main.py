from machine import Pin, SPI, PWM, Timer, ADC
from ST7735 import LCD_0inch96
import framebuf
import utime


# color is BGR
RED   = 0x00F8
GREEN = 0xE007
BLUE  = 0x1F00
WHITE = 0xFFFF
BLACK = 0x0000

# Sampling configuration
SAMPLE_PERIOD_US = 20000   # 10 ms -> 100 Hz sampling
SAMPLE_PERIOD_MS = 20
WAVEFORM_LEN = 160         # screen width in pixels
BPM_WINDOW = 10             # number of intervals averaged for BPM
PEAK_THRESHOLD = 3500       # AC amplitude (in u16 LSB) to qualify a peak
REFRACTORY_MS = 300        # min time between two peaks (-> max 200 BPM)
MAX_INTERVAL_MS = 2000     # -> min 30 BPM

# ADC on GPIO26 (physical pin 31)
adc = ADC(Pin(26, mode=Pin.IN))

# Initialize LCD
lcd = LCD_0inch96()
lcd.fill(BLACK)
lcd.text("Heart Rate", 40, 15, GREEN)
lcd.text("TCRT5000 PPG", 30, 35, BLUE)
lcd.text("Initializing...", 20, 55, WHITE)
lcd.display()
utime.sleep(1)

# Circular buffer of filtered samples for display
waveform = [0] * WAVEFORM_LEN
sample_idx = 0

# Peak detection state
baseline = adc.read_u16()   # running mean (DC component)
prev_x = 0
prev_prev_x = 0
last_peak_ms = 0
intervals = []
bpm = 0

last_display_ms = utime.ticks_ms()

while True:
    t0 = utime.ticks_us()

    # Acquire raw sample
    raw = adc.read_u16()
    t_ms = utime.ticks_ms()

    # High-pass filter: subtract a slowly tracking baseline
    # alpha = 1/32 -> cutoff ~ fs/(2*pi*32) ~= 0.5 Hz at 100 Hz sampling
    baseline = (baseline * 31 + raw) >> 5
    x = raw - baseline

    # Peak detection on the previous sample (local maximum above threshold)
    if (prev_x > PEAK_THRESHOLD) and (prev_x > prev_prev_x) and (prev_x > x):
        peak_time = t_ms - SAMPLE_PERIOD_MS
        if last_peak_ms != 0:
            dt = peak_time - last_peak_ms
            if (dt > REFRACTORY_MS) and (dt < MAX_INTERVAL_MS):
                intervals.append(dt)
                if len(intervals) > BPM_WINDOW:
                    intervals.pop(0)
                avg = sum(intervals) / len(intervals)
                bpm = int(60000 / avg)
                last_peak_ms = peak_time
            elif dt >= MAX_INTERVAL_MS:
                # gap too long -> restart from this peak
                last_peak_ms = peak_time
                intervals = []
                bpm = 0
        else:
            last_peak_ms = peak_time

    prev_prev_x = prev_x
    prev_x = x

    # Save filtered sample for display
    waveform[sample_idx] = x
    sample_idx = (sample_idx + 1) % WAVEFORM_LEN

    # Refresh display every 200 ms (don't redraw at full rate -> too slow)
    if utime.ticks_diff(t_ms, last_display_ms) > 200:
        lcd.fill(BLACK)
        if bpm > 0:
            lcd.text("BPM: " + str(bpm), 35, 5, RED)
        else:
            lcd.text("BPM: --", 45, 5, RED)

        # Plot the waveform centered around y=50, oldest sample on the left
        for i in range(WAVEFORM_LEN):
            idx = (sample_idx + i) % WAVEFORM_LEN
            v = waveform[idx]
            y = 50 - (v // 30)
            if y < 20:
                y = 20
            if y > 79:
                y = 79
            lcd.pixel(i, y, GREEN)

        # Baseline line
        lcd.hline(0, 50, WAVEFORM_LEN, BLUE)

        lcd.display()
        last_display_ms = t_ms

    # Keep the sample period constant
    elapsed = utime.ticks_diff(utime.ticks_us(), t0)
    sleep_us = SAMPLE_PERIOD_US - elapsed
    if sleep_us > 0:
        utime.sleep_us(sleep_us)
