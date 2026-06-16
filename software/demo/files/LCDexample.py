from machine import Pin,SPI,PWM,Timer, Pin, ADC
from ST7735 import LCD_0inch96
import framebuf
import time


#color is BGR
RED = 0x00F8
GREEN = 0xE007
BLUE = 0x1F00
WHITE = 0xFFFF
BLACK = 0x0000

lcd = LCD_0inch96()   #Initializing the scree n
lcd.fill(BLACK)       #clearing any exsiting diplay
    
#First example: displaying text
lcd.text("TELECOM-PARIS!",35,15,GREEN)
lcd.text("This is:",50,35,RED)    
lcd.text("Pico-LCD-0.96",30,55,BLUE)
lcd.display() #this command launches the display
time.sleep(2) #keeping the display for 2 sec

#second example: displaying 2 blue rectangles
lcd.fill(BLACK)
lcd.hline(10,10,140,BLUE)
lcd.hline(10,70,140,BLUE)
lcd.vline(10,10,60,BLUE)
lcd.vline(150,10,60,BLUE)
    
lcd.hline(0,0,160,BLUE)
lcd.hline(0,79,160,BLUE)
lcd.vline(0,0,80,BLUE)
lcd.vline(159,0,80,BLUE)
lcd.display()
time.sleep(2)


#Third example: displaying a custom line of pixels    
lcd.fill(BLACK)
for i in range(80):
  lcd.pixel(i,2*i,GREEN)

lcd.SetWindows(0,0,100,50)
lcd.display()
time.sleep(3)     
    
#Fourth example displaying ADC output   
lcd.fill(BLACK)
adc = ADC(Pin(26, mode=Pin.IN))
lcd.text(str(adc.read_u16()),55,15,GREEN)
lcd.display()
time.sleep(3)       
