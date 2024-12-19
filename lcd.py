from gpiozero import OutputDevice
from time import sleep

LCD_RS = OutputDevice(25)
LCD_E = OutputDevice(24)
LCD_D4 = OutputDevice(23)
LCD_D5 = OutputDevice(18)
LCD_D6 = OutputDevice(15)
LCD_D7 = OutputDevice(14)

LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0

E_PULSE = 0.0005
E_DELAY = 0.0005

def lcd_init():
    lcd_byte(0x33, LCD_CMD)
    lcd_byte(0x32, LCD_CMD)
    lcd_byte(0x28, LCD_CMD)
    lcd_byte(0x0C, LCD_CMD)
    lcd_byte(0x06, LCD_CMD)
    lcd_byte(0x01, LCD_CMD)
    sleep(E_DELAY)
    
def lcd_byte(bits, mode):
    LCD_RS.value = mode
    
    #send high nibble
    LCD_D4.value = bool(bits & 0x10)
    LCD_D5.value = bool(bits & 0x20)
    LCD_D6.value = bool(bits & 0x40)
    LCD_D7.value = bool(bits & 0x80)
    lcd_toggle_enable()
    
    #send low nibble
    LCD_D4.value = bool(bits & 0x01)
    LCD_D5.value = bool(bits & 0x02)
    LCD_D6.value = bool(bits & 0x04)
    LCD_D7.value = bool(bits & 0x08)
    lcd_toggle_enable()
    
def lcd_toggle_enable():
    sleep(E_DELAY)
    LCD_E.on()
    sleep(E_PULSE)
    LCD_E.off()
    sleep(E_DELAY)
    
def lcd_string(message, line):
#     messasge = message.ljust(LCD_WIDTH, " ")
#     
#     lcd_byte(line, LCD_CMD)
#     
#     for i in range(LCD_WIDTH):
#         lcd_byte(ord(message[i]), LCD_CHR)
       if len(message) > LCD_WIDTH:
           message = message[:LCD_WIDTH]
       else:
           message = message.ljust(LCD_WIDTH, " ")
           
       lcd_byte(line, LCD_CMD)
       
       for i in range(LCD_WIDTH):
           lcd_byte(ord(message[i]), LCD_CHR)
        
if __name__ == '__main__':
    lcd_init()
    while True:
        lcd_string("Raspberry Pi 4", LCD_LINE_1)
        lcd_string("16x2 LCD Display", LCD_LINE_2)
        sleep(5)
        

