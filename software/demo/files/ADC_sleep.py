from machine import Pin, ADC
import utime
adc = ADC(Pin(26, mode=Pin.IN))

while True:
    start=utime.ticks_us()
    print(adc.read_u16())
    stop=utime.ticks_us()
    utime.sleep_us(1000-stop+start)

