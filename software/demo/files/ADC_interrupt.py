from machine import Timer, Pin, ADC


def interruption_handler(pin):
     print(adc.read_u16())


if __name__ == "__main__":
    adc = ADC(Pin(26, mode=Pin.IN))
    soft_timer = Timer(mode=Timer.PERIODIC, period=1, callback=interruption_handler)

    
